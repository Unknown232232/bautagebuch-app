"""
API Routes für AJAX-Anfragen
"""
import logging
from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from app import db, cache
from app.models.material import Material
from app.models.aufmass import AufmassEntry
from app.models.user import User
from sqlalchemy import func
from datetime import datetime, timedelta

api_bp = Blueprint('api', __name__)
logger = logging.getLogger(__name__)


@api_bp.route('/material/<int:material_id>')
@login_required
@cache.cached(timeout=300)  # Cache for 5 minutes
def get_material(material_id):
    """Get material information for AJAX requests."""
    try:
        material = Material.query.get_or_404(material_id)
        return jsonify({
            'success': True,
            'material': {
                'id': material.id,
                'name': material.name,
                'description': material.beschreibung,
                'unit': material.einheit,
                'category': material.kategorie
            }
        })
    except Exception as e:
        logger.error(f"Error fetching material {material_id}: {e}")
        return jsonify({'success': False, 'error': 'Material nicht gefunden'}), 404


@api_bp.route('/dashboard/stats')
@login_required
@cache.cached(timeout=60)  # Cache for 1 minute
def dashboard_stats():
    """Get dashboard statistics."""
    try:
        # Base query depending on user role
        if current_user.is_admin():
            base_query = AufmassEntry.query
        elif current_user.is_bauleiter():
            # Bauleiter can see all entries (could be filtered by project in future)
            base_query = AufmassEntry.query
        else:
            # Mitarbeiter can only see their own entries
            base_query = AufmassEntry.query.filter_by(mitarbeiter_id=current_user.id)

        # Calculate statistics
        total_entries = base_query.count()
        
        # Entries this month
        start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        entries_this_month = base_query.filter(AufmassEntry.created_at >= start_of_month).count()
        
        # Entries today
        start_of_day = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        entries_today = base_query.filter(AufmassEntry.created_at >= start_of_day).count()
        
        # Active materials count
        active_materials = Material.query.filter_by(ist_aktiv=True).count()
        
        # Recent entries (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        recent_entries = base_query.filter(AufmassEntry.created_at >= week_ago).count()
        
        stats = {
            'total_entries': total_entries,
            'entries_this_month': entries_this_month,
            'entries_today': entries_today,
            'active_materials': active_materials,
            'recent_entries': recent_entries
        }
        
        return jsonify({'success': True, 'stats': stats})
        
    except Exception as e:
        logger.error(f"Error fetching dashboard stats: {e}")
        return jsonify({'success': False, 'error': 'Fehler beim Laden der Statistiken'}), 500


@api_bp.route('/search/suggestions')
@login_required
@cache.cached(timeout=3600)  # Cache for 1 hour
def search_suggestions():
    """Get search suggestions for autocomplete."""
    try:
        query_type = request.args.get('type', 'ort')
        
        if query_type == 'ort':
            # Get unique locations
            suggestions = db.session.query(AufmassEntry.ort).distinct().limit(20).all()
            suggestions = [s[0] for s in suggestions if s[0]]
            
        elif query_type == 'raumnummer':
            # Get unique room numbers
            suggestions = db.session.query(AufmassEntry.raumnummer).distinct().limit(20).all()
            suggestions = [s[0] for s in suggestions if s[0]]
            
        else:
            suggestions = []
            
        return jsonify({'success': True, 'suggestions': suggestions})
        
    except Exception as e:
        logger.error(f"Error fetching suggestions: {e}")
        return jsonify({'success': False, 'error': 'Fehler beim Laden der Vorschläge'}), 500


@api_bp.route('/aufmass/validate', methods=['POST'])
@login_required
def validate_aufmass():
    """Validate aufmass data before submission."""
    try:
        data = request.get_json()
        
        errors = []
        
        # Validate material
        if not data.get('material_id'):
            errors.append('Material ist erforderlich')
        else:
            material = Material.query.get(data['material_id'])
            if not material or not material.ist_aktiv:
                errors.append('Ungültiges Material ausgewählt')
        
        # Validate location
        if not data.get('ort') or len(data['ort'].strip()) < 2:
            errors.append('Ort muss mindestens 2 Zeichen lang sein')
        
        # Validate quantity
        try:
            menge = float(data.get('menge', 0))
            if menge <= 0:
                errors.append('Menge muss größer als 0 sein')
        except (ValueError, TypeError):
            errors.append('Ungültige Mengenangabe')
        
        # Check for potential duplicates
        if not errors:
            duplicate_check = AufmassEntry.query.filter_by(
                material_id=data['material_id'],
                ort=data['ort'],
                mitarbeiter_id=current_user.id
            ).filter(
                AufmassEntry.created_at >= datetime.now() - timedelta(hours=1)
            ).first()
            
            if duplicate_check:
                errors.append('Ähnlicher Eintrag wurde in der letzten Stunde bereits erstellt')
        
        return jsonify({
            'success': len(errors) == 0,
            'errors': errors
        })
        
    except Exception as e:
        logger.error(f"Error validating aufmass: {e}")
        return jsonify({'success': False, 'errors': ['Validierungsfehler']}), 500


@api_bp.route('/user/activity')
@login_required
def user_activity():
    """Get user activity data."""
    try:
        # Get activity for current user or all users (admin only)
        if current_user.is_admin() and request.args.get('all') == 'true':
            # Admin can see all user activity
            activity_data = db.session.query(
                User.username,
                func.count(AufmassEntry.id).label('entry_count'),
                func.max(AufmassEntry.created_at).label('last_activity')
            ).outerjoin(AufmassEntry).group_by(User.id).all()
            
            activity = [
                {
                    'username': row.username,
                    'entry_count': row.entry_count,
                    'last_activity': row.last_activity.isoformat() if row.last_activity else None
                }
                for row in activity_data
            ]
        else:
            # Regular users see only their own activity
            entry_count = AufmassEntry.query.filter_by(mitarbeiter_id=current_user.id).count()
            last_entry = AufmassEntry.query.filter_by(mitarbeiter_id=current_user.id)\
                .order_by(AufmassEntry.created_at.desc()).first()
            
            activity = [{
                'username': current_user.username,
                'entry_count': entry_count,
                'last_activity': last_entry.created_at.isoformat() if last_entry else None
            }]
        
        return jsonify({'success': True, 'activity': activity})
        
    except Exception as e:
        logger.error(f"Error fetching user activity: {e}")
        return jsonify({'success': False, 'error': 'Fehler beim Laden der Benutzeraktivität'}), 500


@api_bp.route('/materials/search')
@login_required
@cache.cached(timeout=300)
def search_materials():
    """Search materials for autocomplete."""
    try:
        query = request.args.get('q', '').strip()
        
        if len(query) < 2:
            return jsonify({'success': True, 'materials': []})
        
        materials = Material.query.filter(
            Material.ist_aktiv == True,
            Material.name.ilike(f'%{query}%')
        ).limit(10).all()
        
        material_list = [
            {
                'id': m.id,
                'name': m.name,
                'unit': m.einheit,
                'category': m.kategorie
            }
            for m in materials
        ]
        
        return jsonify({'success': True, 'materials': material_list})
        
    except Exception as e:
        logger.error(f"Error searching materials: {e}")
        return jsonify({'success': False, 'error': 'Fehler bei der Materialsuche'}), 500


@api_bp.route('/health')
def health():
    """API health check endpoint."""
    try:
        # Check database connection
        db.session.execute('SELECT 1')
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        })
    except Exception as e:
        logger.error(f"API health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


# Error handlers for API blueprint
@api_bp.errorhandler(404)
def api_not_found(error):
    return jsonify({'success': False, 'error': 'API Endpoint nicht gefunden'}), 404


@api_bp.errorhandler(500)
def api_internal_error(error):
    logger.error(f"API internal error: {error}")
    return jsonify({'success': False, 'error': 'Interner API Fehler'}), 500
