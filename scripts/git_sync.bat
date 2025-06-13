@echo off
REM Git Synchronization Batch Script für Windows
REM Automatisches Backup und Sync mit GitHub

echo ========================================
echo Bautagebuch App - Git Synchronization
echo ========================================

cd /d "%~dp0\.."

REM Überprüfe ob Python verfügbar ist
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python ist nicht installiert oder nicht im PATH verfügbar
    pause
    exit /b 1
)

REM Führe Git-Sync-Skript aus
echo Starte Git-Synchronisation...
python scripts/git_sync.py %1

if errorlevel 1 (
    echo ERROR: Git-Synchronisation fehlgeschlagen
    pause
    exit /b 1
) else (
    echo Git-Synchronisation erfolgreich abgeschlossen
)

echo.
echo Drücken Sie eine beliebige Taste zum Beenden...
pause >nul
