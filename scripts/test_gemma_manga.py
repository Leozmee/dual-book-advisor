#!/usr/bin/env python3
"""
Script de test pour Gemma + Manga RAG
"""
import os
import sys
import django
from pathlib import Path

# Configuration Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

def test_system():
    """Test complet du système"""
    print("🧪 TEST COMPLET DU SYSTÈME")
    print("=" * 50)
    
    try:
        from agents.simple_agents import SimpleAgentManager
        
        # Test avec Gemma
        print("\n1. Test avec Gemma activé:")
        agent_gemma = SimpleAgentManager(use_gemma=True)
        
        status = agent_gemma.get_system_status()
        print(f"   Statut: {status}")
        
        # Test des requêtes
        queries = [
            ("tech", "apprendre Python débutant"),
            ("literature", "romans français classiques"),
            ("manga", "recommande moi des mangas comme Naruto")
        ]
        
        for agent_type, query in queries:
            print(f"\n2. Test {agent_type}: '{query}'")
            try:
                response = agent_gemma.get_agent_response(query, agent_type)
                print(f"   ✅ Longueur réponse: {len(response)} caractères")
                print(f"   📝 Début: {response[:100]}...")
            except Exception as e:
                print(f"   ❌ Erreur: {e}")
        
        # Test sans Gemma (fallback)
        print("\n3. Test sans Gemma (fallback):")
        agent_fallback = SimpleAgentManager(use_gemma=False)
        try:
            response = agent_fallback.get_agent_response("test query", "tech")
            print(f"   ✅ Fallback fonctionne: {len(response)} caractères")
        except Exception as e:
            print(f"   ❌ Erreur fallback: {e}")
        
        print("\n🎉 Tests terminés!")
        
    except Exception as e:
        print(f"❌ Erreur test système: {e}")

if __name__ == "__main__":
    test_system()
