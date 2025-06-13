from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import SelectField, StringField, FloatField, DateTimeField, TextAreaField, SubmitField, FieldList
from wtforms.validators import DataRequired, NumberRange, Length, Optional
from wtforms.widgets import TextInput
from datetime import datetime
from app.models.material import Material  # Fixed import path


class AufmassForm(FlaskForm):
    """Hauptformular für Aufmaß-Eingabe"""

    # Was? - Dropdown für Materialien/Leistungen
    material_id = SelectField(
        'Was? (Material/Leistung)',
        coerce=int,
        validators=[DataRequired(message='Bitte wählen Sie ein Material aus.')],
        render_kw={'class': 'form-select'}
    )

    # Wo? - Ort/Raumnummer
    ort = StringField(
        'Wo? (Ort/Bereich)',
        validators=[
            DataRequired(message='Bitte geben Sie einen Ort an.'),
            Length(min=2, max=200, message='Ort muss zwischen 2 und 200 Zeichen lang sein.')
        ],
        render_kw={'class': 'form-control', 'placeholder': 'z.B. Erdgeschoss, Keller, Außenbereich'}
    )

    raumnummer = StringField(
        'Raumnummer (optional)',
        validators=[Optional(), Length(max=50)],
        render_kw={'class': 'form-control', 'placeholder': 'z.B. R001, Büro 1'}
    )

    # Wie viel? - Menge
    menge = FloatField(
        'Wie viel? (Menge)',
        validators=[
            DataRequired(message='Bitte geben Sie eine Menge an.'),
            NumberRange(min=0.01, message='Menge muss größer als 0 sein.')
        ],
        render_kw={'class': 'form-control', 'step': '0.01', 'min': '0.01'}
    )

    einheit = StringField(
        'Einheit (optional)',
        validators=[Optional(), Length(max=20)],
        render_kw={'class': 'form-control', 'placeholder': 'z.B. m², m³, Stk'}
    )

    # Wann? - Datum
    datum = DateTimeField(
        'Wann? (Datum)',
        validators=[DataRequired(message='Bitte geben Sie ein Datum an.')],
        default=datetime.now,
        format='%Y-%m-%d',
        render_kw={'class': 'form-control', 'type': 'date'}
    )

    # Zusätzliche Informationen
    bemerkungen = TextAreaField(
        'Bemerkungen (optional)',
        validators=[Optional(), Length(max=500)],
        render_kw={'class': 'form-control', 'rows': '3', 'placeholder': 'Zusätzliche Informationen...'}
    )

    # Datei-Upload (mehrere Dateien als FieldList)
    documents = FieldList(
        FileField(
            'Dokument/Bild',
            validators=[
                FileAllowed(['jpg', 'jpeg', 'png', 'pdf', 'doc', 'docx'],
                            'Nur Bilder (JPG, PNG) und Dokumente (PDF, DOC, DOCX) erlaubt!')
            ]
        ),
        min_entries=0,
        max_entries=5,
        label='Dokumente/Bilder (optional)'
    )

    submit = SubmitField(
        'Aufmaß speichern',
        render_kw={'class': 'btn btn-primary btn-lg'}
    )

    def __init__(self, *args, **kwargs):
        super(AufmassForm, self).__init__(*args, **kwargs)
        # Dropdown mit aktiven Materialien füllen
        self.material_id.choices = [
            (material.id, f"{material.name} ({material.einheit or 'Stk'})")
            for material in Material.query.filter_by(ist_aktiv=True).order_by(Material.name).all()
        ]
        self.material_id.choices.insert(0, (0, '-- Bitte wählen --'))


class MaterialForm(FlaskForm):
    """Formular für Admin - Material hinzufügen/bearbeiten"""

    name = StringField(
        'Material-/Leistungsname',
        validators=[
            DataRequired(message='Name ist erforderlich.'),
            Length(min=2, max=200, message='Name muss zwischen 2 und 200 Zeichen lang sein.')
        ],
        render_kw={'class': 'form-control'}
    )

    kategorie = StringField(
        'Kategorie (optional)',
        validators=[Optional(), Length(max=100)],
        render_kw={'class': 'form-control', 'placeholder': 'z.B. Mauerwerk, Putz, Elektrische Arbeiten'}
    )

    einheit = StringField(
        'Standard-Einheit',
        validators=[Optional(), Length(max=20)],
        render_kw={'class': 'form-control', 'placeholder': 'z.B. m², m³, Stk, m'}
    )

    submit = SubmitField(
        'Material speichern',
        render_kw={'class': 'btn btn-success'}
    )


class SearchFilterForm(FlaskForm):
    """Such- und Filterformular für Aufmaß-Übersicht"""

    search_term = StringField(
        'Suche',
        validators=[Optional()],
        render_kw={'class': 'form-control', 'placeholder': 'Suche nach Ort, Material, Mitarbeiter...'}
    )

    material_filter = SelectField(
        'Material',
        coerce=int,
        validators=[Optional()],
        render_kw={'class': 'form-select'}
    )

    datum_von = DateTimeField(
        'Von Datum',
        validators=[Optional()],
        format='%Y-%m-%d',
        render_kw={'class': 'form-control', 'type': 'date'}
    )

    datum_bis = DateTimeField(
        'Bis Datum',
        validators=[Optional()],
        format='%Y-%m-%d',
        render_kw={'class': 'form-control', 'type': 'date'}
    )

    submit = SubmitField(
        'Filtern',
        render_kw={'class': 'btn btn-outline-primary'}
    )

    def __init__(self, *args, **kwargs):
        super(SearchFilterForm, self).__init__(*args, **kwargs)
        # Material-Filter füllen
        self.material_filter.choices = [(0, 'Alle Materialien')]
        self.material_filter.choices.extend([
            (material.id, material.name)
            for material in Material.query.filter_by(ist_aktiv=True).order_by(Material.name).all()
        ])
