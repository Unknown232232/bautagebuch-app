# Kabel-Kategorie-Verwaltung

Eine umfassende Lösung zur Verwaltung von Kabeltypen nach Kategorien für das Bautagebuch-System.

## 📋 Übersicht

Die Kabel-Kategorie-Verwaltung ermöglicht es, Kabeltypen strukturiert nach Kategorien zu organisieren und zu verwalten. Das System ist speziell für Elektroinstallationen im Bauwesen entwickelt und unterstützt verschiedene Kabelkategorien wie BMA (Brandmeldeanlage), ELA (Elektroakustische Anlage) und Netzwerk.

## 🚀 Funktionen

### Kernfunktionen
- **Kategorie-Verwaltung**: Erstellen und verwalten von Kabel-Kategorien
- **Kabeltyp-Verwaltung**: Hinzufügen und bearbeiten von Kabeltypen innerhalb von Kategorien
- **Suchfunktion**: Suche nach Kabeltypen über alle Kategorien hinweg
- **Bulk-Import**: Massenimport von Kabeltypen über Textformat
- **API-Zugriff**: RESTful API für externe Anwendungen

### Benutzeroberfläche
- **Übersichtliche Darstellung**: Kategorien mit zugehörigen Kabeltypen
- **Responsive Design**: Optimiert für Desktop und mobile Geräte
- **Schnell-Hinzufügen**: Direktes Hinzufügen von Kabeltypen über AJAX
- **Filterung**: Nach Kategorien und Suchbegriffen

### Verwaltung
- **Admin-Interface**: Vollständige Verwaltung für Administratoren
- **Benutzerrechte**: Unterschiedliche Zugriffsrechte je nach Benutzerrolle
- **Datenvalidierung**: Umfassende Validierung aller Eingaben
- **Fehlerbehandlung**: Robuste Fehlerbehandlung und Logging

## 📁 Dateistruktur

```
app/
├── models/
│   └── kabel_kategorie.py          # Datenmodelle und Service-Klassen
├── forms/
│   └── kabel_forms.py              # Formulare für Web-Interface
├── routes/
│   └── kabel.py                    # Web-Routen und API-Endpoints
└── templates/kabel/
    ├── index.html                  # Hauptübersicht
    ├── kategorien.html             # Kategorie-Verwaltung
    ├── kategorie_form.html         # Kategorie-Formular
    ├── kabeltyp_form.html          # Kabeltyp-Formular
    └── bulk_import.html            # Bulk-Import Interface

migrations/
└── add_kabel_kategorien.py         # Datenbank-Migration

kabel_helper.py                     # Kommandozeilen-Tool
```

## 🗄️ Datenbank-Schema

### Tabelle: `kabel_kategorien`
- `id` (Primary Key)
- `name` (Eindeutiger Kategorie-Name)
- `beschreibung` (Optionale Beschreibung)
- `ist_aktiv` (Aktiv/Inaktiv Status)
- `sortierung` (Sortierreihenfolge)
- `created_at`, `updated_at` (Zeitstempel)

### Tabelle: `kabeltypen`
- `id` (Primary Key)
- `name` (Kabeltyp-Name)
- `kategorie_id` (Foreign Key zu kabel_kategorien)
- `beschreibung` (Optionale Beschreibung)
- `technische_daten` (Technische Spezifikationen)
- `ist_aktiv` (Aktiv/Inaktiv Status)
- `sortierung` (Sortierreihenfolge)
- `created_at`, `updated_at` (Zeitstempel)

## 🔧 Installation und Setup

### 1. Migration ausführen
```bash
flask db upgrade
```

### 2. Beispiel-Daten werden automatisch eingefügt:
- **BMA**: Alu Rohr, 2x2x0,8 E30 Kabel, 2x2x0,8 Kabel rot
- **ELA**: Alu Rohr, 2x2x0,8 Kabel grau, 4x2x0,6 Grau
- **Netzwerk**: Cat6 UTP, Cat6A S/FTP, Glasfaser OM3

### 3. Navigation
Der Kabel-Link wird automatisch in der Navigation für Bauleiter und Admins angezeigt.

## 💻 Verwendung

### Web-Interface

#### Kabeltypen anzeigen
1. Navigieren Sie zu "Kabel" in der Hauptnavigation
2. Verwenden Sie die Suchfunktion oder Filter nach Kategorien
3. Klicken Sie auf Kabeltypen für Details

#### Neue Kategorie hinzufügen (Admin)
1. Gehen Sie zu "Kabel" → "Verwaltung"
2. Klicken Sie auf "Neue Kategorie"
3. Füllen Sie das Formular aus und speichern Sie

#### Neuen Kabeltyp hinzufügen (Admin)
1. Verwenden Sie das "Schnell hinzufügen" Formular auf der Hauptseite
2. Oder gehen Sie zu "Neuer Kabeltyp" für erweiterte Optionen

#### Bulk-Import (Admin)
1. Gehen Sie zu "Kabel" → "Bulk Import"
2. Wählen Sie die Ziel-Kategorie
3. Fügen Sie Kabeltypen ein (ein Typ pro Zeile)
4. Klicken Sie auf "Importieren"

### Kommandozeilen-Tool

Das `kabel_helper.py` Skript bietet direkten Zugriff auf die Kabel-API:

```bash
# Alle Kategorien anzeigen
python kabel_helper.py --list-kategorien

# Kabeltypen einer Kategorie anzeigen
python kabel_helper.py --kategorie BMA

# Nach Kabeltypen suchen
python kabel_helper.py --search "Alu"

# Neue Kategorie hinzufügen
python kabel_helper.py --add-kategorie "Sicherheit"

# Neuen Kabeltyp hinzufügen
python kabel_helper.py --add-kabeltyp BMA "Neues Kabel"

# JSON-Ausgabe
python kabel_helper.py --list-kategorien --json
```

## 🔌 API-Endpoints

### GET `/kabel/api/kategorien`
Gibt alle verfügbaren Kategorien zurück.

**Response:**
```json
{
  "success": true,
  "kategorien": [
    {
      "id": 1,
      "name": "BMA",
      "beschreibung": "Brandmeldeanlage",
      "kabeltypen_count": 3
    }
  ]
}
```

### GET `/kabel/api/kategorie/<kategorie_name>/kabeltypen`
Gibt alle Kabeltypen einer bestimmten Kategorie zurück.

**Response:**
```json
{
  "success": true,
  "kabeltypen": [
    {
      "id": 1,
      "name": "Alu Rohr",
      "beschreibung": "Aluminiumrohr für Kabelverlegung",
      "technische_daten": null
    }
  ]
}
```

### GET `/kabel/api/search?q=<suchbegriff>`
Sucht nach Kabeltypen über alle Kategorien.

**Response:**
```json
{
  "success": true,
  "ergebnisse": [
    {
      "kabeltyp": {
        "id": 1,
        "name": "Alu Rohr"
      },
      "kategorie": "BMA"
    }
  ]
}
```

### POST `/kabel/api/quick-add`
Fügt schnell einen neuen Kabeltyp hinzu.

**Request:**
```json
{
  "kategorie_name": "BMA",
  "kabeltyp_name": "Neues Kabel"
}
```

## 🎯 Verwendungsbeispiele

### Beispiel 1: Kabeltypen für BMA abrufen
```python
from kabel_helper import KabelHelper

helper = KabelHelper()
result = helper.get_kabeltypen_by_kategorie("BMA")

if result['success']:
    for kabeltyp in result['kabeltypen']:
        print(f"- {kabeltyp['name']}")
else:
    print(f"Fehler: {result['error']}")
```

### Beispiel 2: Neue Kategorie hinzufügen
```python
result = helper.add_kategorie(
    "Sicherheitstechnik", 
    "Kabel für Sicherheitsanlagen"
)

if result['success']:
    print("Kategorie erfolgreich hinzugefügt!")
```

### Beispiel 3: Kabeltypen suchen
```python
result = helper.search_kabeltypen("2x2x0,8")

if result['success']:
    for item in result['ergebnisse']:
        kabel = item['kabeltyp']
        kategorie = item['kategorie']
        print(f"{kabel['name']} (Kategorie: {kategorie})")
```

## 🔒 Berechtigungen

- **Mitarbeiter**: Nur Lesezugriff auf Kabeltypen
- **Bauleiter**: Lesezugriff auf alle Funktionen
- **Admin**: Vollzugriff auf alle Funktionen inkl. Verwaltung

## 🛠️ Erweiterungsmöglichkeiten

### Geplante Features
- **Export-Funktionen**: Excel/CSV Export von Kabeltypen
- **Bilder**: Hinzufügen von Bildern zu Kabeltypen
- **Preise**: Integration von Preisinformationen
- **Lieferanten**: Verknüpfung mit Lieferantendaten
- **Projekte**: Projektspezifische Kabeltypen

### Anpassungen
Das System ist modular aufgebaut und kann leicht erweitert werden:

1. **Neue Felder**: Einfach in den Modellen hinzufügen
2. **Neue Kategorien**: Über das Web-Interface oder API
3. **Custom Validierung**: In den Formularen anpassen
4. **Neue API-Endpoints**: In `routes/kabel.py` hinzufügen

## 🐛 Troubleshooting

### Häufige Probleme

**Problem**: Migration schlägt fehl
**Lösung**: Prüfen Sie die Datenbankverbindung und führen Sie `flask db init` aus

**Problem**: Kabel-Link erscheint nicht in Navigation
**Lösung**: Stellen Sie sicher, dass der Benutzer die Rolle "bauleiter" oder "admin" hat

**Problem**: API gibt Fehler zurück
**Lösung**: Prüfen Sie die Logs in `logs/` für detaillierte Fehlermeldungen

### Debugging
```bash
# Logs anzeigen
tail -f logs/app.log

# Datenbankstatus prüfen
flask db current

# Kabel-Helper testen
python kabel_helper.py --list-kategorien
```

## 📝 Changelog

### Version 1.0.0 (2025-01-14)
- Initiale Implementierung
- Grundlegende CRUD-Operationen
- Web-Interface mit Tailwind CSS
- API-Endpoints
- Kommandozeilen-Tool
- Beispiel-Daten für BMA, ELA und Netzwerk
- Bulk-Import Funktionalität
- Suchfunktion
- Admin-Verwaltung

## 🤝 Beitragen

1. Fork das Repository
2. Erstellen Sie einen Feature-Branch
3. Implementieren Sie Ihre Änderungen
4. Fügen Sie Tests hinzu
5. Erstellen Sie einen Pull Request

## 📄 Lizenz

Dieses Projekt ist Teil des Bautagebuch-Systems von Borrmann Professionals.
