#!/usr/bin/env python3
"""
Script de démarrage du serveur avec affichage des URLs
"""
import os
import sys
import subprocess

def display_server_info(host="127.0.0.1", port="8000"):
    """Affiche les informations du serveur"""
    base_url = f"http://{host}:{port}"
    
    print("")
    print("=" * 70)
    print("🚀 DUAL BOOK ADVISOR - Serveur Django")
    print("=" * 70)
    print("")
    
    # URLs principales
    print(f"🌐 Serveur web      : {base_url}")
    print(f"🔧 Admin Django     : {base_url}/admin/")
    print(f"📚 API Books        : {base_url}/api/books/")
    print(f"💬 API Chat         : {base_url}/api/chat/")
    print(f"🤖 LangChain Agents : {base_url}/api/chat/langchain/")
    print("")
    
    # Endpoints LangChain détaillés
    print("🤖 Endpoints LangChain disponibles :")
    endpoints = [
        ("Routage automatique", "/api/chat/langchain/"),
        ("Agent technique", "/api/chat/langchain/tech/"),
        ("Agent littéraire", "/api/chat/langchain/literature/"),
        ("Statut des agents", "/api/chat/langchain/status/")
    ]
    
    for desc, endpoint in endpoints:
        print(f"   • {desc:<20} : {base_url}{endpoint}")
    
    print("")
    print("📖 Documentation LangChain : README_LANGCHAIN.md")
    print("")
    print("🛑 Pour arrêter le serveur : Ctrl+C")
    print("=" * 70)
    print("")

def start_server():
    """Démarre le serveur Django"""
    # Parser les arguments
    host = "127.0.0.1"
    port = "8000"
    
    if len(sys.argv) > 1:
        addr = sys.argv[1]
        if ':' in addr:
            host, port = addr.rsplit(':', 1)
        else:
            port = addr
    
    # Afficher les infos
    display_server_info(host, port)
    
    # Lancer Django
    try:
        cmd = ["python", "manage.py", "runserver", f"{host}:{port}"]
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n🛑 Serveur arrêté")
    except FileNotFoundError:
        print("❌ Python non trouvé")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    start_server()