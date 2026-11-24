import os
from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BASE_DIR.parent
DATA_DIR = ROOT_DIR / "data"

# Auto-load backend/.env if it exists
_env_file = BASE_DIR / ".env"
if _env_file.exists():
    with open(_env_file, "r", encoding="utf-8") as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                os.environ[_k.strip()] = _v.strip().strip("'\"")

class Settings(BaseModel):
    PROJECT_NAME: str = "LinkShield AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/linkshield.db")
    
    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    
    # Safe Fetcher / SSRF Protection
    MAX_REDIRECT_HOPS: int = 5
    HTTP_TIMEOUT_SECONDS: float = 5.0
    MAX_RESPONSE_BYTES: int = 2 * 1024 * 1024  # 2 MB cap
    MAX_FILE_UPLOAD_BYTES: int = 1 * 1024 * 1024  # 1 MB cap
    
    # Risk Engine Thresholds
    RISK_THRESHOLD_LOW_MAX: int = 24
    RISK_THRESHOLD_MEDIUM_MAX: int = 49
    RISK_SCORE_CAP: int = 100
    
    # Demo dataset path
    DEMO_DATASET_PATH: Path = DATA_DIR / "demo_dataset.json"

    # Known synthetic blacklist for demo/testing
    DEMO_BLACKLIST_DOMAINS: list[str] = [
        "demo-scam.test",
        "fake-sbi-login.test",
        "free-instant-loan.test",
        "crypto-double-returns.test",
        "online-lottery-claims.test",
        "electricity-bill-pay.test",
        "parttime-job-earning.test",
        "ipl-betting-win.test",
        "kyc-update-portal.test",
        "secure-hdfc-update.test",
        "pan-aadhaar-link-urgent.test",
        "pm-kisan-instant-bonus.test",
    ]
    
    # Target brand keywords for look-alike detection
    TARGET_BRANDS: list[str] = [
        "sbi",
        "hdfc",
        "icici",
        "paytm",
        "indiapost",
        "amazon",
        "axisbank",
        "pnb",
        "kotak",
        "phonepe",
        "googlepay",
        "airtel",
        "jio",
        "incometax",
    ]

    # Gemini Enhanced Mode (Optional)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")
    GEMINI_TIMEOUT_SECONDS: float = 20.0
    GEMINI_ASSISTANT_TIMEOUT: float = 20.0
    GEMINI_ANALYSIS_TIMEOUT: float = 10.0
    AI_ASSIST_ANALYSIS: bool = os.getenv("AI_ASSIST_ANALYSIS", "true").lower() in ("true", "1", "yes")
    ALLOW_EXTERNAL_AI_FOR_REAL_CASES: bool = os.getenv("ALLOW_EXTERNAL_AI_FOR_REAL_CASES", "false").lower() in ("true", "1", "yes")
    GOOGLE_SAFE_BROWSING_KEY: str = os.getenv("GOOGLE_SAFE_BROWSING_KEY", "")

    # Authentication & JWT Configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "linkshield-enterprise-auth-secret-key-production-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))
    DEMO_MODE: bool = os.getenv("DEMO_MODE", "true").lower() in ("true", "1", "yes")

    # Default Seeded Officer / Admin Credentials (for seed_users.py)
    OFFICER_DEFAULT_USERNAME: str = os.getenv("OFFICER_USERNAME", "officer_sharma")
    OFFICER_DEFAULT_PASSWORD: str = os.getenv("OFFICER_PASSWORD", "Officer@Shield2026")
    OFFICER_DEFAULT_NAME: str = os.getenv("OFFICER_DISPLAY_NAME", "Insp. Rajesh Sharma")

    ADMIN_DEFAULT_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin_cyber")
    ADMIN_DEFAULT_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "Admin@Shield2026")
    ADMIN_DEFAULT_NAME: str = os.getenv("ADMIN_DISPLAY_NAME", "Admin Cyber Supervisor")

settings = Settings()
