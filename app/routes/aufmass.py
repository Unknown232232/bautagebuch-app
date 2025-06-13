import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from sqlalchemy import or_, and_
from datetime import datetime, timedelta
import uuid

from app import db
from app.models.aufmass import AufmassEntry, AufmassDocument  # Add AufmassDocument import
from app.models.material import Material
from app.models.bautagebuch import BautagebuchEntry
from app.forms.aufmass_forms import AufmassForm, SearchFilterForm  # Fixed import path
from app.utils.decorators import role_required  # Fixed import path
from app.utils.file_utils import allowed_file  # Fixed import path

aufmass_bp = Blueprint('aufmass', __name__, url_prefix='/aufmass')

# Rest of your code remains the same...
@aufmass_bp.route('/eingabe', methods=['GET', 'POST'])
@login_required
@role_required(['mitarbeiter', 'bauleiter', 'admin'])
def eingabe():
    """Aufmaß-Eingabeformular für Mitarbeiter"""
    form = AufmassForm()

    if form.validate_on_submit():
        try:
            datum = form.datum.data
            ort = form.ort.data.strip()
            material_id = form.material_id.data

            # Duplikatsprüfung
            similar_entries = AufmassEntry.query.filter(
                and_(
                    AufmassEntry.datum.between(
                        datetime.combine(datum, datetime.min.time()),
                        datetime.combine(datum, datetime.max.time())
                    ),
                    AufmassEntry.material_id == material_id,
                    AufmassEntry.ort.ilike(f"%{ort}%")
                )
            ).all()

            if similar_entries:
                flash(f'Warnung: {len(similar_entries)} ähnliche(r) Eintrag/Einträge gefunden. Bitte prüfen Sie die Übersicht.', 'warning')

            # Aufmaß-Eintrag erstellen
            aufmass = AufmassEntry(
                material_id=material_id,
                ort=ort,
                raumnummer=form.raumnummer.data.strip() if form.raumnummer.data else None,
                menge=form.menge.data,
                einheit=form.einheit.data.strip() if form.einheit.data else None,
                datum=datum,
                mitarbeiter_id=current_user.id,
                bemerkungen=form.bemerkungen.data.strip() if form.bemerkungen.data else None
            )
            db.session.add(aufmass)
            db.session.flush()

            # Datei-Uploads verarbeiten
            if form.documents.data:
                upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'aufmass')
                os.makedirs(upload_folder, exist_ok=True)
                for file in form.documents.data:
                    if file and file.filename and allowed_file(file.filename):
                        original_filename = secure_filename(file.filename)
                        ext = os.path.splitext(original_filename)[1]
                        unique_filename = f"{uuid.uuid4().hex}{ext}"
                        file_path = os.path.join(upload_folder, unique_filename)
                        file.save(file_path)

                        document = AufmassDocument(
                            aufmass_entry_id=aufmass.id,
                            filename=unique_filename,
                            original_filename=original_filename,
                            file_type=file.content_type or 'unknown',
                            file_size=os.path.getsize(file_path)
                        )
                        db.session.add(document)

            # Bautagebuch-Eintrag automatisch erzeugen
            eintrag = BautagebuchEntry(
                datum=datum.date(),
                text=aufmass.to_bautagebuch_text(),
                aufmass_entry_id=aufmass.id,
                kalenderwoche=datum.isocalendar()[1],
                jahr=datum.year
            )
            db.session.add(eintrag)
            db.session.commit()

            flash('Aufmaß erfolgreich gespeichert und Bautagebuch-Eintrag erstellt!', 'success')
            return redirect(url_for('aufmass.eingabe'))

        except Exception as e:
            db.session.rollback()
            flash(f'Fehler beim Speichern: {str(e)}', 'error')

    # Letzte 5 Einträge für die Anzeige
    recent_entries = AufmassEntry.query.order_by(AufmassEntry.created_at.desc()).limit(5).all()
    
    return render_template('aufmass/eingabe.html', form=form, recent_entries=recent_entries)

@aufmass_bp.route('/liste')
@aufmass_bp.route('/uebersicht')
@login_required
@role_required(['bauleiter', 'admin'])
def liste():
    """Übersicht aller Aufmaß-Einträge mit Filter/Suche"""
    form = SearchFilterForm()
    query = AufmassEntry.query.join(Material)

    if request.args.get('search_term'):
        term = f"%{request.args.get('search_term')}%"
        query = query.filter(or_(
            AufmassEntry.ort.ilike(term),
            AufmassEntry.raumnummer.ilike(term),
            Material.name.ilike(term),
            AufmassEntry.bemerkungen.ilike(term)
        ))

    if request.args.get('material_filter') and request.args.get('material_filter').isdigit():
        query = query.filter(AufmassEntry.material_id == int(request.args.get('material_filter')))

    if request.args.get('datum_von'):
        datum_von = datetime.strptime(request.args.get('datum_von'), '%Y-%m-%d')
        query = query.filter(AufmassEntry.datum >= datum_von)

    if request.args.get('datum_bis'):
        datum_bis = datetime.strptime(request.args.get('datum_bis'), '%Y-%m-%d')
        datum_bis = datum_bis.replace(hour=23, minute=59, second=59)
        query = query.filter(AufmassEntry.datum <= datum_bis)

    sort = request.args.get('sort', 'datum_desc')
    if sort == 'datum_asc':
        query = query.order_by(AufmassEntry.datum.asc())
    elif sort == 'ort':
        query = query.order_by(AufmassEntry.ort.asc())
    elif sort == 'material':
        query = query.order_by(Material.name.asc())
    else:
        query = query.order_by(AufmassEntry.datum.desc())

    page = request.args.get('page', 1, type=int)
    entries = query.paginate(page=page, per_page=20, error_out=False)

    return render_template('aufmass/uebersicht.html', entries=entries, form=form, current_sort=sort)

@aufmass_bp.route('/details/<int:id>')
@login_required
@role_required(['bauleiter', 'admin'])
def details(id):
    aufmass = AufmassEntry.query.get_or_404(id)
    return render_template('aufmass/details.html', aufmass=aufmass)

@aufmass_bp.route('/bearbeiten/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required(['bauleiter', 'admin'])
def bearbeiten(id):
    aufmass = AufmassEntry.query.get_or_404(id)
    form = AufmassForm(obj=aufmass)

    if form.validate_on_submit():
        try:
            form.populate_obj(aufmass)
            aufmass.updated_at = datetime.utcnow()

            eintrag = BautagebuchEntry.query.filter_by(aufmass_entry_id=id).first()
            if eintrag:
                eintrag.text = aufmass.to_bautagebuch_text()
                eintrag.datum = aufmass.datum.date()
                eintrag.kalenderwoche = aufmass.datum.isocalendar()[1]
                eintrag.jahr = aufmass.datum.year

            db.session.commit()
            flash('Aufmaß erfolgreich aktualisiert!', 'success')
            return redirect(url_for('aufmass.details', id=id))

        except Exception as e:
            db.session.rollback()
            flash(f'Fehler beim Aktualisieren: {str(e)}', 'error')

    return render_template('aufmass/bearbeiten.html', form=form, aufmass=aufmass)

@aufmass_bp.route('/loeschen/<int:id>', methods=['POST'])
@login_required
@role_required(['admin'])
def loeschen(id):
    aufmass = AufmassEntry.query.get_or_404(id)

    try:
        eintrag = BautagebuchEntry.query.filter_by(aufmass_entry_id=id).first()
        if eintrag:
            db.session.delete(eintrag)

        for doc in aufmass.documents:
            path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'aufmass', doc.filename)
            if os.path.exists(path):
                os.remove(path)
            db.session.delete(doc)

        db.session.delete(aufmass)
        db.session.commit()
        flash('Aufmaß erfolgreich gelöscht!', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Fehler beim Löschen: {str(e)}', 'error')

    return redirect(url_for('aufmass.uebersicht'))

@aufmass_bp.route('/api/material/<int:material_id>')
@login_required
def api_material_details(material_id):
    material = Material.query.get_or_404(material_id)
    return jsonify({
        'name': material.name,
        'einheit': material.einheit,
        'kategorie': material.kategorie
    })

@aufmass_bp.route('/api/check_duplicate', methods=['POST'])
@login_required
def api_check_duplicate():
    data = request.get_json()
    datum = datetime.strptime(data['datum'], '%Y-%m-%d').date()
    similar_entries = AufmassEntry.query.filter(
        and_(
            AufmassEntry.datum.between(
                datetime.combine(datum, datetime.min.time()),
                datetime.combine(datum, datetime.max.time())
            ),
            AufmassEntry.material_id == data['material_id'],
            AufmassEntry.ort.ilike(f"%{data['ort']}%")
        )
    ).all()

    if similar_entries:
        return jsonify({
            'has_duplicates': True,
            'count': len(similar_entries),
            'message': f"Es wurden {len(similar_entries)} ähnliche Einträge gefunden."
        })

    return jsonify({'has_duplicates': False})
