from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user

def role_required(allowed_roles):
    """
    Decorator um zu prüfen, ob der aktuelle Benutzer eine der erlaubten Rollen hat
    
    Args:
        allowed_roles (list): Liste der erlaubten Rollen ['mitarbeiter', 'bauleiter', 'admin']
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Sie müssen angemeldet sein, um diese Seite zu besuchen.', 'warning')
                return redirect(url_for('auth.login'))
            
            # Normalisiere Rollen zu lowercase für Vergleich
            normalized_allowed = [role.lower() for role in allowed_roles]
            if current_user.role.lower() not in normalized_allowed:
                flash('Sie haben keine Berechtigung für diese Aktion.', 'error')
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """Decorator für Admin-Only Funktionen"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Admin-Berechtigung erforderlich.', 'error')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def bauleiter_or_admin_required(f):
    """Decorator für Bauleiter oder Admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_bauleiter():
            flash('Bauleiter- oder Admin-Berechtigung erforderlich.', 'error')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
