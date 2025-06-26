-- Enhanced Elite Coding Assistant - Supabase Learning Schema
-- =========================================================
-- 
-- This schema supports a comprehensive learning system for the 5-model
-- Elite Coding Assistant, enabling persistent storage of interactions,
-- learning patterns, knowledge accumulation, and performance optimization.
--
-- Author: Manus AI
-- Version: 1.0
-- Date: June 23, 2025

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- =====================================================
-- CORE SYSTEM TABLES
-- =====================================================

-- Users table for tracking individual user learning patterns
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE,
    preferences JSONB DEFAULT '{}',
    learning_profile JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Conversations table for grouping related interactions
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title TEXT,
    context_type TEXT DEFAULT 'general', -- 'general', 'project', 'learning_session'
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ended_at TIMESTAMP WITH TIME ZONE
);

-- =====================================================
-- INTERACTION TRACKING TABLES
-- =====================================================

-- Core interactions table - every request/response pair
CREATE TABLE interactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    user_prompt TEXT NOT NULL,
    user_prompt_embedding VECTOR(1536), -- OpenAI embedding for semantic search
    
    -- Routing and model selection
    initial_classification TEXT, -- 'math' or 'general'
    model_used TEXT NOT NULL, -- which model actually responded
    routing_confidence FLOAT,
    routing_reasoning TEXT,
    
    -- Response data
    response TEXT NOT NULL,
    response_embedding VECTOR(1536),
    response_time_ms INTEGER,
    token_usage JSONB, -- {request_tokens, response_tokens, total_tokens}
    
    -- Quality metrics
    success_rating INTEGER CHECK (success_rating >= 1 AND success_rating <= 5),
    user_feedback TEXT,
    feedback_type TEXT, -- 'positive', 'negative', 'correction', 'clarification'
    
    -- Learning data
    learning_tags TEXT[], -- tags for categorizing learning patterns
    complexity_score FLOAT, -- estimated complexity of the request
    domain_tags TEXT[], -- programming languages, frameworks, concepts
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Indexes for performance
    INDEX idx_interactions_conversation_id (conversation_id),
    INDEX idx_interactions_model_used (model_used),
    INDEX idx_interactions_created_at (created_at),
    INDEX idx_interactions_domain_tags USING GIN (domain_tags),
    INDEX idx_interactions_learning_tags USING GIN (learning_tags)
);

-- Fallback attempts table - tracks when primary models fail
CREATE TABLE fallback_attempts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    interaction_id UUID REFERENCES interactions(id) ON DELETE CASCADE,
    primary_model TEXT NOT NULL,
    fallback_model TEXT NOT NULL,
    fallback_reason TEXT, -- 'timeout', 'error', 'low_confidence', 'user_request'
    fallback_success BOOLEAN,
    fallback_response_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- LEARNING PATTERN TABLES
-- =====================================================

-- Routing patterns - learns optimal routing decisions
CREATE TABLE routing_patterns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pattern_signature TEXT UNIQUE NOT NULL, -- hash of key features
    
    -- Pattern characteristics
    keywords TEXT[],
    context_indicators TEXT[],
    complexity_range NUMRANGE, -- complexity score range
    domain_context TEXT[],
    
    -- Routing decisions
    recommended_model TEXT NOT NULL,
    confidence_threshold FLOAT DEFAULT 0.7,
    
    -- Performance data
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    avg_response_time_ms FLOAT,
    avg_user_rating FLOAT,
    
    -- Learning metadata
    pattern_strength FLOAT DEFAULT 0.5, -- how confident we are in this pattern
    last_reinforced TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_routing_patterns_keywords USING GIN (keywords),
    INDEX idx_routing_patterns_domain USING GIN (domain_context)
);

-- Model performance patterns - tracks how each model performs
CREATE TABLE model_performance_patterns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_name TEXT NOT NULL,
    
    -- Task characteristics
    task_type TEXT, -- 'code_generation', 'debugging', 'explanation', 'optimization'
    domain TEXT, -- 'python', 'javascript', 'algorithms', 'web_development'
    complexity_level TEXT, -- 'simple', 'medium', 'complex', 'expert'
    
    -- Performance metrics
    success_rate FLOAT,
    avg_response_time_ms FLOAT,
    avg_user_rating FLOAT,
    token_efficiency FLOAT, -- quality per token used
    
    -- Trend data
    performance_trend JSONB, -- time-series performance data
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    sample_size INTEGER DEFAULT 0,
    
    UNIQUE(model_name, task_type, domain, complexity_level)
);

-- Prompt optimization patterns - learns better prompts for each model
CREATE TABLE prompt_optimization_patterns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_name TEXT NOT NULL,
    
    -- Context
    task_category TEXT,
    user_preference_profile JSONB,
    
    -- Prompt variations
    base_prompt TEXT,
    optimized_prompt TEXT,
    optimization_type TEXT, -- 'clarity', 'specificity', 'context', 'formatting'
    
    -- Performance comparison
    base_performance JSONB, -- metrics before optimization
    optimized_performance JSONB, -- metrics after optimization
    improvement_score FLOAT,
    
    -- Usage tracking
    usage_count INTEGER DEFAULT 0,
    last_used TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- KNOWLEDGE BASE TABLES
-- =====================================================

-- Knowledge base for accumulated learning
CREATE TABLE knowledge_base (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Content
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    content_embedding VECTOR(1536),
    summary TEXT,
    
    -- Classification
    knowledge_type TEXT, -- 'concept', 'pattern', 'solution', 'best_practice'
    domain_tags TEXT[],
    complexity_level TEXT,
    
    -- Source tracking
    source_type TEXT, -- 'user_feedback', 'document_ingestion', 'interaction_learning'
    source_reference TEXT, -- reference to original source
    confidence_score FLOAT DEFAULT 0.5,
    
    -- Usage and validation
    usage_count INTEGER DEFAULT 0,
    validation_score FLOAT DEFAULT 0.5, -- how well this knowledge works
    last_validated TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_knowledge_base_domain_tags USING GIN (domain_tags),
    INDEX idx_knowledge_base_knowledge_type (knowledge_type),
    INDEX idx_knowledge_base_content_embedding USING ivfflat (content_embedding vector_cosine_ops)
);

-- Knowledge relationships - how concepts relate to each other
CREATE TABLE knowledge_relationships (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_knowledge_id UUID REFERENCES knowledge_base(id) ON DELETE CASCADE,
    target_knowledge_id UUID REFERENCES knowledge_base(id) ON DELETE CASCADE,
    relationship_type TEXT, -- 'prerequisite', 'related', 'contradicts', 'extends'
    strength FLOAT DEFAULT 0.5, -- how strong the relationship is
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(source_knowledge_id, target_knowledge_id, relationship_type)
);

-- =====================================================
-- LEARNING MATERIAL TABLES
-- =====================================================

-- Documents and materials ingested for learning
CREATE TABLE learning_materials (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Content
    title TEXT NOT NULL,
    content TEXT,
    file_path TEXT,
    file_type TEXT, -- 'pdf', 'markdown', 'code', 'url'
    
    -- Processing status
    processing_status TEXT DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed'
    extraction_metadata JSONB,
    
    -- Classification
    material_type TEXT, -- 'documentation', 'tutorial', 'reference', 'example'
    domain_tags TEXT[],
    difficulty_level TEXT,
    
    -- Learning integration
    knowledge_extracted INTEGER DEFAULT 0, -- count of knowledge items extracted
    integration_status TEXT DEFAULT 'pending',
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE,
    
    INDEX idx_learning_materials_domain_tags USING GIN (domain_tags),
    INDEX idx_learning_materials_status (processing_status)
);

-- Extracted knowledge from learning materials
CREATE TABLE extracted_knowledge (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    material_id UUID REFERENCES learning_materials(id) ON DELETE CASCADE,
    knowledge_id UUID REFERENCES knowledge_base(id) ON DELETE CASCADE,
    
    -- Extraction metadata
    extraction_method TEXT, -- 'manual', 'automated', 'ai_assisted'
    extraction_confidence FLOAT,
    page_reference TEXT, -- page number, section, etc.
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- FEEDBACK AND ADAPTATION TABLES
-- =====================================================

-- User feedback for continuous improvement
CREATE TABLE user_feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    interaction_id UUID REFERENCES interactions(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    -- Feedback content
    feedback_type TEXT, -- 'rating', 'correction', 'suggestion', 'complaint'
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    feedback_text TEXT,
    
    -- Specific feedback areas
    accuracy_rating INTEGER CHECK (accuracy_rating >= 1 AND accuracy_rating <= 5),
    helpfulness_rating INTEGER CHECK (helpfulness_rating >= 1 AND helpfulness_rating <= 5),
    clarity_rating INTEGER CHECK (clarity_rating >= 1 AND clarity_rating <= 5),
    
    -- Processing status
    processed BOOLEAN DEFAULT FALSE,
    processing_notes TEXT,
    action_taken TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE
);

-- System adaptations made based on learning
CREATE TABLE system_adaptations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Adaptation details
    adaptation_type TEXT, -- 'routing_rule', 'prompt_optimization', 'threshold_adjustment'
    target_component TEXT, -- which part of the system was adapted
    
    -- Change description
    description TEXT,
    old_configuration JSONB,
    new_configuration JSONB,
    
    -- Justification and results
    reasoning TEXT,
    expected_improvement TEXT,
    actual_results JSONB,
    
    -- Tracking
    implemented_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    evaluated_at TIMESTAMP WITH TIME ZONE,
    success_score FLOAT, -- how well the adaptation worked
    
    -- Rollback capability
    rollback_available BOOLEAN DEFAULT TRUE,
    rolled_back BOOLEAN DEFAULT FALSE,
    rollback_reason TEXT
);

-- =====================================================
-- PERFORMANCE MONITORING TABLES
-- =====================================================

-- System performance metrics over time
CREATE TABLE performance_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Time period
    metric_date DATE NOT NULL,
    metric_hour INTEGER, -- for hourly granularity
    
    -- Overall system metrics
    total_interactions INTEGER DEFAULT 0,
    avg_response_time_ms FLOAT,
    success_rate FLOAT,
    user_satisfaction_avg FLOAT,
    
    -- Model-specific metrics
    model_usage_distribution JSONB, -- usage count per model
    model_performance_scores JSONB, -- performance score per model
    
    -- Learning metrics
    new_patterns_learned INTEGER DEFAULT 0,
    knowledge_base_growth INTEGER DEFAULT 0,
    adaptations_made INTEGER DEFAULT 0,
    
    -- Resource usage
    token_usage_total INTEGER DEFAULT 0,
    processing_time_total_ms BIGINT DEFAULT 0,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(metric_date, metric_hour)
);

-- Learning progress tracking
CREATE TABLE learning_progress (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Progress tracking
    metric_name TEXT NOT NULL, -- 'routing_accuracy', 'response_quality', 'user_satisfaction'
    current_value FLOAT,
    previous_value FLOAT,
    improvement_rate FLOAT,
    
    -- Context
    measurement_period TEXT, -- 'daily', 'weekly', 'monthly'
    domain_context TEXT, -- specific domain if applicable
    
    -- Trend analysis
    trend_direction TEXT, -- 'improving', 'declining', 'stable'
    confidence_level FLOAT,
    
    measured_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_learning_progress_metric (metric_name),
    INDEX idx_learning_progress_measured_at (measured_at)
);

-- =====================================================
-- VIEWS FOR COMMON QUERIES
-- =====================================================

-- View for recent interaction analysis
CREATE VIEW recent_interactions_analysis AS
SELECT 
    i.id,
    i.user_prompt,
    i.model_used,
    i.success_rating,
    i.response_time_ms,
    i.domain_tags,
    i.created_at,
    u.username,
    c.context_type
FROM interactions i
JOIN conversations c ON i.conversation_id = c.id
LEFT JOIN users u ON c.user_id = u.id
WHERE i.created_at >= NOW() - INTERVAL '7 days'
ORDER BY i.created_at DESC;

-- View for model performance summary
CREATE VIEW model_performance_summary AS
SELECT 
    model_name,
    COUNT(*) as total_interactions,
    AVG(success_rate) as avg_success_rate,
    AVG(avg_response_time_ms) as avg_response_time,
    AVG(avg_user_rating) as avg_user_rating,
    MAX(last_updated) as last_updated
FROM model_performance_patterns
GROUP BY model_name;

-- View for learning pattern effectiveness
CREATE VIEW learning_pattern_effectiveness AS
SELECT 
    rp.pattern_signature,
    rp.recommended_model,
    rp.success_count,
    rp.failure_count,
    CASE 
        WHEN (rp.success_count + rp.failure_count) > 0 
        THEN rp.success_count::FLOAT / (rp.success_count + rp.failure_count)
        ELSE 0 
    END as success_rate,
    rp.pattern_strength,
    rp.last_reinforced
FROM routing_patterns rp
WHERE rp.success_count + rp.failure_count >= 5 -- minimum sample size
ORDER BY success_rate DESC, pattern_strength DESC;

-- =====================================================
-- FUNCTIONS FOR LEARNING OPERATIONS
-- =====================================================

-- Function to update routing pattern based on interaction outcome
CREATE OR REPLACE FUNCTION update_routing_pattern(
    p_keywords TEXT[],
    p_domain_context TEXT[],
    p_complexity FLOAT,
    p_model_used TEXT,
    p_success BOOLEAN
) RETURNS VOID AS $$
DECLARE
    pattern_sig TEXT;
    existing_pattern RECORD;
BEGIN
    -- Generate pattern signature
    pattern_sig := md5(array_to_string(p_keywords, ',') || '|' || 
                      array_to_string(p_domain_context, ',') || '|' || 
                      p_complexity::TEXT);
    
    -- Check if pattern exists
    SELECT * INTO existing_pattern 
    FROM routing_patterns 
    WHERE pattern_signature = pattern_sig;
    
    IF FOUND THEN
        -- Update existing pattern
        IF p_success THEN
            UPDATE routing_patterns 
            SET success_count = success_count + 1,
                pattern_strength = LEAST(1.0, pattern_strength + 0.1),
                last_reinforced = NOW()
            WHERE pattern_signature = pattern_sig;
        ELSE
            UPDATE routing_patterns 
            SET failure_count = failure_count + 1,
                pattern_strength = GREATEST(0.1, pattern_strength - 0.05)
            WHERE pattern_signature = pattern_sig;
        END IF;
    ELSE
        -- Create new pattern
        INSERT INTO routing_patterns (
            pattern_signature, keywords, domain_context, 
            recommended_model, success_count, failure_count,
            pattern_strength
        ) VALUES (
            pattern_sig, p_keywords, p_domain_context,
            p_model_used, 
            CASE WHEN p_success THEN 1 ELSE 0 END,
            CASE WHEN p_success THEN 0 ELSE 1 END,
            CASE WHEN p_success THEN 0.6 ELSE 0.4 END
        );
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Function to get optimal model recommendation
CREATE OR REPLACE FUNCTION get_model_recommendation(
    p_keywords TEXT[],
    p_domain_context TEXT[],
    p_complexity FLOAT
) RETURNS TABLE(model_name TEXT, confidence FLOAT) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        rp.recommended_model,
        rp.pattern_strength * (rp.success_count::FLOAT / GREATEST(1, rp.success_count + rp.failure_count))
    FROM routing_patterns rp
    WHERE rp.keywords && p_keywords 
       OR rp.domain_context && p_domain_context
    ORDER BY 
        (rp.keywords && p_keywords)::INT + (rp.domain_context && p_domain_context)::INT DESC,
        rp.pattern_strength DESC
    LIMIT 3;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- TRIGGERS FOR AUTOMATIC UPDATES
-- =====================================================

-- Trigger to update conversation updated_at
CREATE OR REPLACE FUNCTION update_conversation_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE conversations 
    SET updated_at = NOW() 
    WHERE id = NEW.conversation_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_conversation_timestamp
    AFTER INSERT ON interactions
    FOR EACH ROW
    EXECUTE FUNCTION update_conversation_timestamp();

-- Trigger to update user learning profile
CREATE OR REPLACE FUNCTION update_user_learning_profile()
RETURNS TRIGGER AS $$
DECLARE
    user_uuid UUID;
BEGIN
    -- Get user ID from conversation
    SELECT c.user_id INTO user_uuid
    FROM conversations c
    WHERE c.id = NEW.conversation_id;
    
    IF user_uuid IS NOT NULL THEN
        -- Update user's learning profile with interaction data
        UPDATE users 
        SET learning_profile = learning_profile || jsonb_build_object(
            'last_interaction', NOW(),
            'total_interactions', COALESCE((learning_profile->>'total_interactions')::INT, 0) + 1,
            'preferred_domains', NEW.domain_tags
        ),
        updated_at = NOW()
        WHERE id = user_uuid;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_user_learning_profile
    AFTER INSERT ON interactions
    FOR EACH ROW
    EXECUTE FUNCTION update_user_learning_profile();

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Additional indexes for common query patterns
CREATE INDEX idx_interactions_success_rating ON interactions(success_rating);
CREATE INDEX idx_interactions_response_time ON interactions(response_time_ms);
CREATE INDEX idx_interactions_user_feedback ON interactions(feedback_type) WHERE feedback_type IS NOT NULL;

CREATE INDEX idx_routing_patterns_strength ON routing_patterns(pattern_strength);
CREATE INDEX idx_routing_patterns_last_reinforced ON routing_patterns(last_reinforced);

CREATE INDEX idx_knowledge_base_confidence ON knowledge_base(confidence_score);
CREATE INDEX idx_knowledge_base_usage ON knowledge_base(usage_count);

CREATE INDEX idx_performance_metrics_date ON performance_metrics(metric_date);
CREATE INDEX idx_learning_progress_trend ON learning_progress(trend_direction);

-- =====================================================
-- INITIAL DATA AND CONFIGURATION
-- =====================================================

-- Insert default system user for automated learning
INSERT INTO users (id, username, email, preferences) VALUES 
(uuid_generate_v4(), 'system_learning', 'system@learning.ai', '{"automated": true}');

-- Insert initial routing patterns based on the original system design
INSERT INTO routing_patterns (pattern_signature, keywords, domain_context, recommended_model, pattern_strength) VALUES
('math_keywords', ARRAY['algorithm', 'complexity', 'optimization', 'mathematical', 'calculate'], ARRAY['algorithms', 'mathematics'], 'mathstral:7b', 0.8),
('general_coding', ARRAY['function', 'class', 'variable', 'debug', 'implement'], ARRAY['programming', 'development'], 'deepseek-coder-v2:16b-lite-instruct', 0.8),
('architecture_design', ARRAY['design', 'architecture', 'system', 'scalable', 'microservices'], ARRAY['system_design', 'architecture'], 'wizardcoder:13b-python', 0.7);

-- Insert initial model performance baselines
INSERT INTO model_performance_patterns (model_name, task_type, domain, complexity_level, success_rate, avg_response_time_ms, sample_size) VALUES
('openhermes:7b', 'routing', 'general', 'simple', 0.85, 1500, 0),
('mathstral:7b', 'code_generation', 'algorithms', 'medium', 0.80, 3000, 0),
('deepseek-coder-v2:16b-lite-instruct', 'code_generation', 'general', 'medium', 0.85, 4000, 0),
('codellama:13b', 'code_generation', 'general', 'simple', 0.80, 3500, 0),
('wizardcoder:13b-python', 'code_generation', 'complex', 'expert', 0.75, 5000, 0);

COMMENT ON SCHEMA public IS 'Enhanced Elite Coding Assistant Learning Schema - Supports comprehensive learning and adaptation for multi-model AI orchestration system';

