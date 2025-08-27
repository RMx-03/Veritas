-- Veritas Database Schema for Supabase
-- This file can be executed in Supabase SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Analysis Results Table
CREATE TABLE IF NOT EXISTS analysis_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    filename VARCHAR(255),
    analysis_data JSONB NOT NULL,
    nutrition_facts JSONB,
    overall_score INTEGER CHECK (overall_score >= 0 AND overall_score <= 100),
    health_recommendation JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_analysis_results_created_at ON analysis_results(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_analysis_results_score ON analysis_results(overall_score);
CREATE INDEX IF NOT EXISTS idx_analysis_results_filename ON analysis_results(filename);

-- User Sessions Table (optional, for future user management)
CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_token VARCHAR(255) UNIQUE NOT NULL,
    user_agent TEXT,
    ip_address INET,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() + INTERVAL '7 days'
);

-- Analysis History with User Sessions (for future use)
CREATE TABLE IF NOT EXISTS user_analysis_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES user_sessions(id) ON DELETE CASCADE,
    analysis_id UUID REFERENCES analysis_results(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Food Database Cache (to cache USDA/OpenFoodFacts API responses)
CREATE TABLE IF NOT EXISTS food_database_cache (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    food_name VARCHAR(255) NOT NULL,
    source VARCHAR(50) NOT NULL, -- 'usda' or 'openfoodfacts'
    external_id VARCHAR(255),
    cached_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() + INTERVAL '30 days'
);

CREATE INDEX IF NOT EXISTS idx_food_cache_name_source ON food_database_cache(food_name, source);
CREATE INDEX IF NOT EXISTS idx_food_cache_expires ON food_database_cache(expires_at);

-- Ingredient Analysis Cache
CREATE TABLE IF NOT EXISTS ingredient_analysis_cache (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ingredient_name VARCHAR(255) NOT NULL,
    analysis_data JSONB NOT NULL,
    risk_level VARCHAR(20), -- 'low', 'medium', 'high'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_ingredient_cache_name ON ingredient_analysis_cache(ingredient_name);

-- System Statistics Table
CREATE TABLE IF NOT EXISTS system_statistics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    stat_date DATE NOT NULL,
    total_analyses INTEGER DEFAULT 0,
    average_score DECIMAL(5,2) DEFAULT 0,
    api_calls_cohere INTEGER DEFAULT 0,
    api_calls_usda INTEGER DEFAULT 0,
    api_calls_openfoodfacts INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_system_stats_date ON system_statistics(stat_date);

-- Function to update timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for automatic timestamp updates
CREATE TRIGGER update_analysis_results_updated_at 
    BEFORE UPDATE ON analysis_results 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ingredient_cache_updated_at 
    BEFORE UPDATE ON ingredient_analysis_cache 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_system_stats_updated_at 
    BEFORE UPDATE ON system_statistics 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Row Level Security (RLS) - Optional for future user management
-- ALTER TABLE analysis_results ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE user_sessions ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE user_analysis_history ENABLE ROW LEVEL SECURITY;

-- Sample data insertion (for testing)
-- INSERT INTO analysis_results (filename, analysis_data, nutrition_facts, overall_score, health_recommendation)
-- VALUES (
--     'sample_label.jpg',
--     '{"test": true}',
--     '{"calories": 150, "fat": 5, "sodium": 200}',
--     75,
--     '{"level": "safe", "summary": "This is a test product"}'
-- );

-- Views for analytics
CREATE OR REPLACE VIEW daily_analysis_stats AS
SELECT 
    DATE(created_at) as analysis_date,
    COUNT(*) as total_analyses,
    AVG(overall_score) as average_score,
    COUNT(CASE WHEN overall_score >= 75 THEN 1 END) as safe_products,
    COUNT(CASE WHEN overall_score >= 50 AND overall_score < 75 THEN 1 END) as moderate_products,
    COUNT(CASE WHEN overall_score < 50 THEN 1 END) as avoid_products
FROM analysis_results 
GROUP BY DATE(created_at)
ORDER BY analysis_date DESC;

CREATE OR REPLACE VIEW recent_analyses AS
SELECT 
    id,
    filename,
    overall_score,
    (health_recommendation->>'level') as recommendation_level,
    created_at
FROM analysis_results 
ORDER BY created_at DESC 
LIMIT 100;
