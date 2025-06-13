"""
Formulare für Authentifizierung
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models.user import User


class LoginForm(FlaskForm):
    """Login-Formular"""
    username = StringField('Benutzername', validators=[DataRequired()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    remember_me = BooleanField('Angemeldet bleiben')
    submit = SubmitField('Anmelden')

class RegistrationForm(FlaskForm):
    """Registrierungsformular (nur für Admins)"""
    username = StringField('Benutzername', validators=[
        DataRequired(), 
        Length(min=3, max=20, message='Benutzername muss zwischen 3 und 20 Zeichen lang sein')
    ])
    email = StringField('E-Mail', validators=[DataRequired(), Email()])
    vorname = StringField('Vorname', validators=[
        Length(max=64, message='Vorname darf maximal 64 Zeichen lang sein')
    ])
    nachname = StringField('Nachname', validators=[
        Length(max=64, message='Nachname darf maximal 64 Zeichen lang sein')
    ])
    password = PasswordField('Passwort', validators=[
        DataRequired(),
        Length(min=6, message='Passwort muss mindestens 6 Zeichen lang sein')
    ])
    password2 = PasswordField('Passwort wiederholen', validators=[
        DataRequired(), 
        EqualTo('password', message='Passwörter müssen übereinstimmen')
    ])
    role = SelectField('Rolle', choices=[
        ('mitarbeiter', 'Mitarbeiter'),
        ('bauleiter', 'Bauleiter'),
        ('admin', 'Administrator')
    ], default='mitarbeiter')
    submit = SubmitField('Benutzer erstellen')
    
    def validate_username(self, username):
        """Prüft ob Benutzername bereits existiert."""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Benutzername bereits vergeben.')
    
    def validate_email(self, email):
        """Prüft ob E-Mail bereits existiert."""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('E-Mail-Adresse bereits vergeben.')

class PasswordChangeForm(FlaskForm):
    """Passwort ändern"""
    current_password = PasswordField('Aktuelles Passwort', validators=[DataRequired()])
    new_password = PasswordField('Neues Passwort', validators=[
        DataRequired(),
        Length(min=6, message='Passwort muss mindestens 6 Zeichen lang sein')
    ])
    new_password2 = PasswordField('Neues Passwort wiederholen', validators=[
        DataRequired(),
        EqualTo('new_password', message='Passwörter müssen übereinstimmen')
    ])
    submit = SubmitField('Passwort ändern')
