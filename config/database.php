<?php
// Konfiguracja bazy danych
$host = 'localhost';
$dbname = 'tv_panel';
$username = 'root';
$password = '';

// Można także użyć zmiennych środowiskowych
if (getenv('DB_HOST')) {
    $host = getenv('DB_HOST');
}
if (getenv('DB_NAME')) {
    $dbname = getenv('DB_NAME');
}
if (getenv('DB_USER')) {
    $username = getenv('DB_USER');
}
if (getenv('DB_PASS')) {
    $password = getenv('DB_PASS');
}

try {
    $pdo = new PDO(
        "mysql:host=$host;dbname=$dbname;charset=utf8mb4",
        $username,
        $password,
        [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
            PDO::ATTR_EMULATE_PREPARES => false,
        ]
    );
} catch (PDOException $e) {
    // W przypadku błędu połączenia z MySQL, spróbuj SQLite jako fallback
    try {
        $pdo = new PDO(
            'sqlite:../tv_panel.db',
            null,
            null,
            [
                PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
                PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
            ]
        );
    } catch (PDOException $e2) {
        die("Błąd połączenia z bazą danych: " . $e2->getMessage());
    }
}

// Funkcja do inicjalizacji bazy danych
function initializeDatabase($pdo) {
    try {
        // Sprawdź czy tabela admin_users istnieje
        $stmt = $pdo->query("SELECT COUNT(*) FROM admin_users");
        $count = $stmt->fetchColumn();
        
        // Jeśli nie ma użytkowników, utwórz domyślnego admina
        if ($count == 0) {
            $hashedPassword = password_hash('admin123', PASSWORD_DEFAULT);
            $stmt = $pdo->prepare("INSERT INTO admin_users (username, password) VALUES (?, ?)");
            $stmt->execute(['admin', $hashedPassword]);
        }
    } catch (PDOException $e) {
        // Tabela nie istnieje - trzeba utworzyć strukturę bazy danych
        createDatabaseStructure($pdo);
    }
}

function createDatabaseStructure($pdo) {
    // Struktura bazy danych z database_mysql.sql
    $sql = "
    CREATE TABLE IF NOT EXISTS admin_users (
        id INT PRIMARY KEY AUTO_INCREMENT,
        username VARCHAR(50) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS clients (
        id INT PRIMARY KEY AUTO_INCREMENT,
        username VARCHAR(100) NOT NULL,
        password VARCHAR(100) NOT NULL,
        is_trial BOOLEAN DEFAULT FALSE,
        exp_date DATE,
        max_connections INT DEFAULT 1,
        created_by VARCHAR(50),
        bouquet VARCHAR(100),
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS panels (
        id INT PRIMARY KEY AUTO_INCREMENT,
        name VARCHAR(100) NOT NULL,
        url VARCHAR(255) NOT NULL,
        username VARCHAR(100),
        password VARCHAR(100),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS apps (
        id INT PRIMARY KEY AUTO_INCREMENT,
        name VARCHAR(100) NOT NULL,
        package_name VARCHAR(200),
        app_code VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS contact_types (
        id INT PRIMARY KEY AUTO_INCREMENT,
        name VARCHAR(100) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS payment_methods (
        id INT PRIMARY KEY AUTO_INCREMENT,
        name VARCHAR(100) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS pricing_config (
        id INT PRIMARY KEY AUTO_INCREMENT,
        name VARCHAR(100) NOT NULL,
        price DECIMAL(10,2),
        currency VARCHAR(10) DEFAULT 'PLN',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS questions (
        id INT PRIMARY KEY AUTO_INCREMENT,
        question TEXT NOT NULL,
        answer TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS smart_tv_activations (
        id INT PRIMARY KEY AUTO_INCREMENT,
        activation_id VARCHAR(50) UNIQUE NOT NULL,
        app_name VARCHAR(100),
        app_price DECIMAL(10,2),
        currency VARCHAR(10) DEFAULT 'PLN',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS settings (
        id INT PRIMARY KEY AUTO_INCREMENT,
        setting_key VARCHAR(100) UNIQUE NOT NULL,
        setting_value TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    );
    ";

    $pdo->exec($sql);

    // Dodaj domyślnego użytkownika admin
    $hashedPassword = password_hash('admin123', PASSWORD_DEFAULT);
    $stmt = $pdo->prepare("INSERT INTO admin_users (username, password) VALUES (?, ?)");
    $stmt->execute(['admin', $hashedPassword]);

    // Dodaj podstawowe ustawienia
    $settings = [
        ['panel_name', 'TV Panel - SQL Edition'],
        ['admin_email', 'admin@example.com'],
        ['timezone', 'Europe/Warsaw']
    ];

    $stmt = $pdo->prepare("INSERT INTO settings (setting_key, setting_value) VALUES (?, ?)");
    foreach ($settings as $setting) {
        $stmt->execute($setting);
    }
}

// Inicjalizuj bazę danych
initializeDatabase($pdo);
?>