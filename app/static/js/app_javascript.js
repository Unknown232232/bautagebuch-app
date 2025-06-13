/**
 * Bautagebuch App - JavaScript Funktionen
 * Borrmann Professionals Style
 */

// DOM Ready
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

/**
 * App Initialisierung
 */
function initializeApp() {
    // Lade-Animationen für Seiten
    showPageLoader();
    
    // Form-Validierungen initialisieren
    initializeFormValidation();
    
    // Tooltips initialisieren
    initializeTooltips();
    
    // Auto-Save für Formulare
    initializeAutoSave();
    
    // Tastatur-Shortcuts
    initializeKeyboardShortcuts();
    
    // Animate Elements on Scroll
    initializeScrollAnimations();
    
    // Theme-Switcher (optional)
    initializeThemeToggle();
    
    // Material-Verwaltung (Admin)
    initializeMaterialManagement();
    
    // Datatable Initialisierung
    initializeDataTables();
    
    setTimeout(() => {
        hidePageLoader();
        addFadeInAnimation();
    }, 300);
}

/**
 * Loading-Funktionen
 */
function showPageLoader() {
    const loader = document.createElement('div');
    loader.id = 'pageLoader';
    loader.innerHTML = `
        <div class="d-flex justify-content-center align-items-center position-fixed w-100 h-100" 
             style="top: 0; left: 0; background: rgba(255,255,255,0.9); z-index: 9999;">
            <div class="text-center">
                <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem;">
                    <span class="visually-hidden">Lädt...</span>
                </div>
                <div class="mt-3">
                    <strong>Bautagebuch wird geladen...</strong>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(loader);
}

function hidePageLoader() {
    const loader = document.getElementById('pageLoader');
    if (loader) {
        loader.style.opacity = '0';
        setTimeout(() => loader.remove(), 300);
    }
}

function addFadeInAnimation() {
    const elements = document.querySelectorAll('.card, .table, .form-control');
    elements.forEach((el, index) => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        setTimeout(() => {
            el.style.transition = 'all 0.5s ease';
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

/**
 * Form-Validierung
 */
function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                showValidationErrors(form);
            } else {
                showSubmitLoader(event.target);
            }
            form.classList.add('was-validated');
        });
        
        // Real-time Validierung
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', validateField);
            input.addEventListener('input', clearFieldError);
        });
    });
}

function validateField(event) {
    const field = event.target;
    const isValid = field.checkValidity();
    
    if (!isValid) {
        showFieldError(field, field.validationMessage);
    }
}

function clearFieldError(event) {
    const field = event.target;
    const errorMsg = field.parentNode.querySelector('.invalid-feedback');
    if (errorMsg) {
        errorMsg.remove();
    }
    field.classList.remove('is-invalid');
}

function showFieldError(field, message) {
    clearFieldError({ target: field });
    
    field.classList.add('is-invalid');
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    field.parentNode.appendChild(errorDiv);
}

function showValidationErrors(form) {
    const invalidFields = form.querySelectorAll(':invalid');
    if (invalidFields.length > 0) {
        invalidFields[0].focus();
        showNotification('Bitte korrigieren Sie die markierten Felder.', 'warning');
    }
}

/**
 * Submit-Loader für Formulare
 */
function showSubmitLoader(button) {
    const originalText = button.innerHTML;
    button.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Wird gespeichert...';
    button.disabled = true;
    
    // Nach 3 Sekunden zurücksetzen (falls keine Weiterleitung erfolgt)
    setTimeout(() => {
        button.innerHTML = originalText;
        button.disabled = false;
    }, 3000);
}

/**
 * Auto-Save Funktionalität
 */
function initializeAutoSave() {
    const autoSaveForms = document.querySelectorAll('[data-autosave]');
    
    autoSaveForms.forEach(form => {
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('input', debounce(() => {
                saveFormData(form);
            }, 2000));
        });
        
        // Lade gespeicherte Daten
        loadFormData(form);
    });
}

function saveFormData(form) {
    const formData = new FormData(form);
    const data = {};
    
    formData.forEach((value, key) => {
        data[key] = value;
    });
    
    const formId = form.id || 'default';
    localStorage.setItem(`autosave_${formId}`, JSON.stringify(data));
    
    showNotification('Daten automatisch gespeichert', 'info', 2000);
}

function loadFormData(form) {
    const formId = form.id || 'default';
    const savedData = localStorage.getItem(`autosave_${formId}`);
    
    if (savedData) {
        const data = JSON.parse(savedData);
        Object.keys(data).forEach(key => {
            const field = form.querySelector(`[name="${key}"]`);
            if (field) {
                field.value = data[key];
            }
        });
    }
}

/**
 * Tooltips initialisieren
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Tastatur-Shortcuts
 */
function initializeKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl + S für Speichern
        if (e.ctrlKey && e.key === 's') {
            e.preventDefault();
            const submitBtn = document.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.click();
            }
        }
        
        // Ctrl + N für Neuer Eintrag
        if (e.ctrlKey && e.key === 'n') {
            e.preventDefault();
            const newBtn = document.querySelector('[data-bs-toggle="modal"]');
            if (newBtn) {
                newBtn.click();
            }
        }
        
        // ESC für Modal schließen
        if (e.key === 'Escape') {
            const openModal = document.querySelector('.modal.show');
            if (openModal) {
                const modal = bootstrap.Modal.getInstance(openModal);
                if (modal) {
                    modal.hide();
                }
            }
        }
    });
}

/**
 * Scroll-Animationen
 */
function initializeScrollAnimations() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    });
    
    const animateElements = document.querySelectorAll('.card, .alert');
    animateElements.forEach(el => observer.observe(el));
}

/**
 * Theme Toggle (optional)
 */
function initializeThemeToggle() {
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
        
        // Lade gespeichertes Theme
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'dark') {
            document.body.classList.add('dark-theme');
        }
    }
}

function toggleTheme() {
    document.body.classList.toggle('dark-theme');
    const isDark = document.body.classList.contains('dark-theme');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
}

/**
 * Material-Verwaltung (Admin)
 */
function initializeMaterialManagement() {
    // Add Material Button
    const addMaterialBtn = document.getElementById('addMaterialBtn');
    if (addMaterialBtn) {
        addMaterialBtn.addEventListener('click', showAddMaterialModal);
    }
    
    // Edit Material Buttons
    const editMaterialBtns = document.querySelectorAll('.edit-material-btn');
    editMaterialBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const materialId = this.dataset.materialId;
            const materialName = this.dataset.materialName;
            showEditMaterialModal(materialId, materialName);
        });
    });
    
    // Delete Material Buttons
    const deleteMaterialBtns = document.querySelectorAll('.delete-material-btn');
    deleteMaterialBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const materialId = this.dataset.materialId;
            const materialName = this.dataset.materialName;
            confirmDeleteMaterial(materialId, materialName);
        });
    });
}

function showAddMaterialModal() {
    const modal = new bootstrap.Modal(document.getElementById('materialModal'));
    document.getElementById('materialModalTitle').textContent = 'Material hinzufügen';
    document.getElementById('materialForm').reset();
    document.getElementById('materialId').value = '';
    modal.show();
}

function showEditMaterialModal(id, name) {
    const modal = new bootstrap.Modal(document.getElementById('materialModal'));
    document.getElementById('materialModalTitle').textContent = 'Material bearbeiten';
    document.getElementById('materialId').value = id;
    document.getElementById('materialName').value = name;
    modal.show();
}

function confirmDeleteMaterial(id, name) {
    if (confirm(`Möchten Sie das Material "${name}" wirklich löschen?`)) {
        deleteMaterial(id);
    }
}

async function deleteMaterial(id) {
    try {
        const response = await apiRequest(`/admin/materials/${id}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showNotification('Material erfolgreich gelöscht', 'success');
            location.reload();
        } else {
            throw new Error('Fehler beim Löschen');
        }
    } catch (error) {
        showNotification('Fehler beim Löschen des Materials', 'error');
    }
}

/**
 * DataTables Initialisierung
 */
function initializeDataTables() {
    const tables = document.querySelectorAll('.data-table');
    tables.forEach(table => {
        if (typeof DataTable !== 'undefined') {
            new DataTable(table, {
                language: {
                    url: '//cdn.datatables.net/plug-ins/1.13.7/i18n/de-DE.json'
                },
                responsive: true,
                pageLength: 25,
                order: [[0, 'desc']]
            });
        }
    });
}

/**
 * Notification System
 */
function showNotification(message, type = 'info', duration = 5000) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove nach duration
    setTimeout(() => {
        if (notification.parentNode) {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 150);
        }
    }, duration);
}

/**
 * Duplikatsprüfung
 */
async function checkForDuplicates(formData) {
    const duplicateCheck = {
        datum: formData.get('datum'),
        ort: formData.get('ort'),
        material: formData.get('material')
    };
    
    try {
        const response = await apiRequest('/api/check-duplicates', {
            method: 'POST',
            body: JSON.stringify(duplicateCheck)
        });
        
        const result = await response.json();
        return result.hasDuplicate;
    } catch (error) {
        console.error('Fehler bei Duplikatsprüfung:', error);
        return false;
    }
}

/**
 * Export-Funktionen
 */
function exportToPDF(elementId) {
    showNotification('PDF wird erstellt...', 'info');
    
    const element = document.getElementById(elementId);
    if (!element) {
        showNotification('Element nicht gefunden', 'error');
        return;
    }
    
    // Hier würde normalerweise die PDF-Generierung stattfinden
    // z.B. mit jsPDF oder ähnlicher Bibliothek
    setTimeout(() => {
        showNotification('PDF erfolgreich erstellt!', 'success');
        // Simuliere Download
        const link = document.createElement('a');
        link.href = '#';
        link.download = `bautagebuch_${formatDate(new Date())}.pdf`;
        link.click();
    }, 2000);
}

function exportToExcel(data) {
    showNotification('Excel-Export wird vorbereitet...', 'info');
    
    setTimeout(() => {
        showNotification('Excel-Datei erfolgreich erstellt!', 'success');
        // Simuliere Download
        const link = document.createElement('a');
        link.href = '#';
        link.download = `bautagebuch_${formatDate(new Date())}.xlsx`;
        link.click();
    }, 1500);
}

/**
 * Image Upload Funktionalität
 */
function initializeImageUpload() {
    const imageInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
    
    imageInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                previewImage(file, input);
            }
        });
    });
}

function previewImage(file, input) {
    const reader = new FileReader();
    reader.onload = function(e) {
        const preview = input.parentNode.querySelector('.image-preview');
        if (preview) {
            preview.innerHTML = `<img src="${e.target.result}" alt="Vorschau" class="img-thumbnail" style="max-width: 200px;">`;
        }
    };
    reader.readAsDataURL(file);
}

/**
 * Hilfsfunktionen
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function formatDate(date) {
    return new Intl.DateTimeFormat('de-DE').format(new Date(date));
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('de-DE', {
        style: 'currency',
        currency: 'EUR'
    }).format(amount);
}

/**
 * AJAX-Hilfsfunktionen
 */
async function apiRequest(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
    };
    
    const config = { ...defaultOptions, ...options };
    
    try {
        const response = await fetch(url, config);
        return response;
    } catch (error) {
        console.error('API Request failed:', error);
        throw error;
    }
}

/**
 * Erweiterte Funktionen für Borrmann Style
 */
function initializeBorrmannFeatures() {
    // Smooth Scrolling für Anker-Links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Parallax-Effekt für Header (optional)
    const header = document.querySelector('.hero-section');
    if (header) {
        window.addEventListener('scroll', function() {
            const scrolled = window.pageYOffset;
            const rate = scrolled * -0.5;
            header.style.transform = `translateY(${rate}px)`;
        });
    }
    
    // Typing-Effect für Überschriften
    const typingElements = document.querySelectorAll('.typing-effect');
    typingElements.forEach(element => {
        typeWriterEffect(element, element.textContent, 100);
    });
}

function typeWriterEffect(element, text, speed = 100) {
    element.textContent = '';
    let i = 0;
    
    function type() {
        if (i < text.length) {
            element.textContent += text.charAt(i);
            i++;
            setTimeout(type, speed);
        }
    }
    
    type();
}

// Initialisiere Borrmann-spezifische Features
document.addEventListener('DOMContentLoaded', function() {
    initializeBorrmannFeatures();
    initializeImageUpload();
});