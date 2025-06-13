# Bautagebuch App

Eine professionelle Web-Anwendung für die Verwaltung von Aufmaßen und Bautagebüchern, entwickelt für Borrmann Professionals.

## 🚀 Features

### Kernfunktionen
- **Aufmaß-Verwaltung**: Erfassung und Verwaltung von Aufmaßen mit Material, Ort, Menge und Dokumenten
- **Benutzerrollen**: Mitarbeiter, Bauleiter und Admin mit unterschiedlichen Berechtigungen
- **Dokumenten-Upload**: Bilder und Dokumente zu Aufmaß-Einträgen
- **Wochenberichte**: Automatische Generierung von Wochenberichten
- **Duplikate-Erkennung**: Automatische Erkennung und Verwaltung von Duplikaten

### Sicherheit
- **Authentifizierung**: Sichere Benutzeranmeldung mit Passwort-Hashing
- **Autorisierung**: Rollenbasierte Zugriffskontrolle
- **Brute-Force-Schutz**: Rate-Limiting für Login-Versuche
- **CSRF-Schutz**: Cross-Site Request Forgery Protection
- **Security Headers**: Umfassende HTTP-Security-Headers
- **Input-Validierung**: Client- und serverseitige Validierung

### Performance & Monitoring
- **Caching**: Redis-basiertes Caching für bessere Performance
- **Database-Indizes**: Optimierte Datenbankabfragen
- **Monitoring**: Prometheus & Grafana für Application-Monitoring
- **Logging**: Strukturiertes Logging mit verschiedenen Log-Levels
- **Health Checks**: Automatische Gesundheitsprüfungen

## 🛠 Technologie-Stack

### Backend
- **Flask 3.0**: Python Web-Framework
- **SQLAlchemy**: ORM für Datenbankoperationen
- **PostgreSQL**: Produktionsdatenbank (SQLite für Development)
- **Redis**: Caching und Session-Storage
- **Gunicorn**: WSGI HTTP Server

### Frontend
- **Bootstrap 5.3**: CSS Framework
- **Vanilla JavaScript**: Client-seitige Funktionalität
- **Jinja2**: Template Engine

### DevOps & Deployment
- **Docker**: Containerisierung
- **Docker Compose**: Multi-Container-Orchestrierung
- **Nginx**: Reverse Proxy und Load Balancer
- **Prometheus**: Metriken-Sammlung
- **Grafana**: Monitoring-Dashboard

### Testing & Quality
- **Pytest**: Test Framework
- **Factory Boy**: Test-Daten-Generierung
- **Coverage**: Code-Coverage-Analyse

## 📋 Voraussetzungen

### Development
- Python 3.11+
- Node.js 18+ (optional, für Frontend-Tools)
- Git

### Production
- Docker & Docker Compose
- 2GB+ RAM
- 10GB+ Speicherplatz

## 🚀 Installation & Setup

### Development Setup

1. **Repository klonen**
```bash
git clone <repository-url>
cd bautagebuch-app
```

2. **Virtual Environment erstellen**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oder
venv\Scripts\activate     # Windows
```

3. **Dependencies installieren**
```bash
pip install -r requirements.txt
```

4. **Umgebungsvariablen konfigurieren**
```bash
cp .env.example .env
# .env bearbeiten und Werte anpassen
```

5. **Datenbank initialisieren**
```bash
python run.py
```

6. **Anwendung starten**
```bash
python run.py
```

Die Anwendung ist dann unter `http://localhost:5000` erreichbar.

**Standard-Login:**
- Benutzername: `admin`
- Passwort: `admin123` (in Produktion ändern!)

### Production Deployment mit Docker

1. **Repository klonen**
```bash
git clone <repository-url>
cd bautagebuch-app
```

2. **Umgebungsvariablen konfigurieren**
```bash
cp .env.example .env.production
# .env.production bearbeiten
```

3. **SSL-Zertifikate erstellen** (optional)
```bash
mkdir ssl
# SSL-Zertifikate in ssl/ ablegen
```

4. **Services starten**
```bash
docker-compose up -d
```

5. **Services überprüfen**
```bash
docker-compose ps
docker-compose logs web
```

**Zugriff:**
- Anwendung: `http://localhost` (oder `https://localhost` mit SSL)
- Grafana: `http://localhost:3000` (admin/admin)
- Prometheus: `http://localhost:9090`

## 📁 Projektstruktur

```
bautagebuch-app/
├── app/                          # Hauptanwendung
│   ├── __init__.py              # App Factory
│   ├── models/                  # Datenmodelle
│   │   ├── user.py             # Benutzermodell
│   │   ├── material.py         # Materialmodell
│   │   ├── aufmass.py          # Aufmaßmodell
│   │   └── bautagebuch.py      # Bautagebuchmodell
│   ├── routes/                  # URL-Routen
│   │   ├── auth.py             # Authentifizierung
│   │   ├── aufmass.py          # Aufmaß-Verwaltung
│   │   ├── admin.py            # Admin-Panel
│   │   └── api.py              # API-Endpunkte
│   ├── forms/                   # WTForms
│   ├── templates/               # Jinja2-Templates
│   ├── static/                  # Statische Dateien
│   │   ├── css/                # Stylesheets
│   │   ├── js/                 # JavaScript
│   │   └── images/             # Bilder
│   └── utils/                   # Hilfsfunktionen
├── tests/                       # Tests
├── monitoring/                  # Monitoring-Konfiguration
├── docs/                        # Dokumentation
├── instance/                    # Instance-spezifische Dateien
├── migrations/                  # Datenbank-Migrationen
├── docker-compose.yml           # Docker Compose
├── Dockerfile                   # Docker Image
├── requirements.txt             # Python Dependencies
├── config.py                    # Konfiguration
└── run.py                       # Einstiegspunkt
```

## 🔧 Konfiguration

### Umgebungsvariablen

```bash
# Basis-Konfiguration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:pass@localhost/bautagebuch

# Security
SESSION_COOKIE_SECURE=true
WTF_CSRF_ENABLED=true

# Mail-Konfiguration
MAIL_SERVER=smtp.example.com
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-password

# Monitoring
SENTRY_DSN=your-sentry-dsn
ENABLE_METRICS=true

# Admin-Einstellungen
ADMIN_EMAIL=admin@example.com
DEFAULT_ADMIN_PASSWORD=secure-password
```

### Benutzerrollen

1. **Mitarbeiter**
   - Aufmaße erstellen und bearbeiten
   - Eigene Einträge anzeigen
   - Dokumente hochladen

2. **Bauleiter**
   - Alle Aufmaße der Baustelle anzeigen
   - Wochenberichte generieren
   - Duplikate verwalten

3. **Admin**
   - Vollständige Systemverwaltung
   - Benutzerverwaltung
   - Materialverwaltung
   - System-Monitoring

## 🧪 Testing

### Tests ausführen
```bash
# Alle Tests
pytest

# Mit Coverage
pytest --cov=app

# Spezifische Tests
pytest tests/test_models.py
pytest tests/test_auth.py
```

### Test-Datenbank
Tests verwenden eine In-Memory SQLite-Datenbank und sind vollständig isoliert.

## 📊 Monitoring & Logging

### Logs anzeigen
```bash
# Development
tail -f logs/bautagebuch.log

# Docker
docker-compose logs -f web
```

### Metriken
- **Prometheus**: `http://localhost:9090`
- **Grafana**: `http://localhost:3000`

### Health Checks
- **Application**: `/health`
- **API**: `/api/health`
- **Nginx**: `/nginx-health`

## 🔒 Sicherheit

### Produktions-Checkliste
- [ ] `SECRET_KEY` ändern
- [ ] Standard-Admin-Passwort ändern
- [ ] HTTPS aktivieren
- [ ] Firewall konfigurieren
- [ ] Backup-Strategie implementieren
- [ ] Monitoring einrichten
- [ ] Log-Rotation konfigurieren

### Security Features
- Passwort-Hashing mit bcrypt
- CSRF-Protection
- Rate-Limiting
- Input-Sanitization
- SQL-Injection-Schutz
- XSS-Protection
- Security Headers

## 🚀 Performance-Optimierung

### Database
- Indizes für häufige Abfragen
- Connection Pooling
- Query-Optimierung

### Caching
- Redis für Session-Storage
- Application-Level Caching
- Static File Caching

### Frontend
- Asset-Minification
- Gzip-Kompression
- Browser-Caching

## 🐛 Troubleshooting

### Häufige Probleme

**Database Connection Error**
```bash
# Prüfen ob PostgreSQL läuft
docker-compose ps db

# Logs prüfen
docker-compose logs db
```

**Permission Denied**
```bash
# File-Permissions prüfen
ls -la instance/uploads/

# Ownership korrigieren
sudo chown -R $USER:$USER instance/
```

**Memory Issues**
```bash
# Memory-Usage prüfen
docker stats

# Services neu starten
docker-compose restart
```

## 📚 API-Dokumentation

### Authentifizierung
Alle API-Endpunkte erfordern eine gültige Session oder API-Key.

### Endpunkte

#### Aufmaß-API
```
GET    /api/aufmass/           # Liste aller Aufmaße
POST   /api/aufmass/           # Neues Aufmaß erstellen
GET    /api/aufmass/{id}       # Aufmaß abrufen
PUT    /api/aufmass/{id}       # Aufmaß aktualisieren
DELETE /api/aufmass/{id}       # Aufmaß löschen
```

#### Material-API
```
GET    /api/materials/         # Liste aller Materialien
POST   /api/materials/         # Neues Material erstellen
GET    /api/materials/search   # Materialien suchen
```

#### Dashboard-API
```
GET    /api/dashboard/stats    # Dashboard-Statistiken
GET    /api/user/activity      # Benutzeraktivität
```

## 🤝 Contributing

1. Fork das Repository
2. Feature-Branch erstellen (`git checkout -b feature/amazing-feature`)
3. Änderungen committen (`git commit -m 'Add amazing feature'`)
4. Branch pushen (`git push origin feature/amazing-feature`)
5. Pull Request erstellen

### Code-Standards
- PEP 8 für Python-Code
- ESLint für JavaScript
- Pytest für Tests
- Type Hints verwenden

## 📄 Lizenz

Dieses Projekt ist proprietär und gehört Borrmann Professionals.

## 📞 Support

Bei Fragen oder Problemen:
- **Email**: support@borrmann-professionals.de
- **Issues**: GitHub Issues verwenden
- **Dokumentation**: `/docs` Verzeichnis

## 🔄 Changelog

### Version 1.0.0 (2025-01-13)
- Initiale Version
- Grundlegende Aufmaß-Verwaltung
- Benutzerauthentifizierung
- Admin-Panel
- Docker-Support
- Monitoring-Integration

---

**Entwickelt mit ❤️ für Borrmann Professionals**
