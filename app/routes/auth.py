"""
Vereinfachte Authentifizierungs-Routen
"""
import logging
from datetime import datetime, timezone
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, current_user, login_required
from urllib.parse import urlparse
from app import db, limiter
from app.models.user import User
from app.forms.auth import LoginForm, RegistrationForm, PasswordChangeForm

bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)


@bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login():
    """Login-Seite"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(form.password.data) and user.is_active:
            # Successful login
            login_user(user, remember=form.remember_me.data)
            user.update_last_login()
            
            # Prüfen ob Passwort geändert werden muss
            if user.requires_password_change():
                flash('Sie müssen Ihr Passwort beim ersten Login ändern.', 'warning')
                return redirect(url_for('auth.change_password'))
            
            # Redirect to intended page or dashboard
            next_page = request.args.get('next')
            if not next_page or urlparse(next_page).netloc != '':
                next_page = url_for('dashboard.index')
            
            flash(f'Willkommen zurück, {user.username}!', 'success')
            return redirect(next_page)
        else:
            flash('Ungültiger Benutzername oder Passwort', 'error')
    
    return render_template('auth/login.html', title='Anmelden', form=form)


@bp.route('/logout')
@login_required
def logout():
    """Logout"""
    username = current_user.username
    logger.info(f"User logout: {username}")
    logout_user()
    session.clear()
    flash(f'Auf Wiedersehen, {username}!', 'info')
    return redirect(url_for('auth.login'))


@bp.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    """Registrierung neuer Benutzer (nur für Admins)"""
    if not current_user.is_admin():
        flash('Keine Berechtigung für diese Aktion.', 'error')
        return redirect(url_for('dashboard.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            user = User(
                username=form.username.data.strip(),
                email=form.email.data.strip(),
                role=form.role.data,
                vorname=form.vorname.data.strip() if form.vorname.data else None,
                nachname=form.nachname.data.strip() if form.nachname.data else None
            )
            user.set_password(form.password.data)
            
            db.session.add(user)
            db.session.commit()
            
            flash(f'Benutzer {user.username} wurde erfolgreich erstellt.', 'success')
            return redirect(url_for('admin.users'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating user: {e}")
            flash('Fehler beim Erstellen des Benutzers.', 'error')
    
    return render_template('auth/register.html', title='Benutzer erstellen', form=form)


@bp.route('/change-password', methods=['GET', 'POST'])
@login_required
@limiter.limit("5 per minute")
def change_password():
    """Passwort ändern"""
    form = PasswordChangeForm()
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            try:
                current_user.set_password(form.new_password.data)
                db.session.commit()
                
                flash('Passwort wurde erfolgreich geändert.', 'success')
                return redirect(url_for('dashboard.index'))
                
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error changing password for {current_user.username}: {e}")
                flash('Fehler beim Ändern des Passworts.', 'error')
        else:
            flash('Aktuelles Passwort ist falsch.', 'error')
    
    return render_template('auth/change_password.html', title='Passwort ändern', form=form)


@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Benutzerprofil bearbeiten"""
    if request.method == 'POST':
        try:
            current_user.vorname = request.form.get('vorname', '').strip()
            current_user.nachname = request.form.get('nachname', '').strip()
            current_user.email = request.form.get('email', '').strip()
            
            db.session.commit()
            logger.info(f"Profile updated for user: {current_user.username}")
            flash('Profil wurde erfolgreich aktualisiert.', 'success')
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating profile for {current_user.username}: {e}")
            flash('Fehler beim Aktualisieren des Profils.', 'error')
    
    return render_template('auth/profile.html', title='Profil bearbeiten', user=current_user)


# Error handlers for auth blueprint
@bp.errorhandler(429)
def ratelimit_handler(e):
    logger.warning(f"Rate limit exceeded for auth: {request.remote_addr}")
    flash('Zu viele Anfragen. Bitte versuchen Sie es später erneut.', 'warning')
    return redirect(url_for('auth.login')), 429
