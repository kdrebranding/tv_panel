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

$table = $_POST['table'] ?? '';
$id = $_POST['id'] ?? '';

// Walidacja danych wejściowych
if (empty($table) || empty($id)) {
    echo json_encode(['success' => false, 'error' => 'Brakujące dane']);
    exit();
}

// Dozwolone tabele
$allowedTables = [
    'clients',
    'panels', 
    'apps',
    'contact_types',
    'payment_methods',
    'pricing_config',
    'questions',
    'smart_tv_activations'
];

// Sprawdź czy tabela jest dozwolona
if (!in_array($table, $allowedTables)) {
    echo json_encode(['success' => false, 'error' => 'Nieprawidłowa tabela']);
    exit();
}

try {
    // Sprawdź czy rekord istnieje
    $stmt = $pdo->prepare("SELECT COUNT(*) FROM `$table` WHERE id = ?");
    $stmt->execute([$id]);
    
    if ($stmt->fetchColumn() == 0) {
        echo json_encode(['success' => false, 'error' => 'Rekord nie istnieje']);
        exit();
    }
    
    // Usuń rekord
    $stmt = $pdo->prepare("DELETE FROM `$table` WHERE id = ?");
    $result = $stmt->execute([$id]);
    
    if ($result) {
        // Loguj aktywność
        logActivity("DELETE_$table", "Deleted record ID $id");
        
        echo json_encode(['success' => true]);
    } else {
        echo json_encode(['success' => false, 'error' => 'Błąd usuwania z bazy danych']);
    }
    
} catch (PDOException $e) {
    error_log("Database delete error: " . $e->getMessage());
    echo json_encode(['success' => false, 'error' => 'Błąd bazy danych']);
} catch (Exception $e) {
    error_log("Delete error: " . $e->getMessage());
    echo json_encode(['success' => false, 'error' => 'Błąd serwera']);
}
?>