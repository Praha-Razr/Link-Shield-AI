import json
import hashlib
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.models import Case, Indicator, Identifier, SimilarityLink, case_identifiers
from app.analyzers.similarity import find_similar_cases
from app.allowlist import is_linkable_identifier

def generate_next_case_id(db: Session, is_demo: bool = False) -> str:
    """
    Generates sequence ID: LS-0001, LS-0002... or DEMO-001, DEMO-002...
    """
    prefix = "DEMO" if is_demo else "LS"
    # Find max existing ID with this prefix
    cases = db.query(Case.id).filter(Case.id.like(f"{prefix}-%")).all()
    max_num = 0
    for (cid,) in cases:
        try:
            num = int(cid.split("-")[-1])
            if num > max_num:
                max_num = num
        except Exception:
            pass
    return f"{prefix}-{max_num + 1:04d}" if not is_demo else f"{prefix}-{max_num + 1:03d}"

def save_case_with_relations(
    db: Session,
    analysis_data: Dict[str, Any],
    is_demo: bool = False,
    override_case_id: Optional[str] = None,
    submitted_by: Optional[str] = None
) -> Case:
    """
    Persists analysis result to SQLite:
    - Generates or applies case ID
    - Calculates SHA-256 hash and UTC timestamp
    - Detects near-duplicates (similarity >= 0.85) and creates similarity links
    - Normalizes and links identifiers via case_identifiers
    - Records indicators
    """
    raw_content = analysis_data.get("raw_content", "")
    content_hash = hashlib.sha256(raw_content.encode("utf-8")).hexdigest()
    
    # Check if this exact content already exists for demo idempotency
    if is_demo and override_case_id:
        existing = db.query(Case).filter(Case.id == override_case_id).first()
        if existing:
            return existing

    case_id = override_case_id or generate_next_case_id(db, is_demo=is_demo)

    # 1. Similarity link detection
    similar_cases = find_similar_cases(raw_content, db, current_case_id=case_id)
    similarity_records = []
    indicators_to_add = list(analysis_data.get("indicators", []))

    for sim in similar_cases:
        sim_link = SimilarityLink(
            case_id_a=case_id,
            case_id_b=sim["case_id"],
            similarity=sim["similarity"]
        )
        similarity_records.append(sim_link)
        # Add informational indicator
        indicators_to_add.append({
            "name": f"Near-duplicate Content (Case {sim['case_id']})",
            "points": 0,
            "explanation": f"Content shares {int(sim['similarity'] * 100)}% structural text similarity with existing case {sim['case_id']}."
        })

    # 2. Create Case record
    now_utc = datetime.now(timezone.utc)
    ai_op = analysis_data.get("ai_second_opinion")
    ai_op_str = json.dumps(ai_op) if isinstance(ai_op, dict) else (ai_op if isinstance(ai_op, str) else None)
    case = Case(
        id=case_id,
        subject=analysis_data.get("subject", f"Case {case_id}"),
        input_type=analysis_data.get("input_type", "message"),
        raw_content=raw_content,
        content_sha256=content_hash,
        created_at=now_utc,
        risk_score=analysis_data.get("risk_score", 0),
        risk_level=analysis_data.get("risk_level", "LOW"),
        category=analysis_data.get("category", "general"),
        status="analyzed",
        is_demo=is_demo,
        language=analysis_data.get("language", "en"),
        investigator_notes=analysis_data.get("investigator_notes"),
        ai_second_opinion=ai_op_str,
        submitted_by=submitted_by
    )
    db.add(case)
    db.flush()

    # 3. Add Indicators
    for ind in indicators_to_add:
        indicator_obj = Indicator(
            case_id=case.id,
            name=ind.get("name", "Unknown Indicator"),
            points=ind.get("points", 0),
            explanation=ind.get("explanation", "")
        )
        db.add(indicator_obj)

    # 4. Add Similarity Links
    for sl in similarity_records:
        db.add(sl)

    # 5. Link Identifiers (find or create)
    extracted_ids = analysis_data.get("extracted_identifiers", [])
    for ident in extracted_ids:
        itype = ident.get("type", "").strip().lower()
        ivalue = ident.get("value", "").strip()
        if not itype or not ivalue:
            continue
        
        # Case normalization: lowercase ONLY domains, emails and UPI IDs
        if itype in ("domain", "email", "upi"):
            ivalue = ivalue.lower()

        # Find existing identifier: ETH addresses matched case-insensitively, others exact
        if itype == "crypto_wallet" and ivalue.lower().startswith("0x") and len(ivalue) == 42:
            id_obj = db.query(Identifier).filter(
                Identifier.type == itype,
                func.lower(Identifier.value) == ivalue.lower()
            ).first()
        else:
            id_obj = db.query(Identifier).filter(
                Identifier.type == itype,
                Identifier.value == ivalue
            ).first()

        if not id_obj:
            id_obj = Identifier(type=itype, value=ivalue)
            db.add(id_obj)
            db.flush()

        if id_obj not in case.identifiers:
            case.identifiers.append(id_obj)

    db.commit()
    db.refresh(case)
    return case

def get_shared_identifiers(db: Session, min_cases: int = 2) -> List[Dict[str, Any]]:
    """
    Queries identifiers that appear across multiple cases.
    """
    subq = (
        db.query(
            case_identifiers.c.identifier_id,
            func.count(case_identifiers.c.case_id).label("case_count")
        )
        .group_by(case_identifiers.c.identifier_id)
        .having(func.count(case_identifiers.c.case_id) >= min_cases)
        .subquery()
    )

    results = (
        db.query(Identifier, subq.c.case_count)
        .join(subq, Identifier.id == subq.c.identifier_id)
        .order_by(desc(subq.c.case_count))
        .all()
    )

    return [
        {
            "id": ident.id,
            "type": ident.type,
            "value": ident.value,
            "case_count": count
        }
        for ident, count in results
        if is_linkable_identifier(ident.type, ident.value)
    ]

def get_top_identifiers_heatlist(
    db: Session,
    identifier_type: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    include_demo: bool = True,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Returns identifiers ranked by distinct case count ('frequently reported').
    Excludes IFSC branch codes and known legitimate entities.
    """
    query = (
        db.query(
            Identifier.id,
            Identifier.type,
            Identifier.value,
            func.count(Case.id.distinct()).label("distinct_case_count"),
            func.max(Case.created_at).label("latest_seen")
        )
        .join(case_identifiers, Identifier.id == case_identifiers.c.identifier_id)
        .join(Case, Case.id == case_identifiers.c.case_id)
    )

    if not include_demo:
        query = query.filter(Case.is_demo == False)

    if identifier_type:
        query = query.filter(Identifier.type == identifier_type)

    if date_from:
        query = query.filter(Case.created_at >= date_from)
    if date_to:
        query = query.filter(Case.created_at <= date_to)

    # Fetch rows to filter non-linkable identifiers
    candidate_limit = max(limit * 3, 100)
    rows = (
        query.group_by(Identifier.id, Identifier.type, Identifier.value)
        .order_by(desc("distinct_case_count"), desc("latest_seen"), Identifier.value.asc())
        .limit(candidate_limit)
        .all()
    )

    heatlist = []
    for ident_id, itype, ivalue, ccount, latest_seen in rows:
        if not is_linkable_identifier(itype, ivalue):
            continue

        # Fetch associated cases to aggregate risk breakdown
        cases = (
            db.query(Case)
            .join(case_identifiers, Case.id == case_identifiers.c.case_id)
            .filter(case_identifiers.c.identifier_id == ident_id)
            .all()
        )
        risk_summary = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
        categories = set()
        case_ids = []
        for c in cases:
            risk_summary[c.risk_level] = risk_summary.get(c.risk_level, 0) + 1
            categories.add(c.category)
            case_ids.append(c.id)

        heatlist.append({
            "identifier_id": ident_id,
            "type": itype,
            "value": ivalue,
            "distinct_case_count": ccount,
            "risk_summary": risk_summary,
            "categories": sorted(list(categories)),
            "latest_seen": latest_seen,
            "case_ids": case_ids
        })

        if len(heatlist) >= limit:
            break

    return heatlist

def build_intelligence_graph(
    db: Session,
    include_demo: bool = True,
    min_cases: int = 2,
    max_cases: int = 250
) -> Dict[str, Any]:
    """
    Constructs node/edge relationship graph from REAL database connections.
    By default shows identifiers that appear in >= 2 cases (plus their cases).
    When min_cases=1, shows all identifiers and cases.
    """
    # 1. Identify identifiers meeting the min_cases threshold
    shared_ident_subq = (
        db.query(case_identifiers.c.identifier_id)
        .join(Case, Case.id == case_identifiers.c.case_id)
    )
    if not include_demo:
        shared_ident_subq = shared_ident_subq.filter(Case.is_demo == False)
    
    shared_ident_ids = [
        row[0] for row in (
            shared_ident_subq.group_by(case_identifiers.c.identifier_id)
            .having(func.count(case_identifiers.c.case_id) >= min_cases)
            .all()
        )
    ]

    nodes = []
    edges = []
    node_ids = set()

    # If there are matching identifiers, build the graph around them
    if shared_ident_ids:
        identifiers = db.query(Identifier).filter(Identifier.id.in_(shared_ident_ids)).all()
        for ident in identifiers:
            # Exclude IFSC branch codes and known legitimate entities from graph edges/nodes
            if not is_linkable_identifier(ident.type, ident.value):
                continue

            # Fetch linked cases
            c_query = (
                db.query(Case)
                .join(case_identifiers, Case.id == case_identifiers.c.case_id)
                .filter(case_identifiers.c.identifier_id == ident.id)
            )
            if not include_demo:
                c_query = c_query.filter(Case.is_demo == False)
            
            linked_cases = c_query.order_by(Case.created_at.asc()).limit(max_cases).all()
            if not linked_cases:
                continue

            first_seen = linked_cases[0].created_at.isoformat() if linked_cases else None
            last_seen = linked_cases[-1].created_at.isoformat() if linked_cases else None
            connected_case_summaries = [
                {
                    "id": c.id,
                    "subject": c.subject,
                    "risk_level": c.risk_level,
                    "risk_score": c.risk_score,
                    "category": c.category,
                    "created_at": c.created_at.isoformat()
                }
                for c in linked_cases
            ]

            ident_node_id = f"ident-{ident.id}"
            if ident_node_id not in node_ids:
                node_ids.add(ident_node_id)
                nodes.append({
                    "id": ident_node_id,
                    "label": f"{ident.type.upper()}: {ident.value}",
                    "type": ident.type,
                    "value": ident.value,
                    "case_count": len(linked_cases),
                    "first_seen": first_seen,
                    "last_seen": last_seen,
                    "connected_cases": connected_case_summaries
                })

            for c in linked_cases:
                case_node_id = f"case-{c.id}"
                if case_node_id not in node_ids:
                    node_ids.add(case_node_id)
                    nodes.append({
                        "id": case_node_id,
                        "label": f"[{c.id}] {c.subject[:25]}",
                        "type": "case",
                        "risk_level": c.risk_level,
                        "risk_score": c.risk_score,
                        "category": c.category,
                        "is_demo": c.is_demo,
                        "value": c.id
                    })

                edge_id = f"e-{case_node_id}-{ident_node_id}"
                edges.append({
                    "id": edge_id,
                    "source": case_node_id,
                    "target": ident_node_id,
                    "label": f"contains_{ident.type}"
                })

    # Also include similarity links between cases if any
    sim_query = db.query(SimilarityLink)
    if not include_demo:
        sim_query = sim_query.join(Case, Case.id == SimilarityLink.case_id_a).filter(Case.is_demo == False)
    
    sim_links = sim_query.limit(50).all()
    for sl in sim_links:
        source_id = f"case-{sl.case_id_a}"
        target_id = f"case-{sl.case_id_b}"
        if source_id in node_ids and target_id in node_ids:
            edges.append({
                "id": f"sim-{sl.id}",
                "source": source_id,
                "target": target_id,
                "label": f"similar ({int(sl.similarity * 100)}%)"
            })

    return {"nodes": nodes, "edges": edges}

def get_dashboard_statistics(db: Session) -> Dict[str, Any]:
    """
    Computes all dashboard metrics directly from SQLite database.
    NO HARDCODED NUMBERS.
    """
    total_cases = db.query(func.count(Case.id)).scalar() or 0
    high_risk = db.query(func.count(Case.id)).filter(Case.risk_level == "HIGH").scalar() or 0
    med_risk = db.query(func.count(Case.id)).filter(Case.risk_level == "MEDIUM").scalar() or 0
    low_risk = db.query(func.count(Case.id)).filter(Case.risk_level == "LOW").scalar() or 0
    demo_cases = db.query(func.count(Case.id)).filter(Case.is_demo == True).scalar() or 0
    real_cases = db.query(func.count(Case.id)).filter(Case.is_demo == False).scalar() or 0

    # Group by input_type
    type_counts = (
        db.query(Case.input_type, func.count(Case.id))
        .group_by(Case.input_type)
        .all()
    )
    cases_by_type = {t: c for t, c in type_counts}

    # Group by category
    cat_counts = (
        db.query(Case.category, func.count(Case.id))
        .group_by(Case.category)
        .all()
    )
    cases_by_category = {cat: c for cat, c in cat_counts}

    # Count identifiers
    top_identifiers_count = db.query(func.count(Identifier.id)).scalar() or 0

    # Count shared identifiers (case_count >= 2)
    shared_subq = (
        db.query(case_identifiers.c.identifier_id)
        .group_by(case_identifiers.c.identifier_id)
        .having(func.count(case_identifiers.c.case_id) >= 2)
        .subquery()
    )
    total_shared_identifiers = db.query(func.count(shared_subq.c.identifier_id)).scalar() or 0

    return {
        "total_cases": total_cases,
        "high_risk_cases": high_risk,
        "medium_risk_cases": med_risk,
        "low_risk_cases": low_risk,
        "demo_cases": demo_cases,
        "real_cases": real_cases,
        "cases_by_type": cases_by_type,
        "cases_by_category": cases_by_category,
        "top_identifiers_count": top_identifiers_count,
        "total_shared_identifiers": total_shared_identifiers
    }
