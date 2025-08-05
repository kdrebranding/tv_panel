<?php
session_start();
require_once '../config/database.php';
require_once '../includes/functions.php';

// Sprawdź czy użytkownik jest zalogowany
requireLogin();

try {
    $stmt = $pdo->query("SELECT * FROM smart_tv_activations ORDER BY created_at DESC");
    $activations = $stmt->fetchAll();
} catch (PDOException $e) {
    $activations = [];
    error_log("Error fetching smart TV activations: " . $e->getMessage());
}
?>

<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
    <h1 class="h2">
        <i class="fas fa-tv me-2"></i>Smart TV Activation
    </h1>
    <div class="btn-toolbar mb-2 mb-md-0">
        <button type="button" class="btn btn-success" onclick="$('#addActivationModal').modal('show')">
            <i class="fas fa-plus"></i> Dodaj Aktywację
        </button>
    </div>
</div>

<!-- Add Activation Modal -->
<div class="modal fade" id="addActivationModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Dodaj Nową Aktywację Smart TV</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <form id="addActivationForm">
                    <div class="mb-3">
                        <label for="activation_id" class="form-label">ID Aktywacji *</label>
                        <div class="input-group">
                            <input type="text" id="activation_id" name="activation_id" class="form-control" required readonly>
                            <button type="button" id="generateActivationId" class="btn btn-outline-info">
                                <i class="fas fa-random"></i> Generuj
                            </button>
                        </div>
                    </div>
                    
                    <div class="mb-3">
                        <label for="app_name" class="form-label">Nazwa Aplikacji *</label>
                        <input type="text" id="app_name" name="app_name" class="form-control" required placeholder="np. IPTV Pro">
                    </div>
                    
                    <div class="row">
                        <div class="col-md-8 mb-3">
                            <label for="app_price" class="form-label">Cena Aplikacji</label>
                            <input type="number" id="app_price" name="app_price" class="form-control" step="0.01" min="0" placeholder="0.00">
                        </div>
                        
                        <div class="col-md-4 mb-3">
                            <label for="currency" class="form-label">Waluta</label>
                            <select id="currency" name="currency" class="form-select">
                                <option value="PLN" selected>PLN</option>
                                <option value="EUR">EUR</option>
                                <option value="USD">USD</option>
                                <option value="GBP">GBP</option>
                            </select>
                        </div>
                    </div>
                </form>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Anuluj</button>
                <button type="button" id="saveActivation" class="btn btn-success">
                    <i class="fas fa-save"></i> Zapisz
                </button>
            </div>
        </div>
    </div>
</div>

<!-- Activations Table -->
<div class="card">
    <div class="card-body">
        <?php if (empty($activations)): ?>
            <div class="text-center py-5">
                <i class="fas fa-tv fa-3x text-muted mb-3"></i>
                <h5>Brak aktywacji Smart TV</h5>
                <p class="text-muted">Dodaj pierwszą aktywację Smart TV.</p>
                <button class="btn btn-primary" onclick="$('#addActivationModal').modal('show')">
                    <i class="fas fa-plus"></i> Dodaj Aktywację
                </button>
            </div>
        <?php else: ?>
            <div class="table-responsive">
                <table class="table table-dark table-hover">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>ID Aktywacji</th>
                            <th>Nazwa Aplikacji</th>
                            <th>Cena</th>
                            <th>Waluta</th>
                            <th>Data utworzenia</th>
                            <th>Akcje</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($activations as $activation): ?>
                        <tr data-id="<?php echo $activation['id']; ?>">
                            <td><?php echo $activation['id']; ?></td>
                            <td class="editable-cell" data-field="activation_id">
                                <code><?php echo htmlspecialchars($activation['activation_id']); ?></code>
                            </td>
                            <td class="editable-cell" data-field="app_name">
                                <?php echo htmlspecialchars($activation['app_name']); ?>
                            </td>
                            <td class="editable-cell" data-field="app_price">
                                <?php echo number_format($activation['app_price'], 2); ?>
                            </td>
                            <td class="editable-cell" data-field="currency">
                                <?php echo htmlspecialchars($activation['currency']); ?>
                            </td>
                            <td><?php echo formatDate($activation['created_at'], 'd.m.Y H:i'); ?></td>
                            <td>
                                <div class="btn-group btn-group-sm">
                                    <button class="btn btn-outline-info" onclick="copyActivationId('<?php echo $activation['activation_id']; ?>')" title="Kopiuj ID">
                                        <i class="fas fa-copy"></i>
                                    </button>
                                    <button class="btn btn-outline-danger btn-delete" 
                                            data-id="<?php echo $activation['id']; ?>" 
                                            data-table="smart_tv_activations"
                                            data-name="<?php echo htmlspecialchars($activation['activation_id']); ?>"
                                            title="Usuń aktywację">
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
$(document).ready(function() {
    // Generuj ID aktywacji przy otwarciu modala
    $('#addActivationModal').on('show.bs.modal', function() {
        generateNewActivationId();
    });
    
    // Generator ID aktywacji
    $('#generateActivationId').on('click', generateNewActivationId);
    
    function generateNewActivationId() {
        const activationId = 'STV-' + Math.random().toString(36).substr(2, 8).toUpperCase();
        $('#activation_id').val(activationId);
    }
    
    // Zapisz nową aktywację
    $('#saveActivation').on('click', function() {
        const form = $('#addActivationForm')[0];
        
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }
        
        const formData = $('#addActivationForm').serialize();
        const btn = $(this);
        const originalHtml = btn.html();
        
        btn.prop('disabled', true).html('<span class="spinner-border spinner-border-sm me-2"></span>Zapisywanie...');
        
        $.post('../api/add-smart-tv-activation.php', formData)
            .done(function(response) {
                if (response.success) {
                    $('#addActivationModal').modal('hide');
                    showAlert('success', 'Aktywacja Smart TV została dodana');
                    setTimeout(() => loadSection('smart-tv-activation'), 1500);
                } else {
                    showAlert('danger', response.error || 'Błąd dodawania aktywacji');
                }
            })
            .fail(function() {
                showAlert('danger', 'Błąd połączenia z serwerem');
            })
            .always(function() {
                btn.prop('disabled', false).html(originalHtml);
            });
    });
    
    // Reset formularza po zamknięciu modala
    $('#addActivationModal').on('hidden.bs.modal', function() {
        $('#addActivationForm')[0].reset();
        $('#addActivationModal .was-validated').removeClass('was-validated');
    });
});

// Kopiuj ID aktywacji do schowka
function copyActivationId(activationId) {
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(activationId).then(function() {
            showAlert('success', 'ID aktywacji skopiowane do schowka');
        }).catch(function() {
            fallbackCopy(activationId);
        });
    } else {
        fallbackCopy(activationId);
    }
}

function fallbackCopy(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
        showAlert('success', 'ID aktywacji skopiowane do schowka');
    } catch (err) {
        showAlert('warning', 'Nie można skopiować ID. Skopiuj ręcznie: ' + text);
    }
    
    document.body.removeChild(textArea);
}
</script>