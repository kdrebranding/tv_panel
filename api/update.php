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
$field = $_POST['field'] ?? '';
$value = $_POST['value'] ?? '';

// Walidacja danych wejściowych
if (empty($table) || empty($id) || empty($field)) {
    echo json_encode(['success' => false, 'error' => 'Brakujące dane']);
    exit();
}

// Dozwolone tabele i pola
$allowedTables = [
    'clients' => ['username', 'password', 'is_trial', 'exp_date', 'max_connections', 'created_by', 'bouquet', 'notes'],
    'panels' => ['name', 'url', 'username', 'password'],
    'apps' => ['name', 'package_name', 'app_code'],
    'contact_types' => ['name'],
    'payment_methods' => ['name'],
    'pricing_config' => ['name', 'price', 'currency'],
    'questions' => ['question', 'answer'],
    'smart_tv_activations' => ['activation_id', 'app_name', 'app_price', 'currency'],
    'settings' => ['setting_value']
];

// Sprawdź czy tabela i pole są dozwolone
if (!isset($allowedTables[$table]) || !in_array($field, $allowedTables[$table])) {
    echo json_encode(['success' => false, 'error' => 'Nieprawidłowa tabela lub pole']);
    exit();
}

try {
    // Specjalna obsługa tabeli settings
    if ($table === 'settings') {
        $stmt = $pdo->prepare("UPDATE settings SET setting_value = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?");
        $result = $stmt->execute([$value, $id]);
    } else {
        // Przygotuj zapytanie SQL
        $sql = "UPDATE `$table` SET `$field` = ?";
        $params = [$value];
        
        // Dodaj updated_at jeśli tabela ma takie pole
        if (in_array($table, ['clients', 'pricing_config', 'settings'])) {
            $sql .= ", updated_at = CURRENT_TIMESTAMP";
        }
        
        $sql .= " WHERE id = ?";
        $params[] = $id;
        
        $stmt = $pdo->prepare($sql);
        $result = $stmt->execute($params);
    }
    
    if ($result) {
        // Loguj aktywność
        logActivity("UPDATE_$table", "Updated $field for ID $id");
        
        echo json_encode(['success' => true]);
    } else {
        echo json_encode(['success' => false, 'error' => 'Błąd zapisu do bazy danych']);
    }
    
} catch (PDOException $e) {
    error_log("Database update error: " . $e->getMessage());
    echo json_encode(['success' => false, 'error' => 'Błąd bazy danych']);
} catch (Exception $e) {
    error_log("Update error: " . $e->getMessage());
    echo json_encode(['success' => false, 'error' => 'Błąd serwera']);
}
?>