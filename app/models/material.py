from datetime import datetime, timezone
from app import db
from sqlalchemy import Index


class Material(db.Model):
    """Modell für Materialien/Leistungen, die im Aufmaß ausgewählt werden können"""

    __tablename__ = 'materialien'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True, index=True)
    kategorie = db.Column(db.String(100), nullable=True, index=True)
    beschreibung = db.Column(db.Text, nullable=True)
    einheit = db.Column(db.String(50), default='Stück')
    ist_aktiv = db.Column(db.Boolean, default=True, index=True)
    sortierung = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # Beziehungen - KORRIGIERT mit back_populates
    creator = db.relationship('User', foreign_keys=[created_by], backref='erstellt_materialien')
    updater = db.relationship('User', foreign_keys=[updated_by])
    aufmass_entries = db.relationship('AufmassEntry', back_populates='material', lazy='dynamic')

    # Composite Indizes für bessere Performance
    __table_args__ = (
        Index('idx_material_active_kategorie', 'ist_aktiv', 'kategorie'),
        Index('idx_material_active_name', 'ist_aktiv', 'name'),
    )

    def __repr__(self):
        return f'<Material {self.name} ({self.einheit})>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'kategorie': self.kategorie,
            'beschreibung': self.beschreibung,
            'einheit': self.einheit,
            'ist_aktiv': self.ist_aktiv,
            'sortierung': self.sortierung,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    @staticmethod
    def get_active_materials():
        """Gibt alle aktiven Materialien zurück, sortiert nach Kategorie, Sortierung und Name"""
        return Material.query.filter_by(ist_aktiv=True).order_by(
            Material.kategorie.asc(),
            Material.sortierung.asc(),
            Material.name.asc()
        ).all()

    def activate(self):
        """Aktiviert das Material."""
        self.ist_aktiv = True
        db.session.commit()

    def deactivate(self):
        """Deaktiviert das Material."""
        self.ist_aktiv = False
        db.session.commit()

    @staticmethod
    def get_materials_by_kategorie():
        """Gibt aktive Materialien gruppiert nach Kategorien zurück"""
        materials = Material.get_active_materials()
        kategorien = {}

        for material in materials:
            kategorie = material.kategorie or 'Sonstige'
            if kategorie not in kategorien:
                kategorien[kategorie] = []
            kategorien[kategorie].append(material)

        return kategorien
