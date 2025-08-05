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

try {
    $stats = getDashboardStats();
    
    echo json_encode([
        'success' => true,
        'stats' => [
            'all' => $stats['total_clients'],
            'active' => $stats['active_clients'],
            'expiring' => $stats['expiring_soon'],
            'expired' => $stats['expired_clients']
        ]
    ]);
    
} catch (Exception $e) {
    error_log("Dashboard stats error: " . $e->getMessage());
    echo json_encode(['success' => false, 'error' => 'Błąd pobierania statystyk']);
}
?>