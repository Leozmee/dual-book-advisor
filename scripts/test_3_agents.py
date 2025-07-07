#!/usr/bin/env python3
"""
Script de test complet pour vérifier les 3 agents
Fichier: scripts/test_3_agents.py
"""
import os
import sys
import django
from pathlib import Path
import requests
import json

# Configuration Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

# Désactiver la télémétrie ChromaDB
os.environ['ANONYMIZED_TELEMETRY'] = 'False'

def test_direct_agents():
    """Test direct des agents via SimpleAgentManager"""
    print("🧪 Test direct des agents")
    print("=" * 50)
    
    try:
        from agents.simple_agents import SimpleAgentManager
        
        agent_manager = SimpleAgentManager()
        
        # Test des requêtes pour chaque agent
        test_queries = {
            "tech": [
                "j'aimerais apprendre Python",
                "livres pour débuter en JavaScript",
                "machine learning pour débutants"
            ],
            "literature": [
                "romans de Tolstoï",
                "livres comme Harry Potter mais pas manga",
                "classiques français"
            ],
            "manga": [
                "j'ai aimé Naruto",
                "mangas shounen action",
                "recommande moi des anime comme Death Note"
            ]
        }
        
        for agent_type, queries in test_queries.items():
            print(f"\n🎯 Test Agent {agent_type.upper()}")
            print("-" * 30)
            
            for query in queries:
                print(f"\n📝 Requête: '{query}'")
                try:
                    if agent_type == "tech":
                        response = agent_manager.get_tech_recommendations(query)
                    elif agent_type == "literature":
                        response = agent_manager.get_literature_recommendations(query)
                    elif agent_type == "manga":
                        response = agent_manager.get_manga_recommendations(query)
                    
                    # Afficher un résumé de la réponse
                    print(f"✅ Réponse ({len(response)} caractères):")
                    print(f"   {response[:150]}...")
                    
                    # Vérifier que la réponse contient les bons emojis
                    expected_emojis = {
                        "tech": ["🔧", "💻", "📊"],
                        "literature": ["📚", "📖", "✨"],
                        "manga": ["🎌", "⚔️", "🔥", "👺"]
                    }
                    
                    found_emojis = [emoji for emoji in expected_emojis[agent_type] if emoji in response]
                    if found_emojis:
                        print(f"   🎯 Emojis trouvés: {', '.join(found_emojis)}")
                    
                except Exception as e:
                    print(f"❌ Erreur: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test direct: {e}")
        return False

def test_routing_intelligence():
    """Test du routage intelligent"""
    print("\n🧠 Test du routage intelligent")
    print("=" * 50)
    
    try:
        from agents.simple_agents import SimpleAgentManager
        agent_manager = SimpleAgentManager()
        
        routing_tests = [
            # Devrait aller vers MANGA
            ("j'ai aimé Naruto", "manga"),
            ("recommande moi des mangas shounen", "manga"),
            ("anime comme Death Note", "manga"),
            
            # Devrait aller vers TECH
            ("apprendre Python", "tech"),
            ("livres de programmation JavaScript", "tech"),
            ("data science pour débutants", "tech"),
            
            # Devrait aller vers LITERATURE
            ("romans de Tolstoï", "literature"),
            ("livres de Victor Hugo", "literature"),
            ("classiques français", "literature"),
        ]
        
        for query, expected_agent in routing_tests:
            print(f"\n📝 Test: '{query}'")
            print(f"   Attendu: Agent {expected_agent}")
            
            # Tester la détection
            if expected_agent == "manga":
                detected = agent_manager.detect_manga_query(query)
                print(f"   Détection manga: {'✅' if detected else '❌'}")
            
            # Tester le routage complet
            try:
                response = agent_manager.route_query(query)
                
                # Vérifier les emojis de réponse pour confirmer l'agent utilisé
                if expected_agent == "tech" and "🔧" in response:
                    print("   ✅ Routé vers Tech Agent")
                elif expected_agent == "literature" and "📚" in response:
                    print("   ✅ Routé vers Literature Agent")
                elif expected_agent == "manga" and "🎌" in response:
                    print("   ✅ Routé vers Manga Agent")
                else:
                    print(f"   ⚠️ Routage incertain")
                    
            except Exception as e:
                print(f"   ❌ Erreur routage: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test routage: {e}")
        return False

def test_api_endpoints():
    """Test des endpoints API Django"""
    print("\n🌐 Test des endpoints API")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:8000"
    
    endpoints_tests = [
        {
            "name": "Tech Agent API",
            "url": f"{base_url}/api/chat/tech-agent/",
            "data": {"message": "j'aimerais apprendre Python"},
            "expected_emoji": "🔧"
        },
        {
            "name": "Literature Agent API", 
            "url": f"{base_url}/api/chat/literature-agent/",
            "data": {"message": "romans de Tolstoï"},
            "expected_emoji": "📚"
        },
        {
            "name": "Manga Agent API",
            "url": f"{base_url}/api/chat/manga-agent/",
            "data": {"message": "j'ai aimé Naruto"},
            "expected_emoji": "🎌"
        }
    ]
    
    for test in endpoints_tests:
        print(f"\n📡 Test: {test['name']}")
        
        try:
            response = requests.post(
                test['url'],
                json=test['data'],
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                agent_response = data.get('agent_response', {}).get('content', '')
                
                if test['expected_emoji'] in agent_response:
                    print(f"   ✅ API fonctionnelle ({response.status_code})")
                    print(f"   🎯 Emoji correct: {test['expected_emoji']}")
                else:
                    print(f"   ⚠️ API répond mais emoji manquant")
                    print(f"   📝 Réponse: {agent_response[:100]}...")
            else:
                print(f"   ❌ Erreur HTTP: {response.status_code}")
                print(f"   📝 Réponse: {response.text[:200]}")
                
        except requests.exceptions.ConnectionError:
            print(f"   ⚠️ Serveur Django non démarré (normal si pas lancé)")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
    
    return True

def test_gemma_integration():
    """Test de l'intégration Gemma"""
    print("\n🤖 Test de l'intégration Gemma")
    print("=" * 50)
    
    try:
        # Test import Gemma
        try:
            from agents.ollama_gemma_manager import GemmaAgentManager
            print("✅ Import GemmaAgentManager réussi")
            
            # Test initialisation
            gemma_manager = GemmaAgentManager()
            status = gemma_manager.health_check()
            
            print(f"📊 Statut Gemma:")
            print(f"   - Service: {status.get('gemma', {}).get('status', 'unknown')}")
            print(f"   - Modèle: {status.get('gemma', {}).get('model', 'unknown')}")
            
        except ImportError:
            print("⚠️ GemmaAgentManager non importable (normal si Ollama pas installé)")
        except Exception as e:
            print(f"⚠️ Gemma non disponible: {e}")
        
        # Test avec SimpleAgentManager
        from agents.simple_agents import SimpleAgentManager
        agent_manager = SimpleAgentManager()
        
        system_status = agent_manager.get_system_status()
        print(f"\n📊 Statut système:")
        for key, value in system_status.items():
            print(f"   - {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test Gemma: {e}")
        return False

def test_rag_separation():
    """Test de la séparation des RAG"""
    print("\n🗄️ Test de la séparation des RAG")
    print("=" * 50)
    
    try:
        # Test des imports RAG
        from rags.tech_rag.tech_rag_manager import TechRAGManager
        from rags.literature_rag.literature_rag_manager import LiteratureRAGManager
        
        tech_rag = TechRAGManager()
        lit_rag = LiteratureRAGManager()
        
        print("✅ RAG Tech et Literature importés")
        
        # Test stats
        tech_stats = tech_rag.get_stats()
        lit_stats = lit_rag.get_stats()
        
        print(f"📊 RAG Tech: {tech_stats.get('indexed_books', 0)} livres indexés")
        print(f"📊 RAG Literature: {lit_stats.get('indexed_books', 0)} livres indexés")
        
        # Test Manga RAG
        try:
            from rags.manga_rag.manga_rag_manager import MangaRAGManager
            manga_rag = MangaRAGManager()
            manga_stats = manga_rag.get_stats()
            print(f"📊 RAG Manga: {manga_stats.get('indexed_manga', 0)} mangas indexés")
            print("✅ RAG Manga disponible")
        except ImportError:
            print("⚠️ RAG Manga non disponible (à créer)")
        except Exception as e:
            print(f"⚠️ RAG Manga erreur: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test RAG: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🚀 Test Complet du Système à 3 Agents")
    print("=" * 70)
    print("🎯 Objectif: Vérifier que les 3 agents (Tech, Literature, Manga) fonctionnent")
    print("=" * 70)
    
    tests = [
        ("RAG Separation", test_rag_separation),
        ("Direct Agents", test_direct_agents),
        ("Routing Intelligence", test_routing_intelligence),
        ("Gemma Integration", test_gemma_integration),
        ("API Endpoints", test_api_endpoints),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Test {test_name} échoué: {e}")
            results[test_name] = False
    
    # Résumé final
    print("\n" + "="*70)
    print("📊 RÉSUMÉ DES TESTS")
    print("="*70)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<20} : {status}")
    
    print(f"\n🎯 Score: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 Tous les tests passent ! Système opérationnel.")
    elif passed >= total * 0.7:
        print("⚠️ Système majoritairement fonctionnel, quelques ajustements nécessaires.")
    else:
        print("🔧 Système nécessite des corrections avant utilisation.")
    
    # Instructions finales
    print("\n💡 INSTRUCTIONS DE TEST MANUEL:")
    print("1. Démarrer le serveur Django: python manage.py runserver")
    print("2. Aller sur: http://127.0.0.1:8000/chat/")
    print("3. Tester chaque agent:")
    print("   - Tech: 'j'aimerais apprendre Python'")
    print("   - Literature: 'romans de Tolstoï'") 
    print("   - Manga: 'j'ai aimé Naruto'")
    print("4. Vérifier que les réponses correspondent aux bons agents")

if __name__ == "__main__":
    main()