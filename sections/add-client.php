<?php
session_start();
require_once '../includes/functions.php';

// Sprawdź czy użytkownik jest zalogowany
requireLogin();
?>

<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
    <h1 class="h2">
        <i class="fas fa-user-plus me-2"></i>Dodaj Nowego Klienta
    </h1>
    <div class="btn-toolbar mb-2 mb-md-0">
        <button type="button" class="btn btn-secondary" onclick="loadSection('clients')">
            <i class="fas fa-arrow-left"></i> Powrót do listy
        </button>
    </div>
</div>

<div class="row justify-content-center">
    <div class="col-lg-8">
        <div class="card">
            <div class="card-header">
                <h5 class="card-title mb-0">
                    <i class="fas fa-user-plus me-2"></i>Dane nowego klienta
                </h5>
            </div>
            <div class="card-body">
                <form id="addClientForm" class="needs-validation" novalidate>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="username" class="form-label">
                                <i class="fas fa-user me-2"></i>Nazwa użytkownika *
                            </label>
                            <input type="text" id="username" name="username" class="form-control" required minlength="3">
                            <div class="invalid-feedback">
                                Podaj nazwę użytkownika (min. 3 znaki)
                            </div>
                        </div>
                        
                        <div class="col-md-6 mb-3">
                            <label for="password" class="form-label">
                                <i class="fas fa-lock me-2"></i>Hasło *
                            </label>
                            <div class="input-group">
                                <input type="text" id="password" name="password" class="form-control" required minlength="4">
                                <button type="button" id="generatePassword" class="btn btn-outline-info">
                                    <i class="fas fa-random"></i> Generuj
                                </button>
                            </div>
                            <div class="invalid-feedback">
                                Podaj hasło (min. 4 znaki)
                            </div>
                        </div>
                    </div>

                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="exp_date" class="form-label">
                                <i class="fas fa-calendar me-2"></i>Data wygaśnięcia *
                            </label>
                            <input type="date" id="exp_date" name="exp_date" class="form-control" required>
                            <div class="invalid-feedback">
                                Podaj datę wygaśnięcia
                            </div>
                        </div>
                        
                        <div class="col-md-6 mb-3">
                            <label for="max_connections" class="form-label">
                                <i class="fas fa-link me-2"></i>Maksymalne połączenia
                            </label>
                            <select id="max_connections" name="max_connections" class="form-select">
                                <option value="1">1 połączenie</option>
                                <option value="2">2 połączenia</option>
                                <option value="3">3 połączenia</option>
                                <option value="5">5 połączeń</option>
                                <option value="10">10 połączeń</option>
                            </select>
                        </div>
                    </div>

                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="bouquet" class="form-label">
                                <i class="fas fa-tv me-2"></i>Bouquet
                            </label>
                            <input type="text" id="bouquet" name="bouquet" class="form-control" placeholder="np. HD Premium">
                        </div>
                        
                        <div class="col-md-6 mb-3">
                            <div class="form-check mt-4 pt-2">
                                <input type="checkbox" id="is_trial" name="is_trial" class="form-check-input">
                                <label for="is_trial" class="form-check-label">
                                    <i class="fas fa-clock me-2"></i>To jest konto trial
                                </label>
                            </div>
                        </div>
                    </div>

                    <div class="mb-3">
                        <label for="notes" class="form-label">
                            <i class="fas fa-sticky-note me-2"></i>Notatki
                        </label>
                        <textarea id="notes" name="notes" class="form-control" rows="3" placeholder="Dodatkowe informacje o kliencie..."></textarea>
                    </div>

                    <div class="card bg-info bg-opacity-25 border-info">
                        <div class="card-body">
                            <h6 class="card-title">
                                <i class="fas fa-info-circle me-2"></i>Informacje
                            </h6>
                            <ul class="list-unstyled mb-0">
                                <li><i class="fas fa-check text-success me-2"></i>Klient zostanie utworzony z bieżącą datą</li>
                                <li><i class="fas fa-check text-success me-2"></i>Możesz ręcznie wprowadzić hasło lub wygenerować automatycznie</li>
                                <li><i class="fas fa-check text-success me-2"></i>Data wygaśnięcia określi status konta</li>
                                <li><i class="fas fa-check text-success me-2"></i>Konta trial mają specjalne oznaczenie</li>
                            </ul>
                        </div>
                    </div>

                    <div class="d-flex justify-content-between mt-4">
                        <button type="button" class="btn btn-secondary" onclick="loadSection('clients')">
                            <i class="fas fa-times me-2"></i>Anuluj
                        </button>
                        <button type="submit" class="btn btn-success">
                            <i class="fas fa-save me-2"></i>Dodaj Klienta
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>

<script>
$(document).ready(function() {
    // Ustaw domyślną datę wygaśnięcia na 30 dni od dzisiaj
    const today = new Date();
    const futureDate = new Date(today.getTime() + 30 * 24 * 60 * 60 * 1000);
    const formatDate = futureDate.toISOString().split('T')[0];
    $('#exp_date').val(formatDate);
    
    // Generator haseł
    $('#generatePassword').on('click', function() {
        const btn = $(this);
        const originalHtml = btn.html();
        
        btn.prop('disabled', true).html('<span class="spinner-border spinner-border-sm"></span>');
        
        $.get('../api/generate-password.php', { length: 8 })
            .done(function(response) {
                if (response.success) {
                    $('#password').val(response.password);
                    showAlert('success', 'Hasło zostało wygenerowane');
                } else {
                    showAlert('danger', 'Błąd generowania hasła');
                }
            })
            .fail(function() {
                showAlert('danger', 'Błąd połączenia z serwerem');
            })
            .always(function() {
                btn.prop('disabled', false).html(originalHtml);
            });
    });
    
    // Obsługa formularza
    $('#addClientForm').on('submit', function(e) {
        e.preventDefault();
        
        const form = $(this);
        const formData = form.serialize();
        
        // Sprawdź walidację HTML5
        if (!this.checkValidity()) {
            e.stopPropagation();
            form.addClass('was-validated');
            return;
        }
        
        const submitBtn = form.find('button[type="submit"]');
        const originalHtml = submitBtn.html();
        
        submitBtn.prop('disabled', true).html('<span class="spinner-border spinner-border-sm me-2"></span>Dodawanie...');
        
        $.post('../api/add-client.php', formData)
            .done(function(response) {
                if (response.success) {
                    showAlert('success', 'Klient został dodany pomyślnie!');
                    form[0].reset();
                    form.removeClass('was-validated');
                    
                    // Resetuj datę wygaśnięcia
                    const today = new Date();
                    const futureDate = new Date(today.getTime() + 30 * 24 * 60 * 60 * 1000);
                    const formatDate = futureDate.toISOString().split('T')[0];
                    $('#exp_date').val(formatDate);
                    
                    // Opcjonalnie przenieś do listy klientów po 3 sekundach
                    setTimeout(function() {
                        const goToList = confirm('Klient został dodany. Czy chcesz przejść do listy klientów?');
                        if (goToList) {
                            loadSection('clients');
                        }
                    }, 2000);
                    
                } else {
                    showAlert('danger', response.error || 'Błąd dodawania klienta');
                }
            })
            .fail(function() {
                showAlert('danger', 'Błąd połączenia z serwerem');
            })
            .always(function() {
                submitBtn.prop('disabled', false).html(originalHtml);
            });
    });
    
    // Walidacja w czasie rzeczywistym
    $('#username').on('input', function() {
        const username = $(this).val();
        if (username.length >= 3) {
            $(this).removeClass('is-invalid').addClass('is-valid');
        } else {
            $(this).removeClass('is-valid').addClass('is-invalid');
        }
    });
    
    $('#password').on('input', function() {
        const password = $(this).val();
        if (password.length >= 4) {
            $(this).removeClass('is-invalid').addClass('is-valid');
        } else {
            $(this).removeClass('is-valid').addClass('is-invalid');
        }
    });
    
    $('#exp_date').on('change', function() {
        const expDate = new Date($(this).val());
        const today = new Date();
        
        if (expDate > today) {
            $(this).removeClass('is-invalid').addClass('is-valid');
        } else {
            $(this).removeClass('is-valid').addClass('is-invalid');
        }
    });
});
</script>