"""
Modell für Kabel-Kategorien-Verwaltung
"""
from datetime import datetime, timezone
from app import db
from sqlalchemy import Index


class KabelKategorie(db.Model):
    """Modell für Kabel-Kategorien (z.B. BMA, ELA)"""
    
    __tablename__ = 'kabel_kategorien'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True, index=True)
    beschreibung = db.Column(db.Text, nullable=True)
    ist_aktiv = db.Column(db.Boolean, default=True, index=True)
    sortierung = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Beziehung zu Kabeltypen
    kabeltypen = db.relationship('Kabeltyp', back_populates='kategorie', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<KabelKategorie {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'beschreibung': self.beschreibung,
            'ist_aktiv': self.ist_aktiv,
            'sortierung': self.sortierung,
            'kabeltypen_count': self.kabeltypen.count(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @staticmethod
    def get_active_kategorien():
        """Gibt alle aktiven Kategorien zurück, sortiert nach Sortierung und Name"""
        return KabelKategorie.query.filter_by(ist_aktiv=True).order_by(
            KabelKategorie.sortierung.asc(),
            KabelKategorie.name.asc()
        ).all()
    
    def get_kabeltypen(self):
        """Gibt alle aktiven Kabeltypen dieser Kategorie zurück"""
        return self.kabeltypen.filter_by(ist_aktiv=True).order_by(
            Kabeltyp.sortierung.asc(),
            Kabeltyp.name.asc()
        ).all()


class Kabeltyp(db.Model):
    """Modell für Kabeltypen innerhalb einer Kategorie"""
    
    __tablename__ = 'kabeltypen'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, index=True)
    kategorie_id = db.Column(db.Integer, db.ForeignKey('kabel_kategorien.id'), nullable=False)
    beschreibung = db.Column(db.Text, nullable=True)
    technische_daten = db.Column(db.Text, nullable=True)  # JSON-String für technische Eigenschaften
    ist_aktiv = db.Column(db.Boolean, default=True, index=True)
    sortierung = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Beziehung zur Kategorie
    kategorie = db.relationship('KabelKategorie', back_populates='kabeltypen')
    
    # Composite Index für bessere Performance
    __table_args__ = (
        Index('idx_kabeltyp_kategorie_aktiv', 'kategorie_id', 'ist_aktiv'),
        Index('idx_kabeltyp_name_aktiv', 'name', 'ist_aktiv'),
    )
    
    def __repr__(self):
        return f'<Kabeltyp {self.name} ({self.kategorie.name if self.kategorie else "Keine Kategorie"})>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'kategorie_id': self.kategorie_id,
            'kategorie_name': self.kategorie.name if self.kategorie else None,
            'beschreibung': self.beschreibung,
            'technische_daten': self.technische_daten,
            'ist_aktiv': self.ist_aktiv,
            'sortierung': self.sortierung,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class KabelKategorieService:
    """Service-Klasse für Kabel-Kategorie-Verwaltung"""
    
    @staticmethod
    def get_kabeltypen_by_kategorie(kategorie_name):
        """
        Gibt alle Kabeltypen einer bestimmten Kategorie zurück
        
        Args:
            kategorie_name (str): Name der Kategorie (z.B. "BMA", "ELA")
            
        Returns:
            dict: {'success': bool, 'kabeltypen': list, 'error': str}
        """
        try:
            kategorie = KabelKategorie.query.filter_by(
                name=kategorie_name,
                ist_aktiv=True
            ).first()
            
            if not kategorie:
                return {
                    'success': False,
                    'kabeltypen': [],
                    'error': f'Kategorie "{kategorie_name}" nicht gefunden'
                }
            
            kabeltypen = kategorie.get_kabeltypen()
            
            return {
                'success': True,
                'kabeltypen': [kabel.to_dict() for kabel in kabeltypen],
                'error': None
            }
            
        except Exception as e:
            return {
                'success': False,
                'kabeltypen': [],
                'error': f'Fehler beim Laden der Kabeltypen: {str(e)}'
            }
    
    @staticmethod
    def get_all_kategorien():
        """
        Gibt alle verfügbaren Kategorien zurück
        
        Returns:
            dict: {'success': bool, 'kategorien': list, 'error': str}
        """
        try:
            kategorien = KabelKategorie.get_active_kategorien()
            
            return {
                'success': True,
                'kategorien': [kat.to_dict() for kat in kategorien],
                'error': None
            }
            
        except Exception as e:
            return {
                'success': False,
                'kategorien': [],
                'error': f'Fehler beim Laden der Kategorien: {str(e)}'
            }
    
    @staticmethod
    def search_kabeltypen(suchbegriff):
        """
        Sucht nach Kabeltypen über alle Kategorien hinweg
        
        Args:
            suchbegriff (str): Suchbegriff für Kabeltyp-Namen
            
        Returns:
            dict: {'success': bool, 'ergebnisse': list, 'error': str}
        """
        try:
            if not suchbegriff or len(suchbegriff.strip()) < 2:
                return {
                    'success': False,
                    'ergebnisse': [],
                    'error': 'Suchbegriff muss mindestens 2 Zeichen lang sein'
                }
            
            kabeltypen = Kabeltyp.query.join(KabelKategorie).filter(
                Kabeltyp.ist_aktiv == True,
                KabelKategorie.ist_aktiv == True,
                Kabeltyp.name.ilike(f'%{suchbegriff.strip()}%')
            ).order_by(
                KabelKategorie.name.asc(),
                Kabeltyp.name.asc()
            ).all()
            
            ergebnisse = []
            for kabel in kabeltypen:
                ergebnisse.append({
                    'kabeltyp': kabel.to_dict(),
                    'kategorie': kabel.kategorie.name
                })
            
            return {
                'success': True,
                'ergebnisse': ergebnisse,
                'error': None
            }
            
        except Exception as e:
            return {
                'success': False,
                'ergebnisse': [],
                'error': f'Fehler bei der Suche: {str(e)}'
            }
    
    @staticmethod
    def add_kategorie(name, beschreibung=None):
        """
        Fügt eine neue Kategorie hinzu
        
        Args:
            name (str): Name der Kategorie
            beschreibung (str, optional): Beschreibung der Kategorie
            
        Returns:
            dict: {'success': bool, 'kategorie': dict, 'error': str}
        """
        try:
            # Prüfen ob Kategorie bereits existiert
            existing = KabelKategorie.query.filter_by(name=name).first()
            if existing:
                return {
                    'success': False,
                    'kategorie': None,
                    'error': f'Kategorie "{name}" existiert bereits'
                }
            
            kategorie = KabelKategorie(
                name=name,
                beschreibung=beschreibung
            )
            
            db.session.add(kategorie)
            db.session.commit()
            
            return {
                'success': True,
                'kategorie': kategorie.to_dict(),
                'error': None
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'kategorie': None,
                'error': f'Fehler beim Hinzufügen der Kategorie: {str(e)}'
            }
    
    @staticmethod
    def add_kabeltyp(kategorie_name, kabeltyp_name, beschreibung=None, technische_daten=None):
        """
        Fügt einen neuen Kabeltyp zu einer Kategorie hinzu
        
        Args:
            kategorie_name (str): Name der Kategorie
            kabeltyp_name (str): Name des Kabeltyps
            beschreibung (str, optional): Beschreibung des Kabeltyps
            technische_daten (str, optional): Technische Daten als JSON-String
            
        Returns:
            dict: {'success': bool, 'kabeltyp': dict, 'error': str}
        """
        try:
            # Kategorie finden
            kategorie = KabelKategorie.query.filter_by(
                name=kategorie_name,
                ist_aktiv=True
            ).first()
            
            if not kategorie:
                return {
                    'success': False,
                    'kabeltyp': None,
                    'error': f'Kategorie "{kategorie_name}" nicht gefunden'
                }
            
            # Prüfen ob Kabeltyp in dieser Kategorie bereits existiert
            existing = Kabeltyp.query.filter_by(
                name=kabeltyp_name,
                kategorie_id=kategorie.id
            ).first()
            
            if existing:
                return {
                    'success': False,
                    'kabeltyp': None,
                    'error': f'Kabeltyp "{kabeltyp_name}" existiert bereits in Kategorie "{kategorie_name}"'
                }
            
            kabeltyp = Kabeltyp(
                name=kabeltyp_name,
                kategorie_id=kategorie.id,
                beschreibung=beschreibung,
                technische_daten=technische_daten
            )
            
            db.session.add(kabeltyp)
            db.session.commit()
            
            return {
                'success': True,
                'kabeltyp': kabeltyp.to_dict(),
                'error': None
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'kabeltyp': None,
                'error': f'Fehler beim Hinzufügen des Kabeltyps: {str(e)}'
            }
