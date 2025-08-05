<?php
session_start();
require_once '../config/database.php';
require_once '../includes/functions.php';

header('Content-Type: application/json');

// Sprawdź czy użytkownik jest zalogowany
if (!isset($_SESSION['logged_in']) || $_SESSION['logged_in'] !== true) {
    http_response_code(401);
    echo json_encode(['success' => false, 'error' => 'Brak autoryzacji']);
    exit();
}

// Sprawdź czy to POST request
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'error' => 'Metoda niedozwolona']);
    exit();
}

// Pobierz dane z formularza
$username = trim($_POST['username'] ?? '');
$password = trim($_POST['password'] ?? '');
$is_trial = isset($_POST['is_trial']) ? 1 : 0;
$exp_date = trim($_POST['exp_date'] ?? '');
$max_connections = (int)($_POST['max_connections'] ?? 1);
$bouquet = trim($_POST['bouquet'] ?? '');
$notes = trim($_POST['notes'] ?? '');

// Walidacja danych
$errors = [];

if (empty($username)) {
    $errors[] = 'Nazwa użytkownika jest wymagana';
} elseif (strlen($username) < 3) {
    $errors[] = 'Nazwa użytkownika musi mieć co najmniej 3 znaki';
}

if (empty($password)) {
    $errors[] = 'Hasło jest wymagane';
} elseif (strlen($password) < 4) {
    $errors[] = 'Hasło musi mieć co najmniej 4 znaki';
}

if (empty($exp_date)) {
    $errors[] = 'Data wygaśnięcia jest wymagana';
} else {
    // Sprawdź format daty
    $dateObj = DateTime::createFromFormat('Y-m-d', $exp_date);
    if (!$dateObj || $dateObj->format('Y-m-d') !== $exp_date) {
        $errors[] = 'Nieprawidłowy format daty';
    }
}

if ($max_connections < 1 || $max_connections > 100) {
    $errors[] = 'Maksymalna liczba połączeń musi być między 1 a 100';
}

// Jeśli są błędy walidacji
if (!empty($errors)) {
    echo json_encode(['success' => false, 'error' => implode(', ', $errors)]);
    exit();
}

try {
    // Sprawdź czy nazwa użytkownika już istnieje
    $stmt = $pdo->prepare("SELECT COUNT(*) FROM clients WHERE username = ?");
    $stmt->execute([$username]);
    
    if ($stmt->fetchColumn() > 0) {
        echo json_encode(['success' => false, 'error' => 'Nazwa użytkownika już istnieje']);
        exit();
    }
    
    // Dodaj nowego klienta
    $stmt = $pdo->prepare("
        INSERT INTO clients (username, password, is_trial, exp_date, max_connections, created_by, bouquet, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ");
    
    $result = $stmt->execute([
        $username,
        $password,
        $is_trial,
        $exp_date,
        $max_connections,
        $_SESSION['username'],
        $bouquet,
        $notes
    ]);
    
    if ($result) {
        $clientId = $pdo->lastInsertId();
        
        // Loguj aktywność
        logActivity('ADD_CLIENT', "Added client: $username (ID: $clientId)");
        
        echo json_encode([
            'success' => true,
            'message' => 'Klient został dodany pomyślnie',
            'client_id' => $clientId
        ]);
    } else {
        echo json_encode(['success' => false, 'error' => 'Błąd dodawania klienta do bazy danych']);
    }
    
} catch (PDOException $e) {
    error_log("Add client error: " . $e->getMessage());
    
    // Sprawdź czy to błąd duplikatu klucza
    if ($e->getCode() == 23000) {
        echo json_encode(['success' => false, 'error' => 'Nazwa użytkownika już istnieje']);
    } else {
        echo json_encode(['success' => false, 'error' => 'Błąd bazy danych']);
    }
} catch (Exception $e) {
    error_log("Add client error: " . $e->getMessage());
    echo json_encode(['success' => false, 'error' => 'Błąd serwera']);
}
?>