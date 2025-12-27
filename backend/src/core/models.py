from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, unique=True)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)  # 'victim', 'police', 'admin'
    language_preference = Column(String, default='en')
    created_at = Column(DateTime, default=datetime.utcnow)
    consent_given = Column(Boolean, default=False)
    consent_timestamp = Column(DateTime)
    is_active = Column(Boolean, default=True)

class Incident(Base):
    __tablename__ = "incidents"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)
    incident_type = Column(String, nullable=False)  # cyberbullying, threat, harassment
    description = Column(Text)
    risk_score = Column(Float, nullable=False)
    status = Column(String, default='pending')  # pending, reviewed, escalated, resolved
    evidence_hashes = Column(JSON, default=list)
    blockchain_tx_id = Column(String)
    language = Column(String, default='en')
    location = Column(JSON)  # {latitude, longitude, city, state}
    timestamp = Column(DateTime, default=datetime.utcnow)
    predicted_escalation = Column(Boolean)
    escalation_probability = Column(Float)

class Evidence(Base):
    __tablename__ = "evidence"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    incident_id = Column(String, nullable=False)
    evidence_type = Column(String)  # screenshot, chat_log, email, audio
    content_hash = Column(String, nullable=False)
    ipfs_hash = Column(String)
    hyperledger_tx_id = Column(String)
    metadata = Column(JSON)  # timestamp, source, tags
    auto_tags = Column(JSON, default=list)
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_tamper_proof = Column(Boolean, default=True)

class RiskScore(Base):
    __tablename__ = "risk_scores"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)
    incident_id = Column(String)
    score = Column(Float, nullable=False)
    factors = Column(JSON)  # contributing factors
    prediction_model = Column(String)
    confidence = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    threshold_breached = Column(Boolean, default=False)

class FIRKit(Base):
    __tablename__ = "fir_kits"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    incident_id = Column(String, nullable=False)
    police_station_id = Column(String)
    completeness_score = Column(Float)  # 90% completeness
    pre_filled_data = Column(JSON)  # Automated FIR data
    missing_fields = Column(JSON, default=list)
    generated_at = Column(DateTime, default=datetime.utcnow)
    downloaded = Column(Boolean, default=False)
    language = Column(String, default='en')

class PoliceStation(Base):
    __tablename__ = "police_stations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    station_code = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    jurisdiction = Column(JSON)
    contact = Column(JSON)  # {phone, email, address}
    language_support = Column(JSON, default=['en', 'hi'])
    active_cases = Column(Integer, default=0)
