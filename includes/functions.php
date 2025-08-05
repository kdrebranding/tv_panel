<?php
// Funkcje pomocnicze dla aplikacji TV Panel

/**
 * Pobierz statystyki dla dashboard
 */
function getDashboardStats() {
    global $pdo;
    
    $stats = [
        'total_clients' => 0,
        'active_clients' => 0,
        'expiring_soon' => 0,
        'expired_clients' => 0
    ];
    
    try {
        // Całkowita liczba klientów
        $stmt = $pdo->query("SELECT COUNT(*) FROM clients");
        $stats['total_clients'] = $stmt->fetchColumn();
        
        // Aktywni klienci (data wygaśnięcia w przyszłości)
        $stmt = $pdo->query("SELECT COUNT(*) FROM clients WHERE exp_date >= CURDATE()");
        $stats['active_clients'] = $stmt->fetchColumn();
        
        // Wygasający wkrótce (w ciągu 7 dni)
        $stmt = $pdo->query("SELECT COUNT(*) FROM clients WHERE exp_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 7 DAY)");
        $stats['expiring_soon'] = $stmt->fetchColumn();
        
        // Wygasłe konta
        $stmt = $pdo->query("SELECT COUNT(*) FROM clients WHERE exp_date < CURDATE()");
        $stats['expired_clients'] = $stmt->fetchColumn();
        
    } catch (PDOException $e) {
        error_log("Błąd pobierania statystyk: " . $e->getMessage());
    }
    
    return $stats;
}

/**
 * Generuj losowe hasło
 */
function generatePassword($length = 8) {
    $characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    $password = '';
    for ($i = 0; $i < $length; $i++) {
        $password .= $characters[random_int(0, strlen($characters) - 1)];
    }
    return $password;
}

/**
 * Oblicz dni do wygaśnięcia
 */
function getDaysToExpiry($expDate) {
    if (empty($expDate)) {
        return null;
    }
    
    $today = new DateTime();
    $expiry = new DateTime($expDate);
    $diff = $today->diff($expiry);
    
    if ($expiry < $today) {
        return -$diff->days; // Ujemna wartość dla wygasłych
    }
    
    return $diff->days;
}

/**
 * Formatuj datę dla wyświetlenia
 */
function formatDate($date, $format = 'd.m.Y') {
    if (empty($date)) {
        return '-';
    }
    
    try {
        $dateObj = new DateTime($date);
        return $dateObj->format($format);
    } catch (Exception $e) {
        return $date;
    }
}

/**
 * Sprawdź czy użytkownik jest zalogowany
 */
function requireLogin() {
    if (!isset($_SESSION['logged_in']) || $_SESSION['logged_in'] !== true) {
        header('Location: login.php');
        exit();
    }
}

/**
 * Pobierz ustawienie z bazy danych
 */
function getSetting($key, $default = '') {
    global $pdo;
    
    try {
        $stmt = $pdo->prepare("SELECT setting_value FROM settings WHERE setting_key = ?");
        $stmt->execute([$key]);
        $value = $stmt->fetchColumn();
        
        return $value !== false ? $value : $default;
    } catch (PDOException $e) {
        return $default;
    }
}

/**
 * Zapisz ustawienie w bazie danych
 */
function setSetting($key, $value) {
    global $pdo;
    
    try {
        $stmt = $pdo->prepare("
            INSERT INTO settings (setting_key, setting_value) 
            VALUES (?, ?) 
            ON DUPLICATE KEY UPDATE 
            setting_value = VALUES(setting_value),
            updated_at = CURRENT_TIMESTAMP
        ");
        return $stmt->execute([$key, $value]);
    } catch (PDOException $e) {
        error_log("Błąd zapisywania ustawienia: " . $e->getMessage());
        return false;
    }
}

/**
 * Sanityzuj dane wejściowe
 */
function sanitizeInput($input) {
    return htmlspecialchars(trim($input), ENT_QUOTES, 'UTF-8');
}

/**
 * Waliduj email
 */
function isValidEmail($email) {
    return filter_var($email, FILTER_VALIDATE_EMAIL) !== false;
}

/**
 * Formatuj status klienta na podstawie daty wygaśnięcia
 */
function getClientStatus($expDate) {
    $daysToExpiry = getDaysToExpiry($expDate);
    
    if ($daysToExpiry === null) {
        return ['status' => 'unknown', 'class' => 'secondary', 'text' => 'Nieznany'];
    }
    
    if ($daysToExpiry < 0) {
        return ['status' => 'expired', 'class' => 'danger', 'text' => 'Wygasł'];
    }
    
    if ($daysToExpiry <= 7) {
        return ['status' => 'expiring', 'class' => 'warning', 'text' => 'Wygasa wkrótce'];
    }
    
    return ['status' => 'active', 'class' => 'success', 'text' => 'Aktywny'];
}

/**
 * Loguj aktywność użytkownika
 */
function logActivity($action, $details = '') {
    global $pdo;
    
    if (!isset($_SESSION['user_id'])) {
        return false;
    }
    
    try {
        $stmt = $pdo->prepare("
            INSERT INTO activity_log (user_id, action, details, created_at) 
            VALUES (?, ?, ?, NOW())
        ");
        return $stmt->execute([$_SESSION['user_id'], $action, $details]);
    } catch (PDOException $e) {
        // Ignoruj błędy logowania aktywności
        return false;
    }
}
?>