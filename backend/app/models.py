from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    Text,
    DateTime,
    ForeignKey,
    Table,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import relationship
from app.database import Base

case_identifiers = Table(
    "case_identifiers",
    Base.metadata,
    Column("case_id", String(64), ForeignKey("cases.id", ondelete="CASCADE"), primary_key=True),
    Column("identifier_id", Integer, ForeignKey("identifiers.id", ondelete="CASCADE"), primary_key=True),
)

class User(Base):
    __tablename__ = "users"

    id = Column(String(64), primary_key=True, index=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    display_name = Column(String(128), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(32), nullable=False, index=True)  # 'citizen' | 'officer'
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    last_login = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    failed_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime, nullable=True)

class Case(Base):
    __tablename__ = "cases"

    id = Column(String(64), primary_key=True, index=True)
    subject = Column(String(255), nullable=True)
    input_type = Column(String(32), nullable=False, index=True)  # message, url, website
    raw_content = Column(Text, nullable=False)
    content_sha256 = Column(String(64), nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    risk_score = Column(Integer, nullable=False)
    risk_level = Column(String(16), nullable=False, index=True)  # LOW, MEDIUM, HIGH
    category = Column(String(64), nullable=False, index=True)
    status = Column(String(32), default="analyzed", nullable=False)
    is_demo = Column(Boolean, default=False, nullable=False, index=True)
    language = Column(String(16), default="en", nullable=False)
    investigator_notes = Column(Text, nullable=True)
    ai_second_opinion = Column(Text, nullable=True)
    submitted_by = Column(String(64), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    user = relationship("User", foreign_keys=[submitted_by])
    indicators = relationship("Indicator", back_populates="case", cascade="all, delete-orphan")
    identifiers = relationship("Identifier", secondary=case_identifiers, back_populates="cases")


class Indicator(Base):
    __tablename__ = "indicators"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(String(64), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(128), nullable=False)
    points = Column(Integer, nullable=False)
    explanation = Column(Text, nullable=False)

    case = relationship("Case", back_populates="indicators")


class Identifier(Base):
    __tablename__ = "identifiers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(32), nullable=False)  # domain, url, phone, upi, email, bank_account, crypto_wallet
    value = Column(String(512), nullable=False)

    __table_args__ = (
        UniqueConstraint("type", "value", name="uq_identifier_type_value"),
        Index("idx_identifier_type_val", "type", "value"),
    )

    cases = relationship("Case", secondary=case_identifiers, back_populates="identifiers")


class SimilarityLink(Base):
    __tablename__ = "similarity_links"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id_a = Column(String(64), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    case_id_b = Column(String(64), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    similarity = Column(Float, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        Index("idx_similarity_pair", "case_id_a", "case_id_b"),
    )
