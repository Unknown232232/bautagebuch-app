"""
Formulare für Kabel-Kategorie-Verwaltung
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length, Optional, ValidationError
from app.models.kabel_kategorie import KabelKategorie, Kabeltyp


class KabelKategorieForm(FlaskForm):
    """Formular für Kabel-Kategorie hinzufügen/bearbeiten"""
    
    name = StringField(
        'Kategorie-Name',
        validators=[
            DataRequired(message='Name ist erforderlich.'),
            Length(min=2, max=100, message='Name muss zwischen 2 und 100 Zeichen lang sein.')
        ],
        render_kw={'class': 'form-control', 'placeholder': 'z.B. BMA, ELA, Netzwerk'}
    )
    
    beschreibung = TextAreaField(
        'Beschreibung (optional)',
        validators=[Optional(), Length(max=500)],
        render_kw={'class': 'form-control', 'rows': '3', 'placeholder': 'Beschreibung der Kabel-Kategorie...'}
    )
    
    ist_aktiv = BooleanField(
        'Kategorie ist aktiv',
        default=True,
        render_kw={'class': 'form-check-input'}
    )
    
    submit = SubmitField(
        'Kategorie speichern',
        render_kw={'class': 'btn btn-success'}
    )
    
    def __init__(self, kategorie=None, *args, **kwargs):
        super(KabelKategorieForm, self).__init__(*args, **kwargs)
        self.kategorie = kategorie
    
    def validate_name(self, name):
        """Prüft ob Kategorie-Name bereits existiert (außer bei Bearbeitung)"""
        existing = KabelKategorie.query.filter_by(name=name.data).first()
        if existing and (not self.kategorie or existing.id != self.kategorie.id):
            raise ValidationError('Eine Kategorie mit diesem Namen existiert bereits.')


class KabeltypForm(FlaskForm):
    """Formular für Kabeltyp hinzufügen/bearbeiten"""
    
    name = StringField(
        'Kabeltyp-Name',
        validators=[
            DataRequired(message='Name ist erforderlich.'),
            Length(min=2, max=255, message='Name muss zwischen 2 und 255 Zeichen lang sein.')
        ],
        render_kw={'class': 'form-control', 'placeholder': 'z.B. Alu Rohr, 2x2x0,8 E30 Kabel'}
    )
    
    kategorie_id = SelectField(
        'Kategorie',
        validators=[DataRequired(message='Kategorie ist erforderlich.')],
        coerce=int,
        render_kw={'class': 'form-select'}
    )
    
    beschreibung = TextAreaField(
        'Beschreibung (optional)',
        validators=[Optional(), Length(max=500)],
        render_kw={'class': 'form-control', 'rows': '3', 'placeholder': 'Beschreibung des Kabeltyps...'}
    )
    
    technische_daten = TextAreaField(
        'Technische Daten (optional)',
        validators=[Optional(), Length(max=1000)],
        render_kw={'class': 'form-control', 'rows': '4', 'placeholder': 'Technische Eigenschaften, Spezifikationen...'}
    )
    
    ist_aktiv = BooleanField(
        'Kabeltyp ist aktiv',
        default=True,
        render_kw={'class': 'form-check-input'}
    )
    
    submit = SubmitField(
        'Kabeltyp speichern',
        render_kw={'class': 'btn btn-success'}
    )
    
    def __init__(self, kabeltyp=None, *args, **kwargs):
        super(KabeltypForm, self).__init__(*args, **kwargs)
        self.kabeltyp = kabeltyp
        
        # Kategorien für Auswahl laden
        kategorien = KabelKategorie.query.filter_by(ist_aktiv=True).order_by(KabelKategorie.name).all()
        self.kategorie_id.choices = [(k.id, k.name) for k in kategorien]
    
    def validate_name(self, name):
        """Prüft ob Kabeltyp-Name in der gewählten Kategorie bereits existiert"""
        if self.kategorie_id.data:
            existing = Kabeltyp.query.filter_by(
                name=name.data,
                kategorie_id=self.kategorie_id.data
            ).first()
            
            if existing and (not self.kabeltyp or existing.id != self.kabeltyp.id):
                kategorie = KabelKategorie.query.get(self.kategorie_id.data)
                kategorie_name = kategorie.name if kategorie else "dieser Kategorie"
                raise ValidationError(f'Ein Kabeltyp mit diesem Namen existiert bereits in {kategorie_name}.')


class BulkKabeltypForm(FlaskForm):
    """Formular für Bulk-Import von Kabeltypen"""
    
    kategorie_id = SelectField(
        'Ziel-Kategorie',
        validators=[DataRequired(message='Kategorie ist erforderlich.')],
        coerce=int,
        render_kw={'class': 'form-select'}
    )
    
    kabeltypen_text = TextAreaField(
        'Kabeltypen (ein Kabeltyp pro Zeile)',
        validators=[
            DataRequired(message='Bitte geben Sie mindestens einen Kabeltyp ein.'),
            Length(min=1, max=10000, message='Text zu lang.')
        ],
        render_kw={
            'class': 'form-control',
            'rows': '10',
            'placeholder': 'Ein Kabeltyp pro Zeile:\n\nAlu Rohr\n2x2x0,8 E30 Kabel\n2x2x0,8 Kabel rot\n4x2x0,6 Grau'
        }
    )
    
    submit = SubmitField(
        'Kabeltypen importieren',
        render_kw={'class': 'btn btn-primary'}
    )
    
    def __init__(self, *args, **kwargs):
        super(BulkKabeltypForm, self).__init__(*args, **kwargs)
        
        # Kategorien für Auswahl laden
        kategorien = KabelKategorie.query.filter_by(ist_aktiv=True).order_by(KabelKategorie.name).all()
        self.kategorie_id.choices = [(k.id, k.name) for k in kategorien]


class KabelSuchForm(FlaskForm):
    """Such- und Filterformular für Kabel-Übersicht"""
    
    search = StringField(
        'Suche',
        validators=[Optional()],
        render_kw={'class': 'form-control', 'placeholder': 'Suche nach Kabeltyp...'}
    )
    
    kategorie = SelectField(
        'Kategorie',
        validators=[Optional()],
        render_kw={'class': 'form-select'}
    )
    
    submit = SubmitField(
        'Suchen',
        render_kw={'class': 'btn btn-outline-primary'}
    )
    
    def __init__(self, *args, **kwargs):
        super(KabelSuchForm, self).__init__(*args, **kwargs)
        
        # Kategorien für Filter laden
        kategorien = KabelKategorie.query.filter_by(ist_aktiv=True).order_by(KabelKategorie.name).all()
        
        self.kategorie.choices = [('', 'Alle Kategorien')]
        self.kategorie.choices.extend([(k.name, k.name) for k in kategorien])


class QuickKabeltypForm(FlaskForm):
    """Schnell-Formular für Kabeltyp hinzufügen (AJAX)"""
    
    kategorie_name = StringField(
        'Kategorie',
        validators=[DataRequired(message='Kategorie ist erforderlich.')],
        render_kw={'class': 'form-control', 'placeholder': 'z.B. BMA, ELA'}
    )
    
    kabeltyp_name = StringField(
        'Kabeltyp',
        validators=[
            DataRequired(message='Kabeltyp ist erforderlich.'),
            Length(min=2, max=255)
        ],
        render_kw={'class': 'form-control', 'placeholder': 'z.B. Alu Rohr'}
    )
    
    submit = SubmitField(
        'Hinzufügen',
        render_kw={'class': 'btn btn-success btn-sm'}
    )
