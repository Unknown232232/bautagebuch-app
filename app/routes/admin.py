import logging
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from functools import wraps
from sqlalchemy import or_
from app import db
from app.models.material import Material  # Fixed import path
from app.models.user import User  # Fixed import path
from app.forms.material_forms import MaterialForm, BulkMaterialForm, MaterialSearchForm  # Fixed import path
from app.forms.auth import RegistrationForm, PasswordChangeForm

logger = logging.getLogger(__name__)

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Export as 'bp' for consistency with __init__.py
bp = admin_bp


def admin_required(f):
    """Decorator für Admin-only Routen"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Sie haben keine Berechtigung für diesen Bereich.', 'error')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)

    return decorated_function


@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    """Admin Dashboard"""
    # Statistiken sammeln
    total_materials = Material.query.count()
    active_materials = Material.query.filter_by(is_active=True).count()
    inactive_materials = total_materials - active_materials
    total_users = User.query.count()

    stats = {
        'total_materials': total_materials,
        'active_materials': active_materials,
        'inactive_materials': inactive_materials,
        'total_users': total_users
    }

    return render_template('admin/dashboard.html', stats=stats)


@admin_bp.route('/materials')
@login_required
@admin_required
def materials():
    """Materialverwaltung - Übersicht"""
    form = MaterialSearchForm()

    # Query aufbauen
    query = Material.query

    # Filter anwenden
    if request.args.get('search'):
        search_term = f"%{request.args.get('search')}%"
        query = query.filter(or_(
            Material.name.ilike(search_term),
            Material.description.ilike(search_term)
        ))

    if request.args.get('category'):
        query = query.filter_by(category=request.args.get('category'))

    status_filter = request.args.get('status')
    if status_filter == 'active':
        query = query.filter_by(is_active=True)
    elif status_filter == 'inactive':
        query = query.filter_by(is_active=False)

    # Sortierung und Paginierung
    materials = query.order_by(Material.category.asc(), Material.name.asc()).all()

    return render_template('admin/materials.html', materials=materials, form=form)


@admin_bp.route('/materials/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_material():
    """Neues Material hinzufügen"""
    form = MaterialForm()

    if form.validate_on_submit():
        material = Material(
            name=form.name.data,
            category=form.kategorie.data or None,
            unit=form.einheit.data,
            description=form.beschreibung.data,
            is_active=form.ist_aktiv.data,
            created_by=current_user.id
        )

        try:
            db.session.add(material)
            db.session.commit()
            flash(f'Material "{material.name}" wurde erfolgreich hinzugefügt.', 'success')
            return redirect(url_for('admin.materials'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error adding material {form.name.data}: {e}")
            flash('Fehler beim Speichern des Materials.', 'error')

    return render_template('admin/material_form.html', form=form, title='Material hinzufügen')


@admin_bp.route('/materials/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_material(id):
    """Material bearbeiten"""
    material = Material.query.get_or_404(id)
    form = MaterialForm(material=material, obj=material)

    if form.validate_on_submit():
        material.name = form.name.data
        material.category = form.kategorie.data or None
        material.unit = form.einheit.data
        material.description = form.beschreibung.data
        material.is_active = form.ist_aktiv.data

        try:
            db.session.commit()
            flash(f'Material "{material.name}" wurde erfolgreich aktualisiert.', 'success')
            return redirect(url_for('admin.materials'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating material {material.name}: {e}")
            flash('Fehler beim Aktualisieren des Materials.', 'error')

    return render_template('admin/material_form.html',
                           form=form, material=material,
                           title=f'Material bearbeiten: {material.name}')


@admin_bp.route('/materials/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_material(id):
    """Material löschen"""
    material = Material.query.get_or_404(id)

    # Prüfen ob Material in Aufmaß-Einträgen verwendet wird
    if material.aufmass_entries.count() > 0:
        flash(
            f'Material "{material.name}" kann nicht gelöscht werden, da es in Aufmaß-Einträgen verwendet wird. Deaktivieren Sie es stattdessen.',
            'error')
        return redirect(url_for('admin.materials'))

    try:
        db.session.delete(material)
        db.session.commit()
        flash(f'Material "{material.name}" wurde erfolgreich gelöscht.', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting material {material.name}: {e}")
        flash('Fehler beim Löschen des Materials.', 'error')

    return redirect(url_for('admin.materials'))


@admin_bp.route('/materials/bulk-add', methods=['GET', 'POST'])
@login_required
@admin_required
def bulk_add_materials():
    """Mehrere Materialien auf einmal hinzufügen"""
    if request.method == 'POST':
        materials_text = request.form.get('materials_text', '')
        default_kategorie = request.form.get('default_kategorie', '')
        default_einheit = request.form.get('default_einheit', 'Stück')
        
        added_count = 0
        error_count = 0

        lines = materials_text.strip().split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            parts = line.split('|')
            name = parts[0].strip()
            kategorie = parts[1].strip() if len(parts) > 1 and parts[1].strip() else default_kategorie
            einheit = parts[2].strip() if len(parts) > 2 and parts[2].strip() else default_einheit

            # Prüfen ob Material bereits existiert
            existing = Material.query.filter_by(name=name).first()
            if existing:
                error_count += 1
                continue

            material = Material(
                name=name,
                category=kategorie or None,
                unit=einheit,
                is_active=True,
                created_by=current_user.id
            )

            try:
                db.session.add(material)
                added_count += 1
            except:
                error_count += 1

        try:
            db.session.commit()
            flash(f'{added_count} Materialien wurden hinzugefügt. {error_count} Fehler.', 'success')
            return redirect(url_for('admin.materials'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error bulk adding materials: {e}")
            flash('Fehler beim Speichern der Materialien.', 'error')

    return render_template('admin/bulk_material_form.html')


@admin_bp.route('/materials/toggle/<int:id>', methods=['POST'])
@login_required
@admin_required
def toggle_material_status(id):
    """Material aktivieren/deaktivieren"""
    material = Material.query.get_or_404(id)
    material.is_active = not material.is_active

    try:
        db.session.commit()
        status = 'aktiviert' if material.is_active else 'deaktiviert'
        flash(f'Material "{material.name}" wurde {status}.', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error toggling material status for {material.name}: {e}")
        flash('Fehler beim Ändern des Material-Status.', 'error')

    return redirect(url_for('admin.materials'))


@admin_bp.route('/api/materials')
@login_required
@admin_required
def api_materials():
    """API Endpoint für Material-Daten (für AJAX)"""
    materials = Material.get_active_materials()
    return jsonify([material.to_dict() for material in materials])


@admin_bp.route('/api/materials/categories')
@login_required
@admin_required
def api_material_categories():
    """API Endpoint für Material-Kategorien"""
    categories = Material.get_materials_by_category()
    return jsonify({category: [m.to_dict() for m in materials]
                    for category, materials in categories.items()})


# ===== BENUTZERVERWALTUNG =====

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """Benutzerverwaltung - Übersicht"""
    users = User.query.order_by(User.role.asc(), User.username.asc()).all()
    return render_template('admin/users.html', users=users)


@admin_bp.route('/users/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    """Neuen Benutzer hinzufügen"""
    form = RegistrationForm()
    
    if form.validate_on_submit():
        try:
            user = User(
                username=form.username.data.strip(),
                email=form.email.data.strip(),
                role=form.role.data,
                vorname=form.vorname.data.strip() if form.vorname.data else None,
                nachname=form.nachname.data.strip() if form.nachname.data else None,
                password_change_required=True  # Neuer Benutzer muss Passwort beim ersten Login ändern
            )
            user.set_password(form.password.data)
            # Passwort-Änderung wieder auf True setzen, da es beim ersten Login geändert werden muss
            user.password_change_required = True
            
            db.session.add(user)
            db.session.commit()
            
            flash(f'Benutzer "{user.username}" wurde erfolgreich erstellt. Der Benutzer muss beim ersten Login das Passwort ändern.', 'success')
            return redirect(url_for('admin.users'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating user: {e}")
            flash('Fehler beim Erstellen des Benutzers.', 'error')
    
    return render_template('admin/user_form.html', form=form, title='Benutzer hinzufügen')


@admin_bp.route('/users/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(id):
    """Benutzer bearbeiten"""
    user = User.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            user.email = request.form.get('email', '').strip()
            user.vorname = request.form.get('vorname', '').strip() or None
            user.nachname = request.form.get('nachname', '').strip() or None
            user.role = request.form.get('role')
            user.is_active = 'is_active' in request.form
            
            db.session.commit()
            flash(f'Benutzer "{user.username}" wurde erfolgreich aktualisiert.', 'success')
            return redirect(url_for('admin.users'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating user {user.username}: {e}")
            flash('Fehler beim Aktualisieren des Benutzers.', 'error')
    
    return render_template('admin/user_edit.html', user=user, title=f'Benutzer bearbeiten: {user.username}')


@admin_bp.route('/users/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_user(id):
    """Benutzer löschen"""
    user = User.query.get_or_404(id)
    
    # Admin kann sich nicht selbst löschen
    if user.id == current_user.id:
        flash('Sie können sich nicht selbst löschen.', 'error')
        return redirect(url_for('admin.users'))
    
    # Prüfen ob Benutzer Aufmaß-Einträge hat
    if user.aufmass_entries.count() > 0:
        flash(f'Benutzer "{user.username}" kann nicht gelöscht werden, da er Aufmaß-Einträge erstellt hat. Deaktivieren Sie den Benutzer stattdessen.', 'error')
        return redirect(url_for('admin.users'))
    
    try:
        username = user.username
        db.session.delete(user)
        db.session.commit()
        flash(f'Benutzer "{username}" wurde erfolgreich gelöscht.', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting user {user.username}: {e}")
        flash('Fehler beim Löschen des Benutzers.', 'error')
    
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/toggle/<int:id>', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(id):
    """Benutzer aktivieren/deaktivieren"""
    user = User.query.get_or_404(id)
    
    # Admin kann sich nicht selbst deaktivieren
    if user.id == current_user.id:
        flash('Sie können sich nicht selbst deaktivieren.', 'error')
        return redirect(url_for('admin.users'))
    
    user.is_active = not user.is_active
    
    try:
        db.session.commit()
        status = 'aktiviert' if user.is_active else 'deaktiviert'
        flash(f'Benutzer "{user.username}" wurde {status}.', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error toggling user status for {user.username}: {e}")
        flash('Fehler beim Ändern des Benutzer-Status.', 'error')
    
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/reset-password/<int:id>', methods=['POST'])
@login_required
@admin_required
def reset_user_password(id):
    """Benutzer-Passwort zurücksetzen"""
    user = User.query.get_or_404(id)
    
    # Temporäres Passwort generieren
    import secrets
    import string
    temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
    
    try:
        user.set_password(temp_password)
        user.password_change_required = True  # Benutzer muss Passwort beim nächsten Login ändern
        db.session.commit()
        
        flash(f'Passwort für "{user.username}" wurde zurückgesetzt. Neues temporäres Passwort: {temp_password}', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error resetting password for {user.username}: {e}")
        flash('Fehler beim Zurücksetzen des Passworts.', 'error')
    
    return redirect(url_for('admin.users'))
