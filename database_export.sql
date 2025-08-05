-- TV Panel SQL Database Export
-- Generated for MySQL/MariaDB deployment

SET FOREIGN_KEY_CHECKS = 0;





















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
  FOREIGN KEY (panel_id) REFERENCES panels(id),
  FOREIGN KEY (app_id) REFERENCES apps(id),
  FOREIGN KEY (contact_type_id) REFERENCES contact_types(id)
);



SET FOREIGN_KEY_CHECKS = 1;

-- Insert default admin user
INSERT INTO admins (username, password_hash) VALUES ('admin', 'b2.hR1JT1I8E1I8E1I8E1I8E1I8E1I8E1u');