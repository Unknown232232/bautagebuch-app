import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

ALLOWED_EXTENSIONS = {
    'images': {'png', 'jpg', 'jpeg', 'gif'},
    'documents': {'pdf', 'doc', 'docx', 'txt'},
    'all': {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'txt'}
}

def allowed_file(filename, file_type='all'):
    """
    Prüft, ob eine Datei erlaubt ist
    
    Args:
        filename (str): Name der Datei
        file_type (str): Typ der erlaubten Dateien ('images', 'documents', 'all')
    
    Returns:
        bool: True wenn erlaubt, False wenn nicht
    """
    if not filename:
        return False
    
    extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    return extension in ALLOWED_EXTENSIONS.get(file_type, ALLOWED_EXTENSIONS['all'])

def save_uploaded_file(file, subfolder='uploads'):
    """
    Speichert eine hochgeladene Datei sicher
    
    Args:
        file: Werkzeug FileStorage Objekt
        subfolder (str): Unterordner im UPLOAD_FOLDER
    
    Returns:
        tuple: (success: bool, filename: str, error_message: str)
    """
    try:
        if not file or not file.filename:
            return False, None, "Keine Datei ausgewählt"
        
        if not allowed_file(file.filename):
            return False, None, "Dateityp nicht erlaubt"
        
        # Sicherer Dateiname
        original_filename = secure_filename(file.filename)
        file_extension = os.path.splitext(original_filename)[1]
        unique_filename = f"{uuid.uuid4().hex}{file_extension}"
        
        # Ordner erstellen falls nicht vorhanden
        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder)
        os.makedirs(upload_path, exist_ok=True)
        
        # Datei speichern
        file_path = os.path.join(upload_path, unique_filename)
        file.save(file_path)
        
        return True, unique_filename, None
        
    except Exception as e:
        return False, None, str(e)

def get_file_size_mb(file_path):
    """
    Gibt die Dateigröße in MB zurück
    
    Args:
        file_path (str): Pfad zur Datei
    
    Returns:
        float: Dateigröße in MB
    """
    try:
        size_bytes = os.path.getsize(file_path)
        return round(size_bytes / (1024 * 1024), 2)
    except:
        return 0

def delete_file(filename, subfolder='uploads'):
    """
    Löscht eine Datei sicher
    
    Args:
        filename (str): Name der zu löschenden Datei
        subfolder (str): Unterordner im UPLOAD_FOLDER
    
    Returns:
        bool: True wenn erfolgreich gelöscht
    """
    try:
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except:
        return False