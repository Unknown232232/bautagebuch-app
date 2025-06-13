# Sicherheitsdokumentation - Bautagebuch App

## Übersicht

Diese Dokumentation beschreibt die implementierten Sicherheitsfunktionen der Bautagebuch-Anwendung, die zum Schutz von Benutzerdaten und zur Gewährleistung der Anwendungssicherheit entwickelt wurden.

## Implementierte Sicherheitsfunktionen

### 1. Passwort-Sicherheit

#### Passwort-Hashing
- **Algorithmus**: PBKDF2 mit SHA-256
- **Iterationen**: 100.000 (erhöhte Sicherheit)
- **Salt**: Automatisch generiert für jeden Hash
- **Speicherung**: Nur gehashte Passwörter werden in der Datenbank gespeichert

#### Passwort-Stärke-Validierung
- Mindestlänge: 8 Zeichen (konfigurierbar)
- Muss enthalten:
  - Mindestens einen Kleinbuchstaben
  - Mindestens einen Großbuchstaben
  - Mindestens eine Zahl
  - Mindestens ein Sonderzeichen
- Prüfung auf häufig verwendete Muster (123456, password, etc.)

#### Passwort-Ablauf
- Konfigurierbare Passwort-Gültigkeitsdauer (Standard: 90 Tage)
- Automatische Weiterleitung zur Passwort-Änderung bei abgelaufenen Passwörtern
- Verhinderung der Wiederverwendung des aktuellen Passworts

### 2. Account-Sicherheit

#### Brute-Force-Schutz
- **Account-Sperrung**: Nach 5 fehlgeschlagenen Login-Versuchen
- **Sperrdauer**: 15 Minuten (konfigurierbar)
- **Automatische Entsperrung**: Nach Ablauf der Sperrdauer
- **Tracking**: Fehlgeschlagene Versuche werden pro Benutzer verfolgt

#### Session-Sicherheit
- **Sichere Cookies**: HTTPOnly, Secure, SameSite=Lax
- **Session-Timeout**: 8 Stunden (konfigurierbar)
- **Session-Invalidierung**: Bei Logout werden alle Session-Daten gelöscht
- **CSRF-Schutz**: Aktiviert mit 1-Stunden-Token-Gültigkeit

### 3. Datenverschlüsselung

#### Symmetrische Verschlüsselung
- **Algorithmus**: Fernet (AES 128 in CBC-Modus mit HMAC)
- **Schlüsselverwaltung**: Automatische Generierung und sichere Speicherung
- **Anwendung**: Für sensible Daten wie persönliche Informationen

#### Schlüsselverwaltung
- **Speicherort**: `instance/encryption.key` (außerhalb der Versionskontrolle)
- **Berechtigungen**: Nur für Anwendungsbenutzer lesbar (600)
- **Rotation**: Manuell durch Administrator

### 4. Eingabevalidierung und Sanitization

#### Datenvalidierung
- **Benutzername**: Alphanumerisch, Unterstrich, Bindestrich (3-30 Zeichen)
- **E-Mail**: RFC-konforme E-Mail-Adressvalidierung
- **XSS-Schutz**: Entfernung gefährlicher Zeichen und Skripte

#### Input Sanitization
- Automatische Bereinigung aller Benutzereingaben
- Entfernung von HTML-Tags und JavaScript-Code
- Schutz vor SQL-Injection durch ORM-Verwendung

### 5. Audit-Logging

#### Sicherheitsereignisse
- **Login-Versuche**: Erfolgreiche und fehlgeschlagene Anmeldungen
- **Passwort-Änderungen**: Zeitstempel und Benutzer-IP
- **Administrative Aktionen**: Benutzererstellung, Rollenänderungen
- **Sicherheitsverletzungen**: Verdächtige Aktivitäten

#### Log-Format
```
YYYY-MM-DD HH:MM:SS - LEVEL - EVENT_TYPE - Details
```

#### Log-Speicherung
- **Datei**: `logs/security_audit.log`
- **Rotation**: Automatisch bei Größenüberschreitung
- **Aufbewahrung**: Konfigurierbar (Standard: 30 Tage)

### 6. HTTP-Sicherheitsheader

#### Implementierte Header
- **X-Content-Type-Options**: nosniff
- **X-Frame-Options**: DENY
- **X-XSS-Protection**: 1; mode=block
- **Strict-Transport-Security**: max-age=31536000; includeSubDomains
- **Referrer-Policy**: strict-origin-when-cross-origin
- **Content-Security-Policy**: Restriktive CSP-Richtlinien
- **Permissions-Policy**: Deaktivierung unnötiger Browser-APIs

### 7. Rate Limiting

#### Implementierte Limits
- **Login-Versuche**: 10 pro Minute
- **Passwort-Änderungen**: 5 pro Minute
- **Allgemeine API**: 100 pro Stunde (konfigurierbar)

#### Backend
- **Speicher**: Redis (Produktion) oder Memory (Entwicklung)
- **Sliding Window**: Gleitende Zeitfenster für präzise Kontrolle

## Konfiguration

### Umgebungsvariablen

```bash
# Passwort-Sicherheit
PASSWORD_MIN_LENGTH=8
PASSWORD_MAX_AGE_DAYS=90

# Account-Sicherheit
ACCOUNT_LOCKOUT_ATTEMPTS=5
ACCOUNT_LOCKOUT_DURATION=15

# Verschlüsselung
ENCRYPTION_KEY_FILE=instance/encryption.key

# Session-Sicherheit
SESSION_COOKIE_SECURE=true
WTF_CSRF_ENABLED=true
```

### Produktionseinstellungen

```python
# Sichere Cookie-Einstellungen
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# HTTPS erzwingen
PREFERRED_URL_SCHEME = 'https'
```

## Sicherheitsrichtlinien

### Passwort-Richtlinien
1. Mindestens 8 Zeichen Länge
2. Kombination aus Groß-/Kleinbuchstaben, Zahlen und Sonderzeichen
3. Keine Wiederverwendung der letzten Passwörter
4. Regelmäßige Passwort-Änderung (alle 90 Tage)

### Benutzerkonten-Richtlinien
1. Eindeutige Benutzernamen
2. Gültige E-Mail-Adressen erforderlich
3. Rollenbasierte Zugriffskontrolle
4. Automatische Kontosperrung bei verdächtigen Aktivitäten

### Datenverarbeitung
1. Minimale Datensammlung (Privacy by Design)
2. Verschlüsselung sensibler Daten
3. Sichere Datenübertragung (HTTPS)
4. Regelmäßige Sicherheitsaudits

## Wartung und Überwachung

### Regelmäßige Aufgaben
- [ ] Überprüfung der Sicherheitslogs
- [ ] Aktualisierung der Abhängigkeiten
- [ ] Passwort-Richtlinien überprüfen
- [ ] Verschlüsselungsschlüssel rotieren

### Monitoring
- Überwachung fehlgeschlagener Login-Versuche
- Analyse von Sicherheitsereignissen
- Performance-Monitoring der Sicherheitsfunktionen
- Automatische Benachrichtigungen bei kritischen Ereignissen

## Incident Response

### Bei Sicherheitsvorfällen
1. **Sofortige Maßnahmen**
   - Betroffene Konten sperren
   - Verdächtige IP-Adressen blockieren
   - Sicherheitslogs analysieren

2. **Untersuchung**
   - Umfang des Vorfalls bestimmen
   - Betroffene Daten identifizieren
   - Ursache ermitteln

3. **Wiederherstellung**
   - Sicherheitslücken schließen
   - Systeme wiederherstellen
   - Benutzer informieren

4. **Nachbereitung**
   - Incident dokumentieren
   - Sicherheitsmaßnahmen verbessern
   - Schulungen durchführen

## Compliance und Standards

### Eingehaltene Standards
- **OWASP Top 10**: Schutz vor den häufigsten Web-Sicherheitsrisiken
- **GDPR/DSGVO**: Datenschutz-Grundverordnung
- **BSI Grundschutz**: IT-Sicherheitsstandards

### Sicherheitstests
- Regelmäßige Penetrationstests
- Automatisierte Sicherheitsscans
- Code-Reviews mit Fokus auf Sicherheit
- Dependency-Vulnerability-Scans

## Kontakt

Bei Sicherheitsfragen oder -vorfällen wenden Sie sich an:
- **Security Team**: security@bautagebuch.de
- **Administrator**: admin@bautagebuch.de

---

**Letzte Aktualisierung**: 2025-06-13
**Version**: 1.0
