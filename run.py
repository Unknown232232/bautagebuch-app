# =============================================================================
# 1. KORRIGIERTE run.py
# =============================================================================

#!/usr/bin/env python3
"""
Bautagebuch App - Einstiegspunkt
"""
import os
import sys
import logging
from logging.config import fileConfig
from app import create_app, db
from flask_migrate import upgrade
from config import config

# Pfad hinzufügen
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Logging konfigurieren
if os.path.exists('logging.conf'):
    fileConfig('logging.conf')

logger = logging.getLogger(__name__)


def deploy():
    """Deploy function to set up database."""
    app = create_app()
    with app.app_context():
        # Import models INSIDE app context
        from app.models.user import User
        from app.models.material import Material
        from app.models.aufmass import AufmassEntry, AufmassDocument
        from app.models.bautagebuch import BautagebuchEntry, Bautagebuch, WochenExport

        logger.info("Importing models successful")

        # Create database tables
        logger.info("Creating database tables...")
        try:
            db.create_all()
            logger.info("Database tables created")
        except Exception as e:
            logger.error(f"Error creating database: {e}")
            if 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']:
                logger.info("Trying to create SQLite database file manually...")
                import sqlite3
                db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
                conn = sqlite3.connect(db_path)
                conn.close()
                db.create_all()
                logger.info("Database tables created successfully")
            else:
                raise

        # Create admin user if it doesn't exist
        logger.info("Checking for admin user...")
        try:
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                admin_password = app.config.get('DEFAULT_ADMIN_PASSWORD', 'admin123')
                admin = User(
                    username='admin',
                    email=app.config.get('ADMIN_EMAIL', 'admin@bautagebuch.de'),
                    role='admin'
                )
                admin.set_password(admin_password)
                db.session.add(admin)
                db.session.commit()
                logger.info(f"✓ Admin user created: admin / {admin_password}")
                if admin_password == 'admin123':
                    logger.warning("⚠️  Default password used! Change in production!")
            else:
                logger.info("✓ Admin user already exists")
        except Exception as e:
            logger.error(f"Error creating admin user: {e}")
            raise


def create_directories():
    """Create necessary directories."""
    directories = ['logs', 'instance', 'instance/uploads', 'backups']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"Created directory: {directory}")


# Create Flask app instance
app = create_app(os.getenv('FLASK_ENV', 'development'))


@app.route('/health')
def health_check():
    """Health check endpoint for monitoring."""
    try:
        # Check database connection
        db.session.execute('SELECT 1')
        return {'status': 'healthy', 'database': 'connected'}, 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {'status': 'unhealthy', 'error': str(e)}, 500


if __name__ == '__main__':
    # Create necessary directories
    create_directories()
    
    # Deploy database
    deploy()

    # Get configuration
    env = os.getenv('FLASK_ENV', 'development')
    debug_mode = env == 'development'
    
    logger.info(f"Starting Bautagebuch App in {env} mode")
    
    # Start app
    app.run(
        debug=debug_mode, 
        host=os.getenv('HOST', '0.0.0.0'), 
        port=int(os.getenv('PORT', 5000))
    )
