#!/usr/bin/env python3
"""
Git Synchronization Script für Bautagebuch App
Automatisches Backup und Sync mit GitHub
"""
import os
import sys
import subprocess
import datetime
import logging

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/git_sync.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def run_command(command, cwd=None):
    """Führt einen Git-Befehl aus und gibt das Ergebnis zurück."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip(), result.stderr.strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {command}")
        logger.error(f"Error: {e.stderr}")
        return None, e.stderr


def check_git_status():
    """Überprüft den Git-Status."""
    stdout, stderr = run_command("git status --porcelain")
    if stdout is None:
        return False, stderr
    
    if stdout:
        logger.info("Uncommitted changes found:")
        logger.info(stdout)
        return True, stdout
    else:
        logger.info("No uncommitted changes found")
        return False, None


def add_and_commit_changes():
    """Fügt alle Änderungen hinzu und committet sie."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Add all changes
    stdout, stderr = run_command("git add .")
    if stdout is None:
        return False, f"Failed to add changes: {stderr}"
    
    # Commit changes
    commit_message = f"Auto-commit: {timestamp}"
    stdout, stderr = run_command(f'git commit -m "{commit_message}"')
    if stdout is None:
        if "nothing to commit" in stderr:
            logger.info("Nothing to commit")
            return True, "Nothing to commit"
        return False, f"Failed to commit: {stderr}"
    
    logger.info(f"Changes committed: {commit_message}")
    return True, stdout


def push_to_github():
    """Pusht Änderungen zu GitHub."""
    # Überprüfe Remote-Repository
    stdout, stderr = run_command("git remote -v")
    if stdout is None:
        return False, f"Failed to check remotes: {stderr}"
    
    # Bestimme Remote-Name
    remote_name = "origin"
    if "bautagebuch-app" in stdout:
        remote_name = "bautagebuch-app"
    
    # Push to GitHub
    stdout, stderr = run_command(f"git push {remote_name} master")
    if stdout is None:
        return False, f"Failed to push: {stderr}"
    
    logger.info("Successfully pushed to GitHub")
    return True, stdout


def sync_with_github():
    """Hauptfunktion für GitHub-Synchronisation."""
    logger.info("Starting GitHub synchronization...")
    
    # Überprüfe Git-Status
    has_changes, status = check_git_status()
    
    if has_changes:
        # Committe Änderungen
        success, message = add_and_commit_changes()
        if not success:
            logger.error(f"Failed to commit changes: {message}")
            return False
    
    # Push zu GitHub
    success, message = push_to_github()
    if not success:
        logger.error(f"Failed to push to GitHub: {message}")
        return False
    
    logger.info("GitHub synchronization completed successfully")
    return True


def create_backup():
    """Erstellt ein lokales Backup."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"backup_{timestamp}.tar.gz"
    backup_path = os.path.join("backups", backup_name)
    
    # Erstelle Backup (ohne .git, __pycache__, etc.)
    exclude_patterns = [
        "--exclude=.git",
        "--exclude=__pycache__",
        "--exclude=*.pyc",
        "--exclude=.venv",
        "--exclude=venv",
        "--exclude=node_modules",
        "--exclude=data/*.db",
        "--exclude=logs/*.log"
    ]
    
    command = f"tar -czf {backup_path} {' '.join(exclude_patterns)} ."
    stdout, stderr = run_command(command)
    
    if stdout is None:
        logger.error(f"Failed to create backup: {stderr}")
        return False
    
    logger.info(f"Backup created: {backup_path}")
    return True


def cleanup_old_backups(retention_days=7):
    """Löscht alte Backups."""
    if not os.path.exists("backups"):
        return
    
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=retention_days)
    
    for filename in os.listdir("backups"):
        if filename.startswith("backup_") and filename.endswith(".tar.gz"):
            filepath = os.path.join("backups", filename)
            file_time = datetime.datetime.fromtimestamp(os.path.getctime(filepath))
            
            if file_time < cutoff_date:
                os.remove(filepath)
                logger.info(f"Removed old backup: {filename}")


def main():
    """Hauptfunktion."""
    if len(sys.argv) > 1:
        action = sys.argv[1].lower()
    else:
        action = "sync"
    
    if action == "sync":
        success = sync_with_github()
        if success:
            create_backup()
            cleanup_old_backups()
    elif action == "backup":
        create_backup()
        cleanup_old_backups()
    elif action == "status":
        check_git_status()
    else:
        print("Usage: python git_sync.py [sync|backup|status]")
        print("  sync   - Synchronize with GitHub (default)")
        print("  backup - Create local backup only")
        print("  status - Check Git status")
        sys.exit(1)


if __name__ == "__main__":
    main()
