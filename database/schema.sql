
-- ============================================
-- AI Healthcare Assistant
-- Database Schema
-- ============================================

CREATE DATABASE IF NOT EXISTS healthcare_assistant_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE healthcare_assistant_db;

-- 1. User sessions
-- Groups multiple interactions into a conversation.
CREATE TABLE IF NOT EXISTS sessions (
    session_id CHAR(36) PRIMARY KEY,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 2. Interaction history
-- Stores the user's input and AI-generated response.
CREATE TABLE IF NOT EXISTS interactions (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    session_id CHAR(36) NOT NULL,
    user_input TEXT NOT NULL,
    ai_response MEDIUMTEXT NOT NULL,
    response_status ENUM('SUCCESS', 'ERROR')
        NOT NULL DEFAULT 'SUCCESS',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),

    INDEX idx_created_at (created_at),
    INDEX idx_session_id (session_id),

    CONSTRAINT fk_interaction_session
        FOREIGN KEY (session_id)
        REFERENCES sessions(session_id)
        ON DELETE CASCADE
) ENGINE=InnoDB;

-- 3. User feedback
-- Allows users to rate the usefulness of responses.
CREATE TABLE IF NOT EXISTS feedback (
    feedback_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    interaction_id INT UNSIGNED NOT NULL,
    rating TINYINT UNSIGNED NOT NULL,
    comments VARCHAR(500),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (feedback_id),

    CONSTRAINT chk_rating
        CHECK (rating BETWEEN 1 AND 5),

    CONSTRAINT fk_feedback_interaction
        FOREIGN KEY (interaction_id)
        REFERENCES interactions(id)
        ON DELETE CASCADE
) ENGINE=InnoDB;
