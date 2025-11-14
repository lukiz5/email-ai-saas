from sqlalchemy import Column, String, DateTime, Boolean, Text, Enum, Integer
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()


class PlanType(str, enum.Enum):
    FREE = "free"
    PRO = "pro"


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)  # Clerk user ID
    email = Column(String, unique=True, nullable=False)
    plan = Column(Enum(PlanType), default=PlanType.FREE)
    stripe_customer_id = Column(String, nullable=True)
    stripe_subscription_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class EmailIntegration(Base):
    __tablename__ = "email_integrations"

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    integration_type = Column(String, nullable=False)  # gmail, outlook, imap
    encrypted_credentials = Column(Text, nullable=False)  # Encrypted JSON
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class EmailSummary(Base):
    __tablename__ = "email_summaries"

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    email_source = Column(String, nullable=True)  # gmail, outlook, imap, manual
    email_subject = Column(String, nullable=True)
    email_from = Column(String, nullable=True)
    email_date = Column(DateTime, nullable=True)
    summary = Column(Text, nullable=False)
    actions = Column(Text, nullable=True)  # JSON array
    priority_score = Column(Integer, nullable=True)
    original_email_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
