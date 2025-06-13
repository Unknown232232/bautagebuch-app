"""
Dashboard-Routen für verschiedene Benutzerrollen
"""
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import func
from app import db
from app.models.user import User
from app.models.aufmass import AufmassEntry
from app.models.material import Material

bp = Blueprint('dashboard', __name__)

@bp.route('/')
@bp.route('/dashboard')
@login_required
def index():
    """Hauptdashboard - weiterleitung basierend auf Benutzerrolle"""
    if current_user.is_admin():
        return redirect(url_for('dashboard.admin'))
    elif current_user.is_bauleiter():
        return redirect(url_for('dashboard.bauleiter'))
    else:
        return redirect(url_for('dashboard.mitarbeiter'))

@bp.route('/mitarbeiter')
@login_required
def mitarbeiter():
    """Dashboard für Mitarbeiter"""
    if not current_user.is_mitarbeiter():
        return redirect(url_for('dashboard.index'))
    
    # Statistiken für den aktuellen Benutzer
    heute = datetime.now().date()
    diese_woche = heute - timedelta(days=heute.weekday())
    
    aufmasse_heute = AufmassEntry.query.filter(
        AufmassEntry.mitarbeiter_id == current_user.id,
        func.date(AufmassEntry.datum) == heute
    ).count()
    
    aufmasse_woche = AufmassEntry.query.filter(
        AufmassEntry.mitarbeiter_id == current_user.id,
        func.date(AufmassEntry.datum) >= diese_woche
    ).count()
    
    # Letzte Einträge
    letzte_aufmasse = AufmassEntry.query.filter_by(
        mitarbeiter_id=current_user.id
    ).order_by(AufmassEntry.created_at.desc()).limit(5).all()
    
    stats = {
        'aufmasse_heute': aufmasse_heute,
        'aufmasse_woche': aufmasse_woche,
        'letzte_aufmasse': letzte_aufmasse
    }
    
    return render_template('dashboard/mitarbeiter.html', 
                         title='Mitarbeiter Dashboard', 
                         stats=stats)

@bp.route('/bauleiter')
@login_required
def bauleiter():
    """Dashboard für Bauleiter"""
    if not current_user.is_bauleiter():
        return redirect(url_for('dashboard.index'))
    
    # Umfassende Statistiken
    heute = datetime.now().date()
    diese_woche = heute - timedelta(days=heute.weekday())
    dieser_monat = heute.replace(day=1)
    
    # Gesamtstatistiken
    gesamt_aufmasse = AufmassEntry.query.count()
    aufmasse_heute = AufmassEntry.query.filter(
        func.date(AufmassEntry.datum) == heute
    ).count()
    aufmasse_woche = AufmassEntry.query.filter(
        func.date(AufmassEntry.datum) >= diese_woche
    ).count()
    aufmasse_monat = AufmassEntry.query.filter(
        func.date(AufmassEntry.datum) >= dieser_monat
    ).count()
    
    # Mitarbeiter-Aktivität
    aktive_mitarbeiter = db.session.query(
        User.username, 
        func.count(AufmassEntry.id).label('anzahl')
    ).join(AufmassEntry).filter(
        func.date(AufmassEntry.datum) >= diese_woche
    ).group_by(User.id).order_by(func.count(AufmassEntry.id).desc()).limit(5).all()
    
    # Häufigste Materialien
    top_materialien = db.session.query(
        Material.name,
        func.sum(AufmassEntry.menge).label('gesamt_menge')
    ).join(AufmassEntry).filter(
        func.date(AufmassEntry.datum) >= diese_woche
    ).group_by(Material.id).order_by(func.sum(AufmassEntry.menge).desc()).limit(5).all()
    
    # Letzte Aktivitäten
    letzte_aufmasse = AufmassEntry.query.order_by(
        AufmassEntry.created_at.desc()
    ).limit(10).all()
    
    stats = {
        'gesamt_aufmasse': gesamt_aufmasse,
        'aufmasse_heute': aufmasse_heute,
        'aufmasse_woche': aufmasse_woche,
        'aufmasse_monat': aufmasse_monat,
        'aktive_mitarbeiter': aktive_mitarbeiter,
        'top_materialien': top_materialien,
        'letzte_aufmasse': letzte_aufmasse
    }
    
    return render_template('dashboard/bauleiter.html', 
                         title='Bauleiter Dashboard', 
                         stats=stats)

@bp.route('/admin')
@login_required
def admin():
    """Dashboard für Administratoren"""
    if not current_user.is_admin():
        return redirect(url_for('dashboard.index'))
    
    # System-Statistiken
    gesamt_benutzer = User.query.count()
    aktive_benutzer = User.query.filter_by(is_active=True).count()
    gesamt_materialien = Material.query.count()
    gesamt_aufmasse = AufmassEntry.query.count()
    
    # Benutzer nach Rollen
    rollen_stats = db.session.query(
        User.role, 
        func.count(User.id).label('anzahl')
    ).group_by(User.role).all()
    
    # Verdächtige Duplikate (vereinfacht)
    verdaechtige_duplikate = db.session.query(
        AufmassEntry.datum,
        AufmassEntry.ort,
        AufmassEntry.material_id,
        func.count(AufmassEntry.id).label('anzahl')
    ).group_by(
        AufmassEntry.datum, 
        AufmassEntry.ort, 
        AufmassEntry.material_id
    ).having(func.count(AufmassEntry.id) > 1).count()
    
    # Letzte Benutzeraktivitäten
    letzte_logins = User.query.filter(
        User.last_login.isnot(None)
    ).order_by(User.last_login.desc()).limit(5).all()
    
    stats = {
        'gesamt_benutzer': gesamt_benutzer,
        'aktive_benutzer': aktive_benutzer,
        'gesamt_materialien': gesamt_materialien,
        'gesamt_aufmasse': gesamt_aufmasse,
        'rollen_stats': rollen_stats,
        'verdaechtige_duplikate': verdaechtige_duplikate,
        'letzte_logins': letzte_logins
    }
    
    return render_template('dashboard/admin.html', 
                         title='Admin Dashboard', 
                         stats=stats)
