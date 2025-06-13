"""
Routen für Kabel-Kategorie-Verwaltung
"""
import logging
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models.kabel_kategorie import KabelKategorie, Kabeltyp, KabelKategorieService
from app.forms.kabel_forms import (
    KabelKategorieForm, KabeltypForm, BulkKabeltypForm, 
    KabelSuchForm, QuickKabeltypForm
)
from app.utils.decorators import admin_required

kabel_bp = Blueprint('kabel', __name__)
logger = logging.getLogger(__name__)


@kabel_bp.route('/')
@login_required
def index():
    """Übersicht aller Kabel-Kategorien und Kabeltypen"""
    try:
        search_form = KabelSuchForm()
        
        # Filter anwenden
        search_query = request.args.get('search', '').strip()
        kategorie_filter = request.args.get('kategorie', '').strip()
        
        if search_query:
            # Suche über alle Kabeltypen
            result = KabelKategorieService.search_kabeltypen(search_query)
            if result['success']:
                search_results = result['ergebnisse']
                kategorien_data = {}
                
                # Gruppiere Suchergebnisse nach Kategorien
                for item in search_results:
                    kat_name = item['kategorie']
                    if kat_name not in kategorien_data:
                        kategorien_data[kat_name] = []
                    kategorien_data[kat_name].append(item['kabeltyp'])
            else:
                flash(result['error'], 'error')
                kategorien_data = {}
        else:
            # Alle Kategorien laden
            kategorien = KabelKategorie.get_active_kategorien()
            kategorien_data = {}
            
            for kategorie in kategorien:
                # Filter nach Kategorie anwenden
                if kategorie_filter and kategorie.name != kategorie_filter:
                    continue
                    
                kabeltypen = kategorie.get_kabeltypen()
                if kabeltypen:  # Nur Kategorien mit Kabeltypen anzeigen
                    kategorien_data[kategorie.name] = [k.to_dict() for k in kabeltypen]
        
        return render_template(
            'kabel/index.html',
            kategorien_data=kategorien_data,
            search_form=search_form,
            search_query=search_query,
            kategorie_filter=kategorie_filter
        )
        
    except Exception as e:
        logger.error(f"Fehler beim Laden der Kabel-Übersicht: {e}")
        flash('Fehler beim Laden der Kabel-Übersicht', 'error')
        return render_template('kabel/index.html', kategorien_data={}, search_form=KabelSuchForm())


@kabel_bp.route('/kategorien')
@login_required
@admin_required
def kategorien():
    """Verwaltung der Kabel-Kategorien (nur für Admins)"""
    try:
        kategorien = KabelKategorie.query.order_by(
            KabelKategorie.sortierung.asc(),
            KabelKategorie.name.asc()
        ).all()
        
        return render_template('kabel/kategorien.html', kategorien=kategorien)
        
    except Exception as e:
        logger.error(f"Fehler beim Laden der Kategorien: {e}")
        flash('Fehler beim Laden der Kategorien', 'error')
        return redirect(url_for('kabel.index'))


@kabel_bp.route('/kategorie/neu', methods=['GET', 'POST'])
@login_required
@admin_required
def neue_kategorie():
    """Neue Kabel-Kategorie erstellen"""
    form = KabelKategorieForm()
    
    if form.validate_on_submit():
        try:
            kategorie = KabelKategorie(
                name=form.name.data,
                beschreibung=form.beschreibung.data,
                ist_aktiv=form.ist_aktiv.data
            )
            
            db.session.add(kategorie)
            db.session.commit()
            
            flash(f'Kategorie "{kategorie.name}" wurde erfolgreich erstellt.', 'success')
            return redirect(url_for('kabel.kategorien'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Fehler beim Erstellen der Kategorie: {e}")
            flash('Fehler beim Erstellen der Kategorie', 'error')
    
    return render_template('kabel/kategorie_form.html', form=form, title='Neue Kategorie')


@kabel_bp.route('/kategorie/<int:kategorie_id>/bearbeiten', methods=['GET', 'POST'])
@login_required
@admin_required
def kategorie_bearbeiten(kategorie_id):
    """Kabel-Kategorie bearbeiten"""
    kategorie = KabelKategorie.query.get_or_404(kategorie_id)
    form = KabelKategorieForm(kategorie=kategorie, obj=kategorie)
    
    if form.validate_on_submit():
        try:
            form.populate_obj(kategorie)
            kategorie.updated_at = db.func.now()
            
            db.session.commit()
            
            flash(f'Kategorie "{kategorie.name}" wurde erfolgreich aktualisiert.', 'success')
            return redirect(url_for('kabel.kategorien'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Fehler beim Aktualisieren der Kategorie: {e}")
            flash('Fehler beim Aktualisieren der Kategorie', 'error')
    
    return render_template('kabel/kategorie_form.html', form=form, kategorie=kategorie, title='Kategorie bearbeiten')


@kabel_bp.route('/kabeltyp/neu', methods=['GET', 'POST'])
@login_required
@admin_required
def neuer_kabeltyp():
    """Neuen Kabeltyp erstellen"""
    form = KabeltypForm()
    
    if form.validate_on_submit():
        try:
            kabeltyp = Kabeltyp(
                name=form.name.data,
                kategorie_id=form.kategorie_id.data,
                beschreibung=form.beschreibung.data,
                technische_daten=form.technische_daten.data,
                ist_aktiv=form.ist_aktiv.data
            )
            
            db.session.add(kabeltyp)
            db.session.commit()
            
            flash(f'Kabeltyp "{kabeltyp.name}" wurde erfolgreich erstellt.', 'success')
            return redirect(url_for('kabel.index'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Fehler beim Erstellen des Kabeltyps: {e}")
            flash('Fehler beim Erstellen des Kabeltyps', 'error')
    
    return render_template('kabel/kabeltyp_form.html', form=form, title='Neuer Kabeltyp')


@kabel_bp.route('/kabeltyp/<int:kabeltyp_id>/bearbeiten', methods=['GET', 'POST'])
@login_required
@admin_required
def kabeltyp_bearbeiten(kabeltyp_id):
    """Kabeltyp bearbeiten"""
    kabeltyp = Kabeltyp.query.get_or_404(kabeltyp_id)
    form = KabeltypForm(kabeltyp=kabeltyp, obj=kabeltyp)
    
    if form.validate_on_submit():
        try:
            form.populate_obj(kabeltyp)
            kabeltyp.updated_at = db.func.now()
            
            db.session.commit()
            
            flash(f'Kabeltyp "{kabeltyp.name}" wurde erfolgreich aktualisiert.', 'success')
            return redirect(url_for('kabel.index'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Fehler beim Aktualisieren des Kabeltyps: {e}")
            flash('Fehler beim Aktualisieren des Kabeltyps', 'error')
    
    return render_template('kabel/kabeltyp_form.html', form=form, kabeltyp=kabeltyp, title='Kabeltyp bearbeiten')


@kabel_bp.route('/bulk-import', methods=['GET', 'POST'])
@login_required
@admin_required
def bulk_import():
    """Bulk-Import von Kabeltypen"""
    form = BulkKabeltypForm()
    
    if form.validate_on_submit():
        try:
            kategorie = KabelKategorie.query.get(form.kategorie_id.data)
            if not kategorie:
                flash('Kategorie nicht gefunden', 'error')
                return render_template('kabel/bulk_import.html', form=form)
            
            kabeltypen_text = form.kabeltypen_text.data.strip()
            lines = [line.strip() for line in kabeltypen_text.split('\n') if line.strip()]
            
            erfolg_count = 0
            fehler_count = 0
            fehler_details = []
            
            for line in lines:
                try:
                    # Prüfen ob Kabeltyp bereits existiert
                    existing = Kabeltyp.query.filter_by(
                        name=line,
                        kategorie_id=kategorie.id
                    ).first()
                    
                    if existing:
                        fehler_count += 1
                        fehler_details.append(f'"{line}" existiert bereits')
                        continue
                    
                    kabeltyp = Kabeltyp(
                        name=line,
                        kategorie_id=kategorie.id,
                        ist_aktiv=True
                    )
                    
                    db.session.add(kabeltyp)
                    erfolg_count += 1
                    
                except Exception as e:
                    fehler_count += 1
                    fehler_details.append(f'"{line}": {str(e)}')
            
            db.session.commit()
            
            # Erfolgsmeldung
            if erfolg_count > 0:
                flash(f'{erfolg_count} Kabeltypen erfolgreich importiert.', 'success')
            
            if fehler_count > 0:
                flash(f'{fehler_count} Fehler beim Import. Details: {"; ".join(fehler_details[:5])}', 'warning')
            
            return redirect(url_for('kabel.index'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Fehler beim Bulk-Import: {e}")
            flash('Fehler beim Bulk-Import', 'error')
    
    return render_template('kabel/bulk_import.html', form=form)


# API Endpoints für AJAX-Anfragen

@kabel_bp.route('/api/kategorie/<kategorie_name>/kabeltypen')
@login_required
def api_kabeltypen_by_kategorie(kategorie_name):
    """API: Kabeltypen einer Kategorie abrufen"""
    try:
        result = KabelKategorieService.get_kabeltypen_by_kategorie(kategorie_name)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"API Fehler beim Laden der Kabeltypen: {e}")
        return jsonify({
            'success': False,
            'kabeltypen': [],
            'error': 'Interner Serverfehler'
        }), 500


@kabel_bp.route('/api/kategorien')
@login_required
def api_kategorien():
    """API: Alle verfügbaren Kategorien abrufen"""
    try:
        result = KabelKategorieService.get_all_kategorien()
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"API Fehler beim Laden der Kategorien: {e}")
        return jsonify({
            'success': False,
            'kategorien': [],
            'error': 'Interner Serverfehler'
        }), 500


@kabel_bp.route('/api/search')
@login_required
def api_search():
    """API: Kabeltypen suchen"""
    try:
        suchbegriff = request.args.get('q', '').strip()
        result = KabelKategorieService.search_kabeltypen(suchbegriff)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"API Fehler bei der Suche: {e}")
        return jsonify({
            'success': False,
            'ergebnisse': [],
            'error': 'Interner Serverfehler'
        }), 500


@kabel_bp.route('/api/quick-add', methods=['POST'])
@login_required
@admin_required
def api_quick_add():
    """API: Schnell einen Kabeltyp hinzufügen"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Keine Daten empfangen'
            }), 400
        
        kategorie_name = data.get('kategorie_name', '').strip()
        kabeltyp_name = data.get('kabeltyp_name', '').strip()
        
        if not kategorie_name or not kabeltyp_name:
            return jsonify({
                'success': False,
                'error': 'Kategorie und Kabeltyp sind erforderlich'
            }), 400
        
        # Kategorie erstellen falls sie nicht existiert
        kategorie = KabelKategorie.query.filter_by(name=kategorie_name).first()
        if not kategorie:
            kategorie_result = KabelKategorieService.add_kategorie(kategorie_name)
            if not kategorie_result['success']:
                return jsonify(kategorie_result), 400
            kategorie = KabelKategorie.query.filter_by(name=kategorie_name).first()
        
        # Kabeltyp hinzufügen
        result = KabelKategorieService.add_kabeltyp(kategorie_name, kabeltyp_name)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"API Fehler beim Quick-Add: {e}")
        return jsonify({
            'success': False,
            'error': 'Interner Serverfehler'
        }), 500


# Hilfsfunktionen für Templates

@kabel_bp.app_template_filter('kabel_count')
def kabel_count_filter(kategorie_name):
    """Template-Filter: Anzahl Kabeltypen einer Kategorie"""
    try:
        kategorie = KabelKategorie.query.filter_by(name=kategorie_name, ist_aktiv=True).first()
        if kategorie:
            return kategorie.kabeltypen.filter_by(ist_aktiv=True).count()
        return 0
    except:
        return 0


@kabel_bp.app_template_global()
def get_kabel_kategorien():
    """Template-Global: Alle aktiven Kategorien für Navigation"""
    try:
        return KabelKategorie.get_active_kategorien()
    except:
        return []
