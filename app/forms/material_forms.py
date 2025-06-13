"""
Formulare für Materialverwaltung
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, ValidationError
from app.models.material import Material


class MaterialForm(FlaskForm):
    """Formular für Material hinzufügen/bearbeiten"""
    
    name = StringField(
        'Material-/Leistungsname',
        validators=[
            DataRequired(message='Name ist erforderlich.'),
            Length(min=2, max=255, message='Name muss zwischen 2 und 255 Zeichen lang sein.')
        ],
        render_kw={'class': 'form-control', 'placeholder': 'z.B. Mauerwerk, Putz, Elektrische Installation'}
    )
    
    kategorie = StringField(
        'Kategorie (optional)',
        validators=[Optional(), Length(max=100)],
        render_kw={'class': 'form-control', 'placeholder': 'z.B. Rohbau, Ausbau, Haustechnik'}
    )
    
    beschreibung = TextAreaField(
        'Beschreibung (optional)',
        validators=[Optional(), Length(max=500)],
        render_kw={'class': 'form-control', 'rows': '3', 'placeholder': 'Zusätzliche Informationen zum Material...'}
    )
    
    einheit = StringField(
        'Standard-Einheit',
        validators=[Optional(), Length(max=50)],
        default='Stück',
        render_kw={'class': 'form-control', 'placeholder': 'z.B. m², m³, Stk, m, kg'}
    )
    
    ist_aktiv = BooleanField(
        'Material ist aktiv',
        default=True,
        render_kw={'class': 'form-check-input'}
    )
    
    submit = SubmitField(
        'Material speichern',
        render_kw={'class': 'btn btn-success'}
    )
    
    def __init__(self, material=None, *args, **kwargs):
        super(MaterialForm, self).__init__(*args, **kwargs)
        self.material = material
    
    def validate_name(self, name):
        """Prüft ob Materialname bereits existiert (außer bei Bearbeitung)"""
        existing = Material.query.filter_by(name=name.data).first()
        if existing and (not self.material or existing.id != self.material.id):
            raise ValidationError('Ein Material mit diesem Namen existiert bereits.')


class BulkMaterialForm(FlaskForm):
    """Formular für Bulk-Import von Materialien"""
    
    materials_text = TextAreaField(
        'Materialien (ein Material pro Zeile)',
        validators=[
            DataRequired(message='Bitte geben Sie mindestens ein Material ein.'),
            Length(min=1, max=10000, message='Text zu lang.')
        ],
        render_kw={
            'class': 'form-control',
            'rows': '10',
            'placeholder': 'Format: Name|Kategorie|Einheit\n\nBeispiel:\nMauerwerk 24cm|Rohbau|m²\nPutz innen|Ausbau|m²\nElektrische Installation|Haustechnik|Stk'
        }
    )
    
    default_kategorie = StringField(
        'Standard-Kategorie (optional)',
        validators=[Optional(), Length(max=100)],
        render_kw={'class': 'form-control', 'placeholder': 'Wird verwendet wenn keine Kategorie angegeben'}
    )
    
    default_einheit = StringField(
        'Standard-Einheit',
        validators=[Optional(), Length(max=50)],
        default='Stück',
        render_kw={'class': 'form-control', 'placeholder': 'Wird verwendet wenn keine Einheit angegeben'}
    )
    
    submit = SubmitField(
        'Materialien importieren',
        render_kw={'class': 'btn btn-primary'}
    )


class MaterialSearchForm(FlaskForm):
    """Such- und Filterformular für Materialübersicht"""
    
    search = StringField(
        'Suche',
        validators=[Optional()],
        render_kw={'class': 'form-control', 'placeholder': 'Suche nach Name oder Beschreibung...'}
    )
    
    category = SelectField(
        'Kategorie',
        validators=[Optional()],
        render_kw={'class': 'form-select'}
    )
    
    status = SelectField(
        'Status',
        choices=[
            ('', 'Alle'),
            ('active', 'Nur aktive'),
            ('inactive', 'Nur inaktive')
        ],
        validators=[Optional()],
        render_kw={'class': 'form-select'}
    )
    
    submit = SubmitField(
        'Filtern',
        render_kw={'class': 'btn btn-outline-primary'}
    )
    
    def __init__(self, *args, **kwargs):
        super(MaterialSearchForm, self).__init__(*args, **kwargs)
        
        # Kategorien für Filter laden
        kategorien = Material.query.with_entities(Material.kategorie).distinct().filter(
            Material.kategorie.isnot(None)
        ).order_by(Material.kategorie).all()
        
        self.category.choices = [('', 'Alle Kategorien')]
        self.category.choices.extend([(k.kategorie, k.kategorie) for k in kategorien if k.kategorie])
