#!/usr/bin/env python3
"""
Kabel-Kategorie Helper Script

Dieses Skript stellt einfache Funktionen zur Verfügung, um mit der Kabel-Kategorie-API zu arbeiten.
Es kann sowohl als eigenständiges Skript als auch als importiertes Modul verwendet werden.

Beispiel-Nutzung:
    python kabel_helper.py --kategorie BMA
    python kabel_helper.py --search "Alu"
    python kabel_helper.py --list-kategorien
"""

import sys
import os
import argparse
import json
from typing import Dict, List, Optional

# Flask App Context für direkten Datenbankzugriff
def get_app_context():
    """Erstellt Flask App Context für Datenbankzugriff"""
    try:
        # Pfad zur App hinzufügen
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        from app import create_app
        from app.models.kabel_kategorie import KabelKategorieService
        
        app = create_app()
        return app, KabelKategorieService
    except ImportError as e:
        print(f"Fehler beim Importieren der App: {e}")
        return None, None


class KabelHelper:
    """Helper-Klasse für Kabel-Kategorie-Funktionen"""
    
    def __init__(self):
        self.app, self.service = get_app_context()
    
    def get_kabeltypen_by_kategorie(self, kategorie_name: str) -> Dict:
        """
        Gibt alle Kabeltypen einer bestimmten Kategorie zurück
        
        Args:
            kategorie_name (str): Name der Kategorie (z.B. "BMA", "ELA")
            
        Returns:
            dict: {'success': bool, 'kabeltypen': list, 'error': str}
        """
        if not self.app or not self.service:
            return {
                'success': False,
                'kabeltypen': [],
                'error': 'App-Kontext konnte nicht erstellt werden'
            }
        
        with self.app.app_context():
            return self.service.get_kabeltypen_by_kategorie(kategorie_name)
    
    def get_all_kategorien(self) -> Dict:
        """
        Gibt alle verfügbaren Kategorien zurück
        
        Returns:
            dict: {'success': bool, 'kategorien': list, 'error': str}
        """
        if not self.app or not self.service:
            return {
                'success': False,
                'kategorien': [],
                'error': 'App-Kontext konnte nicht erstellt werden'
            }
        
        with self.app.app_context():
            return self.service.get_all_kategorien()
    
    def search_kabeltypen(self, suchbegriff: str) -> Dict:
        """
        Sucht nach Kabeltypen über alle Kategorien hinweg
        
        Args:
            suchbegriff (str): Suchbegriff für Kabeltyp-Namen
            
        Returns:
            dict: {'success': bool, 'ergebnisse': list, 'error': str}
        """
        if not self.app or not self.service:
            return {
                'success': False,
                'ergebnisse': [],
                'error': 'App-Kontext konnte nicht erstellt werden'
            }
        
        with self.app.app_context():
            return self.service.search_kabeltypen(suchbegriff)
    
    def add_kategorie(self, name: str, beschreibung: Optional[str] = None) -> Dict:
        """
        Fügt eine neue Kategorie hinzu
        
        Args:
            name (str): Name der Kategorie
            beschreibung (str, optional): Beschreibung der Kategorie
            
        Returns:
            dict: {'success': bool, 'kategorie': dict, 'error': str}
        """
        if not self.app or not self.service:
            return {
                'success': False,
                'kategorie': None,
                'error': 'App-Kontext konnte nicht erstellt werden'
            }
        
        with self.app.app_context():
            return self.service.add_kategorie(name, beschreibung)
    
    def add_kabeltyp(self, kategorie_name: str, kabeltyp_name: str, 
                     beschreibung: Optional[str] = None, 
                     technische_daten: Optional[str] = None) -> Dict:
        """
        Fügt einen neuen Kabeltyp zu einer Kategorie hinzu
        
        Args:
            kategorie_name (str): Name der Kategorie
            kabeltyp_name (str): Name des Kabeltyps
            beschreibung (str, optional): Beschreibung des Kabeltyps
            technische_daten (str, optional): Technische Daten
            
        Returns:
            dict: {'success': bool, 'kabeltyp': dict, 'error': str}
        """
        if not self.app or not self.service:
            return {
                'success': False,
                'kabeltyp': None,
                'error': 'App-Kontext konnte nicht erstellt werden'
            }
        
        with self.app.app_context():
            return self.service.add_kabeltyp(kategorie_name, kabeltyp_name, beschreibung, technische_daten)


def print_kategorien(kategorien_data: List[Dict]):
    """Gibt Kategorien formatiert aus"""
    print("\n📁 Verfügbare Kategorien:")
    print("=" * 50)
    
    for kategorie in kategorien_data:
        print(f"• {kategorie['name']}")
        if kategorie.get('beschreibung'):
            print(f"  {kategorie['beschreibung']}")
        print(f"  Kabeltypen: {kategorie.get('kabeltypen_count', 0)}")
        print()


def print_kabeltypen(kategorie_name: str, kabeltypen_data: List[Dict]):
    """Gibt Kabeltypen einer Kategorie formatiert aus"""
    print(f"\n🔌 Kabeltypen in Kategorie '{kategorie_name}':")
    print("=" * 50)
    
    if not kabeltypen_data:
        print("Keine Kabeltypen in dieser Kategorie gefunden.")
        return
    
    for kabeltyp in kabeltypen_data:
        print(f"• {kabeltyp['name']}")
        if kabeltyp.get('beschreibung'):
            print(f"  📝 {kabeltyp['beschreibung']}")
        if kabeltyp.get('technische_daten'):
            print(f"  🔧 {kabeltyp['technische_daten']}")
        print()


def print_search_results(suchbegriff: str, ergebnisse: List[Dict]):
    """Gibt Suchergebnisse formatiert aus"""
    print(f"\n🔍 Suchergebnisse für '{suchbegriff}':")
    print("=" * 50)
    
    if not ergebnisse:
        print("Keine Ergebnisse gefunden.")
        return
    
    # Gruppiere nach Kategorien
    kategorien = {}
    for item in ergebnisse:
        kat_name = item['kategorie']
        if kat_name not in kategorien:
            kategorien[kat_name] = []
        kategorien[kat_name].append(item['kabeltyp'])
    
    for kat_name, kabeltypen in kategorien.items():
        print(f"\n📁 {kat_name}:")
        for kabeltyp in kabeltypen:
            print(f"  • {kabeltyp['name']}")
            if kabeltyp.get('beschreibung'):
                print(f"    📝 {kabeltyp['beschreibung']}")


def main():
    """Hauptfunktion für Kommandozeilen-Interface"""
    parser = argparse.ArgumentParser(
        description='Kabel-Kategorie Helper Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  %(prog)s --list-kategorien                 # Alle Kategorien anzeigen
  %(prog)s --kategorie BMA                   # Kabeltypen der Kategorie BMA anzeigen
  %(prog)s --search "Alu"                    # Nach Kabeltypen mit "Alu" suchen
  %(prog)s --add-kategorie "Sicherheit"      # Neue Kategorie hinzufügen
  %(prog)s --add-kabeltyp BMA "Neues Kabel" # Neuen Kabeltyp hinzufügen
        """
    )
    
    parser.add_argument('--list-kategorien', action='store_true',
                       help='Alle verfügbaren Kategorien anzeigen')
    
    parser.add_argument('--kategorie', type=str,
                       help='Kabeltypen einer bestimmten Kategorie anzeigen')
    
    parser.add_argument('--search', type=str,
                       help='Nach Kabeltypen suchen')
    
    parser.add_argument('--add-kategorie', type=str,
                       help='Neue Kategorie hinzufügen')
    
    parser.add_argument('--add-kabeltyp', nargs=2, metavar=('KATEGORIE', 'KABELTYP'),
                       help='Neuen Kabeltyp hinzufügen (Kategorie Kabeltyp)')
    
    parser.add_argument('--json', action='store_true',
                       help='Ausgabe als JSON formatieren')
    
    args = parser.parse_args()
    
    # Mindestens ein Argument erforderlich
    if not any([args.list_kategorien, args.kategorie, args.search, 
                args.add_kategorie, args.add_kabeltyp]):
        parser.print_help()
        return
    
    # Helper initialisieren
    helper = KabelHelper()
    
    try:
        if args.list_kategorien:
            result = helper.get_all_kategorien()
            if result['success']:
                if args.json:
                    print(json.dumps(result, indent=2, ensure_ascii=False))
                else:
                    print_kategorien(result['kategorien'])
            else:
                print(f"❌ Fehler: {result['error']}")
        
        elif args.kategorie:
            result = helper.get_kabeltypen_by_kategorie(args.kategorie)
            if result['success']:
                if args.json:
                    print(json.dumps(result, indent=2, ensure_ascii=False))
                else:
                    print_kabeltypen(args.kategorie, result['kabeltypen'])
            else:
                print(f"❌ Fehler: {result['error']}")
        
        elif args.search:
            result = helper.search_kabeltypen(args.search)
            if result['success']:
                if args.json:
                    print(json.dumps(result, indent=2, ensure_ascii=False))
                else:
                    print_search_results(args.search, result['ergebnisse'])
            else:
                print(f"❌ Fehler: {result['error']}")
        
        elif args.add_kategorie:
            result = helper.add_kategorie(args.add_kategorie)
            if result['success']:
                print(f"✅ Kategorie '{args.add_kategorie}' erfolgreich hinzugefügt!")
                if args.json:
                    print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                print(f"❌ Fehler: {result['error']}")
        
        elif args.add_kabeltyp:
            kategorie, kabeltyp = args.add_kabeltyp
            result = helper.add_kabeltyp(kategorie, kabeltyp)
            if result['success']:
                print(f"✅ Kabeltyp '{kabeltyp}' erfolgreich zu Kategorie '{kategorie}' hinzugefügt!")
                if args.json:
                    print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                print(f"❌ Fehler: {result['error']}")
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Abgebrochen durch Benutzer")
    except Exception as e:
        print(f"❌ Unerwarteter Fehler: {e}")


if __name__ == '__main__':
    main()
