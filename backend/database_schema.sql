-- =====================================================
-- AYRAQ Database Schema for Supabase
-- AI-powered mobile application for women's safety
-- =====================================================
-- Run this SQL in your Supabase SQL Editor to create the required tables

-- =====================================================
-- UTILITY FUNCTIONS
-- =====================================================

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- =====================================================
-- USERS TABLE
-- =====================================================

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    user_type VARCHAR(50) NOT NULL CHECK (user_type IN ('Student', 'Professional', 'Other')),
    gender VARCHAR(10) NOT NULL CHECK (gender IN ('Male', 'Female', 'Other')),
    dob DATE NOT NULL,
    avatar_url TEXT,
    is_active BOOLEAN DEFAULT true,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for users table
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);

-- Create trigger to automatically update updated_at for users
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- USER CONNECTIONS/REQUESTS TABLE
-- =====================================================

-- Create user connections table for friend/connection requests
CREATE TABLE IF NOT EXISTS user_connections (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    requester_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    requested_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'rejected', 'blocked')),
    message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(requester_id, requested_id)
);

-- Create indexes for user connections
CREATE INDEX IF NOT EXISTS idx_user_connections_requester ON user_connections(requester_id);
CREATE INDEX IF NOT EXISTS idx_user_connections_requested ON user_connections(requested_id);
CREATE INDEX IF NOT EXISTS idx_user_connections_status ON user_connections(status);

-- Create trigger for user connections
CREATE TRIGGER update_user_connections_updated_at
    BEFORE UPDATE ON user_connections
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- CHAT CONVERSATIONS TABLE
-- =====================================================

-- Create conversations table
CREATE TABLE IF NOT EXISTS conversations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    participant_1_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    participant_2_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    last_message_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(participant_1_id, participant_2_id)
);

-- Create indexes for conversations
CREATE INDEX IF NOT EXISTS idx_conversations_participant_1 ON conversations(participant_1_id);
CREATE INDEX IF NOT EXISTS idx_conversations_participant_2 ON conversations(participant_2_id);
CREATE INDEX IF NOT EXISTS idx_conversations_last_message ON conversations(last_message_at);

-- Create trigger for conversations
CREATE TRIGGER update_conversations_updated_at
    BEFORE UPDATE ON conversations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- CHAT MESSAGES TABLE
-- =====================================================

-- Create messages table
CREATE TABLE IF NOT EXISTS messages (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    sender_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    message_text TEXT NOT NULL,
    message_type VARCHAR(20) DEFAULT 'text' CHECK (message_type IN ('text', 'image', 'file', 'location')),
    file_url TEXT,
    is_read BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for messages
CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_sender ON messages(sender_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);
CREATE INDEX IF NOT EXISTS idx_messages_is_read ON messages(is_read);

-- =====================================================
-- THREAT DETECTION TABLE
-- =====================================================

-- Create threat detections table for AI-powered threat analysis
CREATE TABLE IF NOT EXISTS threat_detections (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    threat_type VARCHAR(50) NOT NULL CHECK (threat_type IN ('cyberbullying', 'harassment', 'stalking', 'inappropriate_content', 'phishing', 'other')),
    threat_level VARCHAR(20) NOT NULL DEFAULT 'low' CHECK (threat_level IN ('low', 'medium', 'high', 'critical')),
    content_analyzed TEXT NOT NULL,
    ai_confidence_score DECIMAL(3,2) CHECK (ai_confidence_score >= 0 AND ai_confidence_score <= 1),
    source_platform VARCHAR(100),
    source_url TEXT,
    is_verified BOOLEAN DEFAULT false,
    action_taken VARCHAR(50) CHECK (action_taken IN ('none', 'reported', 'blocked', 'escalated')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for threat detections
CREATE INDEX IF NOT EXISTS idx_threat_detections_user ON threat_detections(user_id);
CREATE INDEX IF NOT EXISTS idx_threat_detections_type ON threat_detections(threat_type);
CREATE INDEX IF NOT EXISTS idx_threat_detections_level ON threat_detections(threat_level);
CREATE INDEX IF NOT EXISTS idx_threat_detections_created_at ON threat_detections(created_at);
CREATE INDEX IF NOT EXISTS idx_threat_detections_verified ON threat_detections(is_verified);

-- Create trigger for threat detections
CREATE TRIGGER update_threat_detections_updated_at
    BEFORE UPDATE ON threat_detections
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- EVIDENCE STORAGE TABLE
-- =====================================================

-- Create evidence table for secure storage of screenshots and files
CREATE TABLE IF NOT EXISTS evidence (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    threat_detection_id UUID REFERENCES threat_detections(id) ON DELETE SET NULL,
    evidence_type VARCHAR(20) NOT NULL CHECK (evidence_type IN ('screenshot', 'document', 'audio', 'video', 'text')),
    file_name VARCHAR(255) NOT NULL,
    file_url TEXT NOT NULL,
    file_size BIGINT,
    mime_type VARCHAR(100),
    description TEXT,
    is_encrypted BOOLEAN DEFAULT true,
    hash_value VARCHAR(64), -- For file integrity verification
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for evidence
CREATE INDEX IF NOT EXISTS idx_evidence_user ON evidence(user_id);
CREATE INDEX IF NOT EXISTS idx_evidence_threat ON evidence(threat_detection_id);
CREATE INDEX IF NOT EXISTS idx_evidence_type ON evidence(evidence_type);
CREATE INDEX IF NOT EXISTS idx_evidence_created_at ON evidence(created_at);

-- =====================================================
-- NOTIFICATIONS TABLE
-- =====================================================

-- Create notifications table for alerts and updates
CREATE TABLE IF NOT EXISTS notifications (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    notification_type VARCHAR(50) NOT NULL CHECK (notification_type IN ('threat_alert', 'connection_request', 'message', 'system_update', 'legal_guidance', 'support_resource')),
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    priority VARCHAR(20) DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    is_read BOOLEAN DEFAULT false,
    action_url TEXT,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for notifications
CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_type ON notifications(notification_type);
CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON notifications(is_read);
CREATE INDEX IF NOT EXISTS idx_notifications_priority ON notifications(priority);
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at);

-- =====================================================
-- LEGAL GUIDANCE TABLE
-- =====================================================

-- Create legal guidance table for legal resources and advice
CREATE TABLE IF NOT EXISTS legal_guidance (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL CHECK (category IN ('cybercrime', 'harassment', 'privacy', 'reporting', 'emergency', 'general')),
    content TEXT NOT NULL,
    jurisdiction VARCHAR(100), -- Country/State specific laws
    is_active BOOLEAN DEFAULT true,
    priority_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for legal guidance
CREATE INDEX IF NOT EXISTS idx_legal_guidance_category ON legal_guidance(category);
CREATE INDEX IF NOT EXISTS idx_legal_guidance_is_active ON legal_guidance(is_active);
CREATE INDEX IF NOT EXISTS idx_legal_guidance_priority ON legal_guidance(priority_order);

-- Create trigger for legal guidance
CREATE TRIGGER update_legal_guidance_updated_at
    BEFORE UPDATE ON legal_guidance
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- SUPPORT RESOURCES TABLE
-- =====================================================

-- Create support resources table for emotional support and helplines
CREATE TABLE IF NOT EXISTS support_resources (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    resource_type VARCHAR(50) NOT NULL CHECK (resource_type IN ('helpline', 'counseling', 'legal_aid', 'emergency', 'online_support', 'self_help')),
    description TEXT,
    contact_phone VARCHAR(20),
    contact_email VARCHAR(255),
    website_url TEXT,
    address TEXT,
    availability VARCHAR(100), -- e.g., "24/7", "Mon-Fri 9AM-5PM"
    is_emergency BOOLEAN DEFAULT false,
    country VARCHAR(100),
    state_province VARCHAR(100),
    city VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for support resources
CREATE INDEX IF NOT EXISTS idx_support_resources_type ON support_resources(resource_type);
CREATE INDEX IF NOT EXISTS idx_support_resources_emergency ON support_resources(is_emergency);
CREATE INDEX IF NOT EXISTS idx_support_resources_location ON support_resources(country, state_province, city);
CREATE INDEX IF NOT EXISTS idx_support_resources_is_active ON support_resources(is_active);

-- Create trigger for support resources
CREATE TRIGGER update_support_resources_updated_at
    BEFORE UPDATE ON support_resources
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- USER SETTINGS TABLE
-- =====================================================

-- Create user settings table for app preferences
CREATE TABLE IF NOT EXISTS user_settings (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    threat_detection_enabled BOOLEAN DEFAULT true,
    notification_preferences JSONB DEFAULT '{"threat_alerts": true, "connection_requests": true, "messages": true, "system_updates": false}',
    privacy_settings JSONB DEFAULT '{"profile_visibility": "friends", "location_sharing": false, "data_sharing": false}',
    emergency_contacts JSONB DEFAULT '[]', -- Array of contact objects
    auto_screenshot BOOLEAN DEFAULT false,
    overlay_enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for user settings
CREATE INDEX IF NOT EXISTS idx_user_settings_user ON user_settings(user_id);

-- Create trigger for user settings
CREATE TRIGGER update_user_settings_updated_at
    BEFORE UPDATE ON user_settings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- PROFESSIONAL PROFILES TABLE
-- =====================================================

-- Create professional profiles table for advocates, police, doctors, etc.
CREATE TABLE IF NOT EXISTS professional_profiles (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    profession VARCHAR(50) NOT NULL CHECK (profession IN ('Advocate', 'Police', 'Doctor', 'Engineer', 'Counselor', 'Legal_Aid', 'Other')),
    license_number VARCHAR(100),
    organization VARCHAR(255),
    specialization TEXT,
    years_of_experience INTEGER,
    verification_status VARCHAR(20) DEFAULT 'pending' CHECK (verification_status IN ('pending', 'verified', 'rejected')),
    verification_documents JSONB DEFAULT '[]', -- Array of document URLs
    availability_hours JSONB DEFAULT '{"monday": [], "tuesday": [], "wednesday": [], "thursday": [], "friday": [], "saturday": [], "sunday": []}',
    consultation_fee DECIMAL(10,2),
    rating DECIMAL(2,1) DEFAULT 0.0 CHECK (rating >= 0 AND rating <= 5),
    total_reviews INTEGER DEFAULT 0,
    is_available BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for professional profiles
CREATE INDEX IF NOT EXISTS idx_professional_profiles_user ON professional_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_professional_profiles_profession ON professional_profiles(profession);
CREATE INDEX IF NOT EXISTS idx_professional_profiles_verification ON professional_profiles(verification_status);
CREATE INDEX IF NOT EXISTS idx_professional_profiles_available ON professional_profiles(is_available);
CREATE INDEX IF NOT EXISTS idx_professional_profiles_rating ON professional_profiles(rating);

-- Create trigger for professional profiles
CREATE TRIGGER update_professional_profiles_updated_at
    BEFORE UPDATE ON professional_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- REVIEWS AND RATINGS TABLE
-- =====================================================

-- Create reviews table for professional ratings
CREATE TABLE IF NOT EXISTS reviews (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    reviewer_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    professional_id UUID NOT NULL REFERENCES professional_profiles(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT,
    is_anonymous BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(reviewer_id, professional_id)
);

-- Create indexes for reviews
CREATE INDEX IF NOT EXISTS idx_reviews_reviewer ON reviews(reviewer_id);
CREATE INDEX IF NOT EXISTS idx_reviews_professional ON reviews(professional_id);
CREATE INDEX IF NOT EXISTS idx_reviews_rating ON reviews(rating);
CREATE INDEX IF NOT EXISTS idx_reviews_created_at ON reviews(created_at);

-- =====================================================
-- EMERGENCY CONTACTS TABLE
-- =====================================================

-- Create emergency contacts table
CREATE TABLE IF NOT EXISTS emergency_contacts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    contact_name VARCHAR(255) NOT NULL,
    contact_phone VARCHAR(20) NOT NULL,
    contact_email VARCHAR(255),
    relationship VARCHAR(50), -- e.g., "Mother", "Friend", "Lawyer"
    is_primary BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for emergency contacts
CREATE INDEX IF NOT EXISTS idx_emergency_contacts_user ON emergency_contacts(user_id);
CREATE INDEX IF NOT EXISTS idx_emergency_contacts_primary ON emergency_contacts(is_primary);

-- Create trigger for emergency contacts
CREATE TRIGGER update_emergency_contacts_updated_at
    BEFORE UPDATE ON emergency_contacts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- =====================================================

-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_connections ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE threat_detections ENABLE ROW LEVEL SECURITY;
ALTER TABLE evidence ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE professional_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE reviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE emergency_contacts ENABLE ROW LEVEL SECURITY;

-- Users table policies
CREATE POLICY "Users can view their own profile" ON users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update their own profile" ON users
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Allow user registration" ON users
    FOR INSERT WITH CHECK (true);

-- User connections policies
CREATE POLICY "Users can view their own connections" ON user_connections
    FOR SELECT USING (auth.uid() = requester_id OR auth.uid() = requested_id);

CREATE POLICY "Users can create connection requests" ON user_connections
    FOR INSERT WITH CHECK (auth.uid() = requester_id);

CREATE POLICY "Users can update their connection requests" ON user_connections
    FOR UPDATE USING (auth.uid() = requester_id OR auth.uid() = requested_id);

-- Conversations policies
CREATE POLICY "Users can view their own conversations" ON conversations
    FOR SELECT USING (auth.uid() = participant_1_id OR auth.uid() = participant_2_id);

CREATE POLICY "Users can create conversations" ON conversations
    FOR INSERT WITH CHECK (auth.uid() = participant_1_id OR auth.uid() = participant_2_id);

-- Messages policies
CREATE POLICY "Users can view messages in their conversations" ON messages
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM conversations
            WHERE id = conversation_id
            AND (participant_1_id = auth.uid() OR participant_2_id = auth.uid())
        )
    );

CREATE POLICY "Users can send messages in their conversations" ON messages
    FOR INSERT WITH CHECK (
        auth.uid() = sender_id AND
        EXISTS (
            SELECT 1 FROM conversations
            WHERE id = conversation_id
            AND (participant_1_id = auth.uid() OR participant_2_id = auth.uid())
        )
    );

-- Threat detections policies
CREATE POLICY "Users can view their own threat detections" ON threat_detections
    FOR ALL USING (auth.uid() = user_id);

-- Evidence policies
CREATE POLICY "Users can manage their own evidence" ON evidence
    FOR ALL USING (auth.uid() = user_id);

-- Notifications policies
CREATE POLICY "Users can view their own notifications" ON notifications
    FOR ALL USING (auth.uid() = user_id);

-- User settings policies
CREATE POLICY "Users can manage their own settings" ON user_settings
    FOR ALL USING (auth.uid() = user_id);

-- Professional profiles policies
CREATE POLICY "Users can view verified professional profiles" ON professional_profiles
    FOR SELECT USING (verification_status = 'verified' OR auth.uid() = user_id);

CREATE POLICY "Users can manage their own professional profile" ON professional_profiles
    FOR ALL USING (auth.uid() = user_id);

-- Reviews policies
CREATE POLICY "Users can view all reviews" ON reviews
    FOR SELECT USING (true);

CREATE POLICY "Users can create reviews" ON reviews
    FOR INSERT WITH CHECK (auth.uid() = reviewer_id);

-- Emergency contacts policies
CREATE POLICY "Users can manage their own emergency contacts" ON emergency_contacts
    FOR ALL USING (auth.uid() = user_id);

-- Legal guidance and support resources are public (no RLS needed)
-- These tables contain general information accessible to all users

-- =====================================================
-- SAMPLE DATA (Optional - Remove in Production)
-- =====================================================

-- Insert sample legal guidance
INSERT INTO legal_guidance (title, category, content, jurisdiction) VALUES
('Reporting Cyberbullying', 'cybercrime', 'Steps to report cyberbullying incidents to authorities...', 'General'),
('Online Harassment Laws', 'harassment', 'Understanding legal protections against online harassment...', 'General'),
('Privacy Rights', 'privacy', 'Your rights regarding personal data and privacy online...', 'General'),
('Emergency Reporting', 'emergency', 'How to report immediate threats and emergencies...', 'General');

-- Insert sample support resources
INSERT INTO support_resources (name, resource_type, description, contact_phone, website_url, availability, is_emergency, country) VALUES
('National Domestic Violence Hotline', 'helpline', '24/7 confidential support for domestic violence victims', '1-800-799-7233', 'https://www.thehotline.org', '24/7', true, 'USA'),
('Crisis Text Line', 'helpline', 'Free 24/7 crisis support via text message', '741741', 'https://www.crisistextline.org', '24/7', true, 'USA'),
('RAINN National Sexual Assault Hotline', 'helpline', 'Support for sexual assault survivors', '1-800-656-4673', 'https://www.rainn.org', '24/7', true, 'USA'),
('Women''s Legal Aid', 'legal_aid', 'Free legal assistance for women', '1-800-555-0123', 'https://example.com', 'Mon-Fri 9AM-5PM', false, 'USA');

-- Create a function to automatically create user settings when a user is created
CREATE OR REPLACE FUNCTION create_user_settings()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO user_settings (user_id) VALUES (NEW.id);
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically create user settings
CREATE TRIGGER create_user_settings_trigger
    AFTER INSERT ON users
    FOR EACH ROW
    EXECUTE FUNCTION create_user_settings();

-- =====================================================
-- COMPLETION MESSAGE
-- =====================================================

-- Database schema creation completed successfully!
-- All tables, indexes, triggers, and policies have been created.
-- The database is ready for the AYRAQ application.
