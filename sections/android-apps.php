<?php
session_start();
require_once '../config/database.php';
require_once '../includes/functions.php';

// Sprawdź czy użytkownik jest zalogowany
requireLogin();

try {
    $stmt = $pdo->query("SELECT * FROM apps ORDER BY created_at DESC");
    $apps = $stmt->fetchAll();
} catch (PDOException $e) {
    $apps = [];
    error_log("Error fetching android apps: " . $e->getMessage());
}
?>

<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
    <h1 class="h2">
        <i class="fas fa-mobile-alt me-2"></i>Aplikacje Android
    </h1>
    <div class="btn-toolbar mb-2 mb-md-0">
        <button type="button" class="btn btn-success" onclick="$('#addAppModal').modal('show')">
            <i class="fas fa-plus"></i> Dodaj Aplikację
        </button>
    </div>
</div>

<!-- Add App Modal -->
<div class="modal fade" id="addAppModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Dodaj Nową Aplikację Android</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <form id="addAppForm">
                    <div class="mb-3">
                        <label for="app_name" class="form-label">Nazwa Aplikacji *</label>
                        <input type="text" id="app_name" name="name" class="form-control" required placeholder="np. IPTV Smarters Pro">
                    </div>
                    
                    <div class="mb-3">
                        <label for="package_name" class="form-label">Package Name</label>
                        <input type="text" id="package_name" name="package_name" class="form-control" placeholder="np. com.nst.iptvsmartersPro">
                        <div class="form-text">Opcjonalne - nazwa pakietu aplikacji Android</div>
                    </div>
                    
                    <div class="mb-3">
                        <label for="app_code" class="form-label">App Code</label>
                        <div class="input-group">
                            <input type="text" id="app_code" name="app_code" class="form-control" placeholder="Kod aplikacji dla bota">
                            <button type="button" id="generateAppCode" class="btn btn-outline-info">
                                <i class="fas fa-random"></i> Generuj
                            </button>
                        </div>
                        <div class="form-text">Kod używany przez Telegram Bot do identyfikacji aplikacji</div>
                    </div>
                </form>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Anuluj</button>
                <button type="button" id="saveApp" class="btn btn-success">
                    <i class="fas fa-save"></i> Zapisz
                </button>
            </div>
        </div>
    </div>
</div>

<!-- Apps Table -->
<div class="card">
    <div class="card-body">
        <?php if (empty($apps)): ?>
            <div class="text-center py-5">
                <i class="fas fa-mobile-alt fa-3x text-muted mb-3"></i>
                <h5>Brak aplikacji Android</h5>
                <p class="text-muted">Dodaj pierwszą aplikację Android do systemu.</p>
                <button class="btn btn-primary" onclick="$('#addAppModal').modal('show')">
                    <i class="fas fa-plus"></i> Dodaj Aplikację
                </button>
            </div>
        <?php else: ?>
            <div class="table-responsive">
                <table class="table table-dark table-hover">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Nazwa Aplikacji</th>
                            <th>Package Name</th>
                            <th>App Code</th>
                            <th>Data utworzenia</th>
                            <th>Akcje</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($apps as $app): ?>
                        <tr data-id="<?php echo $app['id']; ?>">
                            <td><?php echo $app['id']; ?></td>
                            <td class="editable-cell" data-field="name">
                                <i class="fab fa-android text-success me-2"></i>
                                <?php echo htmlspecialchars($app['name']); ?>
                            </td>
                            <td class="editable-cell" data-field="package_name">
                                <?php if ($app['package_name']): ?>
                                    <code><?php echo htmlspecialchars($app['package_name']); ?></code>
                                <?php else: ?>
                                    <span class="text-muted">Brak</span>
                                <?php endif; ?>
                            </td>
                            <td class="editable-cell" data-field="app_code">
                                <?php if ($app['app_code']): ?>
                                    <span class="badge bg-info">
                                        <?php echo htmlspecialchars($app['app_code']); ?>
                                    </span>
                                <?php else: ?>
                                    <span class="text-muted">Brak</span>
                                <?php endif; ?>
                            </td>
                            <td><?php echo formatDate($app['created_at'], 'd.m.Y H:i'); ?></td>
                            <td>
                                <div class="btn-group btn-group-sm">
                                    <?php if ($app['package_name']): ?>
                                    <button class="btn btn-outline-info" onclick="copyText('<?php echo htmlspecialchars($app['package_name']); ?>')" title="Kopiuj Package Name">
                                        <i class="fas fa-copy"></i>
                                    </button>
                                    <?php endif; ?>
                                    <?php if ($app['app_code']): ?>
                                    <button class="btn btn-outline-success" onclick="copyText('<?php echo htmlspecialchars($app['app_code']); ?>')" title="Kopiuj App Code">
                                        <i class="fas fa-code"></i>
                                    </button>
                                    <?php endif; ?>
                                    <button class="btn btn-outline-danger btn-delete" 
                                            data-id="<?php echo $app['id']; ?>" 
                                            data-table="apps"
                                            data-name="<?php echo htmlspecialchars($app['name']); ?>"
                                            title="Usuń aplikację">
                                        <i class="fas fa-trash"></i>
                                    </button>
                                </div>
                            </td>
                        </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            </div>
            
            <!-- Bot Integration Info -->
            <div class="card bg-info bg-opacity-25 border-info mt-3">
                <div class="card-body">
                    <h6 class="card-title">
                        <i class="fab fa-telegram text-info me-2"></i>Integracja z Telegram Bot
                    </h6>
                    <p class="card-text mb-0">
                        App Code jest używany przez Telegram Bot do identyfikacji aplikacji. 
                        Upewnij się, że każda aplikacja ma unikalny kod dla prawidłowego działania bota.
                    </p>
                </div>
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
    // Generator App Code
    $('#generateAppCode').on('click', function() {
        const appCode = 'APP-' + Math.random().toString(36).substr(2, 6).toUpperCase();
        $('#app_code').val(appCode);
    });
    
    // Auto-generuj package name na podstawie nazwy aplikacji
    $('#app_name').on('input', function() {
        const appName = $(this).val();
        const packageSuggestion = appName
            .toLowerCase()
            .replace(/[^a-z0-9\s]/g, '')
            .replace(/\s+/g, '.')
            .replace(/^\.+|\.+$/g, '');
            
        if (packageSuggestion && !$('#package_name').val()) {
            $('#package_name').attr('placeholder', 'np. com.app.' + packageSuggestion);
        }
    });
    
    // Zapisz nową aplikację
    $('#saveApp').on('click', function() {
        const form = $('#addAppForm')[0];
        
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }
        
        const formData = $('#addAppForm').serialize();
        const btn = $(this);
        const originalHtml = btn.html();
        
        btn.prop('disabled', true).html('<span class="spinner-border spinner-border-sm me-2"></span>Zapisywanie...');
        
        $.post('../api/add-android-app.php', formData)
            .done(function(response) {
                if (response.success) {
                    $('#addAppModal').modal('hide');
                    showAlert('success', 'Aplikacja Android została dodana');
                    setTimeout(() => loadSection('android-apps'), 1500);
                } else {
                    showAlert('danger', response.error || 'Błąd dodawania aplikacji');
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
    $('#addAppModal').on('hidden.bs.modal', function() {
        $('#addAppForm')[0].reset();
        $('#addAppModal .was-validated').removeClass('was-validated');
    });
});

// Funkcja kopiowania tekstu
function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(function() {
            showAlert('success', 'Skopiowane do schowka');
        }).catch(function() {
            fallbackCopyText(text);
        });
    } else {
        fallbackCopyText(text);
    }
}

function fallbackCopyText(text) {
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
        showAlert('success', 'Skopiowane do schowka');
    } catch (err) {
        showAlert('warning', 'Nie można skopiować. Tekst: ' + text);
    }
    
    document.body.removeChild(textArea);
}
</script>