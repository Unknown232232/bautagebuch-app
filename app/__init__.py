"""
Flask App Factory für Bautagebuch
"""
import os
import logging
import signal
import atexit
from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, logout_user
from flask_mail import Mail
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from dotenv import load_dotenv
from config.config import config
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from prometheus_flask_exporter import PrometheusMetrics

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()
cache = Cache()
limiter = Limiter(key_func=get_remote_address)

logger = logging.getLogger(__name__)


def create_app(config_name=None):
    """Application factory pattern."""
    # Load environment variables
    load_dotenv()

    app = Flask(__name__)

    # Configuration
    config_name = config_name or os.getenv('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # Initialize Sentry for error tracking
    if app.config.get('SENTRY_DSN'):
        sentry_sdk.init(
            dsn=app.config['SENTRY_DSN'],
            integrations=[
                FlaskIntegration(),
                SqlalchemyIntegration(),
            ],
            traces_sample_rate=1.0
        )

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    cache.init_app(app)
    limiter.init_app(app)

    # Security headers
    if not app.debug:
        Talisman(app, **{
            'force_https': False,  # Set to True in production with HTTPS
            'strict_transport_security': True,
            'content_security_policy': {
                'default-src': "'self'",
                'script-src': "'self' 'unsafe-inline' cdn.tailwindcss.com unpkg.com",
                'style-src': "'self' 'unsafe-inline' fonts.googleapis.com",
                'font-src': "'self' fonts.gstatic.com",
                'img-src': "'self' data:",
                'connect-src': "'self'"
            }
        })

    # Prometheus metrics
    if app.config.get('ENABLE_METRICS'):
        metrics = PrometheusMetrics(app)
        metrics.info('app_info', 'Application info', version='1.0.0')

    # Login manager configuration
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Bitte melden Sie sich an, um diese Seite zu sehen.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        from .models.user import User
        return User.query.get(int(user_id))

    # Import models to ensure they are registered with SQLAlchemy
    from .models import user, aufmass, bautagebuch, material, kabel_kategorie

    # Template context processors
    @app.context_processor
    def inject_csrf_token():
        from flask_wtf.csrf import generate_csrf
        return dict(csrf_token=generate_csrf)

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        logger.warning(f"404 error: {request.url}")
        return jsonify({'error': 'Seite nicht gefunden'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"500 error: {error}")
        db.session.rollback()
        return jsonify({'error': 'Interner Serverfehler'}), 500

    @app.errorhandler(403)
    def forbidden_error(error):
        logger.warning(f"403 error: {request.url}")
        return jsonify({'error': 'Zugriff verweigert'}), 403

    @app.errorhandler(429)
    def ratelimit_handler(e):
        logger.warning(f"Rate limit exceeded: {request.remote_addr}")
        return jsonify({'error': 'Zu viele Anfragen. Bitte versuchen Sie es später erneut.'}), 429

    # Security headers middleware
    @app.after_request
    def after_request(response):
        # Add security headers
        for header, value in app.config.get('SECURITY_HEADERS', {}).items():
            response.headers[header] = value
        
        # Add CSRF token to response headers for AJAX
        if hasattr(request, 'csrf_token'):
            response.headers['X-CSRFToken'] = request.csrf_token
            
        return response

    # Request logging
    @app.before_request
    def log_request_info():
        if not request.endpoint or request.endpoint == 'static':
            return
        logger.debug(f"Request: {request.method} {request.url} from {request.remote_addr}")

    # Register blueprints
    from .routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from .routes.dashboard import bp as dashboard_bp
    app.register_blueprint(dashboard_bp)

    from .routes.aufmass import aufmass_bp
    app.register_blueprint(aufmass_bp, url_prefix='/aufmass')

    from .routes.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    from .routes.wochenbericht import wochenbericht_bp
    app.register_blueprint(wochenbericht_bp, url_prefix='/wochenbericht')

    from .routes.duplikate import duplikate_bp
    app.register_blueprint(duplikate_bp, url_prefix='/duplikate')

    # API Blueprint for AJAX endpoints
    from .routes.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    # Kabel Blueprint for cable category management
    from .routes.kabel import kabel_bp
    app.register_blueprint(kabel_bp, url_prefix='/kabel')

    # Dark Mode Demo Blueprint
    from .routes.darkmode_demo import darkmode_demo_bp
    app.register_blueprint(darkmode_demo_bp)

    # Root route - redirect to login or dashboard
    @app.route('/')
    def index():
        from flask_login import current_user
        from flask import redirect, url_for
        if current_user.is_authenticated:
            return redirect(url_for('dashboard.index'))
        else:
            return redirect(url_for('auth.login'))

    # Create upload directory
    upload_dir = os.path.join(app.instance_path, 'uploads')
    os.makedirs(upload_dir, exist_ok=True)

    # Session cleanup on shutdown
    def cleanup_sessions():
        """Clean up all active sessions when the application shuts down."""
        try:
            from datetime import datetime
            invalidation_time = datetime.utcnow().isoformat()
            
            # Write invalidation time to file for persistence
            invalidation_file = app.config.get('SESSION_INVALIDATION_FILE', 'instance/session_invalidation.txt')
            os.makedirs(os.path.dirname(invalidation_file), exist_ok=True)
            
            with open(invalidation_file, 'w') as f:
                f.write(invalidation_time)
            
            app.config['SESSION_INVALIDATION_TIME'] = invalidation_time
            logger.info(f"All user sessions invalidated due to application shutdown at {invalidation_time}")
        except Exception as e:
            logger.error(f"Error during session cleanup: {e}")

    def signal_handler(signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, cleaning up sessions...")
        cleanup_sessions()
        logger.info("Application shutdown complete")

    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    # Register cleanup function to run at exit
    atexit.register(cleanup_sessions)

    # Load session invalidation time from file on startup
    def load_session_invalidation_time():
        """Load session invalidation time from file if it exists."""
        try:
            invalidation_file = app.config.get('SESSION_INVALIDATION_FILE', 'instance/session_invalidation.txt')
            if os.path.exists(invalidation_file):
                with open(invalidation_file, 'r') as f:
                    invalidation_time = f.read().strip()
                    if invalidation_time:
                        app.config['SESSION_INVALIDATION_TIME'] = invalidation_time
                        logger.info(f"Loaded session invalidation time from file: {invalidation_time}")
        except Exception as e:
            logger.error(f"Error loading session invalidation time: {e}")

    # Load invalidation time on startup
    load_session_invalidation_time()

    # Add session validation middleware
    @app.before_request
    def validate_session():
        """Validate session on each request."""
        if request.endpoint and request.endpoint.startswith('static'):
            return
            
        # Check if session should be invalidated
        invalidation_time = app.config.get('SESSION_INVALIDATION_TIME')
        if invalidation_time and 'login_time' in session:
            from datetime import datetime
            try:
                session_time = datetime.fromisoformat(session['login_time'])
                invalid_time = datetime.fromisoformat(invalidation_time)
                if session_time < invalid_time:
                    session.clear()
                    from flask_login import current_user
                    if current_user.is_authenticated:
                        logout_user()
                        from flask import flash, redirect, url_for
                        flash('Ihre Sitzung wurde aufgrund eines Anwendungsneustarts beendet. Bitte melden Sie sich erneut an.', 'warning')
                        return redirect(url_for('auth.login'))
            except (ValueError, KeyError):
                pass

    logger.info(f"Bautagebuch App initialized in {config_name} mode")
    return app
