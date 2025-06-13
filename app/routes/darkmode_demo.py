"""
Dark Mode Demo Route
Bautagebuch App - Borrmann Professionals
"""

from flask import Blueprint, render_template
from flask_login import login_required

# Create blueprint
darkmode_demo_bp = Blueprint('darkmode_demo', __name__)

@darkmode_demo_bp.route('/darkmode-demo')
@login_required
def demo():
    """
    Dark Mode Demo Page
    
    Zeigt eine Demo-Seite mit verschiedenen UI-Komponenten
    um den Dark Mode zu testen.
    """
    return render_template('darkmode_demo.html')
