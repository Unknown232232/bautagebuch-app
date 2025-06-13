# Dark Mode Implementation - Bautagebuch App

## Übersicht

Diese Implementierung fügt einen vollständigen Dark Mode zur Bautagebuch App hinzu. Der Dark Mode unterstützt:

- ✅ Automatische Erkennung der Systemeinstellungen
- ✅ Manueller Toggle zwischen Light/Dark Mode
- ✅ Persistente Speicherung der Benutzereinstellung
- ✅ Sanfte Übergänge zwischen den Modi
- ✅ Vollständige Unterstützung aller UI-Komponenten
- ✅ Responsive Design
- ✅ Accessibility-Features

## Implementierte Dateien

### CSS
- `app/static/css/main.css` - Erweitert um Dark Mode CSS-Variablen und Styles

### JavaScript
- `app/static/js/darkmode.js` - Dark Mode Manager Klasse mit vollständiger Funktionalität

### Templates
- `app/templates/base.html` - Aktualisiert um Dark Mode JavaScript einzubinden
- `app/templates/darkmode_demo.html` - Demo-Seite zum Testen aller Komponenten

### Routes
- `app/routes/darkmode_demo.py` - Flask Route für die Demo-Seite
- `app/__init__.py` - Registrierung der neuen Route

## Funktionen

### 1. Automatischer Theme Toggle
Der Dark Mode Toggle wird automatisch in der Navigation hinzugefügt und zeigt:
- ☀️ Sonne-Icon im Light Mode
- 🌙 Mond-Icon im Dark Mode
- Smooth Animation beim Wechsel

### 2. CSS-Variablen System
```css
:root {
    /* Light Mode Variablen */
    --bg-primary: #ffffff;
    --text-primary: #111827;
    /* ... */
}

[data-theme="dark"] {
    /* Dark Mode Variablen */
    --bg-primary: #0f172a;
    --text-primary: #f8fafc;
    /* ... */
}
```

### 3. JavaScript API
```javascript
// Theme wechseln
window.DarkModeManager.toggleTheme();

// Spezifisches Theme setzen
window.DarkModeManager.setTheme('dark');
window.DarkModeManager.setTheme('light');

// Aktuelles Theme abfragen
const currentTheme = window.DarkModeManager.getCurrentTheme();

// Zu Systemeinstellung zurückkehren
window.DarkModeManager.resetToSystemPreference();
```

### 4. Event System
```javascript
// Theme-Änderungen überwachen
window.addEventListener('themeChanged', (e) => {
    console.log('Theme changed to:', e.detail.theme);
});

// Dark Mode Status prüfen
if (window.isDarkMode()) {
    // Dark Mode ist aktiv
}
```

## Unterstützte Komponenten

### UI-Elemente
- ✅ Navigation & Header
- ✅ Cards & Panels
- ✅ Buttons (alle Varianten)
- ✅ Forms & Inputs
- ✅ Tables
- ✅ Modals
- ✅ Alerts & Notifications
- ✅ Badges & Status Indicators
- ✅ Loading Spinners
- ✅ Footer

### Tailwind CSS Integration
Automatische Überschreibung von Tailwind-Klassen im Dark Mode:
- `bg-white` → Dark Mode Hintergrund
- `text-gray-900` → Dark Mode Text
- `border-gray-200` → Dark Mode Borders
- Alle Schatten werden angepasst

## Verwendung

### 1. Demo-Seite besuchen
```
http://localhost:5000/darkmode-demo
```

### 2. Toggle in der Navigation
Der Toggle-Button erscheint automatisch in der oberen Navigation neben dem Benutzerprofil.

### 3. Programmatische Steuerung
```javascript
// In Templates oder JavaScript
window.BautagebuchApp.darkMode.toggle();
window.BautagebuchApp.darkMode.setTheme('dark');
```

## Konfiguration

### Lokale Speicherung
- Schlüssel: `bautagebuch-theme`
- Werte: `'light'` oder `'dark'`
- Fallback: Systemeinstellung

### Systemeinstellung
Automatische Erkennung über:
```javascript
window.matchMedia('(prefers-color-scheme: dark)')
```

### Meta Theme Color
Automatische Anpassung der Browser-Theme-Farbe für mobile Geräte:
- Light Mode: `#2c5aa0`
- Dark Mode: `#0f172a`

## Accessibility

### Keyboard Navigation
- Tab-Navigation für Toggle-Button
- Enter/Space zum Aktivieren

### Screen Reader Support
- `aria-label` für Toggle-Button
- Semantische HTML-Struktur beibehalten

### Kontrast
- WCAG 2.1 AA konforme Farbkontraste
- Verbesserte Fokus-Indikatoren im Dark Mode

## Browser-Unterstützung

### Moderne Browser
- ✅ Chrome 76+
- ✅ Firefox 67+
- ✅ Safari 12.1+
- ✅ Edge 79+

### Fallbacks
- CSS Custom Properties Fallback
- LocalStorage Fallback
- Graceful Degradation ohne JavaScript

## Performance

### Optimierungen
- CSS-Variablen für minimale Repaints
- Debounced Theme-Wechsel
- Lazy Loading von Icons
- Minimale DOM-Manipulationen

### Ladezeit
- Dark Mode JavaScript: ~8KB (minified)
- CSS Overhead: ~3KB
- Keine externen Abhängigkeiten

## Anpassungen

### Eigene Farben hinzufügen
```css
:root {
    --custom-color: #your-light-color;
}

[data-theme="dark"] {
    --custom-color: #your-dark-color;
}
```

### Komponenten erweitern
```css
.my-component {
    background: var(--bg-primary);
    color: var(--text-primary);
    border: 1px solid var(--border-color);
    transition: var(--transition-theme);
}
```

### JavaScript Events
```javascript
// Eigene Theme-Handler
window.addEventListener('themeChanged', (e) => {
    // Eigene Logik hier
    updateMyComponent(e.detail.theme);
});
```

## Troubleshooting

### Toggle erscheint nicht
1. Prüfen Sie, ob `darkmode.js` geladen wird
2. Überprüfen Sie die Navigation-Struktur
3. Console auf JavaScript-Fehler prüfen

### Styles werden nicht angewendet
1. CSS-Variablen Browser-Support prüfen
2. `data-theme` Attribut im HTML überprüfen
3. CSS-Spezifität prüfen

### LocalStorage Probleme
1. Browser-Einstellungen für LocalStorage prüfen
2. Inkognito-Modus kann LocalStorage blockieren
3. Fallback auf Systemeinstellung funktioniert

## Zukünftige Erweiterungen

### Geplante Features
- [ ] Automatischer Theme-Wechsel basierend auf Tageszeit
- [ ] Mehr Theme-Varianten (z.B. High Contrast)
- [ ] Theme-Einstellungen im Benutzerprofil
- [ ] Animierte Theme-Übergänge
- [ ] Theme-spezifische Bilder/Icons

### Integration Möglichkeiten
- [ ] Chart.js Dark Mode Support
- [ ] PDF-Export mit Theme-Unterstützung
- [ ] E-Mail Templates mit Theme
- [ ] Print Styles für Dark Mode

## Support

Bei Problemen oder Fragen zur Dark Mode Implementierung:

1. Demo-Seite testen: `/darkmode-demo`
2. Browser-Console auf Fehler prüfen
3. CSS-Variablen im DevTools überprüfen
4. JavaScript-API in Console testen

---

**Entwickelt für Bautagebuch App - Borrmann Professionals**  
Version: 1.0  
Datum: Juni 2025
