-- Patch 0071: Web authentication tables
-- web_users - whitelist of Google accounts allowed to access the dashboard

CREATE TABLE IF NOT EXISTS web_users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    display_name VARCHAR(100) NOT NULL,
    role VARCHAR(20) DEFAULT 'admin',
    google_name VARCHAR(255),
    google_picture TEXT,
    is_active BOOLEAN DEFAULT true,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Seed the two authorized users
INSERT INTO web_users (email, display_name, role) VALUES
    ('adge.denkers@gmail.com', 'Ka''tuar''el', 'admin'),
    ('rebecca.denkers@gmail.com', 'Seraphe', 'admin')
ON CONFLICT (email) DO NOTHING;
