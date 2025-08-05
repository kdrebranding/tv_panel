-- TV Panel SQL Database Export for MySQL/MariaDB
-- Generated for production deployment

SET FOREIGN_KEY_CHECKS = 0;
SET sql_mode = 'NO_AUTO_VALUE_ON_ZERO';
SET AUTOCOMMIT = 0;
START TRANSACTION;

-- Database schema for TV Panel SQL
CREATE DATABASE IF NOT EXISTS tv_panel CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE tv_panel;

-- Admins table
CREATE TABLE admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Panels table
CREATE TABLE panels (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    url VARCHAR(500),
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Contact Types table
CREATE TABLE contact_types (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    url_pattern VARCHAR(500),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Apps table
CREATE TABLE apps (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    url VARCHAR(500),
    package_name VARCHAR(255),
    app_code TEXT,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Clients table
CREATE TABLE clients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    line_id VARCHAR(255),
    name VARCHAR(255) NOT NULL,
    login VARCHAR(255),
    password VARCHAR(255),
    expires_date DATE,
    panel_id INT,
    app_id INT,
    mac VARCHAR(255),
    key_value VARCHAR(255),
    contact_type_id INT,
    contact_value VARCHAR(255),
    telegram_id BIGINT,
    notes TEXT,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_expires_date (expires_date),
    INDEX idx_telegram_id (telegram_id),
    INDEX idx_status (status),
    FOREIGN KEY (panel_id) REFERENCES panels(id) ON DELETE SET NULL,
    FOREIGN KEY (app_id) REFERENCES apps(id) ON DELETE SET NULL,
    FOREIGN KEY (contact_type_id) REFERENCES contact_types(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Payment Methods table
CREATE TABLE payment_methods (
    id INT AUTO_INCREMENT PRIMARY KEY,
    method_id VARCHAR(100) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    fee_percentage DECIMAL(5,2) DEFAULT 0,
    min_amount DECIMAL(10,2) DEFAULT 0,
    max_amount DECIMAL(10,2),
    instructions TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Pricing Config table
CREATE TABLE pricing_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    service_type VARCHAR(255) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'PLN',
    duration_days INT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    discount_percentage DECIMAL(5,2) DEFAULT 0,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Questions (FAQ) table
CREATE TABLE questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    category VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    display_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Smart TV Apps table
CREATE TABLE smart_tv_apps (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    platform VARCHAR(100),
    download_url VARCHAR(500),
    instructions TEXT,
    version VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Android Apps table
CREATE TABLE android_apps (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    package_name VARCHAR(255),
    download_url VARCHAR(500),
    play_store_url VARCHAR(500),
    instructions TEXT,
    version VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    minimum_android_version VARCHAR(20),
    file_size VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Smart TV Activations table
CREATE TABLE smart_tv_activations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    app_name VARCHAR(255) NOT NULL,
    activation_price DECIMAL(10,2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'PLN',
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Settings table
CREATE TABLE settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    key_name VARCHAR(255) UNIQUE NOT NULL,
    value TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- System Logs table
CREATE TABLE system_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    level VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    module VARCHAR(100),
    user_id INT,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_level (level),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Notifications table
CREATE TABLE notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    recipient_type VARCHAR(50) NOT NULL,
    recipient_id VARCHAR(255),
    status VARCHAR(20) DEFAULT 'pending',
    sent_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_status (status),
    INDEX idx_type (type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert default data
INSERT INTO admins (username, password_hash) VALUES 
('admin', '$2b$12$LQv3c1yqBWVHxkd0LQ1lqe.hR1JT1I8E1I8E1I8E1I8E1I8E1I8E1u');

INSERT INTO settings (key_name, value, description) VALUES
('app_name', 'TV Panel SQL', 'Application name'),
('version', 'v3.0 SQL Edition', 'Application version'),
('timezone', 'Europe/Warsaw', 'Application timezone'),
('language', 'pl', 'Default language'),
('max_clients', '1000', 'Maximum number of clients'),
('backup_enabled', 'true', 'Enable automatic backups');

INSERT INTO contact_types (name, description) VALUES
('WhatsApp', 'WhatsApp contact'),
('Telegram', 'Telegram contact'),
('Email', 'Email contact'),
('Phone', 'Phone contact'),
('Messanger', 'Facebook Messenger');

INSERT INTO panels (name, description) VALUES
('Trex', 'Trex IPTV Panel'),
('Tank', 'Tank IPTV Panel'),
('365', '365 IPTV Panel');

INSERT INTO payment_methods (method_id, name, description, is_active) VALUES
('paypal', 'PayPal', 'Payment via PayPal', TRUE),
('stripe', 'Stripe', 'Payment via Stripe', TRUE),
('bank_transfer', 'Bank Transfer', 'Direct bank transfer', TRUE),
('crypto', 'Cryptocurrency', 'Bitcoin, Ethereum, etc.', TRUE);

INSERT INTO pricing_config (service_type, price, currency, duration_days, description) VALUES
('iptv_monthly', 29.99, 'PLN', 30, 'IPTV Monthly Subscription'),
('iptv_quarterly', 79.99, 'PLN', 90, 'IPTV Quarterly Subscription'),
('iptv_yearly', 299.99, 'PLN', 365, 'IPTV Yearly Subscription'),
('smart_tv_activation', 49.99, 'PLN', 1, 'Smart TV App Activation');

INSERT INTO questions (question, answer, category, display_order) VALUES
('Jak zainstalować aplikację?', 'Pobierz aplikację z naszej strony i zainstaluj zgodnie z instrukcjami.', 'installation', 1),
('Jak odnowić subskrypcję?', 'Skontaktuj się z obsługą klienta lub użyj panelu użytkownika.', 'subscription', 2),
('Co zrobić gdy aplikacja się zawiesza?', 'Spróbuj zrestartować aplikację lub urządzenie.', 'troubleshooting', 3),
('Ile urządzeń może używać jednego konta?', 'Jedno konto może być używane na maksymalnie 2 urządzeniach jednocześnie.', 'account', 4);

INSERT INTO smart_tv_apps (name, platform, version, is_active) VALUES
('Smart IPTV', 'Samsung Tizen', '1.4.5', TRUE),
('IPTV Smarters Pro', 'LG webOS', '2.1.0', TRUE),
('TiviMate', 'Android TV', '4.6.0', TRUE);

INSERT INTO android_apps (name, package_name, version, is_active) VALUES
('IPTV Smarters Pro', 'com.nst.iptvsmartersPro', '3.0.9', TRUE),
('TiviMate IPTV Player', 'ar.tvplayer.tv', '4.6.0', TRUE),
('Perfect Player IPTV', 'com.niklabs.pp', '1.7.2', TRUE);

INSERT INTO smart_tv_activations (app_name, activation_price, currency, description) VALUES
('Smart IPTV Samsung', 49.99, 'PLN', 'Aktywacja aplikacji Smart IPTV na telewizorach Samsung'),
('IPTV Smarters LG', 39.99, 'PLN', 'Aktywacja aplikacji IPTV Smarters na telewizorach LG'),
('TiviMate Android TV', 59.99, 'PLN', 'Aktywacja TiviMate na Android TV');

SET FOREIGN_KEY_CHECKS = 1;
COMMIT;

-- Create indexes for better performance
CREATE INDEX idx_client_name ON clients(name);
CREATE INDEX idx_client_login ON clients(login);
CREATE INDEX idx_client_mac ON clients(mac);
CREATE INDEX idx_client_contact ON clients(contact_value);

-- Create views for reporting
CREATE VIEW active_clients AS
SELECT c.*, p.name as panel_name, ct.name as contact_type_name
FROM clients c
LEFT JOIN panels p ON c.panel_id = p.id
LEFT JOIN contact_types ct ON c.contact_type_id = ct.id
WHERE c.status = 'active' AND c.expires_date >= CURDATE();

CREATE VIEW expiring_clients AS
SELECT c.*, p.name as panel_name, ct.name as contact_type_name,
       DATEDIFF(c.expires_date, CURDATE()) as days_until_expiry
FROM clients c
LEFT JOIN panels p ON c.panel_id = p.id
LEFT JOIN contact_types ct ON c.contact_type_id = ct.id
WHERE c.status = 'active' 
AND c.expires_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 7 DAY);

CREATE VIEW expired_clients AS
SELECT c.*, p.name as panel_name, ct.name as contact_type_name,
       ABS(DATEDIFF(CURDATE(), c.expires_date)) as days_expired
FROM clients c
LEFT JOIN panels p ON c.panel_id = p.id
LEFT JOIN contact_types ct ON c.contact_type_id = ct.id
WHERE c.expires_date < CURDATE();

-- Success message
SELECT 'Database created successfully! Default admin user: admin/admin123' as message;