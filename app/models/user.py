"""
Vereinfachtes Benutzermodell ohne erweiterte Sicherheitsfelder
"""
from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(UserMixin, db.Model):
    """Vereinfachtes Benutzermodell mit Rollen und Profilinformationen

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
    
    # Passwort-Management
    password_change_required = db.Column(db.Boolean, default=True)  # Erster Login erfordert Passwort-Änderung
    password_changed_at = db.Column(db.DateTime)

    # Beziehungen (konsistent mit den anderen Modellen)
    aufmass_entries = db.relationship('AufmassEntry', back_populates='mitarbeiter', foreign_keys='AufmassEntry.mitarbeiter_id')

    # --- Passwort Methoden ---
    def set_password(self, password):
        """Passwort hashen und speichern."""
        self.password_hash = generate_password_hash(password)
        self.password_changed_at = datetime.now(timezone.utc)
        self.password_change_required = False

    def check_password(self, password):
        """Passwort gegen Hash prüfen."""
        return check_password_hash(self.password_hash, password)
    
    def requires_password_change(self):
        """Prüft ob Benutzer sein Passwort ändern muss."""
        return self.password_change_required

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
