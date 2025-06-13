from app import db
from datetime import datetime, timezone
from sqlalchemy import event, Index
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

# KEIN IMPORT von AufmassEntry hier - verhindert zirkulären Import


class Bautagebuch(db.Model):
    """Haupt-Bautagebuch Klasse"""
    __tablename__ = 'bautagebuch'

    id = Column(Integer, primary_key=True)
    projekt_name = Column(String(200), nullable=False, index=True)
    projekt_nummer = Column(String(100), nullable=True, index=True)
    bauleiter = Column(String(100), nullable=False)
    erstellt_am = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    aktualisiert_am = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Audit-Trail
    created_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    updated_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, index=True)

    # Beziehung zu den Einträgen
    entries = relationship('BautagebuchEntry', backref='bautagebuch', lazy=True)
    creator = relationship('User', foreign_keys=[created_by])
    updater = relationship('User', foreign_keys=[updated_by])

    def __repr__(self):
        return f'<Bautagebuch {self.projekt_name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'projekt_name': self.projekt_name,
            'projekt_nummer': self.projekt_nummer,
            'bauleiter': self.bauleiter,
            'erstellt_am': self.erstellt_am.isoformat() if self.erstellt_am else None,
            'aktualisiert_am': self.aktualisiert_am.isoformat() if self.aktualisiert_am else None
        }


class BautagebuchEntry(db.Model):
    """Einträge im Bautagebuch"""
    __tablename__ = 'bautagebuch_entries'

    id = Column(Integer, primary_key=True)
    bautagebuch_id = Column(Integer, ForeignKey('bautagebuch.id'), nullable=True)
    aufmass_entry_id = Column(Integer, ForeignKey('aufmass_entries.id'), nullable=True)
    text = Column(Text, nullable=False)
    datum = Column(Date, nullable=False)
    kalenderwoche = Column(Integer, nullable=False)
    jahr = Column(Integer, nullable=False)
    erstellt_am = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Beziehungen - String-Referenz statt Import
    aufmass_entry = relationship(
        'AufmassEntry',
        back_populates='bautagebuch_entries'
    )

    def __repr__(self):
        return f'<BautagebuchEntry {self.id} - KW{self.kalenderwoche}/{self.jahr}>'

    def to_dict(self):
        return {
            'id': self.id,
            'text': self.text,
            'datum': self.datum.isoformat(),
            'kalenderwoche': self.kalenderwoche,
            'jahr': self.jahr,
            'aufmass_id': self.aufmass_entry_id,
            'bautagebuch_id': self.bautagebuch_id
        }


class WochenExport(db.Model):
    """Exportierte Wochenberichte"""
    __tablename__ = 'wochen_exports'

    id = Column(Integer, primary_key=True)
    kalenderwoche = Column(Integer, nullable=False)
    jahr = Column(Integer, nullable=False)
    exportiert_am = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    exportiert_von = Column(String(100), nullable=False)
    dateiname = Column(String(200))

    def __repr__(self):
        return f'<WochenExport {self.id} - KW{self.kalenderwoche}/{self.jahr}>'

    def to_dict(self):
        return {
            'id': self.id,
            'kalenderwoche': self.kalenderwoche,
            'jahr': self.jahr,
            'exportiert_am': self.exportiert_am.isoformat(),
            'exportiert_von': self.exportiert_von,
            'dateiname': self.dateiname
        }


# Event-Listener - mit spätem Import um zirkuläre Imports zu vermeiden
@event.listens_for(db.Model, 'mapper_configured', propagate=True)
def receive_mapper_configured(mapper, cls):
    """Setup event listener after all models are configured"""
    if cls.__name__ == 'AufmassEntry':
        @event.listens_for(cls, 'after_insert')
        def create_bautagebuch_eintrag(mapper, connection, target):
            """Erstellt automatisch einen Bautagebuch-Eintrag nach dem Speichern eines Aufmaßes"""
            from datetime import date
            from sqlalchemy import text

            # Kalenderwoche berechnen
            kw = target.datum.isocalendar()[1]
            jahr = target.datum.year

            # Text generieren mit SQL-Query um Beziehungen zu laden
            user_query = text("SELECT username FROM users WHERE id = :user_id")
            material_query = text("SELECT name, einheit FROM materialien WHERE id = :material_id")
            
            user_result = connection.execute(user_query, {"user_id": target.mitarbeiter_id}).fetchone()
            material_result = connection.execute(material_query, {"material_id": target.material_id}).fetchone()
            
            if user_result and material_result:
                username = user_result[0]
                material_name = material_result[0]
                material_einheit = material_result[1]
                
                # Text generieren
                datum_str = target.datum.strftime('%d.%m.%Y')
                raum_text = f" (Raum {target.raumnummer})" if target.raumnummer else ""
                einheit_text = target.einheit or material_einheit or ''
                
                bautagebuch_text = (f"Am {datum_str} führte {username} "
                                   f"in {target.ort}{raum_text} folgende Leistung aus: "
                                   f"{material_name}, Menge: {target.menge} {einheit_text}. "
                                   f"{'Bemerkungen: ' + target.bemerkungen if target.bemerkungen else ''}")

                # Bautagebuch-Eintrag erstellen
                connection.execute(
                    BautagebuchEntry.__table__.insert().values(
                        aufmass_entry_id=target.id,
                        text=bautagebuch_text,
                        datum=target.datum.date(),
                        kalenderwoche=kw,
                        jahr=jahr
                    )
                )
