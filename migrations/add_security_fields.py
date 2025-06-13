"""
Migration: Sicherheitsfelder zu User-Tabelle hinzufügen
Fügt erweiterte Sicherheitsfunktionen hinzu
"""

from alembic import op
import sqlalchemy as sa
from datetime import datetime, timezone

# revision identifiers
revision = 'add_security_fields'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    """Upgrade database schema - add security fields"""
    
    # Add new security columns to users table
    with op.batch_alter_table('users', schema=None) as batch_op:
        # Failed login tracking
        batch_op.add_column(sa.Column('failed_login_attempts', sa.Integer(), default=0))
        batch_op.add_column(sa.Column('account_locked_until', sa.DateTime(), nullable=True))
        
        # Password management
        batch_op.add_column(sa.Column('password_changed_at', sa.DateTime(), 
                                    default=lambda: datetime.now(timezone.utc)))

def downgrade():
    """Downgrade database schema - remove security fields"""
    
    # Remove security columns from users table
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('failed_login_attempts')
        batch_op.drop_column('account_locked_until')
        batch_op.drop_column('password_changed_at')
