-- Luma MVP Database Migrations
-- PostgreSQL / Supabase Schema

-- ======================
-- 1. Companies Table
-- ======================
CREATE TABLE IF NOT EXISTS companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    sector VARCHAR(100),
    country VARCHAR(2) DEFAULT 'ES',
    size INTEGER,
    cif VARCHAR(20),
    cnae_code VARCHAR(10),
    email VARCHAR(255),
    industry_code TEXT,
    status TEXT DEFAULT 'active',
    contact_email TEXT,
    last_login TIMESTAMP,
    data_points INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_companies_email ON companies(email);
CREATE INDEX IF NOT EXISTS idx_companies_status ON companies(status);


-- ======================
-- 2. Documents Table
-- ======================
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_type VARCHAR(20) NOT NULL,
    file_size VARCHAR(50),
    status VARCHAR(20) DEFAULT 'uploaded',
    upload_date TIMESTAMP DEFAULT NOW(),
    processed_date TIMESTAMP,
    error_message VARCHAR(1000)
);

CREATE INDEX IF NOT EXISTS idx_documents_company ON documents(company_id);
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);
CREATE INDEX IF NOT EXISTS idx_documents_upload_date ON documents(upload_date);


-- ======================
-- 3. Records Table
-- ======================
CREATE TABLE IF NOT EXISTS records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    supplier VARCHAR(255),
    category VARCHAR(100),
    usage NUMERIC(12, 3),
    unit VARCHAR(20),
    cost NUMERIC(10, 2),
    scope INTEGER,
    co2e NUMERIC(12, 3),
    factor_source VARCHAR(100),
    emission_factor NUMERIC(10, 6),
    date DATE,
    invoice_number VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_records_document ON records(document_id);
CREATE INDEX IF NOT EXISTS idx_records_date ON records(date);
CREATE INDEX IF NOT EXISTS idx_records_category ON records(category);
CREATE INDEX IF NOT EXISTS idx_records_scope ON records(scope);


-- ======================
-- 4. Emission Factors Table
-- ======================
CREATE TABLE IF NOT EXISTS emission_factors (
    id SERIAL PRIMARY KEY,
    category VARCHAR(100) NOT NULL,
    unit VARCHAR(20) NOT NULL,
    factor NUMERIC(10, 6) NOT NULL,
    source VARCHAR(100) NOT NULL,
    year INTEGER NOT NULL,
    region VARCHAR(10) DEFAULT 'EU',
    notes VARCHAR(500),
    UNIQUE(category, unit, source, year)
);

CREATE INDEX IF NOT EXISTS idx_emission_factors_category ON emission_factors(category);


-- ======================
-- 5. Reports Table
-- ======================
CREATE TABLE IF NOT EXISTS reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    year INTEGER NOT NULL,
    total_co2e NUMERIC(12, 3),
    scope1_co2e NUMERIC(12, 3),
    scope2_co2e NUMERIC(12, 3),
    scope3_co2e NUMERIC(12, 3),
    breakdown JSONB,
    monthly_data JSONB,
    coverage NUMERIC(5, 2),
    data_sources_count INTEGER,
    pdf_url VARCHAR(500),
    excel_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW(),
    methodology VARCHAR(1000)
);

CREATE INDEX IF NOT EXISTS idx_reports_company ON reports(company_id);
CREATE INDEX IF NOT EXISTS idx_reports_year ON reports(year);


-- ======================
-- 6. Usage Logs Table (Admin Tracking)
-- ======================
CREATE TABLE IF NOT EXISTS usage_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW(),
    details JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_usage_logs_company_time ON usage_logs(company_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_usage_logs_event_type ON usage_logs(event_type);
CREATE INDEX IF NOT EXISTS idx_usage_logs_timestamp ON usage_logs(timestamp);


-- ======================
-- 7. Company Stats Table (Admin Analytics)
-- ======================
CREATE TABLE IF NOT EXISTS company_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    month DATE NOT NULL,
    uploads_count INTEGER DEFAULT 0,
    records_count INTEGER DEFAULT 0,
    total_emissions NUMERIC DEFAULT 0,
    reports_generated INTEGER DEFAULT 0,
    active_users INTEGER DEFAULT 0,
    UNIQUE (company_id, month)
);

CREATE INDEX IF NOT EXISTS idx_company_stats_company_month ON company_stats(company_id, month);


-- ======================
-- Row-Level Security (RLS) - Supabase
-- ======================

-- Enable RLS on all tables
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE records ENABLE ROW LEVEL SECURITY;
ALTER TABLE usage_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE company_stats ENABLE ROW LEVEL SECURITY;
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;

-- Admin policies (full access)
CREATE POLICY admin_all_companies ON companies FOR ALL
    USING (auth.jwt() ->> 'role' = 'admin');

CREATE POLICY admin_all_documents ON documents FOR ALL
    USING (auth.jwt() ->> 'role' = 'admin');

CREATE POLICY admin_all_records ON records FOR ALL
    USING (auth.jwt() ->> 'role' = 'admin');

CREATE POLICY admin_all_usage ON usage_logs FOR ALL
    USING (auth.jwt() ->> 'role' = 'admin');

CREATE POLICY admin_all_stats ON company_stats FOR ALL
    USING (auth.jwt() ->> 'role' = 'admin');

CREATE POLICY admin_all_reports ON reports FOR ALL
    USING (auth.jwt() ->> 'role' = 'admin');

-- Company user policies (scoped by company_id)
CREATE POLICY company_read_companies ON companies FOR SELECT
    USING (id::text = auth.jwt() ->> 'company_id');

CREATE POLICY company_update_companies ON companies FOR UPDATE
    USING (id::text = auth.jwt() ->> 'company_id');

CREATE POLICY company_docs ON documents FOR ALL
    USING (company_id::text = auth.jwt() ->> 'company_id');

CREATE POLICY company_records ON records FOR ALL
    USING (EXISTS (
        SELECT 1 FROM documents d
        WHERE d.id = records.document_id
        AND d.company_id::text = auth.jwt() ->> 'company_id'
    ));

CREATE POLICY company_usage ON usage_logs FOR SELECT
    USING (company_id::text = auth.jwt() ->> 'company_id');

CREATE POLICY company_stats_read ON company_stats FOR SELECT
    USING (company_id::text = auth.jwt() ->> 'company_id');

CREATE POLICY company_reports ON reports FOR ALL
    USING (company_id::text = auth.jwt() ->> 'company_id');

-- Emission factors: public read access
ALTER TABLE emission_factors ENABLE ROW LEVEL SECURITY;
CREATE POLICY public_read_emission_factors ON emission_factors FOR SELECT
    USING (true);


-- ======================
-- Functions & Triggers
-- ======================

-- Update updated_at timestamp automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_companies_updated_at BEFORE UPDATE ON companies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
