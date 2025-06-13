/**
 * Enhanced Form Validation Module
 * Bautagebuch App - Client-side validation
 */

class FormValidator {
    constructor(form, options = {}) {
        this.form = form;
        this.options = {
            realTimeValidation: true,
            showSuccessStates: true,
            validateOnBlur: true,
            validateOnInput: false,
            ...options
        };
        
        this.rules = new Map();
        this.errors = new Map();
        this.isValid = false;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.loadValidationRules();
    }
    
    setupEventListeners() {
        // Form submission
        this.form.addEventListener('submit', (e) => {
            if (!this.validateAll()) {
                e.preventDefault();
                this.showValidationSummary();
            }
        });
        
        // Field-level validation
        const fields = this.form.querySelectorAll('input, select, textarea');
        fields.forEach(field => {
            if (this.options.validateOnBlur) {
                field.addEventListener('blur', () => this.validateField(field));
            }
            
            if (this.options.validateOnInput) {
                field.addEventListener('input', () => {
                    this.clearFieldError(field);
                    if (field.value) {
                        setTimeout(() => this.validateField(field), 300);
                    }
                });
            }
        });
    }
    
    loadValidationRules() {
        const fields = this.form.querySelectorAll('[data-validate]');
        fields.forEach(field => {
            const rules = field.getAttribute('data-validate').split('|');
            this.rules.set(field.name, rules);
        });
    }
    
    validateAll() {
        this.errors.clear();
        let isFormValid = true;
        
        const fields = this.form.querySelectorAll('input, select, textarea');
        fields.forEach(field => {
            if (!this.validateField(field)) {
                isFormValid = false;
            }
        });
        
        this.isValid = isFormValid;
        return isFormValid;
    }
    
    validateField(field) {
        const value = field.value.trim();
        const fieldName = field.name;
        const rules = this.rules.get(fieldName) || [];
        
        // Clear previous errors
        this.errors.delete(fieldName);
        this.clearFieldError(field);
        
        // Apply validation rules
        for (const rule of rules) {
            const error = this.applyRule(field, value, rule);
            if (error) {
                this.errors.set(fieldName, error);
                this.showFieldError(field, error);
                return false;
            }
        }
        
        // Show success state
        if (this.options.showSuccessStates && value) {
            this.showFieldSuccess(field);
        }
        
        return true;
    }
    
    applyRule(field, value, rule) {
        const [ruleName, ...params] = rule.split(':');
        
        switch (ruleName) {
            case 'required':
                return !value ? 'Dieses Feld ist erforderlich' : null;
                
            case 'email':
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                return value && !emailRegex.test(value) ? 'Bitte geben Sie eine gültige E-Mail-Adresse ein' : null;
                
            case 'min':
                const minLength = parseInt(params[0]);
                return value && value.length < minLength ? `Mindestens ${minLength} Zeichen erforderlich` : null;
                
            case 'max':
                const maxLength = parseInt(params[0]);
                return value && value.length > maxLength ? `Maximal ${maxLength} Zeichen erlaubt` : null;
                
            case 'numeric':
                return value && isNaN(value) ? 'Bitte geben Sie eine Zahl ein' : null;
                
            case 'min_value':
                const minValue = parseFloat(params[0]);
                return value && parseFloat(value) < minValue ? `Wert muss mindestens ${minValue} sein` : null;
                
            case 'max_value':
                const maxValue = parseFloat(params[0]);
                return value && parseFloat(value) > maxValue ? `Wert darf höchstens ${maxValue} sein` : null;
                
            case 'pattern':
                const pattern = new RegExp(params[0]);
                return value && !pattern.test(value) ? 'Ungültiges Format' : null;
                
            case 'match':
                const matchField = this.form.querySelector(`[name="${params[0]}"]`);
                return value && matchField && value !== matchField.value ? 'Felder stimmen nicht überein' : null;
                
            case 'unique':
                // This would typically involve an AJAX call to check uniqueness
                return this.validateUnique(field, value);
                
            default:
                return null;
        }
    }
    
    validateUnique(field, value) {
        // Placeholder for unique validation
        // In a real implementation, this would make an AJAX call
        return null;
    }
    
    showFieldError(field, message) {
        field.classList.remove('is-valid');
        field.classList.add('is-invalid');
        
        // Remove existing error message
        const existingError = field.parentNode.querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }
        
        // Add new error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        errorDiv.textContent = message;
        field.parentNode.appendChild(errorDiv);
        
        // Add error icon
        this.addFieldIcon(field, 'error');
    }
    
    showFieldSuccess(field) {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');
        
        // Remove error message
        const errorDiv = field.parentNode.querySelector('.invalid-feedback');
        if (errorDiv) {
            errorDiv.remove();
        }
        
        // Add success icon
        this.addFieldIcon(field, 'success');
    }
    
    clearFieldError(field) {
        field.classList.remove('is-invalid', 'is-valid');
        
        const errorDiv = field.parentNode.querySelector('.invalid-feedback');
        if (errorDiv) {
            errorDiv.remove();
        }
        
        this.removeFieldIcon(field);
    }
    
    addFieldIcon(field, type) {
        this.removeFieldIcon(field);
        
        const icon = document.createElement('i');
        icon.className = `field-validation-icon bi ${type === 'success' ? 'bi-check-circle-fill text-success' : 'bi-x-circle-fill text-danger'}`;
        icon.style.cssText = `
            position: absolute;
            right: 10px;
            top: 50%;
            transform: translateY(-50%);
            pointer-events: none;
            z-index: 5;
        `;
        
        field.parentNode.style.position = 'relative';
        field.parentNode.appendChild(icon);
        field.style.paddingRight = '35px';
    }
    
    removeFieldIcon(field) {
        const icon = field.parentNode.querySelector('.field-validation-icon');
        if (icon) {
            icon.remove();
            field.style.paddingRight = '';
        }
    }
    
    showValidationSummary() {
        if (this.errors.size === 0) return;
        
        const errorMessages = Array.from(this.errors.values());
        const message = `Bitte korrigieren Sie folgende Fehler:\n• ${errorMessages.join('\n• ')}`;
        
        if (window.BautagebuchApp && window.BautagebuchApp.showToast) {
            window.BautagebuchApp.showToast(message, 'error', 8000);
        } else {
            alert(message);
        }
        
        // Focus first invalid field
        const firstInvalidField = this.form.querySelector('.is-invalid');
        if (firstInvalidField) {
            firstInvalidField.focus();
        }
    }
    
    // Public methods
    addRule(fieldName, rule) {
        const existingRules = this.rules.get(fieldName) || [];
        existingRules.push(rule);
        this.rules.set(fieldName, existingRules);
    }
    
    removeRule(fieldName, rule) {
        const existingRules = this.rules.get(fieldName) || [];
        const index = existingRules.indexOf(rule);
        if (index > -1) {
            existingRules.splice(index, 1);
            this.rules.set(fieldName, existingRules);
        }
    }
    
    getErrors() {
        return Object.fromEntries(this.errors);
    }
    
    clearErrors() {
        this.errors.clear();
        const fields = this.form.querySelectorAll('.is-invalid, .is-valid');
        fields.forEach(field => this.clearFieldError(field));
    }
    
    setCustomError(fieldName, message) {
        const field = this.form.querySelector(`[name="${fieldName}"]`);
        if (field) {
            this.errors.set(fieldName, message);
            this.showFieldError(field, message);
        }
    }
}

// Password strength validator
class PasswordStrengthValidator {
    constructor(passwordField, options = {}) {
        this.passwordField = passwordField;
        this.options = {
            minLength: 8,
            requireUppercase: true,
            requireLowercase: true,
            requireNumbers: true,
            requireSpecialChars: true,
            showStrengthMeter: true,
            ...options
        };
        
        this.init();
    }
    
    init() {
        if (this.options.showStrengthMeter) {
            this.createStrengthMeter();
        }
        
        this.passwordField.addEventListener('input', () => {
            this.updateStrengthMeter();
        });
    }
    
    createStrengthMeter() {
        const meterContainer = document.createElement('div');
        meterContainer.className = 'password-strength-meter mt-2';
        meterContainer.innerHTML = `
            <div class="progress" style="height: 8px;">
                <div class="progress-bar" role="progressbar" style="width: 0%"></div>
            </div>
            <small class="password-strength-text text-muted">Passwort-Stärke</small>
        `;
        
        this.passwordField.parentNode.appendChild(meterContainer);
        this.strengthBar = meterContainer.querySelector('.progress-bar');
        this.strengthText = meterContainer.querySelector('.password-strength-text');
    }
    
    updateStrengthMeter() {
        const password = this.passwordField.value;
        const strength = this.calculateStrength(password);
        
        if (this.strengthBar) {
            this.strengthBar.style.width = `${strength.percentage}%`;
            this.strengthBar.className = `progress-bar ${strength.colorClass}`;
        }
        
        if (this.strengthText) {
            this.strengthText.textContent = strength.text;
            this.strengthText.className = `password-strength-text ${strength.textClass}`;
        }
    }
    
    calculateStrength(password) {
        let score = 0;
        let feedback = [];
        
        // Length check
        if (password.length >= this.options.minLength) {
            score += 20;
        } else {
            feedback.push(`Mindestens ${this.options.minLength} Zeichen`);
        }
        
        // Uppercase check
        if (this.options.requireUppercase) {
            if (/[A-Z]/.test(password)) {
                score += 20;
            } else {
                feedback.push('Großbuchstaben');
            }
        }
        
        // Lowercase check
        if (this.options.requireLowercase) {
            if (/[a-z]/.test(password)) {
                score += 20;
            } else {
                feedback.push('Kleinbuchstaben');
            }
        }
        
        // Numbers check
        if (this.options.requireNumbers) {
            if (/\d/.test(password)) {
                score += 20;
            } else {
                feedback.push('Zahlen');
            }
        }
        
        // Special characters check
        if (this.options.requireSpecialChars) {
            if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
                score += 20;
            } else {
                feedback.push('Sonderzeichen');
            }
        }
        
        // Determine strength level
        let level, colorClass, textClass, text;
        
        if (score < 40) {
            level = 'weak';
            colorClass = 'bg-danger';
            textClass = 'text-danger';
            text = 'Schwach';
        } else if (score < 60) {
            level = 'fair';
            colorClass = 'bg-warning';
            textClass = 'text-warning';
            text = 'Ausreichend';
        } else if (score < 80) {
            level = 'good';
            colorClass = 'bg-info';
            textClass = 'text-info';
            text = 'Gut';
        } else {
            level = 'strong';
            colorClass = 'bg-success';
            textClass = 'text-success';
            text = 'Stark';
        }
        
        if (feedback.length > 0) {
            text += ` (Benötigt: ${feedback.join(', ')})`;
        }
        
        return {
            score,
            percentage: score,
            level,
            colorClass,
            textClass,
            text,
            feedback
        };
    }
    
    isValid() {
        const strength = this.calculateStrength(this.passwordField.value);
        return strength.score >= 80;
    }
}

// Auto-initialize validation for forms with data-validate attribute
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form[data-validate]');
    forms.forEach(form => {
        new FormValidator(form);
    });
    
    // Initialize password strength meters
    const passwordFields = document.querySelectorAll('input[type="password"][data-strength]');
    passwordFields.forEach(field => {
        new PasswordStrengthValidator(field);
    });
});

// Export for use in other modules
window.FormValidator = FormValidator;
window.PasswordStrengthValidator = PasswordStrengthValidator;
