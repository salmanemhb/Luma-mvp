-- Add waitlist_submissions table to MVP database
-- This allows both landing and MVP to share the same database

CREATE TABLE IF NOT EXISTS waitlist_submissions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    company VARCHAR(150) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('sme', 'consultant', 'corporate', 'other')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_waitlist_email ON waitlist_submissions(email);
CREATE INDEX IF NOT EXISTS idx_waitlist_created_at ON waitlist_submissions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_waitlist_role ON waitlist_submissions(role);

-- Add comment
COMMENT ON TABLE waitlist_submissions IS 'Waitlist submissions from landing page (getluma.es)';
