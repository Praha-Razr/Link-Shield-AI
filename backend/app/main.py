import json
import csv
import io
import re
import uuid
import hashlib
from datetime import datetime, timezone
from typing import Optional, List, Union
from fastapi import FastAPI, Depends, HTTPException, Query, UploadFile, File, Form, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, text

from app.config import settings
from app.database import engine, Base, get_db
from app.models import Case, Indicator, Identifier, SimilarityLink, case_identifiers, User
from app.schemas import (
    MessageAnalyzeRequest,
    URLAnalyzeRequest,
    WebsiteAnalyzeRequest,
    AnalysisResult,
    CaseListResponse,
    CaseSummaryItem,
    CaseDetailResponse,
    DashboardStatsResponse,
    IntelligenceGraphResponse,
    HeatlistResponse,
    NotesUpdateRequest,
    DemoClearRequest,
    ImportResponse,
    AssistantAskRequest,
    AssistantAskResponse,
    AssistantStatusResponse,
    IndicatorSchema,
    IdentifierSchema,
    SimilarityLinkSchema,
    RelatedCaseSchema,
    EvidenceSchema,
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse,
    TokenResponse,
    AwarenessCategoryStat,
    PublicAwarenessResponse
)
from app.analyzers.message import analyze_message_content
from app.analyzers.url import analyze_url_target
from app.analyzers.website import analyze_website_content
from app.analyzers.ai_opinion import evaluate_ai_second_opinion
from app.linker import (
    save_case_with_relations,
    get_top_identifiers_heatlist,
    build_intelligence_graph,
    get_dashboard_statistics
)
from app.security import validate_uploaded_file
from app.reports.pdf import generate_case_pdf_report
from app.allowlist import is_ifsc_code, is_legitimate_identifier, is_linkable_identifier
from app.assistant import ask_assistant, get_assistant_status
from app.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    require_officer,
    require_citizen_or_officer,
    authenticate_user
)
import logging

logger = logging.getLogger(__name__)

# Create tables if not present
Base.metadata.create_all(bind=engine)

# Auto-migrate columns for existing SQLite databases
try:
    with engine.connect() as conn:
        result = conn.execute(text("PRAGMA table_info(cases)")).fetchall()
        cols = [r[1] for r in result]
        if "submitted_by" not in cols:
            conn.execute(text("ALTER TABLE cases ADD COLUMN submitted_by VARCHAR(36) REFERENCES users(id)"))
            conn.commit()
except Exception as _schema_err:
    logger.warning(f"Schema migration check: {_schema_err}")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="LINKSHIELD AI - Scam Message & Phishing Link Detection with Fraudulent Website Analysis"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]
)

def format_case_detail(case: Case, db: Session) -> CaseDetailResponse:
    # Indicators
    indicators = [
        IndicatorSchema(id=ind.id, name=ind.name, points=ind.points, explanation=ind.explanation)
        for ind in case.indicators
    ]
    # Identifiers
    identifiers = [
        IdentifierSchema(
            id=ident.id,
            type=ident.type,
            value=ident.value,
            is_legitimate=is_legitimate_identifier(ident.type, ident.value),
            is_linkable=is_linkable_identifier(ident.type, ident.value)
        )
        for ident in case.identifiers
    ]
    # Similarity links
    sim_links = (
        db.query(SimilarityLink)
        .filter(or_(SimilarityLink.case_id_a == case.id, SimilarityLink.case_id_b == case.id))
        .all()
    )
    sim_schemas = []
    for sl in sim_links:
        partner_id = sl.case_id_b if sl.case_id_a == case.id else sl.case_id_a
        partner = db.query(Case).filter(Case.id == partner_id).first()
        sim_schemas.append(SimilarityLinkSchema(
            case_id=partner_id,
            similarity=sl.similarity,
            subject=partner.subject if partner else None,
            risk_level=partner.risk_level if partner else None
        ))

    # Related cases sharing identifiers (excluding IFSC branch codes & legitimate entities)
    related_map = {}
    for ident in case.identifiers:
        if not is_linkable_identifier(ident.type, ident.value):
            continue
        for other_c in ident.cases:
            if other_c.id != case.id:
                if other_c.id not in related_map:
                    related_map[other_c.id] = {
                        "case_id": other_c.id,
                        "subject": other_c.subject,
                        "risk_level": other_c.risk_level,
                        "input_type": other_c.input_type,
                        "shared_identifiers": []
                    }
                related_map[other_c.id]["shared_identifiers"].append(f"{ident.type}: {ident.value}")
    related_cases = [RelatedCaseSchema(**data) for data in related_map.values()]

    ai_opinion_data = None
    if getattr(case, "ai_second_opinion", None):
        try:
            ai_opinion_data = json.loads(case.ai_second_opinion)
        except Exception:
            pass

    return CaseDetailResponse(
        id=case.id,
        subject=case.subject,
        input_type=case.input_type,
        raw_content=case.raw_content,
        content_sha256=case.content_sha256,
        created_at=case.created_at,
        risk_score=case.risk_score,
        risk_level=case.risk_level,
        category=case.category,
        status=case.status,
        is_demo=case.is_demo,
        language=case.language,
        investigator_notes=case.investigator_notes,
        indicators=indicators,
        identifiers=identifiers,
        similarity_links=sim_schemas,
        related_cases=related_cases,
        ai_second_opinion=ai_opinion_data
    )

@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# --- Authentication Endpoints ---
@app.post("/api/auth/register", response_model=TokenResponse)
def register_user_endpoint(
    req: UserRegisterRequest,
    response: Response,
    db: Session = Depends(get_db)
):
    norm_username = req.username.strip().lower()
    if len(norm_username) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters.")
    if len(req.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters.")

    existing = db.query(User).filter(User.username == norm_username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username is already registered.")

    now_utc = datetime.now(timezone.utc)
    user_id = str(uuid.uuid4())
    new_user = User(
        id=user_id,
        username=norm_username,
        display_name=req.display_name.strip(),
        password_hash=hash_password(req.password),
        role="citizen",  # Strictly force citizen role on registration
        is_active=True,
        created_at=now_utc,
        last_login=now_utc,
        failed_attempts=0
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token(data={"sub": new_user.id, "role": new_user.role, "username": new_user.username})
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(new_user)
    )

@app.post("/api/auth/login", response_model=TokenResponse)
def login_user_endpoint(
    req: UserLoginRequest,
    response: Response,
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, req.username, req.password)
    token = create_access_token(data={"sub": user.id, "role": user.role, "username": user.username})
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )

@app.post("/api/auth/logout")
def logout_user_endpoint(response: Response):
    response.delete_cookie(key="access_token", samesite="lax")
    return {"status": "success", "message": "Logged out successfully"}

@app.get("/api/auth/me", response_model=UserResponse)
def get_current_user_endpoint(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)

# --- Citizen & Officer Public Awareness Endpoint ---
@app.get("/api/public/awareness", response_model=PublicAwarenessResponse)
def get_public_awareness_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_citizen_or_officer)
):
    """
    Returns high-level aggregate scam statistics and safety advisories for Citizen awareness.
    Strictly aggregate-only: NEVER returns individual phone numbers, UPI IDs, emails, domains, or case records.
    """
    total_cases = db.query(Case).count()
    high_risk_count = db.query(Case).filter(Case.risk_level == "HIGH").count()
    medium_risk_count = db.query(Case).filter(Case.risk_level == "MEDIUM").count()
    low_risk_count = db.query(Case).filter(Case.risk_level == "LOW").count()

    cat_counts = (
        db.query(Case.category, func.count(Case.id))
        .group_by(Case.category)
        .all()
    )
    category_labels = {
        "electricity_scam": "Electricity Bill Fraud",
        "fake_kyc": "Banking KYC Expiry",
        "job_fraud": "Part-Time Task & Job Scam",
        "lottery_prize": "Lottery & Gift Fraud",
        "loan_fraud": "Instant Loan / Extortion",
        "investment_fraud": "Guaranteed Return Schemes",
        "phishing_link": "Credential Phishing Links",
        "parcel_scam": "Customs Parcel Impersonation",
        "illegal_betting": "Unlicensed Gaming & Betting",
        "general": "General Scam Communications"
    }
    categories = []
    for cat, cnt in cat_counts:
        cat_key = cat or "general"
        pct = round((cnt / total_cases * 100), 1) if total_cases > 0 else 0.0
        categories.append(AwarenessCategoryStat(
            category=cat_key,
            label=category_labels.get(cat_key, cat_key.replace("_", " ").title()),
            count=cnt,
            percentage=pct
        ))
    categories.sort(key=lambda x: x.count, reverse=True)

    top_threat_vectors = [
        "Urgent electricity power cut threats requesting APK download",
        "Fake bank SMS demanding PAN/Aadhaar update via shortlinks",
        "Telegram/WhatsApp daily part-time YouTube rating tasks",
        "Customs department courier parcel impound impersonation calls"
    ]
    advisory = (
        "Never share OTPs, UPI PINs, or net banking passwords with anyone. "
        "Official government agencies and banks will never ask you to install APK files or click unverified links. "
        "Immediately report any financial cyber fraud to the National Cybercrime Portal (cybercrime.gov.in) or call 1930."
    )

    return PublicAwarenessResponse(
        total_cases=total_cases,
        high_risk_count=high_risk_count,
        medium_risk_count=medium_risk_count,
        low_risk_count=low_risk_count,
        categories=categories,
        top_threat_vectors=top_threat_vectors,
        safety_advisory=advisory
    )

@app.post("/api/analyze/message", response_model=AnalysisResult)
def analyze_message_endpoint(
    req: MessageAnalyzeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_citizen_or_officer)
):
    analysis_data = analyze_message_content(req.content, subject=req.subject)
    _, analysis_data = evaluate_ai_second_opinion(req.content, "message", analysis_data)
    case = save_case_with_relations(db, analysis_data, is_demo=False, submitted_by=current_user.id)

    evidence = EvidenceSchema(
        content_sha256=case.content_sha256,
        timestamp_utc=case.created_at.isoformat(),
        char_count=len(case.raw_content),
        excerpt=case.raw_content[:200]
    )

    detail = format_case_detail(case, db)
    sim_matches = [] if current_user.role == "citizen" else detail.similarity_links

    return AnalysisResult(
        case_id=case.id,
        subject=case.subject,
        input_type=case.input_type,
        risk_score=case.risk_score,
        risk_level=case.risk_level,
        category=case.category,
        language=case.language,
        indicators=detail.indicators,
        extracted_identifiers=detail.identifiers,
        suspicious_phrases=analysis_data.get("suspicious_phrases", []),
        safety_recommendations=analysis_data.get("safety_recommendations", []),
        verified_official=analysis_data.get("verified_official"),
        verified_links=analysis_data.get("verified_links", []),
        evidence=evidence,
        similarity_matches=sim_matches,
        ai_second_opinion=analysis_data.get("ai_second_opinion")
    )

@app.post("/api/analyze/url", response_model=AnalysisResult)
def analyze_url_endpoint(
    req: URLAnalyzeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_citizen_or_officer)
):
    analysis_data = analyze_url_target(
        req.url,
        subject=req.subject,
        perform_live_check=req.perform_live_check
    )
    _, analysis_data = evaluate_ai_second_opinion(req.url, "url", analysis_data)
    case = save_case_with_relations(db, analysis_data, is_demo=False, submitted_by=current_user.id)

    evidence = EvidenceSchema(
        content_sha256=case.content_sha256,
        timestamp_utc=case.created_at.isoformat(),
        char_count=len(case.raw_content),
        excerpt=case.raw_content[:200]
    )

    detail = format_case_detail(case, db)
    sim_matches = [] if current_user.role == "citizen" else detail.similarity_links

    return AnalysisResult(
        case_id=case.id,
        subject=case.subject,
        input_type=case.input_type,
        risk_score=case.risk_score,
        risk_level=case.risk_level,
        category=case.category,
        language=case.language,
        indicators=detail.indicators,
        extracted_identifiers=detail.identifiers,
        suspicious_phrases=analysis_data.get("suspicious_phrases", []),
        safety_recommendations=analysis_data.get("safety_recommendations", []),
        verified_official=analysis_data.get("verified_official"),
        verified_links=analysis_data.get("verified_links", []),
        evidence=evidence,
        similarity_matches=sim_matches,
        live_checks=analysis_data.get("live_checks", {}),
        ai_second_opinion=analysis_data.get("ai_second_opinion")
    )

@app.post("/api/analyze/website", response_model=AnalysisResult)
async def analyze_website_endpoint(
    request: Request,
    url: Optional[str] = Form(None),
    html_content: Optional[str] = Form(None),
    subject: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_citizen_or_officer)
):
    target_url = url
    target_html = html_content
    target_subject = subject

    # Support JSON payload if content-type is application/json
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            body = await request.json()
            target_url = body.get("url")
            target_html = body.get("html_content") or body.get("raw_html")
            target_subject = body.get("subject")
        except Exception:
            pass

    # Handle file upload if provided
    if file:
        file_bytes = await file.read()
        is_valid, reason = validate_uploaded_file(file.filename or "upload.html", len(file_bytes), file_bytes)
        if not is_valid:
            raise HTTPException(status_code=400, detail=reason)
        try:
            target_html = file_bytes.decode("utf-8", errors="replace")
        except Exception:
            target_html = file_bytes.decode("latin-1", errors="replace")
        if not target_subject:
            target_subject = f"File Upload: {file.filename}"

    if not target_url and not target_html:
        raise HTTPException(
            status_code=400,
            detail="Either 'url', 'html_content', or an uploaded HTML file must be provided."
        )

    analysis_data = analyze_website_content(
        url=target_url,
        html_content=target_html,
        subject=target_subject
    )
    web_sample = target_html or target_url or ""
    _, analysis_data = evaluate_ai_second_opinion(web_sample, "website", analysis_data)

    case = save_case_with_relations(db, analysis_data, is_demo=False, submitted_by=current_user.id)

    evidence = EvidenceSchema(
        content_sha256=case.content_sha256,
        timestamp_utc=case.created_at.isoformat(),
        char_count=len(case.raw_content),
        excerpt=case.raw_content[:200]
    )

    detail = format_case_detail(case, db)
    sim_matches = [] if current_user.role == "citizen" else detail.similarity_links

    return AnalysisResult(
        case_id=case.id,
        subject=case.subject,
        input_type=case.input_type,
        risk_score=case.risk_score,
        risk_level=case.risk_level,
        category=case.category,
        language=case.language,
        indicators=detail.indicators,
        extracted_identifiers=detail.identifiers,
        suspicious_phrases=analysis_data.get("suspicious_phrases", []),
        safety_recommendations=analysis_data.get("safety_recommendations", []),
        verified_official=analysis_data.get("verified_official"),
        verified_links=analysis_data.get("verified_links", []),
        evidence=evidence,
        similarity_matches=sim_matches,
        live_checks=analysis_data.get("live_checks", {}),
        ai_second_opinion=analysis_data.get("ai_second_opinion")
    )

@app.get("/api/dashboard/stats", response_model=DashboardStatsResponse)
def get_dashboard_stats_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_officer)
):
    return get_dashboard_statistics(db)

def normalize_case_id_query(q_str: str) -> list[str]:
    """
    Normalizes a search query for case IDs (e.g. LS0032, ls-0032, 'LS 0032', 'ls0032', 'DEMO0001', 'demo-001').
    Returns candidate canonical IDs.
    """
    clean = re.sub(r'[\s\-_]', '', q_str).upper()
    candidates = []
    m = re.match(r'^([A-Z]+)(\d+)$', clean)
    if m:
        prefix, num_str = m.group(1), m.group(2)
        num_val = int(num_str)
        for width in (1, 2, 3, 4, 5):
            candidates.append(f"{prefix}-{num_val:0{width}d}")
        candidates.append(f"{prefix}-{num_str}")
        candidates.append(f"{prefix}-{num_val}")
    return list(set(candidates))

@app.get("/api/cases", response_model=CaseListResponse)
def get_cases_endpoint(
    q: Optional[str] = Query(None, description="Search term in ID, subject, content or identifiers"),
    risk: Optional[str] = Query(None, description="Risk level (LOW, MEDIUM, HIGH)"),
    category: Optional[str] = Query(None, description="Category filter"),
    input_type: Optional[str] = Query(None, description="message, url, or website"),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    include_demo: bool = Query(True, description="Whether to include demo cases"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_officer)
):
    query = db.query(Case)

    if not include_demo:
        query = query.filter(Case.is_demo == False)

    if q and q.strip():
        trimmed_q = q.strip()
        search_pattern = f"%{trimmed_q}%"
        norm_term = re.sub(r'[\s\-_]', '', trimmed_q).lower()
        id_candidates = normalize_case_id_query(trimmed_q)
        norm_id = func.replace(func.replace(func.replace(func.lower(Case.id), '-', ''), ' ', ''), '_', '')

        search_conditions = [
            Case.subject.ilike(search_pattern),
            Case.raw_content.ilike(search_pattern),
            Case.id.ilike(search_pattern),
            norm_id.like(f"%{norm_term}%"),
            Case.identifiers.any(Identifier.value.ilike(search_pattern))
        ]
        if id_candidates:
            search_conditions.append(Case.id.in_(id_candidates))

        query = query.filter(or_(*search_conditions))

    if risk:
        query = query.filter(Case.risk_level == risk.upper())

    if category:
        query = query.filter(Case.category == category)

    if input_type:
        query = query.filter(Case.input_type == input_type.lower())

    if date_from:
        query = query.filter(Case.created_at >= date_from)
    if date_to:
        query = query.filter(Case.created_at <= date_to)

    total = query.count()
    cases = (
        query.order_by(Case.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    summary_items = []
    for c in cases:
        summary_items.append(CaseSummaryItem(
            id=c.id,
            subject=c.subject,
            input_type=c.input_type,
            created_at=c.created_at,
            risk_score=c.risk_score,
            risk_level=c.risk_level,
            category=c.category,
            status=c.status,
            is_demo=c.is_demo,
            language=c.language,
            identifier_count=len(c.identifiers),
            indicator_count=len(c.indicators)
        ))

    return CaseListResponse(
        total=total,
        page=page,
        page_size=page_size,
        cases=summary_items
    )

@app.get("/api/cases/{case_id}", response_model=CaseDetailResponse)
def get_case_detail_endpoint(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_officer)
):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail=f"Case with ID '{case_id}' not found.")
    return format_case_detail(case, db)

@app.patch("/api/cases/{case_id}/notes")
@app.post("/api/cases/{case_id}/notes")
def update_case_notes_endpoint(
    case_id: str,
    req: NotesUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_officer)
):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail=f"Case with ID '{case_id}' not found.")
    case.investigator_notes = req.notes
    db.commit()
    return {
        "status": "success",
        "case_id": case.id,
        "investigator_notes": case.investigator_notes
    }

@app.get("/api/intelligence/graph", response_model=IntelligenceGraphResponse)
def get_intelligence_graph_endpoint(
    include_demo: bool = Query(True),
    min_cases: int = Query(2, ge=1, description="Minimum cases an identifier must appear in (1=all, 2=shared)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_officer)
):
    graph = build_intelligence_graph(db, include_demo=include_demo, min_cases=min_cases)
    return graph

@app.get("/api/intelligence/heatlist", response_model=HeatlistResponse)
def get_heatlist_endpoint(
    type: Optional[str] = Query(None, description="Identifier type filter (domain, phone, upi, etc.)"),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    include_demo: bool = Query(True),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_officer)
):
    items = get_top_identifiers_heatlist(
        db,
        identifier_type=type,
        date_from=date_from,
        date_to=date_to,
        include_demo=include_demo,
        limit=limit
    )
    return HeatlistResponse(total=len(items), items=items)

@app.get("/api/assistant/status", response_model=AssistantStatusResponse)
def get_assistant_status_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_officer)
):
    """
    Returns the real connection status of Gemini API (Officer only).
    Performs a tiny live test call without exposing any API keys.
    """
    return get_assistant_status(db)

@app.post("/api/assistant/ask", response_model=AssistantAskResponse)
def ask_assistant_endpoint(
    req: AssistantAskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_officer)
):
    """
    Investigation Assistant Chat Endpoint.
    Deterministic, offline rule-based query engine with evidence verification.
    Supports grounded multi-turn Gemini Enhanced Mode with tool calling.
    """
    history_dicts = [m.model_dump() for m in req.history] if req.history else []
    return ask_assistant(db, question=req.question, use_enhanced=req.use_enhanced, history=history_dicts)

@app.post("/api/demo/load")
def load_demo_data_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_officer)
):
    """
    Idempotent loader for the synthetic demo dataset.
    Runs each record through the REAL analysis pipeline.
    Repeated clicks will NOT duplicate records.
    """
    if not settings.DEMO_DATASET_PATH.exists():
        raise HTTPException(
            status_code=500,
            detail=f"Demo dataset not found at {settings.DEMO_DATASET_PATH}"
        )

    with open(settings.DEMO_DATASET_PATH, "r", encoding="utf-8") as f:
        records = json.load(f)

    loaded_count = 0
    skipped_count = 0

    for rec in records:
        cid = rec["case_id"]
        # Check idempotency
        existing = db.query(Case).filter(Case.id == cid).first()
        if existing:
            skipped_count += 1
            continue

        input_type = rec.get("input_type", "message")
        content = rec.get("submitted_content", "")
        subject = f"DEMO: {rec.get('category', 'sample').replace('_', ' ').title()}"

        # Run REAL analysis pipeline
        if input_type == "message":
            analysis_data = analyze_message_content(content, subject=subject)
        elif input_type == "url":
            analysis_data = analyze_url_target(content, subject=subject, perform_live_check=False)
        elif input_type == "website":
            analysis_data = analyze_website_content(html_content=content, subject=subject)
        else:
            analysis_data = analyze_message_content(content, subject=subject)

        save_case_with_relations(
            db=db,
            analysis_data=analysis_data,
            is_demo=True,
            override_case_id=cid
        )
        loaded_count += 1

    return {
        "status": "success",
        "message": f"Demo dataset processed: {loaded_count} loaded, {skipped_count} already existed.",
        "loaded_count": loaded_count,
        "skipped_count": skipped_count,
        "total_demo_records": len(records)
    }

@app.post("/api/demo/clear")
def clear_demo_data_endpoint(
    req: DemoClearRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_officer)
):
    """
    Deletes ONLY is_demo records. Requires {"confirm": true}.
    """
    if not req.confirm:
        raise HTTPException(
            status_code=400,
            detail="Confirmation required. Set {'confirm': true} to delete demo records."
        )

    demo_cases = db.query(Case).filter(Case.is_demo == True).all()
    demo_count = len(demo_cases)

    # Delete similarity links referencing demo cases
    demo_ids = [c.id for c in demo_cases]
    if demo_ids:
        db.query(SimilarityLink).filter(
            or_(SimilarityLink.case_id_a.in_(demo_ids), SimilarityLink.case_id_b.in_(demo_ids))
        ).delete(synchronize_session=False)

        # Delete cases (cascades to indicators and case_identifiers)
        db.query(Case).filter(Case.is_demo == True).delete(synchronize_session=False)

        # Clean up orphaned identifiers
        orphaned_ids = (
            db.query(Identifier.id)
            .outerjoin(case_identifiers, Identifier.id == case_identifiers.c.identifier_id)
            .filter(case_identifiers.c.case_id == None)
            .all()
        )
        if orphaned_ids:
            orph_list = [oid for (oid,) in orphaned_ids]
            db.query(Identifier).filter(Identifier.id.in_(orph_list)).delete(synchronize_session=False)

    db.commit()
    return {
        "status": "success",
        "message": f"Successfully deleted {demo_count} demo cases.",
        "cleared_cases": demo_count
    }

@app.get("/api/reports/{case_id}/pdf")
def get_case_pdf_report_endpoint(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_officer)
):
    """
    Generates a complete, law-enforcement ready PDF dossier report using ReportLab.
    """
    clean_id = (case_id or "").strip()
    case = db.query(Case).filter(Case.id == clean_id).first()
    if not case:
        # Also try case-insensitive / normalized search (e.g. LS0032 -> LS-0032)
        norm_id = clean_id.upper().replace("-", "").replace(" ", "").replace("_", "")
        all_cases = db.query(Case).all()
        for c in all_cases:
            if c.id.upper().replace("-", "").replace(" ", "").replace("_", "") == norm_id:
                case = c
                break
        if not case:
            raise HTTPException(status_code=404, detail=f"Case with ID '{case_id}' not found.")

    try:
        detail = format_case_detail(case, db)
        case_dict = detail.model_dump()
        pdf_bytes = generate_case_pdf_report(case_dict)
        filename = f"LinkShield_Report_{case.id}.pdf"

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
    except Exception as e:
        logger.error(f"Error generating PDF dossier for case {case_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate PDF dossier for case '{case_id}': {str(e)}"
        )

@app.post("/api/import", response_model=ImportResponse)
async def import_external_data_endpoint(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_officer)
):
    """
    Imports external CSV or JSON dataset (e.g. R4C callset / complaints).
    Marks all imported records as is_demo=False and runs through the real analysis pipeline.
    """
    filename = (file.filename or "").lower()
    content_bytes = await file.read()
    if len(content_bytes) > settings.MAX_RESPONSE_BYTES:
        raise HTTPException(status_code=400, detail="Import file size exceeds 2 MB limit.")

    imported = 0
    skipped = 0
    errors = []

    try:
        text_content = content_bytes.decode("utf-8", errors="replace")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {str(e)}")

    if filename.endswith(".json"):
        try:
            records = json.loads(text_content)
            if not isinstance(records, list):
                records = [records]
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON format: {str(e)}")

        for idx, item in enumerate(records):
            content = item.get("content") or item.get("text") or item.get("message") or item.get("url") or ""
            if not content.strip():
                skipped += 1
                continue
            itype = item.get("input_type", "message")
            subject = item.get("subject") or f"Imported Case #{idx + 1}"

            try:
                if itype == "url":
                    analysis = analyze_url_target(content, subject=subject)
                elif itype == "website":
                    analysis = analyze_website_content(html_content=content, subject=subject)
                else:
                    analysis = analyze_message_content(content, subject=subject)

                save_case_with_relations(db, analysis, is_demo=False)
                imported += 1
            except Exception as e:
                errors.append(f"Row {idx + 1}: {str(e)}")

    elif filename.endswith(".csv"):
        try:
            reader = csv.DictReader(io.StringIO(text_content))
            for idx, row in enumerate(reader):
                content = (
                    row.get("content") or row.get("text") or row.get("message")
                    or row.get("url") or row.get("raw_content") or ""
                )
                if not content.strip():
                    skipped += 1
                    continue
                itype = row.get("input_type") or ("url" if content.startswith("http") else "message")
                subject = row.get("subject") or f"Imported CSV #{idx + 1}"

                try:
                    if itype == "url":
                        analysis = analyze_url_target(content, subject=subject)
                    elif itype == "website":
                        analysis = analyze_website_content(html_content=content, subject=subject)
                    else:
                        analysis = analyze_message_content(content, subject=subject)

                    save_case_with_relations(db, analysis, is_demo=False)
                    imported += 1
                except Exception as e:
                    errors.append(f"Row {idx + 1}: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid CSV format: {str(e)}")
    else:
        raise HTTPException(status_code=400, detail="Only .csv and .json files are supported for import.")

    return ImportResponse(
        imported_count=imported,
        skipped_count=skipped,
        errors=errors[:10]
    )
