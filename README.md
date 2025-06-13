# Bautagebuch App

Eine moderne Web-Anwendung für die Verwaltung von Bautagebüchern mit erweiterten Sicherheitsfunktionen.

## 📁 Projektstruktur

```
bautagebuch-app/
├── app/                          # Hauptanwendung
│   ├── forms/                    # WTForms Formulare
│   ├── models/                   # SQLAlchemy Datenmodelle
│   ├── routes/                   # Flask Routen/Views
│   ├── static/                   # Statische Dateien (CSS, JS, Bilder)
│   ├── templates/                # Jinja2 Templates
│   └── utils/                    # Hilfsfunktionen und Utilities
├── deployment/                   # Deployment-Konfigurationen
│   ├── docker-compose.yml        # Docker Compose Setup
│   ├── Dockerfile                # Docker Container Definition
│   ├── nginx.conf                # Nginx Konfiguration
│   └── monitoring/               # Monitoring Setup (Prometheus, Grafana)
├── docs/                         # Dokumentation
│   ├── api/                      # API Dokumentation
│   ├── user-guide/               # Benutzerhandbuch
│   ├── README.md                 # Projekt-Übersicht
│   └── SECURITY.md               # Sicherheitsdokumentation
├── migrations/                   # Datenbank-Migrationen
├── scripts/                      # Utility-Skripte
│   └── setup_security.py         # Sicherheits-Setup-Skript
├── security/                     # Sicherheitsdateien
│   └── SECURITY_CHECKLIST.md     # Sicherheits-Checkliste
├── tests/                        # Unit Tests
├── backups/                      # Backup-Verzeichnis
├── instance/                     # Instanz-spezifische Dateien
├── logs/                         # Log-Dateien
├── config.py                     # Anwendungskonfiguration
├── requirements.txt              # Python-Abhängigkeiten
├── run.py                        # Anwendungsstart
└── .env.example                  # Umgebungsvariablen-Vorlage
```

## 🚀 Schnellstart

### 1. Repository klonen
```bash
git clone <repository-url>
cd bautagebuch-app
```

### 2. Virtuelle Umgebung erstellen
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oder
venv\Scripts\activate     # Windows
```

### 3. Abhängigkeiten installieren
```bash
pip install -r requirements.txt
```

### 4. Sicherheitssetup ausführen
```bash
python scripts/setup_security.py
```

### 5. Umgebungsvariablen konfigurieren
```bash
cp .env.example .env
# .env Datei bearbeiten und anpassen
```

### 6. Datenbank initialisieren
```bash
flask db upgrade
```

### 7. Anwendung starten
```bash
python run.py
```

## 🔒 Sicherheitsfeatures

- **Passwort-Sicherheit**: PBKDF2-Hashing mit 100.000 Iterationen
- **Brute-Force-Schutz**: Account-Sperrung nach fehlgeschlagenen Versuchen
- **Datenverschlüsselung**: Fernet-Verschlüsselung für sensible Daten
- **Session-Sicherheit**: Sichere Cookies und CSRF-Schutz
- **Audit-Logging**: Umfassendes Sicherheits-Logging
- **Rate Limiting**: Schutz vor DoS-Angriffen
- **HTTP-Sicherheitsheader**: CSP, HSTS, X-Frame-Options

Weitere Details in der [Sicherheitsdokumentation](docs/SECURITY.md).

## 🐳 Docker Deployment

### Entwicklung
```bash
cd deployment
docker-compose up -d
```

### Produktion
```bash
cd deployment
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 📊 Monitoring

Das Projekt enthält vorkonfigurierte Monitoring-Tools:
- **Prometheus**: Metriken-Sammlung
- **Grafana**: Dashboards und Visualisierung

Zugriff über:
- Grafana: http://localhost:3000
- Prometheus: http://localhost:9090

## 🧪 Tests ausführen

```bash
# Alle Tests
pytest

# Mit Coverage
pytest --cov=app

# Spezifische Tests
pytest tests/test_auth.py
```

## 📚 Dokumentation

- [Sicherheitsdokumentation](docs/SECURITY.md)
- [API Dokumentation](docs/api/)
- [Benutzerhandbuch](docs/user-guide/)
- [Sicherheits-Checkliste](security/SECURITY_CHECKLIST.md)

## 🔧 Entwicklung

### Code-Stil
```bash
# Code formatieren
black app/
flake8 app/
```

### Neue Migration erstellen
```bash
flask db migrate -m "Beschreibung der Änderung"
flask db upgrade
```

### Logs anzeigen
```bash
tail -f logs/bautagebuch.log
tail -f logs/security_audit.log
```

## 🤝 Beitragen

1. Fork des Repositories erstellen
2. Feature-Branch erstellen (`git checkout -b feature/AmazingFeature`)
3. Änderungen committen (`git commit -m 'Add some AmazingFeature'`)
4. Branch pushen (`git push origin feature/AmazingFeature`)
5. Pull Request erstellen

## 📄 Lizenz

Dieses Projekt steht unter der MIT-Lizenz. Siehe [LICENSE](LICENSE) für Details.

## 📞 Support

Bei Fragen oder Problemen:
- Issue erstellen: [GitHub Issues](../../issues)
- Sicherheitsprobleme: security@bautagebuch.de
- Allgemeine Fragen: admin@bautagebuch.de

## 🔄 Changelog

### Version 2.0.0 (2025-06-13)
- ✅ Erweiterte Sicherheitsfunktionen implementiert
- ✅ Datenverschlüsselung hinzugefügt
- ✅ Audit-Logging implementiert
- ✅ Projektstruktur reorganisiert
- ✅ Docker-Support verbessert
- ✅ Monitoring-Integration

### Version 1.0.0
- ✅ Grundlegende Bautagebuch-Funktionalität
- ✅ Benutzerauthentifizierung
- ✅ Aufmaß-Verwaltung
- ✅ Reporting-Features
