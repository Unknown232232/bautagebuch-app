"""
Benutzermodell für Authentifizierung und Rechteverwaltung
Kombiniert alle Funktionen aus beiden Versionen mit erweiterten Sicherheitsfunktionen
"""
from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.utils.security import password_security, data_sanitizer, audit_logger

class User(UserMixin, db.Model):
    """Erweitertes Benutzermodell mit Rollen und Profilinformationen

    Rollen:
    - mitarbeiter: Kann Aufmaße erstellen und eigene Einträge sehen
    - bauleiter: Kann alle Aufmaße der Baustelle sehen und bearbeiten
    - admin: Vollständige Administrationsrechte
    """

    __tablename__ = 'users'

    # Basis-Authentifizierungsfelder
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    # Rollen und Status
    role = db.Column(db.String(20), nullable=False, default='mitarbeiter')
    is_active = db.Column(db.Boolean, default=True)

    # Profilinformationen
    vorname = db.Column(db.String(64))
    nachname = db.Column(db.String(64))

    # Zeitstempel
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Sicherheitsfelder für erweiterte Funktionen
    failed_login_attempts = db.Column(db.Integer, default=0)
    account_locked_until = db.Column(db.DateTime)
    password_changed_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Beziehungen (konsistent mit den anderen Modellen)
    aufmass_entries = db.relationship('AufmassEntry', back_populates='mitarbeiter', foreign_keys='AufmassEntry.mitarbeiter_id')

    # --- Erweiterte Passwort Methoden ---
    def set_password(self, password, validate_strength=True):
        """Passwort hashen und speichern mit Stärkevalidierung."""
        if validate_strength:
            errors = password_security.validate_password_strength(password)
            if errors:
                raise ValueError(f"Passwort nicht sicher genug: {', '.join(errors)}")
        
        # Verwende erweiterte Passwort-Hashing-Funktion
        self.password_hash = password_security.hash_password(password)
        self.password_changed_at = datetime.now(timezone.utc)
        
        # Reset failed login attempts
        self.failed_login_attempts = 0
        self.account_locked_until = None

    def check_password(self, password):
        """Passwort gegen Hash prüfen mit erweiterten Sicherheitsfunktionen."""
        # Prüfe ob Account gesperrt ist
        if self.is_account_locked():
            return False
        
        # Verwende erweiterte Passwort-Verifikation
        is_valid = password_security.verify_password(password, self.password_hash)
        
        if not is_valid:
            self.increment_failed_login_attempts()
        else:
            self.reset_failed_login_attempts()
        
        return is_valid

    def is_account_locked(self):
        """Prüft ob Account temporär gesperrt ist."""
        if not self.account_locked_until:
            return False
        
        if datetime.now(timezone.utc) > self.account_locked_until:
            # Sperre ist abgelaufen, zurücksetzen
            self.account_locked_until = None
            self.failed_login_attempts = 0
            db.session.commit()
            return False
        
        return True

    def increment_failed_login_attempts(self):
        """Erhöht fehlgeschlagene Login-Versuche und sperrt Account bei Bedarf."""
        from datetime import timedelta
        self.failed_login_attempts += 1
        
        # Sperre Account nach 5 fehlgeschlagenen Versuchen für 15 Minuten
        if self.failed_login_attempts >= 5:
            self.account_locked_until = datetime.now(timezone.utc) + timedelta(minutes=15)
            audit_logger.log_security_event(
                "ACCOUNT_LOCKED", 
                f"Account {self.username} locked due to failed login attempts",
                "WARNING"
            )
        
        db.session.commit()

    def reset_failed_login_attempts(self):
        """Setzt fehlgeschlagene Login-Versuche zurück."""
        self.failed_login_attempts = 0
        self.account_locked_until = None
        db.session.commit()

    def is_password_expired(self, max_age_days=90):
        """Prüft ob Passwort abgelaufen ist."""
        from datetime import timedelta
        if not self.password_changed_at:
            return True
        
        expiry_date = self.password_changed_at + timedelta(days=max_age_days)
        return datetime.now(timezone.utc) > expiry_date

    # --- Rollenprüfungen ---
    def has_role(self, required_role):
        """Prüft ob Benutzer die angegebene Rolle oder höher hat."""
        role_hierarchy = {'mitarbeiter': 1, 'bauleiter': 2, 'admin': 3}
        current_role_level = role_hierarchy.get(self.role, 0)
        required_role_level = role_hierarchy.get(required_role, 0)
        return current_role_level >= required_role_level

    def is_admin(self):
        """Prüft ob Benutzer Admin ist."""
        return self.role == 'admin'

    def is_bauleiter(self):
        """Prüft ob Benutzer Bauleiter oder Admin ist."""
        return self.has_role('bauleiter')

    def is_mitarbeiter(self):
        """Prüft ob Benutzer mindestens Mitarbeiter ist."""
        return self.has_role('mitarbeiter')

    # --- Status Methoden ---
    def update_last_login(self):
        """Aktualisiert das letzte Login-Datum."""
        self.last_login = datetime.now(timezone.utc)
        db.session.add(self)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise

    def activate(self):
        """Aktiviert den Benutzeraccount."""
        self.is_active = True
        db.session.commit()

    def deactivate(self):
        """Deaktiviert den Benutzeraccount."""
        self.is_active = False
        db.session.commit()

    # --- Serialisierung ---
    def to_dict(self):
        """Gibt Benutzerdaten als Dictionary zurück."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'vorname': self.vorname,
            'nachname': self.nachname,
            'role': self.role,
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

    def get_full_name(self):
        """Gibt den vollständigen Namen zurück."""
        return f"{self.vorname or ''} {self.nachname or ''}".strip() or self.username
    
    def __repr__(self):
        return f'<User {self.username} ({self.role})>'
