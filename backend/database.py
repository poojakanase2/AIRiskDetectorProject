from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import os

# Database Path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, 'data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

SQLALCHEMY_DATABASE_URL = f"sqlite:///{os.path.join(DATA_DIR, 'risk_history.db ')}"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class RiskAssessmentRecord(Base):
    __tablename__ = "risk_assessments"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    risk_score = Column(Float)
    status = Column(String)
    reasons = Column(JSON)  # Stores list of strings
    latency_ms = Column(Float)
    error_rate = Column(Float)
    cpu_usage = Column(Float)

class LogAnalysisRecord(Base):
    __tablename__ = "log_analyses"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    log_snippet = Column(String)
    category = Column(String)
    root_cause = Column(String)
    suggested_fix = Column(String)
    commands = Column(JSON) # List of strings
    prevention_tips = Column(JSON) # List of strings

class HealingHistoryRecord(Base):
    __tablename__ = "healing_history"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    job_id = Column(String)
    source = Column(String) # e.g. Jenkins, GitHub Actions
    category = Column(String)
    root_cause = Column(String)
    execution_status = Column(String) # Fix Applied & Pushed, Universal Bypass, etc.
    retry_status = Column(String)
    confidence = Column(Float)

# Create tables
def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
