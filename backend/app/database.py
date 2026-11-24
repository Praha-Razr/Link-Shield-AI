from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def run_migrations():
    """Ensures dynamic SQLite column additions (like ai_second_opinion) are applied safely."""
    try:
        with engine.connect() as conn:
            res = conn.exec_driver_sql("PRAGMA table_info(cases)").fetchall()
            cols = [r[1] for r in res]
            if cols and "ai_second_opinion" not in cols:
                conn.exec_driver_sql("ALTER TABLE cases ADD COLUMN ai_second_opinion TEXT")
                conn.commit()
    except Exception:
        pass

run_migrations()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
