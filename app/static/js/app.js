/**
 * Bautagebuch App - Enhanced JavaScript
 * Borrmann Professionals Design System
 */

// ===== GLOBAL VARIABLES ===== 
let loadingOverlay = null;
let toastContainer = null;

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    createLoadingOverlay();
    createToastContainer();
    initializeFormValidation();
    initializeTableSorting();
    initializeSearchFilters();
    initializeDatePickers();
    initializeFileUploads();
    initializeTooltips();
    setupAjaxDefaults();
}

// ===== LOADING SYSTEM =====
function createLoadingOverlay() {
    loadingOverlay = document.createElement('div');
    loadingOverlay.className = 'loading-overlay d-none';
    loadingOverlay.innerHTML = `
        <div class="text-center">
            <div class="loading-spinner dark mb-3"></div>
            <p class="text-secondary">Lädt...</p>
        </div>
    `;
    document.body.appendChild(loadingOverlay);
}

function showLoading(message = 'Lädt...') {
    if (loadingOverlay) {
        loadingOverlay.querySelector('p').textContent = message;
        loadingOverlay.classList.remove('d-none');
    }
}

function hideLoading() {
    if (loadingOverlay) {
        loadingOverlay.classList.add('d-none');
    }
}

// ===== TOAST NOTIFICATION SYSTEM =====
function createToastContainer() {
    toastContainer = document.createElement('div');
    toastContainer.id = 'toast-container';
    toastContainer.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 10000;
        max-width: 350px;
    `;
    document.body.appendChild(toastContainer);
}

function showToast(message, type = 'info', duration = 5000) {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} shadow mb-2`;
    toast.style.cssText = `
        opacity: 0;
        transform: translateX(100%);
        transition: all 0.3s ease;
        cursor: pointer;
    `;
    
    const icon = getIconForType(type);
    toast.innerHTML = `
        <div class="d-flex align-items-center">
            <span class="me-2">${icon}</span>
            <span>${message}</span>
            <button type="button" class="btn-close ms-auto" onclick="closeToast(this)"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Animate in
    setTimeout(() => {
        toast.style.opacity = '1';
        toast.style.transform = 'translateX(0)';
    }, 10);
    
    // Auto remove
    if (duration > 0) {
        setTimeout(() => closeToast(toast), duration);
    }
    
    // Click to close
    toast.addEventListener('click', () => closeToast(toast));
    
    return toast;
}

function closeToast(element) {
    const toast = element.closest ? element.closest('.alert') : element;
    if (toast) {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => toast.remove(), 300);
    }
}

function getIconForType(type) {
    const icons = {
        success: '✅',
        warning: '⚠️',
        danger: '❌',
        error: '❌',
        info: 'ℹ️'
    };
    return icons[type] || icons.info;
}

// ===== FORM VALIDATION =====
function initializeFormValidation() {
    const forms = document.querySelectorAll('form[data-validate]');
    forms.forEach(form => {
        form.addEventListener('submit', handleFormSubmit);
        
        // Real-time validation
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', () => validateField(input));
            input.addEventListener('input', () => clearFieldError(input));
        });
    });
}

function handleFormSubmit(event) {
    const form = event.target;
    const isValid = validateForm(form);
    
    if (!isValid) {
        event.preventDefault();
        showToast('Bitte korrigieren Sie die Eingabefehler', 'danger');
        return false;
    }
    
    // Show loading for AJAX forms
    if (form.hasAttribute('data-ajax')) {
        event.preventDefault();
        submitFormAjax(form);
    }
}

function validateForm(form) {
    let isValid = true;
    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    
    inputs.forEach(input => {
        if (!validateField(input)) {
            isValid = false;
        }
    });
    
    return isValid;
}

function validateField(field) {
    const value = field.value.trim();
    const type = field.type;
    let isValid = true;
    let errorMessage = '';
    
    // Required validation
    if (field.hasAttribute('required') && !value) {
        isValid = false;
        errorMessage = 'Dieses Feld ist erforderlich';
    }
    
    // Email validation
    if (type === 'email' && value && !isValidEmail(value)) {
        isValid = false;
        errorMessage = 'Bitte geben Sie eine gültige E-Mail-Adresse ein';
    }
    
    // Number validation
    if (type === 'number' && value) {
        const min = field.getAttribute('min');
        const max = field.getAttribute('max');
        const numValue = parseFloat(value);
        
        if (min && numValue < parseFloat(min)) {
            isValid = false;
            errorMessage = `Wert muss mindestens ${min} sein`;
        }
        if (max && numValue > parseFloat(max)) {
            isValid = false;
            errorMessage = `Wert darf höchstens ${max} sein`;
        }
    }
    
    // Custom validation
    const customPattern = field.getAttribute('data-pattern');
    if (customPattern && value && !new RegExp(customPattern).test(value)) {
        isValid = false;
        errorMessage = field.getAttribute('data-error') || 'Ungültiges Format';
    }
    
    showFieldError(field, isValid ? '' : errorMessage);
    return isValid;
}

function showFieldError(field, message) {
    clearFieldError(field);
    
    if (message) {
        field.classList.add('is-invalid');
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        errorDiv.textContent = message;
        field.parentNode.appendChild(errorDiv);
    } else {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');
    }
}

function clearFieldError(field) {
    field.classList.remove('is-invalid', 'is-valid');
    const errorDiv = field.parentNode.querySelector('.invalid-feedback');
    if (errorDiv) {
        errorDiv.remove();
    }
}

function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

// ===== AJAX FORM SUBMISSION =====
function submitFormAjax(form) {
    const formData = new FormData(form);
    const url = form.action || window.location.href;
    const method = form.method || 'POST';
    
    showLoading('Speichere...');
    
    fetch(url, {
        method: method,
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        
        if (data.success) {
            showToast(data.message || 'Erfolgreich gespeichert', 'success');
            if (data.redirect) {
                setTimeout(() => window.location.href = data.redirect, 1000);
            }
            if (data.reload) {
                setTimeout(() => window.location.reload(), 1000);
            }
        } else {
            showToast(data.message || 'Ein Fehler ist aufgetreten', 'danger');
        }
    })
    .catch(error => {
        hideLoading();
        console.error('Ajax error:', error);
        showToast('Verbindungsfehler. Bitte versuchen Sie es erneut.', 'danger');
    });
}

// ===== TABLE FUNCTIONALITY =====
function initializeTableSorting() {
    const tables = document.querySelectorAll('table[data-sortable]');
    tables.forEach(table => {
        const headers = table.querySelectorAll('th[data-sort]');
        headers.forEach(header => {
            header.style.cursor = 'pointer';
            header.addEventListener('click', () => sortTable(table, header));
        });
    });
}

function sortTable(table, header) {
    const column = header.getAttribute('data-sort');
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const isAscending = !header.classList.contains('sort-asc');
    
    // Clear other sort indicators
    table.querySelectorAll('th').forEach(th => {
        th.classList.remove('sort-asc', 'sort-desc');
    });
    
    // Set current sort indicator
    header.classList.add(isAscending ? 'sort-asc' : 'sort-desc');
    
    rows.sort((a, b) => {
        const aVal = getCellValue(a, column);
        const bVal = getCellValue(b, column);
        
        if (isNumeric(aVal) && isNumeric(bVal)) {
            return isAscending ? aVal - bVal : bVal - aVal;
        }
        
        return isAscending 
            ? aVal.localeCompare(bVal)
            : bVal.localeCompare(aVal);
    });
    
    rows.forEach(row => tbody.appendChild(row));
}

function getCellValue(row, column) {
    const cell = row.querySelector(`td[data-sort="${column}"]`) || 
                 row.cells[parseInt(column)] ||
                 row.cells[0];
    return cell ? cell.textContent.trim() : '';
}

function isNumeric(str) {
    return !isNaN(str) && !isNaN(parseFloat(str));
}

// ===== SEARCH AND FILTER =====
function initializeSearchFilters() {
    const searchInputs = document.querySelectorAll('input[data-search]');
    searchInputs.forEach(input => {
        input.addEventListener('input', debounce(() => filterTable(input), 300));
    });
    
    const filterSelects = document.querySelectorAll('select[data-filter]');
    filterSelects.forEach(select => {
        select.addEventListener('change', () => filterTable(select));
    });
}

function filterTable(element) {
    const target = element.getAttribute('data-search') || element.getAttribute('data-filter');
    const table = document.querySelector(target);
    if (!table) return;
    
    const searchTerm = element.value.toLowerCase();
    const rows = table.querySelectorAll('tbody tr');
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        const shouldShow = searchTerm === '' || text.includes(searchTerm);
        row.style.display = shouldShow ? '' : 'none';
    });
    
    updateTableStats(table);
}

function updateTableStats(table) {
    const totalRows = table.querySelectorAll('tbody tr').length;
    const visibleRows = table.querySelectorAll('tbody tr:not([style*="display: none"])').length;
    
    const statsElement = document.querySelector(`[data-table-stats="${table.id}"]`);
    if (statsElement) {
        statsElement.textContent = `${visibleRows} von ${totalRows} Einträgen`;
    }
}

// ===== DATE PICKER ENHANCEMENT =====
function initializeDatePickers() {
    const dateInputs = document.querySelectorAll('input[type="date"], input[data-datepicker]');
    dateInputs.forEach(input => {
        // Set default date format for German locale
        input.setAttribute('lang', 'de');
        
        // Add calendar icon
        if (!input.parentNode.querySelector('.date-icon')) {
            const icon = document.createElement('span');
            icon.className = 'date-icon';
            icon.innerHTML = '📅';
            icon.style.cssText = `
                position: absolute;
                right: 10px;
                top: 50%;
                transform: translateY(-50%);
                pointer-events: none;
                color: #6b7280;
            `;
            
            input.parentNode.style.position = 'relative';
            input.parentNode.appendChild(icon);
        }
    });
}

// ===== FILE UPLOAD ENHANCEMENT =====
function initializeFileUploads() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        const wrapper = createFileUploadWrapper(input);
        input.parentNode.insertBefore(wrapper, input);
        wrapper.appendChild(input);
        
        input.addEventListener('change', (e) => handleFileSelect(e, wrapper));
    });
}

function createFileUploadWrapper(input) {
    const wrapper = document.createElement('div');
    wrapper.className = 'file-upload-wrapper';
    wrapper.style.cssText = `
        border: 2px dashed var(--border-gray);
        border-radius: var(--radius-lg);
        padding: var(--spacing-xl);
        text-align: center;
        transition: all var(--transition-normal);
        cursor: pointer;
    `;
    
    wrapper.innerHTML = `
        <div class="file-upload-content">
            <div class="file-upload-icon">📁</div>
            <p class="file-upload-text">Dateien hier ablegen oder klicken zum Auswählen</p>
            <small class="text-muted">Unterstützte Formate: JPG, PNG, PDF (max. 10MB)</small>
        </div>
        <div class="file-list mt-3"></div>
    `;
    
    // Drag and drop events
    wrapper.addEventListener('dragover', (e) => {
        e.preventDefault();
        wrapper.style.borderColor = 'var(--primary-blue)';
        wrapper.style.backgroundColor = 'rgba(59, 130, 246, 0.05)';
    });
    
    wrapper.addEventListener('dragleave', (e) => {
        e.preventDefault();
        wrapper.style.borderColor = 'var(--border-gray)';
        wrapper.style.backgroundColor = 'transparent';
    });
    
    wrapper.addEventListener('drop', (e) => {
        e.preventDefault();
        wrapper.style.borderColor = 'var(--border-gray)';
        wrapper.style.backgroundColor = 'transparent';
        
        const files = e.dataTransfer.files;
        input.files = files;
        handleFileSelect({ target: input }, wrapper);
    });
    
    wrapper.addEventListener('click', () => input.click());
    
    return wrapper;
}

function handleFileSelect(event, wrapper) {
    const files = event.target.files;
    const fileList = wrapper.querySelector('.file-list');
    fileList.innerHTML = '';
    
    if (files.length === 0) return;
    
    Array.from(files).forEach((file, index) => {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item d-flex align-items-center justify-content-between p-2 bg-light rounded mb-2';
        
        const fileInfo = document.createElement('div');
        fileInfo.innerHTML = `
            <strong>${file.name}</strong><br>
            <small class="text-muted">${formatFileSize(file.size)}</small>
        `;
        
        const removeBtn = document.createElement('button');
        removeBtn.type = 'button';
        removeBtn.className = 'btn btn-sm btn-outline-danger';
        removeBtn.innerHTML = '×';
        removeBtn.onclick = () => removeFile(event.target, index, wrapper);
        
        fileItem.appendChild(fileInfo);
        fileItem.appendChild(removeBtn);
        fileList.appendChild(fileItem);
    });
}

function removeFile(input, index, wrapper) {
    const dt = new DataTransfer();
    const files = input.files;
    
    for (let i = 0; i < files.length; i++) {
        if (i !== index) {
            dt.items.add(files[i]);
        }
    }
    
    input.files = dt.files;
    handleFileSelect({ target: input }, wrapper);
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// ===== TOOLTIP SYSTEM =====
function initializeTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
    });
}

function showTooltip(event) {
    const element = event.target;
    const text = element.getAttribute('data-tooltip');
    
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip-custom';
    tooltip.textContent = text;
    tooltip.style.cssText = `
        position: absolute;
        background: var(--dark-gray);
        color: white;
        padding: var(--spacing-sm) var(--spacing-md);
        border-radius: var(--radius-md);
        font-size: 0.875rem;
        z-index: 10000;
        pointer-events: none;
        opacity: 0;
        transition: opacity var(--transition-fast);
    `;
    
    document.body.appendChild(tooltip);
    
    const rect = element.getBoundingClientRect();
    tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
    tooltip.style.top = rect.top - tooltip.offsetHeight - 5 + 'px';
    
    setTimeout(() => tooltip.style.opacity = '1', 10);
    
    element._tooltip = tooltip;
}

function hideTooltip(event) {
    const element = event.target;
    if (element._tooltip) {
        element._tooltip.remove();
        delete element._tooltip;
    }
}

// ===== AJAX SETUP =====
function setupAjaxDefaults() {
    // Add CSRF token to all AJAX requests
    const csrfToken = document.querySelector('meta[name="csrf-token"]');
    if (csrfToken) {
        const originalFetch = window.fetch;
        window.fetch = function(url, options = {}) {
            if (!options.headers) {
                options.headers = {};
            }
            options.headers['X-CSRFToken'] = csrfToken.getAttribute('content');
            return originalFetch(url, options);
        };
    }
}

// ===== UTILITY FUNCTIONS =====
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

function formatDate(date, locale = 'de-DE') {
    return new Date(date).toLocaleDateString(locale);
}

function formatDateTime(date, locale = 'de-DE') {
    return new Date(date).toLocaleString(locale);
}

function formatCurrency(amount, currency = 'EUR', locale = 'de-DE') {
    return new Intl.NumberFormat(locale, {
        style: 'currency',
        currency: currency
    }).format(amount);
}

// ===== SPECIFIC APP FUNCTIONS =====

// Aufmaß Form Enhancement
function initializeAufmassForm() {
    const form = document.querySelector('#aufmass-form');
    if (!form) return;
    
    const materialSelect = form.querySelector('#material');
    const ortInput = form.querySelector('#ort');
    const mengeInput = form.querySelector('#menge');
    
    // Auto-suggest for Ort field
    if (ortInput) {
        initializeAutoSuggest(ortInput, 'ort-suggestions');
    }
    
    // Material change handler
    if (materialSelect) {
        materialSelect.addEventListener('change', function() {
            const selectedMaterial = this.value;
            updateMaterialInfo(selectedMaterial);
        });
    }
    
    // Menge validation
    if (mengeInput) {
        mengeInput.addEventListener('input', function() {
            validateMenge(this);
        });
    }
}

function initializeAutoSuggest(input, suggestionListId) {
    const suggestions = JSON.parse(input.getAttribute('data-suggestions') || '[]');
    
    input.addEventListener('input', function() {
        const value = this.value.toLowerCase();
        const matches = suggestions.filter(s => s.toLowerCase().includes(value));
        showSuggestions(this, matches);
    });
}

function showSuggestions(input, suggestions) {
    // Remove existing suggestions
    const existingSuggestions = document.querySelector('.suggestions-list');
    if (existingSuggestions) {
        existingSuggestions.remove();
    }
    
    if (suggestions.length === 0) return;
    
    const suggestionsList = document.createElement('div');
    suggestionsList.className = 'suggestions-list';
    suggestionsList.style.cssText = `
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        background: white;
        border: 1px solid var(--border-gray);
        border-top: none;
        border-radius: 0 0 var(--radius-md) var(--radius-md);
        max-height: 200px;
        overflow-y: auto;
        z-index: 1000;
        box-shadow: var(--shadow-md);
    `;
    
    suggestions.forEach(suggestion => {
        const item = document.createElement('div');
        item.className = 'suggestion-item';
        item.textContent = suggestion;
        item.style.cssText = `
            padding: var(--spacing-md);
            cursor: pointer;
            border-bottom: 1px solid var(--border-gray);
        `;
        
        item.addEventListener('mouseenter', () => {
            item.style.backgroundColor = 'var(--light-gray)';
        });
        
        item.addEventListener('mouseleave', () => {
            item.style.backgroundColor = 'white';
        });
        
        item.addEventListener('click', () => {
            input.value = suggestion;
            suggestionsList.remove();
            input.focus();
        });
        
        suggestionsList.appendChild(item);
    });
    
    input.parentNode.style.position = 'relative';
    input.parentNode.appendChild(suggestionsList);
}

function updateMaterialInfo(materialId) {
    if (!materialId) return;
    
    fetch(`/aufmass/api/material/${materialId}`)
        .then(response => response.json())
        .then(data => {
            // Update material info display
            const infoDiv = document.querySelector('#material-info');
            if (infoDiv && data) {
                infoDiv.innerHTML = `
                    <small class="text-muted">
                        ${data.kategorie || ''}
                        ${data.einheit ? ` (Einheit: ${data.einheit})` : ''}
                    </small>
                `;
            }
        })
        .catch(error => console.error('Material info error:', error));
}

function validateMenge(input) {
    const value = parseFloat(input.value);
    const min = parseFloat(input.getAttribute('min') || 0);
    const max = parseFloat(input.getAttribute('max') || Infinity);
    
    if (isNaN(value) || value < min || value > max) {
        input.classList.add('is-invalid');
    } else {
        input.classList.remove('is-invalid');
        input.classList.add('is-valid');
    }
}

// Dashboard Enhancement
function initializeDashboard() {
    updateDashboardStats();
    initializeCharts();
    setupRealTimeUpdates();
}

function updateDashboardStats() {
    fetch('/api/dashboard/stats')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateStatCards(data.stats);
            }
        })
        .catch(error => console.error('Dashboard stats error:', error));
}

function updateStatCards(stats) {
    Object.keys(stats).forEach(key => {
        const element = document.querySelector(`[data-stat="${key}"]`);
        if (element) {
            animateNumber(element, stats[key]);
        }
    });
}

function animateNumber(element, targetValue) {
    const startValue = parseInt(element.textContent) || 0;
    const duration = 1000;
    const startTime = performance.now();
    
    function updateNumber(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        const currentValue = Math.floor(startValue + (targetValue - startValue) * progress);
        element.textContent = currentValue.toLocaleString('de-DE');
        
        if (progress < 1) {
            requestAnimationFrame(updateNumber);
        }
    }
    
    requestAnimationFrame(updateNumber);
}

function initializeCharts() {
    // Chart initialization would go here
    // This depends on which charting library you choose
}

function setupRealTimeUpdates() {
    // Setup WebSocket or polling for real-time updates
    setInterval(updateDashboardStats, 30000); // Update every 30 seconds
}

// Export functions for global access
window.BautagebuchApp = {
    showLoading,
    hideLoading,
    showToast,
    closeToast,
    validateForm,
    initializeAufmassForm,
    initializeDashboard,
    formatDate,
    formatDateTime,
    formatCurrency
};

// Initialize specific modules based on page
if (document.querySelector('#aufmass-form')) {
    document.addEventListener('DOMContentLoaded', initializeAufmassForm);
}

if (document.querySelector('.dashboard')) {
    document.addEventListener('DOMContentLoaded', initializeDashboard);
}
