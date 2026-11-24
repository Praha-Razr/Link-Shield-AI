from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field, ConfigDict

class IndicatorSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: Optional[int] = None
    name: str
    points: int
    explanation: str

class IdentifierSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: Optional[int] = None
    type: str  # domain, url, phone, upi, email, bank_account, crypto_wallet
    value: str
    is_legitimate: bool = False
    is_linkable: bool = True

class SimilarityLinkSchema(BaseModel):
    case_id: str
    similarity: float
    subject: Optional[str] = None
    risk_level: Optional[str] = None

class EvidenceSchema(BaseModel):
    content_sha256: str
    timestamp_utc: str
    char_count: int
    excerpt: str

class AISecondOpinionSchema(BaseModel):
    scam_likelihood: str  # low | medium | high
    category: Optional[str] = None
    impersonated_brand: Optional[str] = None
    reasons: list[str] = []
    confidence: float = 0.0
    status: str = "ok"  # ok | unavailable | skipped
    disclaimer: str = "AI opinion, verify manually"
    is_ai_assisted: bool = True
    error: Optional[str] = None

class AnalysisResult(BaseModel):
    case_id: str
    subject: str
    input_type: str
    risk_score: int
    risk_level: str  # LOW, MEDIUM, HIGH
    category: str
    language: str
    indicators: list[IndicatorSchema]
    extracted_identifiers: list[IdentifierSchema]
    suspicious_phrases: list[str]
    safety_recommendations: list[str]
    verified_official: Optional[dict[str, Any]] = None
    verified_links: list[dict[str, Any]] = []
    evidence: EvidenceSchema
    similarity_matches: list[SimilarityLinkSchema] = []
    live_checks: dict[str, Any] = {}
    ai_second_opinion: Optional[AISecondOpinionSchema] = None

class MessageAnalyzeRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=50000, description="Raw message text to analyze")
    subject: Optional[str] = None

class URLAnalyzeRequest(BaseModel):
    url: str = Field(..., min_length=3, max_length=2048, description="URL to analyze")
    subject: Optional[str] = None
    perform_live_check: bool = Field(default=False, description="Whether to safely fetch live headers/redirects")

class WebsiteAnalyzeRequest(BaseModel):
    url: Optional[str] = None
    html_content: Optional[str] = None
    subject: Optional[str] = None

class RelatedCaseSchema(BaseModel):
    case_id: str
    subject: Optional[str] = None
    risk_level: Optional[str] = None
    input_type: Optional[str] = None
    shared_identifiers: list[str] = []

class CaseDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    subject: Optional[str]
    input_type: str
    raw_content: str
    content_sha256: str
    created_at: datetime
    risk_score: int
    risk_level: str
    category: str
    status: str
    is_demo: bool
    language: str
    investigator_notes: Optional[str] = None
    indicators: list[IndicatorSchema] = []
    identifiers: list[IdentifierSchema] = []
    similarity_links: list[SimilarityLinkSchema] = []
    related_cases: list[RelatedCaseSchema] = []
    ai_second_opinion: Optional[AISecondOpinionSchema] = None

class CaseSummaryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    subject: Optional[str]
    input_type: str
    created_at: datetime
    risk_score: int
    risk_level: str
    category: str
    status: str
    is_demo: bool
    language: str
    identifier_count: int = 0
    indicator_count: int = 0

class CaseListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    cases: list[CaseSummaryItem]

class DashboardStatsResponse(BaseModel):
    total_cases: int
    high_risk_cases: int
    medium_risk_cases: int
    low_risk_cases: int
    demo_cases: int
    real_cases: int
    cases_by_type: dict[str, int]
    cases_by_category: dict[str, int]
    top_identifiers_count: int
    total_shared_identifiers: int

class GraphNode(BaseModel):
    id: str
    label: str
    type: str  # "case" or identifier type ("phone", "domain", "upi", etc.)
    risk_level: Optional[str] = None
    risk_score: Optional[int] = None
    category: Optional[str] = None
    value: Optional[str] = None
    is_demo: Optional[bool] = None
    case_count: Optional[int] = None
    first_seen: Optional[str] = None
    last_seen: Optional[str] = None
    connected_cases: Optional[list[dict[str, Any]]] = None

class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    label: Optional[str] = None

class IntelligenceGraphResponse(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]

class HeatlistItem(BaseModel):
    identifier_id: int
    type: str
    value: str
    distinct_case_count: int
    risk_summary: dict[str, int]
    categories: list[str]
    latest_seen: Optional[datetime]
    case_ids: list[str]

class HeatlistResponse(BaseModel):
    total: int
    items: list[HeatlistItem]

class NotesUpdateRequest(BaseModel):
    notes: str = Field(..., max_length=10000)

class DemoClearRequest(BaseModel):
    confirm: bool

class ImportResponse(BaseModel):
    imported_count: int
    skipped_count: int

class AssistantChatMessage(BaseModel):
    role: str = "user"  # user | model | assistant
    content: str = ""

class AssistantAskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)
    use_enhanced: bool = True
    history: list[AssistantChatMessage] = []

class AssistantStatusResponse(BaseModel):
    key_configured: bool
    model: str
    status: str  # ok | error | not_configured
    error: Optional[str] = None

class AssistantAskResponse(BaseModel):
    question: str
    answer: str
    case_ids: list[str] = []
    evidence_references: list[str] = []
    mode: str = "rule_based"  # "rule_based" | "enhanced" | "fallback"
    is_ai_assisted: bool = False
    fallback_reason: Optional[str] = None

# --- Authentication & User Schemas ---
class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_.-]+$")
    password: str = Field(..., min_length=8, max_length=128)
    display_name: str = Field(..., min_length=2, max_length=100)
    role: Optional[str] = "citizen"  # Server strictly forces "citizen"

class UserLoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1, max_length=128)

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    username: str
    display_name: str
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class AwarenessCategoryStat(BaseModel):
    category: str
    label: str
    count: int
    percentage: float

class PublicAwarenessResponse(BaseModel):
    total_cases: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    categories: list[AwarenessCategoryStat]
    top_threat_vectors: list[str]
    safety_advisory: str
