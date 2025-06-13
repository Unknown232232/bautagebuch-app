# Projektstruktur und Organisation

## 📁 Ordnerstruktur

Die Bautagebuch-App folgt einer klaren und organisierten Ordnerstruktur:

```
bautagebuch-app/
├── app/                          # Hauptanwendung
│   ├── forms/                    # WTForms Formulare
│   ├── models/                   # SQLAlchemy Datenmodelle
│   ├── routes/                   # Flask Routen/Views
│   ├── static/                   # Statische Dateien (CSS, JS, Bilder)
│   ├── templates/                # Jinja2 Templates
│   └── utils/                    # Hilfsfunktionen und Utilities
├── config/                       # Konfigurationsdateien
│   ├── config.py                 # Anwendungskonfiguration
│   └── logging.conf              # Logging-Konfiguration
├── data/                         # Datenbank und Datendateien (nicht in Git)
│   └── bautagebuch.db            # SQLite Datenbank
├── deployment/                   # Deployment-Konfigurationen
│   ├── docker-compose.yml        # Docker Compose Setup
│   ├── Dockerfile                # Docker Container Definition
│   ├── nginx.conf                # Nginx Konfiguration
│   └── monitoring/               # Monitoring Setup (Prometheus, Grafana)
├── docs/                         # Dokumentation
│   ├── api/                      # API Dokumentation
│   ├── user-guide/               # Benutzerhandbuch
│   ├── README.md                 # Projekt-Übersicht
│   ├── SECURITY.md               # Sicherheitsdokumentation
│   └── STRUCTURE.md              # Diese Datei
├── migrations/                   # Datenbank-Migrationen
├── scripts/                      # Utility-Skripte
│   ├── setup_security.py         # Sicherheits-Setup-Skript
│   ├── git_sync.py               # Git-Synchronisations-Skript
│   └── git_sync.bat              # Windows Batch-Skript für Git-Sync
├── security/                     # Sicherheitsdateien
│   └── SECURITY_CHECKLIST.md     # Sicherheits-Checkliste
├── tests/                        # Unit Tests
├── backups/                      # Backup-Verzeichnis
├── instance/                     # Instanz-spezifische Dateien
├── logs/                         # Log-Dateien
├── requirements.txt              # Python-Abhängigkeiten
├── run.py                        # Anwendungsstart
└── .env.example                  # Umgebungsvariablen-Vorlage
```

## 🔧 Konfiguration

### Konfigurationsdateien

Alle Konfigurationsdateien befinden sich im `config/` Ordner:

- **config.py**: Hauptkonfiguration der Flask-Anwendung
- **logging.conf**: Logging-Konfiguration

### Umgebungsvariablen

Erstellen Sie eine `.env` Datei basierend auf `.env.example`:

```bash
cp .env.example .env
```

Wichtige Umgebungsvariablen:
- `SECRET_KEY`: Geheimer Schlüssel für Flask
- `DATABASE_URL`: Datenbank-URL (optional, Standard: SQLite)
- `FLASK_ENV`: Umgebung (development/production)

## 💾 Datenbank

Die Datenbank befindet sich im `data/` Ordner und wird nicht in Git versioniert:

- **Entwicklung**: SQLite-Datei in `data/bautagebuch.db`
- **Produktion**: PostgreSQL (konfigurierbar über `DATABASE_URL`)

## 📝 Logging

Log-Dateien werden im `logs/` Ordner gespeichert:

- `bautagebuch.log`: Allgemeine Anwendungslogs
- `security_audit.log`: Sicherheits-Audit-Logs
- `git_sync.log`: Git-Synchronisations-Logs

## 🔄 Git-Synchronisation

### Automatische Synchronisation

Das Projekt enthält Skripte für automatische Git-Synchronisation:

```bash
# Python-Skript (plattformübergreifend)
python scripts/git_sync.py

# Windows Batch-Skript
scripts/git_sync.bat
```

### Verfügbare Aktionen

```bash
# Vollständige Synchronisation (Standard)
python scripts/git_sync.py sync

# Nur lokales Backup erstellen
python scripts/git_sync.py backup

# Git-Status überprüfen
python scripts/git_sync.py status
```

### Automatisierung

Für regelmäßige Synchronisation können Sie einen Cron-Job (Linux/Mac) oder Task Scheduler (Windows) einrichten:

**Linux/Mac (Crontab):**
```bash
# Alle 30 Minuten synchronisieren
*/30 * * * * cd /path/to/bautagebuch-app && python scripts/git_sync.py sync
```

**Windows (Task Scheduler):**
- Programm: `scripts/git_sync.bat`
- Arbeitsverzeichnis: Projektordner
- Zeitplan: Nach Bedarf

## 🔒 Sicherheit

### Ausgeschlossene Dateien

Die `.gitignore` Datei schließt folgende sensible Dateien aus:

- `.env` (Umgebungsvariablen)
- `data/` (Datenbankdateien)
- `logs/` (Log-Dateien)
- `instance/` (Instanz-spezifische Dateien)
- `__pycache__/` (Python Cache)
- `.venv/` (Virtuelle Umgebung)

### Backup-Strategie

- **Lokale Backups**: Automatisch im `backups/` Ordner
- **Remote Backups**: GitHub Repository
- **Retention**: 7 Tage für lokale Backups (konfigurierbar)

## 🚀 Deployment

### Entwicklung

```bash
python run.py
```

### Docker

```bash
cd deployment
docker-compose up -d
```

### Produktion

Siehe [Deployment-Dokumentation](deployment/README.md) für detaillierte Anweisungen.

## 📊 Monitoring

Das Projekt enthält vorkonfigurierte Monitoring-Tools im `deployment/monitoring/` Ordner:

- **Prometheus**: Metriken-Sammlung
- **Grafana**: Dashboards und Visualisierung

## 🧪 Tests

Tests befinden sich im `tests/` Ordner:

```bash
# Alle Tests ausführen
pytest

# Mit Coverage-Report
pytest --cov=app

# Spezifische Tests
pytest tests/test_auth.py
```

## 📚 Dokumentation

Die Dokumentation ist im `docs/` Ordner organisiert:

- **README.md**: Projekt-Übersicht
- **SECURITY.md**: Sicherheitsdokumentation
- **STRUCTURE.md**: Diese Strukturdokumentation
- **api/**: API-Dokumentation
- **user-guide/**: Benutzerhandbuch

## 🔧 Wartung

### Regelmäßige Aufgaben

1. **Git-Synchronisation**: Täglich oder nach größeren Änderungen
2. **Backup-Bereinigung**: Automatisch durch Git-Sync-Skript
3. **Log-Rotation**: Konfiguriert in `config/logging.conf`
4. **Sicherheitsupdates**: Regelmäßige Überprüfung der Dependencies

### Troubleshooting

Bei Problemen überprüfen Sie:

1. **Logs**: `logs/bautagebuch.log`
2. **Git-Status**: `git status`
3. **Konfiguration**: `config/config.py`
4. **Umgebungsvariablen**: `.env` Datei

## 📞 Support

Bei Fragen zur Projektstruktur:

- **Issues**: [GitHub Issues](../../issues)
- **Dokumentation**: Siehe `docs/` Ordner
- **Sicherheit**: Siehe `docs/SECURITY.md`
