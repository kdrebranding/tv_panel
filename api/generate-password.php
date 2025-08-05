<?php
session_start();
require_once '../includes/functions.php';

header('Content-Type: application/json');

// Sprawdź czy użytkownik jest zalogowany
if (!isset($_SESSION['logged_in']) || $_SESSION['logged_in'] !== true) {
    http_response_code(401);
    echo json_encode(['success' => false, 'error' => 'Brak autoryzacji']);
    exit();
}

// Generuj hasło
$length = $_GET['length'] ?? 8;
$length = max(6, min(32, (int)$length)); // Ogranicz długość do 6-32 znaków

$password = generatePassword($length);

echo json_encode([
    'success' => true,
    'password' => $password,
    'length' => $length
]);
?>