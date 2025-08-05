// TV Panel - SQL Edition JavaScript

// Global variables
let currentSection = 'dashboard';
let editingCell = null;

// Initialize application
$(document).ready(function() {
    console.log('TV Panel initialized');
    
    // Set up AJAX defaults
    $.ajaxSetup({
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        },
        error: function(xhr, status, error) {
            console.error('AJAX Error:', error);
            showAlert('danger', 'Błąd połączenia z serwerem');
        }
    });
});

// Load section dynamically
function loadSection(section, filter = '') {
    currentSection = section;
    
    // Update active nav item
    $('.nav-link').removeClass('active');
    $(`.nav-link[onclick*="${section}"]`).addClass('active');
    
    // Show loading
    $('#main-content').html('<div class="text-center py-5"><div class="spinner-border" role="status"></div></div>');
    
    // Load section content
    $.get('sections/' + section + '.php', { filter: filter })
        .done(function(data) {
            $('#main-content').html(data);
            initializeSectionFeatures(section);
        })
        .fail(function() {
            $('#main-content').html('<div class="alert alert-danger">Błąd ładowania sekcji</div>');
        });
}

// Initialize section-specific features
function initializeSectionFeatures(section) {
    switch(section) {
        case 'clients':
            initializeClientsTable();
            break;
        case 'add-client':
            initializeAddClientForm();
            break;
        case 'smart-tv-activation':
            initializeSmartTVSection();
            break;
        default:
            initializeEditableTables();
    }
    
    // Initialize common features
    initializeModals();
    initializeFormValidation();
}

// Initialize editable tables
function initializeEditableTables() {
    $('.editable-cell').off('click').on('click', function() {
        if (editingCell !== null) {
            return; // Already editing another cell
        }
        
        const cell = $(this);
        const currentValue = cell.text().trim();
        const field = cell.data('field');
        const id = cell.closest('tr').data('id');
        
        if (!field || !id) {
            return;
        }
        
        editingCell = cell;
        
        // Create input field
        const input = $('<input type="text" class="inline-edit-input">');
        input.val(currentValue);
        
        cell.html(input);
        cell.addClass('editing');
        input.focus().select();
        
        // Handle save on Enter or blur
        input.on('keypress blur', function(e) {
            if (e.type === 'keypress' && e.which !== 13) {
                return;
            }
            
            const newValue = input.val().trim();
            
            if (newValue === currentValue) {
                cancelEdit();
                return;
            }
            
            saveInlineEdit(id, field, newValue, cell, currentValue);
        });
        
        // Handle cancel on Escape
        input.on('keyup', function(e) {
            if (e.which === 27) { // Escape key
                cancelEdit();
            }
        });
    });
}

// Save inline edit
function saveInlineEdit(id, field, newValue, cell, oldValue) {
    const table = getCurrentTableName();
    
    $.post('api/update.php', {
        table: table,
        id: id,
        field: field,
        value: newValue
    })
    .done(function(response) {
        if (response.success) {
            cell.html(newValue);
            cell.removeClass('editing');
            editingCell = null;
            showAlert('success', 'Zapisano zmiany');
        } else {
            cell.html(oldValue);
            cell.removeClass('editing');
            editingCell = null;
            showAlert('danger', response.error || 'Błąd zapisu');
        }
    })
    .fail(function() {
        cancelEdit();
        showAlert('danger', 'Błąd połączenia z serwerem');
    });
}

// Cancel inline edit
function cancelEdit() {
    if (editingCell) {
        const originalValue = editingCell.find('input').attr('data-original') || '';
        editingCell.html(originalValue);
        editingCell.removeClass('editing');
        editingCell = null;
    }
}

// Get current table name based on section
function getCurrentTableName() {
    const sectionTableMap = {
        'clients': 'clients',
        'panels': 'panels',
        'android-apps': 'apps',
        'contact-types': 'contact_types',
        'payment-methods': 'payment_methods',
        'pricing-config': 'pricing_config',
        'faq': 'questions',
        'smart-tv-activation': 'smart_tv_activations'
    };
    
    return sectionTableMap[currentSection] || 'clients';
}

// Initialize clients table
function initializeClientsTable() {
    initializeEditableTables();
    
    // Initialize search
    $('#clientSearch').on('keyup', function() {
        const searchTerm = $(this).val().toLowerCase();
        $('#clientsTable tbody tr').each(function() {
            const row = $(this);
            const text = row.text().toLowerCase();
            row.toggle(text.includes(searchTerm));
        });
    });
    
    // Initialize filters
    $('#statusFilter').on('change', function() {
        const status = $(this).val();
        if (status === '') {
            $('#clientsTable tbody tr').show();
            return;
        }
        
        $('#clientsTable tbody tr').each(function() {
            const row = $(this);
            const statusCell = row.find('.client-status');
            const hasStatus = statusCell.hasClass('status-' + status);
            row.toggle(hasStatus);
        });
    });
}

// Initialize add client form
function initializeAddClientForm() {
    // Generate password button
    $('#generatePassword').on('click', function() {
        $.get('api/generate-password.php')
            .done(function(response) {
                if (response.success) {
                    $('#password').val(response.password);
                }
            });
    });
    
    // Form submission
    $('#addClientForm').on('submit', function(e) {
        e.preventDefault();
        
        const formData = $(this).serialize();
        
        $.post('api/add-client.php', formData)
            .done(function(response) {
                if (response.success) {
                    showAlert('success', 'Klient został dodany pomyślnie');
                    $('#addClientForm')[0].reset();
                } else {
                    showAlert('danger', response.error || 'Błąd dodawania klienta');
                }
            });
    });
}

// Initialize Smart TV section
function initializeSmartTVSection() {
    // Generate activation ID
    $('#generateActivationId').on('click', function() {
        const activationId = 'STV-' + Math.random().toString(36).substr(2, 8).toUpperCase();
        $('#activation_id').val(activationId);
    });
    
    // Add new activation
    $('#addActivationForm').on('submit', function(e) {
        e.preventDefault();
        
        const formData = $(this).serialize();
        
        $.post('api/add-smart-tv-activation.php', formData)
            .done(function(response) {
                if (response.success) {
                    showAlert('success', 'Aktywacja Smart TV została dodana');
                    location.reload(); // Refresh to show new activation
                } else {
                    showAlert('danger', response.error || 'Błąd dodawania aktywacji');
                }
            });
    });
}

// Initialize modals
function initializeModals() {
    // Delete confirmation modal
    $('.btn-delete').on('click', function() {
        const id = $(this).data('id');
        const table = $(this).data('table');
        const name = $(this).data('name');
        
        $('#deleteModal .modal-body').html(`Czy na pewno chcesz usunąć: <strong>${name}</strong>?`);
        $('#confirmDelete').data('id', id).data('table', table);
        $('#deleteModal').modal('show');
    });
    
    $('#confirmDelete').on('click', function() {
        const id = $(this).data('id');
        const table = $(this).data('table');
        
        $.post('api/delete.php', { id: id, table: table })
            .done(function(response) {
                if (response.success) {
                    showAlert('success', 'Rekord został usunięty');
                    $(`tr[data-id="${id}"]`).fadeOut(300, function() {
                        $(this).remove();
                    });
                } else {
                    showAlert('danger', response.error || 'Błąd usuwania');
                }
                $('#deleteModal').modal('hide');
            });
    });
}

// Initialize form validation
function initializeFormValidation() {
    $('form.needs-validation').on('submit', function(e) {
        const form = $(this)[0];
        
        if (!form.checkValidity()) {
            e.preventDefault();
            e.stopPropagation();
            showAlert('warning', 'Proszę wypełnić wszystkie wymagane pola');
        }
        
        $(form).addClass('was-validated');
    });
}

// Show alert message
function showAlert(type, message, duration = 5000) {
    const alert = $(`
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `);
    
    // Remove existing alerts
    $('.alert').remove();
    
    // Add new alert at top of main content
    $('#main-content').prepend(alert);
    
    // Auto-hide after duration
    setTimeout(() => {
        alert.fadeOut(300, function() {
            $(this).remove();
        });
    }, duration);
}

// CSV Import functionality
function initializeCSVImport() {
    $('#csvFile').on('change', function(e) {
        const file = e.target.files[0];
        if (!file) return;
        
        if (file.type !== 'text/csv' && !file.name.endsWith('.csv')) {
            showAlert('danger', 'Proszę wybrać plik CSV');
            return;
        }
        
        $('#uploadCsv').prop('disabled', false);
    });
    
    $('#uploadCsv').on('click', function() {
        const fileInput = $('#csvFile')[0];
        if (!fileInput.files.length) {
            showAlert('warning', 'Proszę wybrać plik CSV');
            return;
        }
        
        const formData = new FormData();
        formData.append('csv_file', fileInput.files[0]);
        
        $(this).prop('disabled', true).html('<span class="spinner-border spinner-border-sm me-2"></span>Importowanie...');
        
        $.ajax({
            url: 'api/import-csv.php',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                if (response.success) {
                    showAlert('success', `Zaimportowano ${response.count} rekordów`);
                    setTimeout(() => location.reload(), 2000);
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

// Export data functionality
function exportData(table, format = 'csv') {
    const url = `api/export.php?table=${table}&format=${format}`;
    window.open(url, '_blank');
}

// Telegram Bot functionality
function refreshBotStats() {
    $.get('api/telegram-stats.php')
        .done(function(response) {
            if (response.success) {
                $('.bot-stats').html(response.html);
            }
        });
}

// Utility functions
function formatDate(dateString) {
    if (!dateString) return '-';
    
    const date = new Date(dateString);
    return date.toLocaleDateString('pl-PL');
}

function calculateDaysToExpiry(expDate) {
    if (!expDate) return null;
    
    const today = new Date();
    const expiry = new Date(expDate);
    const diffTime = expiry - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    return diffDays;
}

// Keyboard shortcuts
$(document).on('keydown', function(e) {
    // Escape key - cancel current operation
    if (e.which === 27) {
        if (editingCell) {
            cancelEdit();
        }
        $('.modal').modal('hide');
    }
    
    // Ctrl+S - save (prevent default browser save)
    if (e.ctrlKey && e.which === 83) {
        e.preventDefault();
        if (editingCell) {
            editingCell.find('input').blur();
        }
    }
});

// Auto-refresh stats every 30 seconds
setInterval(function() {
    if (currentSection === 'dashboard') {
        // Refresh dashboard stats silently
        $.get('api/dashboard-stats.php')
            .done(function(response) {
                if (response.success) {
                    Object.keys(response.stats).forEach(function(key) {
                        $(`.stat-card[onclick*="${key}"] .h5`).text(response.stats[key]);
                    });
                }
            });
    }
}, 30000);