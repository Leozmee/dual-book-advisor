#!/usr/bin/env python3
"""
Script de diagnostic pour identifier les problèmes du système
"""
import os
import sys
import subprocess
import django
from pathlib import Path

# Configuration Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

def check_django_config():
    """Vérifie la configuration Django"""
    print("🔍 Vérification de la configuration Django...")
    
    try:
        django.setup()
        print("✅ Django configuré correctement")
        
        # Vérifier les modèles
        from apps.books.models import TechBook, LiteratureBook
        from apps.accounts.models import User
        
        tech_count = TechBook.objects.count()
        lit_count = LiteratureBook.objects.count()
        user_count = User.objects.count()
        
        print(f"📊 Statistiques base de données:")
        print(f"   - Livres techniques: {tech_count}")
        print(f"   - Livres littéraires: {lit_count}")
        print(f"   - Utilisateurs: {user_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur Django: {e}")
        return False

def check_rag_system():
    """Vérifie le système RAG"""
    print("\n🔍 Vérification du système RAG...")
    
    try:
        from rags.tech_rag.tech_rag_manager import TechRAGManager
        from rags.literature_rag.literature_rag_manager import LiteratureRAGManager
        
        # Test RAG technique
        tech_rag = TechRAGManager()
        tech_stats = tech_rag.get_stats()
        print(f"📊 RAG Technique: {tech_stats}")
        
        # Test RAG littéraire
        lit_rag = LiteratureRAGManager()
        lit_stats = lit_rag.get_stats()
        print(f"📊 RAG Littéraire: {lit_stats}")
        
        # Test de recherche
        print("\n🧪 Test de recherche RAG...")
        tech_results = tech_rag.search_books("Python programming", n_results=2)
        print(f"   - Résultats techniques: {len(tech_results)} trouvés")
        
        lit_results = lit_rag.search_books("Tolstoy", n_results=2)
        print(f"   - Résultats littéraires: {len(lit_results)} trouvés")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur RAG: {e}")
        return False

def check_server_config():
    """Vérifie la configuration du serveur"""
    print("\n🔍 Vérification de la configuration serveur...")
    
    # Vérifier les ports disponibles
    import socket
    
    def is_port_available(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('127.0.0.1', port))
                return True
            except OSError:
                return False
    
    ports_to_check = [8000, 8080, 8001]
    available_ports = []
    
    for port in ports_to_check:
        if is_port_available(port):
            available_ports.append(port)
            print(f"✅ Port {port} disponible")
        else:
            print(f"❌ Port {port} occupé")
    
    if available_ports:
        print(f"💡 Ports recommandés: {available_ports}")
        return available_ports[0]
    else:
        print("⚠️ Aucun port standard disponible")
        return 8090

def test_simple_agents():
    """Test des agents simples"""
    print("\n🔍 Test des agents simples...")
    
    try:
        from agents.simple_agents import SimpleAgentManager
        
        agent_manager = SimpleAgentManager()
        
        # Test agent technique
        tech_response = agent_manager.get_tech_recommendations("Python programming")
        print(f"✅ Agent technique: {len(tech_response)} caractères de réponse")
        
        # Test agent littéraire
        lit_response = agent_manager.get_literature_recommendations("Tolstoy")
        print(f"✅ Agent littéraire: {len(lit_response)} caractères de réponse")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur agents: {e}")
        return False

def suggest_fixes():
    """Suggère des corrections"""
    print("\n🔧 Suggestions de correction:")
    
    print("1. Pour le serveur Django:")
    print("   python manage.py runserver 127.0.0.1:8000")
    print("   ou")
    print("   python start_server.py")
    
    print("\n2. Pour réinitialiser le RAG:")
    print("   python scripts/setup_rag.py --reset")
    
    print("\n3. Pour vérifier les données:")
    print("   python manage.py shell")
    print("   >>> from apps.books.models import TechBook, LiteratureBook")
    print("   >>> print(f'Tech: {TechBook.objects.count()}, Lit: {LiteratureBook.objects.count()}')")
    
    print("\n4. Pour tester les agents:")
    print("   python test_agents.py")

def main():
    """Fonction principale de diagnostic"""
    print("🚀 Diagnostic du système Dual Book Advisor")
    print("=" * 50)
    
    # Tests
    django_ok = check_django_config()
    rag_ok = check_rag_system()
    port = check_server_config()
    agents_ok = test_simple_agents()
    
    print("\n📊 Résumé du diagnostic:")
    print(f"   - Django: {'✅' if django_ok else '❌'}")
    print(f"   - RAG: {'✅' if rag_ok else '❌'}")
    print(f"   - Agents: {'✅' if agents_ok else '❌'}")
    print(f"   - Port recommandé: {port}")
    
    if not all([django_ok, rag_ok, agents_ok]):
        suggest_fixes()
    else:
        print("\n🎉 Système opérationnel!")
        print(f"Démarrez avec: python manage.py runserver 127.0.0.1:{port}")

if __name__ == "__main__":
    main()