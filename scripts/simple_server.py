#!/usr/bin/env python3
"""
Serveur Django simplifié pour tester
"""
import os
import sys
import django
from pathlib import Path

# Configuration Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')

def start_simple_server():
    """Démarre un serveur Django simplifié"""
    try:
        django.setup()
        
        from django.core.management import execute_from_command_line
        
        print("🚀 Démarrage du serveur Django...")
        print("📍 Adresse: http://127.0.0.1:8000")
        print("🛑 Pour arrêter: Ctrl+C")
        print("-" * 50)
        
        # Lancer le serveur
        execute_from_command_line(['manage.py', 'runserver', '127.0.0.1:8000', '--insecure'])
        
    except KeyboardInterrupt:
        print("\n🛑 Serveur arrêté")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    
    return True

if __name__ == "__main__":
    start_simple_server()