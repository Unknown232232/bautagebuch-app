"""
Authentifizierungs-Routen mit erweiterten Sicherheitsfunktionen
"""
import logging
from datetime import datetime, timedelta, timezone
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app
from flask_login import login_user, logout_user, current_user, login_required
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from urllib.parse import urlparse
from app import db, limiter
from app.models.user import User
from app.forms.auth import LoginForm, RegistrationForm, PasswordChangeForm
from app.utils.security import audit_logger, data_sanitizer, password_security

bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

# Track failed login attempts
failed_attempts = {}


def is_account_locked(username):
    """Check if account is temporarily locked due to failed attempts."""
    if username not in failed_attempts:
        return False
    
    attempts, last_attempt = failed_attempts[username]
    
    # Reset after 15 minutes
    if datetime.now(timezone.utc) - last_attempt > timedelta(minutes=15):
        del failed_attempts[username]
        return False
    
    return attempts >= 5


def record_failed_attempt(username):
    """Record a failed login attempt."""
    now = datetime.now(timezone.utc)
    if username in failed_attempts:
        attempts, _ = failed_attempts[username]
        failed_attempts[username] = (attempts + 1, now)
    else:
        failed_attempts[username] = (1, now)


def clear_failed_attempts(username):
    """Clear failed attempts for successful login."""
    if username in failed_attempts:
        del failed_attempts[username]


@bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login():
    """Login-Seite mit erweiterten Sicherheitsfunktionen"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        # Sanitize input
        username = data_sanitizer.sanitize_input(form.username.data)
        
        # Validate username format
        if not data_sanitizer.validate_username(username):
            flash('Ungültiges Benutzername-Format', 'error')
            return render_template('auth/login.html', title='Anmelden', form=form)
        
        user = User.query.filter_by(username=username).first()
        
        if user:
            # Check if account is locked (using User model method)
            if user.is_account_locked():
                audit_logger.log_login_attempt(username, request.remote_addr, False, "Account locked")
                flash('Account temporär gesperrt. Versuchen Sie es später erneut.', 'error')
                return render_template('auth/login.html', title='Anmelden', form=form)
            
            # Check password and account status
            if user.check_password(form.password.data) and user.is_active:
                # Check if password is expired
                if user.is_password_expired():
                    flash('Ihr Passwort ist abgelaufen. Bitte ändern Sie es.', 'warning')
                    session['password_change_required'] = True
                    session['temp_user_id'] = user.id
                    return redirect(url_for('auth.change_password'))
                
                # Successful login
                login_user(user, remember=form.remember_me.data)
                user.update_last_login()
                
                # Log successful login with audit logger
                audit_logger.log_login_attempt(username, request.remote_addr, True)
                
                # Redirect to intended page or dashboard
                next_page = request.args.get('next')
                if not next_page or urlparse(next_page).netloc != '':
                    next_page = url_for('dashboard.index')
                
                flash(f'Willkommen zurück, {user.username}!', 'success')
                return redirect(next_page)
            else:
                # Failed login - let User model handle failed attempts
                audit_logger.log_login_attempt(username, request.remote_addr, False, "Invalid credentials")
                flash('Ungültiger Benutzername oder Passwort', 'error')
        else:
            # User not found
            audit_logger.log_login_attempt(username, request.remote_addr, False, "User not found")
            flash('Ungültiger Benutzername oder Passwort', 'error')
    
    return render_template('auth/login.html', title='Anmelden', form=form)


@bp.route('/logout')
@login_required
def logout():
    """Logout"""
    username = current_user.username
    logger.info(f"User logout: {username}")
    logout_user()
    session.clear()  # Clear all session data
    flash(f'Auf Wiedersehen, {username}!', 'info')
    return redirect(url_for('auth.login'))


@bp.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    """Registrierung neuer Benutzer (nur für Admins) mit erweiterten Sicherheitsfunktionen"""
    if not current_user.is_admin():
        audit_logger.log_security_event(
            "UNAUTHORIZED_ACCESS", 
            f"User {current_user.username} attempted to access registration",
            "WARNING"
        )
        flash('Keine Berechtigung für diese Aktion.', 'error')
        return redirect(url_for('dashboard.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            # Sanitize input data
            username = data_sanitizer.sanitize_input(form.username.data)
            email = data_sanitizer.sanitize_input(form.email.data)
            vorname = data_sanitizer.sanitize_input(form.vorname.data)
            nachname = data_sanitizer.sanitize_input(form.nachname.data)
            
            # Validate input formats
            if not data_sanitizer.validate_username(username):
                flash('Ungültiges Benutzername-Format', 'error')
                return render_template('auth/register.html', title='Benutzer erstellen', form=form)
            
            if not data_sanitizer.validate_email(email):
                flash('Ungültiges E-Mail-Format', 'error')
                return render_template('auth/register.html', title='Benutzer erstellen', form=form)
            
            # Validate password strength
            password_errors = password_security.validate_password_strength(form.password.data)
            if password_errors:
                for error in password_errors:
                    flash(error, 'error')
                return render_template('auth/register.html', title='Benutzer erstellen', form=form)
            
            user = User(
                username=username,
                email=email,
                role=form.role.data,
                vorname=vorname,
                nachname=nachname
            )
            user.set_password(form.password.data)
            
            db.session.add(user)
            db.session.commit()
            
            # Log admin action
            audit_logger.log_admin_action(
                current_user.username, 
                "USER_CREATED", 
                username, 
                request.remote_addr
            )
            
            flash(f'Benutzer {user.username} wurde erfolgreich erstellt.', 'success')
            return redirect(url_for('admin.users'))
            
        except ValueError as e:
            # Password validation error
            flash(str(e), 'error')
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating user: {e}")
            flash('Fehler beim Erstellen des Benutzers.', 'error')
    
    return render_template('auth/register.html', title='Benutzer erstellen', form=form)


@bp.route('/change-password', methods=['GET', 'POST'])
@login_required
@limiter.limit("5 per minute")
def change_password():
    """Passwort ändern mit erweiterten Sicherheitsfunktionen"""
    form = PasswordChangeForm()
    if form.validate_on_submit():
        # Validate password strength first
        password_errors = password_security.validate_password_strength(form.new_password.data)
        if password_errors:
            for error in password_errors:
                flash(error, 'error')
            return render_template('auth/change_password.html', title='Passwort ändern', form=form)
        
        # Check if new password is different from current
        if password_security.verify_password(form.new_password.data, current_user.password_hash):
            flash('Das neue Passwort muss sich vom aktuellen Passwort unterscheiden.', 'error')
            return render_template('auth/change_password.html', title='Passwort ändern', form=form)
        
        if current_user.check_password(form.current_password.data):
            try:
                current_user.set_password(form.new_password.data)
                db.session.commit()
                
                # Log password change
                audit_logger.log_password_change(current_user.username, request.remote_addr)
                
                # Clear password change requirement if it was set
                session.pop('password_change_required', None)
                session.pop('temp_user_id', None)
                
                flash('Passwort wurde erfolgreich geändert.', 'success')
                return redirect(url_for('dashboard.index'))
                
            except ValueError as e:
                # Password validation error from User model
                flash(str(e), 'error')
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error changing password for {current_user.username}: {e}")
                flash('Fehler beim Ändern des Passworts.', 'error')
        else:
            audit_logger.log_security_event(
                "WRONG_PASSWORD", 
                f"User {current_user.username} provided wrong current password",
                "WARNING"
            )
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
