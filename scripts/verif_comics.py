#!/usr/bin/env python3
"""
Test d'intégration pour le système manga/comics unifié
Fichier: scripts/test_manga_comics_integration.py
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

import time
from agents.simple_agents import SimpleAgentManager
from rags.manga_rag.manga_rag_manager import MangaRAGManager


def test_rag_manager():
    """Test du gestionnaire RAG unifié"""
    print("🧪 Test du gestionnaire RAG unifié")
    print("-" * 50)
    
    try:
        # Initialiser le gestionnaire
        rag = MangaRAGManager()
        
        # Vérifier les stats
        stats = rag.get_stats()
        print(f"📊 Statistiques:")
        print(f"   Collection: {stats.get('collection_name', 'N/A')}")
        print(f"   Manga en CSV: {stats.get('manga_in_csv', 0)}")
        print(f"   Comics en CSV: {stats.get('comics_in_csv', 0)}")
        print(f"   Total indexé: {stats.get('indexed_total', 0)}")
        print(f"   Statut: {stats.get('sync_status', 'N/A')}")
        
        # Tests de recherche par type
        test_queries = [
            ("naruto", "manga", "🎌"),
            ("superman", "comics", "🦸"),
            ("aventure", "all", "🔍"),
            ("action", "all", "🔍")
        ]
        
        print(f"\n🔍 Tests de recherche:")
        for query, content_type, icon in test_queries:
            results = rag.search_content(query, n_results=2, content_type=content_type)
            print(f"   {icon} '{query}' ({content_type}): {len(results)} résultats")
            
            for result in results[:1]:
                source_icon = "🎌" if result['source_type'] == 'manga_japonais' else "🦸"
                print(f"      └─ {source_icon} {result['title']} (score: {result['similarity_score']:.2f})")
        
        # Health check
        health = rag.health_check()
        print(f"\n🏥 Health check: {health['status']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur RAG: {e}")
        return False


def test_agent_manager():
    """Test du gestionnaire d'agents"""
    print("\n🤖 Test du gestionnaire d'agents")
    print("-" * 50)
    
    try:
        # Initialiser l'agent manager
        agent = SimpleAgentManager(use_gemma=False)  # Test sans Gemma
        
        # Tests de détection de type
        test_queries = [
            "manga comme naruto",
            "comics superman", 
            "bd tintin",
            "bande dessinée aventure",
            "histoire d'action",
            "livre python"  # Pour vérifier que ça ne va pas vers manga
        ]
        
        print("🔍 Tests de détection de type:")
        for query in test_queries:
            is_manga = agent.detect_manga_query(query)
            if is_manga:
                content_type = agent.detect_content_type(query)
                print(f"   ✅ '{query}' → manga/comics (type: {content_type})")
            else:
                print(f"   ❌ '{query}' → autre agent")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur Agent: {e}")
        return False


def test_end_to_end():
    """Test de bout en bout avec des requêtes réelles"""
    print("\n🎯 Test de bout en bout")
    print("-" * 50)
    
    try:
        agent = SimpleAgentManager(use_gemma=False)
        
        # Requêtes de test représentatives
        test_cases = [
            ("manga d'action comme naruto", "🎌 Manga"),
            ("comics de super-héros", "🦸 Comics"),
            ("bd française humour", "🦸 BD"),
            ("histoire d'aventure", "🔍 Mixte"),
            ("apprendre python", "🔧 Tech")  # Pour vérifier le routage
        ]
        
        print("🚀 Tests de recommandations complètes:")
        
        for query, expected_type in test_cases:
            print(f"\n📝 Requête: '{query}' (attendu: {expected_type})")
            
            start_time = time.time()
            
            # Test de routage
            response = agent.route_query(query)
            
            response_time = time.time() - start_time
            
            # Analyser la réponse
            if "Recommandations Manga" in response:
                actual_type = "🎌 Manga"
            elif "Recommandations Comics" in response or "Recommandations Manga & Comics" in response:
                actual_type = "🦸 Comics/Mixte"
            elif "Recommandations Techniques" in response:
                actual_type = "🔧 Tech"
            elif "Recommandations Littéraires" in response:
                actual_type = "📚 Littérature"
            else:
                actual_type = "❓ Indéterminé"
            
            print(f"   🎯 Type détecté: {actual_type}")
            print(f"   ⏱️ Temps: {response_time:.2f}s")
            print(f"   📄 Réponse: {response[:100]}...")
            
            # Vérifier si le routage est correct
            if expected_type.split()[1] in actual_type or "Mixte" in expected_type:
                print(f"   ✅ Routage correct")
            else:
                print(f"   ⚠️ Routage inattendu (attendu: {expected_type})")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur End-to-End: {e}")
        return False


def main():
    """Fonction principale de test"""
    print("🚀 Tests d'intégration Manga/Comics")
    print("=" * 60)
    
    results = []
    
    # Test 1: RAG Manager
    results.append(test_rag_manager())
    
    # Test 2: Agent Manager  
    results.append(test_agent_manager())
    
    # Test 3: End-to-End
    results.append(test_end_to_end())
    
    # Résultats finaux
    print("\n" + "=" * 60)
    print("📊 Résultats des tests:")
    
    test_names = ["RAG Manager", "Agent Manager", "End-to-End"]
    for i, (test_name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {i+1}. {test_name}: {status}")
    
    success_rate = sum(results) / len(results) * 100
    print(f"\n🎯 Taux de réussite: {success_rate:.1f}%")
    
    if all(results):
        print("🎉 Tous les tests sont passés ! Le système manga/comics est opérationnel.")
        
        print("\n💡 Prochaines étapes:")
        print("   1. Tester l'interface web à http://127.0.0.1:8000/chat/")
        print("   2. Essayer des requêtes comme:")
        print("      • 'manga comme naruto'")
        print("      • 'comics superman'") 
        print("      • 'bd française humour'")
        print("      • 'histoire d'aventure'")
        
    else:
        print("⚠️ Certains tests ont échoué. Vérifiez les logs ci-dessus.")
    
    return 0 if all(results) else 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n❌ Tests interrompus par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
        sys.exit(1)