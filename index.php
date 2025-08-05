<?php
session_start();

// Sprawdź czy użytkownik jest zalogowany
if (!isset($_SESSION['logged_in']) || $_SESSION['logged_in'] !== true) {
    header('Location: login.php');
    exit();
}

require_once 'config/database.php';
require_once 'includes/functions.php';

// Pobierz statystyki dla dashboard
$stats = getDashboardStats();
?>
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TV Panel - Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="assets/css/style.css" rel="stylesheet">
</head>
<body class="bg-dark text-light">
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container-fluid">
            <a class="navbar-brand" href="index.php">
                <i class="fas fa-tv me-2"></i>TV Panel - SQL Edition
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="logout.php">
                    <i class="fas fa-sign-out-alt"></i> Wyloguj
                </a>
            </div>
        </div>
    </nav>

    <div class="container-fluid">
        <div class="row">
            <!-- Sidebar -->
            <nav class="col-md-3 col-lg-2 d-md-block bg-dark sidebar">
                <div class="position-sticky pt-3">
                    <ul class="nav flex-column">
                        <li class="nav-item">
                            <a class="nav-link active" href="index.php">
                                <i class="fas fa-home"></i> Dashboard
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#" onclick="loadSection('clients')">
                                <i class="fas fa-users"></i> Klienci
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#" onclick="loadSection('add-client')">
                                <i class="fas fa-user-plus"></i> Dodaj Klienta
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#" onclick="loadSection('panels')">
                                <i class="fas fa-tv"></i> Panele
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#" onclick="loadSection('android-apps')">
                                <i class="fas fa-mobile-alt"></i> Aplikacje Android
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#" onclick="loadSection('smart-tv-activation')">
                                <i class="fas fa-tv"></i> Smart TV Activation
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#" onclick="loadSection('contact-types')">
                                <i class="fas fa-address-book"></i> Typy Kontaktów
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#" onclick="loadSection('payment-methods')">
                                <i class="fas fa-credit-card"></i> Metody Płatności
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#" onclick="loadSection('pricing-config')">
                                <i class="fas fa-dollar-sign"></i> Konfiguracja Cen
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#" onclick="loadSection('faq')">
                                <i class="fas fa-question-circle"></i> FAQ
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#" onclick="loadSection('settings')">
                                <i class="fas fa-cog"></i> Ustawienia
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#" onclick="loadSection('telegram-bot')">
                                <i class="fab fa-telegram"></i> Bot Telegram
                            </a>
                        </li>
                    </ul>
                </div>
            </nav>

            <!-- Main content -->
            <main class="col-md-9 ms-sm-auto col-lg-10 px-md-4">
                <div id="main-content">
                    <!-- Dashboard -->
                    <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
                        <h1 class="h2">Dashboard</h1>
                    </div>

                    <!-- Stats Cards -->
                    <div class="row mb-4">
                        <div class="col-xl-3 col-md-6 mb-4">
                            <div class="card stat-card bg-primary text-white h-100" onclick="loadSection('clients', 'all')">
                                <div class="card-body">
                                    <div class="row no-gutters align-items-center">
                                        <div class="col mr-2">
                                            <div class="text-xs font-weight-bold text-uppercase mb-1">
                                                Wszyscy Klienci
                                            </div>
                                            <div class="h5 mb-0 font-weight-bold">
                                                <?php echo $stats['total_clients']; ?>
                                            </div>
                                        </div>
                                        <div class="col-auto">
                                            <i class="fas fa-users fa-2x text-gray-300"></i>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="col-xl-3 col-md-6 mb-4">
                            <div class="card stat-card bg-success text-white h-100" onclick="loadSection('clients', 'active')">
                                <div class="card-body">
                                    <div class="row no-gutters align-items-center">
                                        <div class="col mr-2">
                                            <div class="text-xs font-weight-bold text-uppercase mb-1">
                                                Aktywni
                                            </div>
                                            <div class="h5 mb-0 font-weight-bold">
                                                <?php echo $stats['active_clients']; ?>
                                            </div>
                                        </div>
                                        <div class="col-auto">
                                            <i class="fas fa-user-check fa-2x text-gray-300"></i>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="col-xl-3 col-md-6 mb-4">
                            <div class="card stat-card bg-warning text-white h-100" onclick="loadSection('clients', 'expiring')">
                                <div class="card-body">
                                    <div class="row no-gutters align-items-center">
                                        <div class="col mr-2">
                                            <div class="text-xs font-weight-bold text-uppercase mb-1">
                                                Wygasają Wkrótce
                                            </div>
                                            <div class="h5 mb-0 font-weight-bold">
                                                <?php echo $stats['expiring_soon']; ?>
                                            </div>
                                        </div>
                                        <div class="col-auto">
                                            <i class="fas fa-clock fa-2x text-gray-300"></i>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="col-xl-3 col-md-6 mb-4">
                            <div class="card stat-card bg-danger text-white h-100" onclick="loadSection('clients', 'expired')">
                                <div class="card-body">
                                    <div class="row no-gutters align-items-center">
                                        <div class="col mr-2">
                                            <div class="text-xs font-weight-bold text-uppercase mb-1">
                                                Wygasłe
                                            </div>
                                            <div class="h5 mb-0 font-weight-bold">
                                                <?php echo $stats['expired_clients']; ?>
                                            </div>
                                        </div>
                                        <div class="col-auto">
                                            <i class="fas fa-user-times fa-2x text-gray-300"></i>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Recent Activity -->
                    <div class="row">
                        <div class="col-12">
                            <div class="card bg-secondary">
                                <div class="card-header">
                                    <h5 class="mb-0">Ostatnie Aktywności</h5>
                                </div>
                                <div class="card-body">
                                    <p>Panel TV został pomyślnie zmigrowany na SQL!</p>
                                    <p>Wszystkie funkcje są dostępne i gotowe do użycia.</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="assets/js/app.js"></script>
</body>
</html>