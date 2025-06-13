from app import db
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean, Index
from sqlalchemy.orm import relationship


class AufmassEntry(db.Model):
    """Aufmaß-Einträge von Mitarbeitern"""
    __tablename__ = 'aufmass_entries'

    id = Column(Integer, primary_key=True)

    # Fremdschlüssel - referenziert auf materialien Tabelle
    material_id = Column(Integer, ForeignKey('materialien.id'), nullable=False, index=True)
    mitarbeiter_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)

    # Hauptdaten
    ort = Column(String(200), nullable=False, index=True)
    raumnummer = Column(String(50), nullable=True)
    menge = Column(Float, nullable=False)
    einheit = Column(String(20), nullable=True)
    datum = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    bemerkungen = Column(Text, nullable=True)

    # Status-Felder
    is_duplicate_checked = Column(Boolean, default=False, index=True)
    is_approved = Column(Boolean, default=True, index=True)

    # Zeitstempel
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Audit-Trail
    created_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    updated_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # Soft Delete
    is_deleted = Column(Boolean, default=False, index=True)
    deleted_at = Column(DateTime, nullable=True)
    deleted_by = Column(Integer, ForeignKey('users.id'), nullable=True)

    # Beziehungen - Material kommt aus material.py
    material = relationship('Material', back_populates='aufmass_entries')
    mitarbeiter = relationship('User', back_populates='aufmass_entries', foreign_keys=[mitarbeiter_id])
    documents = relationship('AufmassDocument', back_populates='aufmass_entry', cascade='all, delete-orphan')

    # Audit-Beziehungen
    creator = relationship('User', foreign_keys=[created_by])
    updater = relationship('User', foreign_keys=[updated_by])
    deleter = relationship('User', foreign_keys=[deleted_by])

    # Bautagebuch-Beziehung
    bautagebuch_entries = relationship(
        'BautagebuchEntry',
        back_populates='aufmass_entry'
    )

    # Composite Indizes für bessere Performance
    __table_args__ = (
        Index('idx_aufmass_material_date', 'material_id', 'datum'),
        Index('idx_aufmass_mitarbeiter_date', 'mitarbeiter_id', 'datum'),
        Index('idx_aufmass_ort_date', 'ort', 'datum'),
        Index('idx_aufmass_active', 'is_deleted', 'is_approved'),
    )

    def __repr__(self):
        return f'<AufmassEntry {self.id} - {self.ort}>'

    def soft_delete(self, user_id=None):
        """Soft delete the entry."""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
        self.deleted_by = user_id
        db.session.commit()

    def restore(self):
        """Restore a soft-deleted entry."""
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
        db.session.commit()

    @classmethod
    def active(cls):
        """Query only active (non-deleted) entries."""
        return cls.query.filter_by(is_deleted=False)

    def to_dict(self):
        return {
            'id': self.id,
            'material': self.material.name if self.material else None,
            'material_id': self.material_id,
            'ort': self.ort,
            'raumnummer': self.raumnummer,
            'menge': self.menge,
            'einheit': self.einheit,
            'datum': self.datum.isoformat(),
            'mitarbeiter': self.mitarbeiter.username if self.mitarbeiter else None,
            'mitarbeiter_id': self.mitarbeiter_id,
            'bemerkungen': self.bemerkungen,
            'is_approved': self.is_approved,
            'is_duplicate_checked': self.is_duplicate_checked,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def to_bautagebuch_text(self):
        """Generiert automatischen Bautagebuch-Eintrag"""
        datum_str = self.datum.strftime('%d.%m.%Y')
        raum_text = f" (Raum {self.raumnummer})" if self.raumnummer else ""
        return (f"Am {datum_str} führte {self.mitarbeiter.username} "
                f"in {self.ort}{raum_text} folgende Leistung aus: "
                f"{self.material.name}, Menge: {self.menge} {self.einheit or self.material.einheit or ''}. "
                f"{'Bemerkungen: ' + self.bemerkungen if self.bemerkungen else ''}")

    def validate(self):
        """Validate entry data."""
        errors = []
        
        if not self.material_id:
            errors.append('Material ist erforderlich')
        
        if not self.ort or len(self.ort.strip()) < 2:
            errors.append('Ort muss mindestens 2 Zeichen lang sein')
        
        if not self.menge or self.menge <= 0:
            errors.append('Menge muss größer als 0 sein')
        
        if not self.mitarbeiter_id:
            errors.append('Mitarbeiter ist erforderlich')
        
        return errors


class AufmassDocument(db.Model):
    """Dokumente/Bilder zu Aufmaß-Einträgen"""
    __tablename__ = 'aufmass_documents'

    id = Column(Integer, primary_key=True)
    aufmass_entry_id = Column(Integer, ForeignKey('aufmass_entries.id'), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer, nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Audit-Trail
    uploaded_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # Soft Delete
    is_deleted = Column(Boolean, default=False, index=True)
    deleted_at = Column(DateTime, nullable=True)
    deleted_by = Column(Integer, ForeignKey('users.id'), nullable=True)

    # Beziehungen
    aufmass_entry = relationship('AufmassEntry', back_populates='documents')
    uploader = relationship('User', foreign_keys=[uploaded_by])
    deleter = relationship('User', foreign_keys=[deleted_by])

    def __repr__(self):
        return f'<AufmassDocument {self.id} - {self.original_filename}>'

    def soft_delete(self, user_id=None):
        """Soft delete the document."""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
        self.deleted_by = user_id
        db.session.commit()

    @classmethod
    def active(cls):
        """Query only active (non-deleted) documents."""
        return cls.query.filter_by(is_deleted=False)

    def to_dict(self):
        return {
            'id': self.id,
            'original_filename': self.original_filename,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'upload_date': self.upload_date.isoformat(),
            'uploaded_by': self.uploader.username if self.uploader else None
        }
