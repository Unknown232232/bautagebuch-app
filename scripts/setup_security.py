#!/usr/bin/env python3
"""
Sicherheits-Setup-Skript für Bautagebuch App
Initialisiert alle Sicherheitsfunktionen und erstellt notwendige Verzeichnisse
"""

import os
import sys
import secrets
import logging
from pathlib import Path
from cryptography.fernet import Fernet

def setup_logging():
    """Setup logging for the setup script"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def create_directories():
    """Create necessary directories for security features"""
    directories = [
        'instance',
        'logs',
        'backups'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        logger.info(f"Created directory: {directory}")

def generate_secret_key():
    """Generate a secure secret key for Flask"""
    return secrets.token_urlsafe(32)

def generate_encryption_key():
    """Generate encryption key for sensitive data"""
    key_file = Path('instance/encryption.key')
    
    if key_file.exists():
        logger.warning("Encryption key already exists. Skipping generation.")
        return
    
    # Generate new encryption key
    key = Fernet.generate_key()
    
    # Write key to file
    with open(key_file, 'wb') as f:
        f.write(key)
    
    # Set restrictive permissions (Unix/Linux only)
    if os.name != 'nt':  # Not Windows
        os.chmod(key_file, 0o600)
    
    logger.info(f"Generated encryption key: {key_file}")

def create_env_file():
    """Create .env file with secure defaults if it doesn't exist"""
    env_file = Path('.env')
    
    if env_file.exists():
        logger.warning(".env file already exists. Skipping creation.")
        return
    
    # Generate secure values
    secret_key = generate_secret_key()
    
    env_content = f"""# =============================================================================
# Bautagebuch App - Environment Variables
# =============================================================================
# Generated by setup_security.py on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# =============================================================================
# Application Settings
# =============================================================================
FLASK_ENV=development
SECRET_KEY={secret_key}
HOST=127.0.0.1
PORT=5000

# =============================================================================
# Database Configuration
# =============================================================================
DATABASE_URL=sqlite:///bautagebuch.db

# =============================================================================
# Security Settings
# =============================================================================
SESSION_COOKIE_SECURE=false
WTF_CSRF_ENABLED=true

# Enhanced Security Settings
ENCRYPTION_KEY_FILE=instance/encryption.key
PASSWORD_MIN_LENGTH=8
PASSWORD_MAX_AGE_DAYS=90
ACCOUNT_LOCKOUT_ATTEMPTS=5
ACCOUNT_LOCKOUT_DURATION=15

# =============================================================================
# Logging
# =============================================================================
LOG_LEVEL=INFO
LOG_FILE=logs/bautagebuch.log

# =============================================================================
# Rate Limiting
# =============================================================================
RATELIMIT_DEFAULT=100 per hour

# =============================================================================
# Admin Settings
# =============================================================================
ADMIN_EMAIL=admin@localhost
DEFAULT_ADMIN_PASSWORD=ChangeMe123!
"""
    
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    logger.info(f"Created .env file: {env_file}")
    logger.warning("Please review and update the .env file with your specific settings!")

def setup_gitignore():
    """Ensure security-sensitive files are in .gitignore"""
    gitignore_file = Path('.gitignore')
    
    security_entries = [
        '# Security files',
        '.env',
        'instance/encryption.key',
        'logs/*.log',
        'instance/uploads/*',
        '*.key',
        '*.pem'
    ]
    
    if gitignore_file.exists():
        with open(gitignore_file, 'r') as f:
            existing_content = f.read()
        
        # Add missing entries
        missing_entries = []
        for entry in security_entries:
            if entry not in existing_content:
                missing_entries.append(entry)
        
        if missing_entries:
            with open(gitignore_file, 'a') as f:
                f.write('\n\n# Added by setup_security.py\n')
                f.write('\n'.join(missing_entries))
            logger.info(f"Updated .gitignore with {len(missing_entries)} security entries")
    else:
        with open(gitignore_file, 'w') as f:
            f.write('\n'.join(security_entries))
        logger.info("Created .gitignore with security entries")

def check_dependencies():
    """Check if required security dependencies are installed"""
    required_packages = [
        'cryptography',
        'flask-talisman',
        'flask-limiter',
        'bcrypt'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"Missing required packages: {', '.join(missing_packages)}")
        logger.info("Install missing packages with: pip install " + ' '.join(missing_packages))
        return False
    
    logger.info("All required security dependencies are installed")
    return True

def create_security_checklist():
    """Create a security checklist for manual review"""
    checklist_content = """# Sicherheits-Checkliste für Bautagebuch App

## Vor der Produktionsbereitstellung

### Konfiguration
- [ ] .env Datei mit produktionsspezifischen Werten aktualisiert
- [ ] SECRET_KEY durch sicheren, zufälligen Wert ersetzt
- [ ] DATABASE_URL für Produktionsdatenbank konfiguriert
- [ ] SESSION_COOKIE_SECURE=true für HTTPS gesetzt
- [ ] Starke Admin-Passwörter gesetzt

### Sicherheit
- [ ] Verschlüsselungsschlüssel generiert und sicher gespeichert
- [ ] HTTPS-Zertifikat installiert und konfiguriert
- [ ] Firewall-Regeln konfiguriert
- [ ] Backup-Strategie implementiert
- [ ] Monitoring und Logging aktiviert

### Benutzerkonten
- [ ] Standard-Admin-Passwort geändert
- [ ] Benutzerrollen und -berechtigungen überprüft
- [ ] Passwort-Richtlinien kommuniziert

### Tests
- [ ] Sicherheitstests durchgeführt
- [ ] Penetrationstests abgeschlossen
- [ ] Vulnerability-Scans durchgeführt
- [ ] Backup-Wiederherstellung getestet

### Dokumentation
- [ ] Sicherheitsdokumentation aktualisiert
- [ ] Incident-Response-Plan erstellt
- [ ] Benutzerhandbuch mit Sicherheitsrichtlinien

### Compliance
- [ ] DSGVO-Compliance überprüft
- [ ] Datenschutzerklärung aktualisiert
- [ ] Audit-Logs konfiguriert

## Nach der Bereitstellung

### Überwachung
- [ ] Sicherheitslogs regelmäßig überprüfen
- [ ] Failed-Login-Attempts monitoren
- [ ] Performance-Metriken überwachen
- [ ] Automatische Benachrichtigungen einrichten

### Wartung
- [ ] Regelmäßige Sicherheitsupdates
- [ ] Passwort-Rotation durchführen
- [ ] Verschlüsselungsschlüssel rotieren
- [ ] Backup-Integrität prüfen

### Schulung
- [ ] Benutzer über Sicherheitsrichtlinien informieren
- [ ] Admin-Team in Sicherheitsverfahren schulen
- [ ] Incident-Response-Verfahren testen
"""
    
    with open('SECURITY_CHECKLIST.md', 'w') as f:
        f.write(checklist_content)
    
    logger.info("Created security checklist: SECURITY_CHECKLIST.md")

def main():
    """Main setup function"""
    global logger
    logger = setup_logging()
    
    logger.info("Starting security setup for Bautagebuch App...")
    
    # Check dependencies first
    if not check_dependencies():
        logger.error("Please install missing dependencies before continuing")
        sys.exit(1)
    
    # Create necessary directories
    create_directories()
    
    # Generate encryption key
    generate_encryption_key()
    
    # Create .env file if it doesn't exist
    create_env_file()
    
    # Setup .gitignore
    setup_gitignore()
    
    # Create security checklist
    create_security_checklist()
    
    logger.info("Security setup completed successfully!")
    logger.info("Next steps:")
    logger.info("1. Review and update the .env file with your specific settings")
    logger.info("2. Run database migrations: flask db upgrade")
    logger.info("3. Create an admin user: python create_admin.py")
    logger.info("4. Review the security checklist: SECURITY_CHECKLIST.md")
    logger.info("5. Read the security documentation: docs/SECURITY.md")

if __name__ == '__main__':
    from datetime import datetime
    main()
