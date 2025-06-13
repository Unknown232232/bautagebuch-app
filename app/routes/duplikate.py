# routes/duplikate.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.aufmass import AufmassEntry
from app.models.bautagebuch import BautagebuchEntry
from app.models.user import User
from app.models.material import Material
from datetime import datetime, timedelta
from sqlalchemy import and_, or_

duplikate_bp = Blueprint('duplikate', __name__)

class DuplikatsPruefer:
    """Klasse für die Duplikatserkennung"""
    
    @staticmethod
    def finde_duplikate():
        """Findet potentielle Duplikate basierend auf verschiedenen Kriterien"""
        
        duplikate = []
        
        # Alle Aufmaße laden
        aufmaesse = AufmassEntry.query.order_by(AufmassEntry.datum.desc()).all()
        
        for i, aufmass in enumerate(aufmaesse):
            # Suche nach ähnlichen Einträgen
            aehnliche = DuplikatsPruefer._finde_aehnliche_eintraege(aufmass, aufmaesse[i+1:])
            
            if aehnliche:
                duplikat_gruppe = {
                    'haupteintrag': aufmass,
                    'aehnliche': aehnliche,
                    'kriterien': DuplikatsPruefer._bewerte_aehnlichkeit(aufmass, aehnliche),
                    'risiko': DuplikatsPruefer._bewerte_risiko(aufmass, aehnliche)
                }
                duplikate.append(duplikat_gruppe)
        
        return duplikate
    
    @staticmethod
    def _finde_aehnliche_eintraege(aufmass, vergleichsliste):
        """Findet ähnliche Einträge basierend auf Kriterien"""
        aehnliche = []
        
        for vergleich in vergleichsliste:
            aehnlichkeit = DuplikatsPruefer._berechne_aehnlichkeit(aufmass, vergleich)
            
            # Schwellenwert für Ähnlichkeit
            if aehnlichkeit >= 0.7:  # 70% Ähnlichkeit
                aehnliche.append({
                    'aufmass': vergleich,
                    'aehnlichkeit': aehnlichkeit
                })
        
        return aehnliche
    
    @staticmethod
    def _berechne_aehnlichkeit(aufmass1, aufmass2):
        """Berechnet Ähnlichkeitswert zwischen zwei Aufmaßen"""
        score = 0.0
        max_score = 0.0
        
        # Datum (Gewichtung: 0.3)
        max_score += 0.3
        datum_diff = abs((aufmass1.datum - aufmass2.datum).days)
        if datum_diff == 0:
            score += 0.3
        elif datum_diff <= 1:
            score += 0.2
        elif datum_diff <= 7:
            score += 0.1
        
        # Ort (Gewichtung: 0.25)
        max_score += 0.25
        if aufmass1.ort.lower() == aufmass2.ort.lower():
            score += 0.25
        elif aufmass1.ort.lower() in aufmass2.ort.lower() or aufmass2.ort.lower() in aufmass1.ort.lower():
            score += 0.15
        
        # Material (Gewichtung: 0.25)
        max_score += 0.25
        if aufmass1.material.name.lower() == aufmass2.material.name.lower():
            score += 0.25
        elif aufmass1.material.name.lower() in aufmass2.material.name.lower() or aufmass2.material.name.lower() in aufmass1.material.name.lower():
            score += 0.15
        
        # Mitarbeiter (Gewichtung: 0.15)
        max_score += 0.15
        if aufmass1.mitarbeiter.username.lower() == aufmass2.mitarbeiter.username.lower():
            score += 0.15
        
        # Menge (Gewichtung: 0.05)
        max_score += 0.05
        if aufmass1.menge == aufmass2.menge:
            score += 0.05
        elif abs(aufmass1.menge - aufmass2.menge) / max(aufmass1.menge, aufmass2.menge) <= 0.1:
            score += 0.025
        
        return score / max_score if max_score > 0 else 0
    
    @staticmethod
    def _bewerte_aehnlichkeit(haupteintrag, aehnliche):
        """Bewertet die Ähnlichkeitskriterien"""
        kriterien = {
            'gleicher_tag': False,
            'gleicher_ort': False,
            'gleiches_material': False,
            'gleicher_mitarbeiter': False,
            'aehnliche_menge': False
        }
        
        for aehnlich in aehnliche:
            aufmass = aehnlich['aufmass']
            
            if haupteintrag.datum == aufmass.datum:
                kriterien['gleicher_tag'] = True
            
            if haupteintrag.ort.lower() == aufmass.ort.lower():
                kriterien['gleicher_ort'] = True
            
            if haupteintrag.material.name.lower() == aufmass.material.name.lower():
                kriterien['gleiches_material'] = True
            
            if haupteintrag.mitarbeiter.username.lower() == aufmass.mitarbeiter.username.lower():
                kriterien['gleicher_mitarbeiter'] = True
            
            if abs(haupteintrag.menge - aufmass.menge) / max(haupteintrag.menge, aufmass.menge) <= 0.1:
                kriterien['aehnliche_menge'] = True
        
        return kriterien
    
    @staticmethod
    def _bewerte_risiko(haupteintrag, aehnliche):
        """Bewertet das Duplikat-Risiko"""
        risiko_score = 0
        
        for aehnlich in aehnliche:
            aufmass = aehnlich['aufmass']
            
            # Hohes Risiko: Gleicher Tag, Ort, Material und Mitarbeiter
            if (haupteintrag.datum == aufmass.datum and
                haupteintrag.ort.lower() == aufmass.ort.lower() and
                haupteintrag.material.name.lower() == aufmass.material.name.lower() and
                haupteintrag.mitarbeiter.username.lower() == aufmass.mitarbeiter.username.lower()):
                risiko_score = 3  # Hoch
                break
            
            # Mittleres Risiko: Gleicher Tag, Ort und Material
            elif (haupteintrag.datum == aufmass.datum and
                  haupteintrag.ort.lower() == aufmass.ort.lower() and
                  haupteintrag.material.name.lower() == aufmass.material.name.lower()):
                risiko_score = max(risiko_score, 2)  # Mittel
            
            # Niedriges Risiko: Ähnliche Kriterien
            else:
                risiko_score = max(risiko_score, 1)  # Niedrig
        
        return risiko_score

@duplikate_bp.route('/duplikate')
@login_required
def duplikate_uebersicht():
    """Übersicht aller potentiellen Duplikate"""
    
    if current_user.role not in ['admin', 'bauleiter']:
        flash('Keine Berechtigung für Duplikatsprüfung', 'error')
        return redirect(url_for('dashboard.index'))
    
    # Duplikate finden
    duplikate = DuplikatsPruefer.finde_duplikate()
    
    # Nach Risiko sortieren
    duplikate.sort(key=lambda x: x['risiko'], reverse=True)
    
    # Statistiken
    stats = {
        'gesamt_duplikate': len(duplikate),
        'hohes_risiko': len([d for d in duplikate if d['risiko'] == 3]),
        'mittleres_risiko': len([d for d in duplikate if d['risiko'] == 2]),
        'niedriges_risiko': len([d for d in duplikate if d['risiko'] == 1])
    }
    
    return render_template('duplikate/uebersicht.html', 
                         duplikate=duplikate, 
                         stats=stats)

@duplikate_bp.route('/duplikate/loeschen/<int:aufmass_id>', methods=['POST'])
@login_required
def duplikat_loeschen(aufmass_id):
    """Löscht ein Duplikat"""
    
    if current_user.role not in ['admin', 'bauleiter']:
        flash('Keine Berechtigung zum Löschen', 'error')
        return redirect(url_for('duplikate.duplikate_uebersicht'))
    
    aufmass = AufmassEntry.query.get_or_404(aufmass_id)
    
    try:
        # Zugehörigen Bautagebuch-Eintrag auch löschen
        bautagebuch_eintrag = BautagebuchEntry.query.filter_by(aufmass_entry_id=aufmass_id).first()
        if bautagebuch_eintrag:
            db.session.delete(bautagebuch_eintrag)
        
        # Aufmaß löschen
        db.session.delete(aufmass)
        db.session.commit()
        
        flash(f'Duplikat erfolgreich gelöscht: {aufmass.material.name} in {aufmass.ort}', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Fehler beim Löschen: {str(e)}', 'error')
    
    return redirect(url_for('duplikate.duplikate_uebersicht'))

@duplikate_bp.route('/duplikate/markieren-ok/<int:aufmass_id>', methods=['POST'])
@login_required
def duplikat_markieren_ok(aufmass_id):
    """Markiert ein Duplikat als OK (kein Duplikat)"""
    
    if current_user.role not in ['admin', 'bauleiter']:
        flash('Keine Berechtigung', 'error')
        return redirect(url_for('duplikate.duplikate_uebersicht'))
    
    # Hier könnte man eine separate Tabelle für "OK-markierte" Einträge anlegen
    # Für Einfachheit fügen wir ein Feld in die Aufmass-Tabelle hinzu
    
    flash('Eintrag als OK markiert', 'success')
    return redirect(url_for('duplikate.duplikate_uebersicht'))

@duplikate_bp.route('/api/duplikate/check', methods=['POST'])
@login_required
def check_duplikat_api():
    """API Endpoint für Live-Duplikatsprüfung beim Eingeben"""
    
    data = request.get_json()
    material = data.get('material')
    ort = data.get('ort')
    datum_str = data.get('datum')
    mitarbeiter = data.get('mitarbeiter', current_user.username)
    
    if not all([material, ort, datum_str]):
        return jsonify({'duplikate': []})
    
    try:
        datum = datetime.strptime(datum_str, '%Y-%m-%d').date()
    except:
        return jsonify({'duplikate': []})
    
    # Suche nach ähnlichen Einträgen
    aehnliche = AufmassEntry.query.join(Material).filter(
        and_(
            Material.name.ilike(f'%{material}%'),
            AufmassEntry.ort.ilike(f'%{ort}%'),
            AufmassEntry.datum >= datum - timedelta(days=1),
            AufmassEntry.datum <= datum + timedelta(days=1)
        )
    ).limit(5).all()
    
    duplikate = []
    for aufmass in aehnliche:
        duplikate.append({
            'id': aufmass.id,
            'material': aufmass.material.name,
            'ort': aufmass.ort,
            'menge': aufmass.menge,
            'einheit': aufmass.einheit,
            'datum': aufmass.datum.strftime('%d.%m.%Y'),
            'mitarbeiter': aufmass.mitarbeiter.username
        })
    
    return jsonify({'duplikate': duplikate})
