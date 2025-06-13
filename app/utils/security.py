"""
Erweiterte Sicherheitsfunktionen für Bautagebuch App
Verschlüsselung, Hashing und sichere Datenverarbeitung
"""
import os
import secrets
import hashlib
import base64
from datetime import datetime, timedelta, timezone
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from werkzeug.security import generate_password_hash, check_password_hash
import logging

logger = logging.getLogger(__name__)

class SecurityManager:
    """Zentrale Klasse für Sicherheitsfunktionen"""
    
    def __init__(self, app=None):
        self.app = app
        self._encryption_key = None
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize security manager with Flask app"""
        self.app = app
        
        # Generate or load encryption key
        self._encryption_key = self._get_or_create_encryption_key()
        
        # Store in app config for access
        app.config['SECURITY_MANAGER'] = self
    
    def _get_or_create_encryption_key(self):
        """Get or create encryption key for sensitive data"""
        key_file = os.path.join('instance', 'encryption.key')
        
        # Create instance directory if it doesn't exist
        os.makedirs('instance', exist_ok=True)
        
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            # Generate new key
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            
            # Set restrictive permissions
            os.chmod(key_file, 0o600)
            logger.info("New encryption key generated")
            return key
    
    def encrypt_data(self, data):
        """Encrypt sensitive data"""
        if not data:
            return None
        
        try:
            fernet = Fernet(self._encryption_key)
            if isinstance(data, str):
                data = data.encode('utf-8')
            encrypted = fernet.encrypt(data)
            return base64.urlsafe_b64encode(encrypted).decode('utf-8')
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            raise
    
    def decrypt_data(self, encrypted_data):
        """Decrypt sensitive data"""
        if not encrypted_data:
            return None
        
        try:
            fernet = Fernet(self._encryption_key)
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode('utf-8'))
            decrypted = fernet.decrypt(encrypted_bytes)
            return decrypted.decode('utf-8')
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            raise
    
    def hash_sensitive_data(self, data, salt=None):
        """Hash sensitive data with salt"""
        if not data:
            return None
        
        if salt is None:
            salt = secrets.token_bytes(32)
        
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        # Use PBKDF2 for key derivation
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        key = kdf.derive(data)
        
        # Return salt + hash for storage
        return base64.urlsafe_b64encode(salt + key).decode('utf-8')
    
    def verify_hashed_data(self, data, hashed_data):
        """Verify data against hash"""
        if not data or not hashed_data:
            return False
        
        try:
            # Decode the stored hash
            decoded = base64.urlsafe_b64decode(hashed_data.encode('utf-8'))
            salt = decoded[:32]
            stored_hash = decoded[32:]
            
            # Hash the input data with the same salt
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            
            key = kdf.derive(data)
            return secrets.compare_digest(stored_hash, key)
        except Exception as e:
            logger.error(f"Hash verification error: {e}")
            return False


class PasswordSecurity:
    """Enhanced password security functions"""
    
    @staticmethod
    def generate_secure_password(length=16):
        """Generate a secure random password"""
        alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    @staticmethod
    def validate_password_strength(password):
        """Validate password strength"""
        errors = []
        
        if len(password) < 8:
            errors.append("Passwort muss mindestens 8 Zeichen lang sein")
        
        if not any(c.islower() for c in password):
            errors.append("Passwort muss mindestens einen Kleinbuchstaben enthalten")
        
        if not any(c.isupper() for c in password):
            errors.append("Passwort muss mindestens einen Großbuchstaben enthalten")
        
        if not any(c.isdigit() for c in password):
            errors.append("Passwort muss mindestens eine Zahl enthalten")
        
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            errors.append("Passwort muss mindestens ein Sonderzeichen enthalten")
        
        # Check for common patterns
        common_patterns = ['123456', 'password', 'admin', 'qwerty', 'abc123']
        if any(pattern in password.lower() for pattern in common_patterns):
            errors.append("Passwort enthält häufig verwendete Muster")
        
        return errors
    
    @staticmethod
    def hash_password(password):
        """Hash password with enhanced security"""
        return generate_password_hash(password, method='pbkdf2:sha256:100000')
    
    @staticmethod
    def verify_password(password, password_hash):
        """Verify password against hash"""
        return check_password_hash(password_hash, password)


class SessionSecurity:
    """Enhanced session security"""
    
    @staticmethod
    def generate_csrf_token():
        """Generate CSRF token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def generate_session_id():
        """Generate secure session ID"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def is_session_expired(session_time, max_age_hours=8):
        """Check if session is expired"""
        if not session_time:
            return True
        
        if isinstance(session_time, str):
            session_time = datetime.fromisoformat(session_time)
        
        expiry_time = session_time + timedelta(hours=max_age_hours)
        return datetime.now(timezone.utc) > expiry_time


class DataSanitizer:
    """Data sanitization and validation"""
    
    @staticmethod
    def sanitize_input(data):
        """Sanitize user input"""
        if not data:
            return data
        
        # Remove potential XSS characters
        dangerous_chars = ['<', '>', '"', "'", '&', 'javascript:', 'data:', 'vbscript:']
        sanitized = str(data)
        
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        return sanitized.strip()
    
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_username(username):
        """Validate username format"""
        import re
        # Allow alphanumeric, underscore, hyphen
        pattern = r'^[a-zA-Z0-9_-]{3,30}$'
        return re.match(pattern, username) is not None


class AuditLogger:
    """Security audit logging"""
    
    def __init__(self):
        self.logger = logging.getLogger('security_audit')
        
        # Create security log handler
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        handler = logging.FileHandler('logs/security_audit.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def log_login_attempt(self, username, ip_address, success=True, reason=None):
        """Log login attempts"""
        status = "SUCCESS" if success else "FAILED"
        message = f"LOGIN {status} - User: {username}, IP: {ip_address}"
        if reason:
            message += f", Reason: {reason}"
        
        if success:
            self.logger.info(message)
        else:
            self.logger.warning(message)
    
    def log_password_change(self, username, ip_address):
        """Log password changes"""
        message = f"PASSWORD CHANGE - User: {username}, IP: {ip_address}"
        self.logger.info(message)
    
    def log_admin_action(self, admin_user, action, target=None, ip_address=None):
        """Log administrative actions"""
        message = f"ADMIN ACTION - Admin: {admin_user}, Action: {action}"
        if target:
            message += f", Target: {target}"
        if ip_address:
            message += f", IP: {ip_address}"
        
        self.logger.info(message)
    
    def log_security_event(self, event_type, details, severity="INFO"):
        """Log general security events"""
        message = f"SECURITY EVENT - Type: {event_type}, Details: {details}"
        
        if severity == "WARNING":
            self.logger.warning(message)
        elif severity == "ERROR":
            self.logger.error(message)
        else:
            self.logger.info(message)


# Global instances
security_manager = SecurityManager()
password_security = PasswordSecurity()
session_security = SessionSecurity()
data_sanitizer = DataSanitizer()
audit_logger = AuditLogger()
