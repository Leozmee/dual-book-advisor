#!/usr/bin/env python3
"""
Test des agents corrigés
"""
import os
import sys
import django
from pathlib import Path

# Configuration Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')

def test_agents():
    """Test des agents corrigés"""
    try:
        django.setup()
        
        from agents.simple_agents import SimpleAgentManager
        
        print("🧪 Test des agents corrigés")
        print("=" * 50)
        
        # Créer le manager
        agent_manager = SimpleAgentManager()
        
        # Test agent technique
        print("\n🔧 Test Agent Technique:")
        tech_query = "j'aimerais apprendre le C#"
        print(f"Requête: '{tech_query}'")
        
        tech_response = agent_manager.get_tech_recommendations(tech_query)
        print(f"Réponse: {tech_response[:200]}...")
        
        # Test agent littéraire
        print("\n📚 Test Agent Littéraire:")
        lit_query = "j'aimerais que tu me recommande des oeuvres comme harry potter"
        print(f"Requête: '{lit_query}'")
        
        lit_response = agent_manager.get_literature_recommendations(lit_query)
        print(f"Réponse: {lit_response[:200]}...")
        
        # Test routage
        print("\n🤖 Test Routage:")
        route_query = "je veux apprendre Python"
        print(f"Requête: '{route_query}'")
        
        route_response = agent_manager.route_query(route_query)
        print(f"Réponse: {route_response[:200]}...")
        
        print("\n✅ Tests terminés avec succès !")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_agents()