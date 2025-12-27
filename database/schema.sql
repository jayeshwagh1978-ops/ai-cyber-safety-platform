-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('victim', 'police', 'admin', 'analyst')),
    language_preference VARCHAR(10) DEFAULT 'en',
    consent_given BOOLEAN DEFAULT FALSE,
    consent_timestamp TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_users_email (email),
    INDEX idx_users_phone (phone),
    INDEX idx_users_role (role)
);

-- Incidents table
CREATE TABLE incidents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    incident_type VARCHAR(100) NOT NULL,
    description TEXT,
    risk_score DECIMAL(5,2) NOT NULL CHECK (risk_score >= 0 AND risk_score <= 100),
    status VARCHAR(50) DEFAULT 'pending' 
        CHECK (status IN ('pending', 'reviewed', 'escalated', 'resolved', 'dismissed')),
    evidence_hashes JSONB DEFAULT '[]',
    blockchain_tx_id VARCHAR(255),
    language VARCHAR(10) DEFAULT 'en',
    location JSONB,
    predicted_escalation BOOLEAN,
    escalation_probability DECIMAL(5,4),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_incidents_user_id (user_id),
    INDEX idx_incidents_status (status),
    INDEX idx_incidents_risk_score (risk_score),
    INDEX idx_incidents_timestamp (timestamp)
);

-- Evidence table
CREATE TABLE evidence (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    incident_id UUID NOT NULL REFERENCES incidents(id) ON DELETE CASCADE,
    evidence_type VARCHAR(50) NOT NULL,
    content_hash VARCHAR(255) NOT NULL,
    ipfs_hash VARCHAR(255),
    hyperledger_tx_id VARCHAR(255),
    metadata JSONB,
    auto_tags JSONB DEFAULT '[]',
    is_tamper_proof BOOLEAN DEFAULT TRUE,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_evidence_incident_id (incident_id),
    INDEX idx_evidence_content_hash (content_hash),
    UNIQUE (content_hash)
);

-- Risk scores table
CREATE TABLE risk_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    incident_id UUID REFERENCES incidents(id) ON DELETE SET NULL,
    score DECIMAL(5,2) NOT NULL CHECK (score >= 0 AND score <= 100),
    factors JSONB,
    prediction_model VARCHAR(100),
    confidence DECIMAL(5,4),
    threshold_breached BOOLEAN DEFAULT FALSE,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_risk_scores_user_id (user_id),
    INDEX idx_risk_scores_incident_id (incident_id),
    INDEX idx_risk_scores_timestamp (timestamp)
);

-- FIR Kits table
CREATE TABLE fir_kits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    incident_id UUID NOT NULL REFERENCES incidents(id) ON DELETE CASCADE,
    police_station_id UUID REFERENCES police_stations(id) ON DELETE SET NULL,
    completeness_score DECIMAL(5,2) CHECK (completeness_score >= 0 AND completeness_score <= 100),
    pre_filled_data JSONB NOT NULL,
    missing_fields JSONB DEFAULT '[]',
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    downloaded BOOLEAN DEFAULT FALSE,
    language VARCHAR(10) DEFAULT 'en',
    
    -- Indexes
    INDEX idx_fir_kits_incident_id (incident_id),
    INDEX idx_fir_kits_police_station_id (police_station_id)
);

-- Police stations table
CREATE TABLE police_stations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    station_code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    jurisdiction JSONB,
    contact JSONB,
    language_support JSONB DEFAULT '["en", "hi"]',
    active_cases INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_police_stations_station_code (station_code)
);

-- Audit log table
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100),
    entity_id VARCHAR(255),
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_audit_logs_user_id (user_id),
    INDEX idx_audit_logs_timestamp (timestamp),
    INDEX idx_audit_logs_action (action)
);

-- Create update trigger for timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to users table
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create materialized view for dashboard analytics
CREATE MATERIALIZED VIEW dashboard_analytics AS
SELECT 
    DATE(timestamp) as date,
    COUNT(*) as total_incidents,
    COUNT(CASE WHEN risk_score > 70 THEN 1 END) as high_risk_incidents,
    COUNT(CASE WHEN predicted_escalation = TRUE THEN 1 END) as predicted_escalations,
    AVG(risk_score) as avg_risk_score,
    COUNT(DISTINCT user_id) as unique_users
FROM incidents
WHERE timestamp >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(timestamp);

-- Refresh the materialized view periodically
CREATE OR REPLACE FUNCTION refresh_dashboard_analytics()
RETURNS VOID AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY dashboard_analytics;
END;
$$ LANGUAGE plpgsql;
