<?php
session_start();
require_once '../config/database.php';
require_once '../includes/functions.php';

// Sprawdź czy użytkownik jest zalogowany
requireLogin();

// Pobierz filtr jeśli jest
$filter = $_GET['filter'] ?? '';

// Przygotuj zapytanie SQL na podstawie filtra
$whereClause = '';
$params = [];

switch ($filter) {
    case 'active':
        $whereClause = 'WHERE exp_date >= CURDATE()';
        break;
    case 'expiring':
        $whereClause = 'WHERE exp_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 7 DAY)';
        break;
    case 'expired':
        $whereClause = 'WHERE exp_date < CURDATE()';
        break;
}

try {
    $stmt = $pdo->query("SELECT * FROM clients $whereClause ORDER BY created_at DESC");
    $clients = $stmt->fetchAll();
} catch (PDOException $e) {
    $clients = [];
    error_log("Error fetching clients: " . $e->getMessage());
}
?>

<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
    <h1 class="h2">
        <i class="fas fa-users me-2"></i>
        <?php
        switch ($filter) {
            case 'active': echo 'Aktywni Klienci'; break;
            case 'expiring': echo 'Klienci Wygasający Wkrótce'; break;
            case 'expired': echo 'Wygasłe Konta'; break;
            default: echo 'Wszyscy Klienci'; break;
        }
        ?>
    </h1>
    <div class="btn-toolbar mb-2 mb-md-0">
        <div class="btn-group me-2">
            <button type="button" class="btn btn-success" onclick="loadSection('add-client')">
                <i class="fas fa-plus"></i> Dodaj Klienta
            </button>
            <button type="button" class="btn btn-info" onclick="initializeCSVImport()">
                <i class="fas fa-file-import"></i> Import CSV
            </button>
            <button type="button" class="btn btn-secondary" onclick="exportData('clients')">
                <i class="fas fa-download"></i> Eksport
            </button>
        </div>
    </div>
</div>

<!-- Filtry i wyszukiwanie -->
<div class="row mb-3">
    <div class="col-md-6">
        <div class="input-group">
            <span class="input-group-text"><i class="fas fa-search"></i></span>
            <input type="text" id="clientSearch" class="form-control" placeholder="Szukaj klientów...">
        </div>
    </div>
    <div class="col-md-3">
        <select id="statusFilter" class="form-select">
            <option value="">Wszystkie statusy</option>
            <option value="active">Aktywne</option>
            <option value="expiring">Wygasające wkrótce</option>
            <option value="expired">Wygasłe</option>
        </select>
    </div>
    <div class="col-md-3">
        <div class="d-flex justify-content-end">
            <span class="badge bg-primary fs-6">Łącznie: <?php echo count($clients); ?></span>
        </div>
    </div>
</div>

<!-- CSV Import Modal -->
<div class="modal fade" id="csvImportModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Import Klientów z CSV</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <div class="mb-3">
                    <label for="csvFile" class="form-label">Wybierz plik CSV</label>
                    <input type="file" id="csvFile" class="form-control" accept=".csv">
                    <div class="form-text">
                        Format CSV: username,password,exp_date,max_connections,bouquet,notes
                    </div>
                </div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Anuluj</button>
                <button type="button" id="uploadCsv" class="btn btn-primary" disabled>
                    <i class="fas fa-upload"></i> Importuj
                </button>
            </div>
        </div>
    </div>
</div>

<!-- Tabela klientów -->
<div class="card">
    <div class="card-body">
        <?php if (empty($clients)): ?>
            <div class="text-center py-5">
                <i class="fas fa-users fa-3x text-muted mb-3"></i>
                <h5>Brak klientów do wyświetlenia</h5>
                <p class="text-muted">
                    <?php if ($filter): ?>
                        Nie znaleziono klientów spełniających wybrane kryteria.
                    <?php else: ?>
                        Dodaj pierwszego klienta, aby rozpocząć.
                    <?php endif; ?>
                </p>
                <button class="btn btn-primary" onclick="loadSection('add-client')">
                    <i class="fas fa-plus"></i> Dodaj Klienta
                </button>
            </div>
        <?php else: ?>
            <div class="table-responsive">
                <table id="clientsTable" class="table table-dark table-hover">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Nazwa użytkownika</th>
                            <th>Hasło</th>
                            <th>Status</th>
                            <th>Data wygaśnięcia</th>
                            <th>Za ile dni wygasa</th>
                            <th>Maks. połączenia</th>
                            <th>Trial</th>
                            <th>Bouquet</th>
                            <th>Notatki</th>
                            <th>Utworzony przez</th>
                            <th>Akcje</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($clients as $client): 
                            $status = getClientStatus($client['exp_date']);
                            $daysToExpiry = getDaysToExpiry($client['exp_date']);
                        ?>
                        <tr data-id="<?php echo $client['id']; ?>">
                            <td><?php echo $client['id']; ?></td>
                            <td class="editable-cell" data-field="username"><?php echo htmlspecialchars($client['username']); ?></td>
                            <td class="editable-cell" data-field="password"><?php echo htmlspecialchars($client['password']); ?></td>
                            <td>
                                <span class="badge bg-<?php echo $status['class']; ?> client-status status-<?php echo $status['status']; ?>">
                                    <?php echo $status['text']; ?>
                                </span>
                            </td>
                            <td class="editable-cell" data-field="exp_date"><?php echo formatDate($client['exp_date']); ?></td>
                            <td class="days-expiry <?php 
                                if ($daysToExpiry < 0) echo 'expired';
                                elseif ($daysToExpiry <= 7) echo 'expiring-soon';
                                else echo 'active';
                            ?>">
                                <?php 
                                if ($daysToExpiry === null) {
                                    echo '-';
                                } elseif ($daysToExpiry < 0) {
                                    echo 'Wygasł ' . abs($daysToExpiry) . ' dni temu';
                                } elseif ($daysToExpiry == 0) {
                                    echo 'Wygasa dziś';
                                } else {
                                    echo $daysToExpiry . ' dni';
                                }
                                ?>
                            </td>
                            <td class="editable-cell" data-field="max_connections"><?php echo $client['max_connections']; ?></td>
                            <td>
                                <?php if ($client['is_trial']): ?>
                                    <span class="badge bg-info">Trial</span>
                                <?php else: ?>
                                    <span class="badge bg-secondary">Pełna</span>
                                <?php endif; ?>
                            </td>
                            <td class="editable-cell" data-field="bouquet"><?php echo htmlspecialchars($client['bouquet'] ?? '-'); ?></td>
                            <td class="editable-cell" data-field="notes" style="max-width: 200px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                                <?php echo htmlspecialchars($client['notes'] ?? '-'); ?>
                            </td>
                            <td><?php echo htmlspecialchars($client['created_by'] ?? '-'); ?></td>
                            <td>
                                <div class="btn-group btn-group-sm">
                                    <button class="btn btn-outline-danger btn-delete" 
                                            data-id="<?php echo $client['id']; ?>" 
                                            data-table="clients"
                                            data-name="<?php echo htmlspecialchars($client['username']); ?>"
                                            title="Usuń klienta">
                                        <i class="fas fa-trash"></i>
                                    </button>
                                </div>
                            </td>
                        </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            </div>
        <?php endif; ?>
    </div>
</div>

<!-- Delete Modal -->
<div class="modal fade" id="deleteModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Potwierdzenie usunięcia</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <!-- Content filled by JavaScript -->
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Anuluj</button>
                <button type="button" id="confirmDelete" class="btn btn-danger">Usuń</button>
            </div>
        </div>
    </div>
</div>

<script>
// Initialize CSV import when modal is shown
function initializeCSVImport() {
    $('#csvImportModal').modal('show');
    
    // Reset file input
    $('#csvFile').val('').trigger('change');
    
    // Initialize file upload
    $('#csvFile').off('change').on('change', function(e) {
        const file = e.target.files[0];
        if (!file) {
            $('#uploadCsv').prop('disabled', true);
            return;
        }
        
        if (file.type !== 'text/csv' && !file.name.endsWith('.csv')) {
            showAlert('danger', 'Proszę wybrać plik CSV');
            $('#uploadCsv').prop('disabled', true);
            return;
        }
        
        $('#uploadCsv').prop('disabled', false);
    });
    
    $('#uploadCsv').off('click').on('click', function() {
        const fileInput = $('#csvFile')[0];
        if (!fileInput.files.length) {
            showAlert('warning', 'Proszę wybrać plik CSV');
            return;
        }
        
        const formData = new FormData();
        formData.append('csv_file', fileInput.files[0]);
        
        $(this).prop('disabled', true).html('<span class="spinner-border spinner-border-sm me-2"></span>Importowanie...');
        
        $.ajax({
            url: '../api/import-csv.php',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                if (response.success) {
                    $('#csvImportModal').modal('hide');
                    showAlert('success', `Zaimportowano ${response.count} klientów`);
                    setTimeout(() => loadSection('clients'), 2000);
                } else {
                    showAlert('danger', response.error || 'Błąd importu');
                }
            },
            error: function() {
                showAlert('danger', 'Błąd połączenia z serwerem');
            },
            complete: function() {
                $('#uploadCsv').prop('disabled', false).html('<i class="fas fa-upload"></i> Importuj');
            }
        });
    });
}
</script>