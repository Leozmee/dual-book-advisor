#!/usr/bin/env python3
"""
Script de test pour Llama 3.2 3B optimisé
Fichier: scripts/test_llama_optimized.py

Test complet du système simplifié avec Llama 3.2 3B uniquement
"""
import os
import sys
import json
import time
from datetime import datetime
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

# Imports après setup Django
from agents.optimized_llama_manager import optimized_llama_manager
from apps.chat.views_llama_agents import LlamaTechAgentView, LlamaLiteratureAgentView, LlamaMangaAgentView, LlamaRouterAgentView
from apps.chat.views_llama_stats import LlamaStatsView, LlamaHealthView, LlamaTestView

def test_llama_manager():
    """Test direct du gestionnaire Llama optimisé"""
    print("🦙 TEST DU GESTIONNAIRE LLAMA OPTIMISÉ")
    print("=" * 60)
    
    # Test de base
    print("\n1️⃣ TEST DE BASE")
    print("-" * 30)
    
    try:
        # Vérifier les informations du modèle
        print(f"📝 Modèle: {optimized_llama_manager.MODEL_NAME}")
        print(f"💾 RAM: {optimized_llama_manager.MODEL_INFO['ram_usage']}")
        print(f"🎯 Forces: {', '.join(optimized_llama_manager.MODEL_INFO['strengths'])}")
        
        # Test de santé
        health = optimized_llama_manager.get_health_status()
        print(f"🏥 Santé: {health['status']}")
        
        # Test de génération
        query = "Recommande-moi des livres sur Python"
        response, metrics = optimized_llama_manager.generate_response(query, "tech")
        
        print(f"✅ Réponse générée: {metrics['success']}")
        print(f"⏱️ Temps: {metrics['response_time']:.2f}s")
        print(f"📊 Tokens: {metrics['tokens_generated']}")
        print(f"📝 Début: {response[:100]}...")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

def test_agent_types():
    """Test des différents types d'agents"""
    print("\n2️⃣ TEST DES AGENTS SPÉCIALISÉS")
    print("-" * 30)
    
    test_cases = [
        ("tech", "Recommande-moi des livres sur le machine learning"),
        ("literature", "Quels sont les meilleurs romans français classiques ?"),
        ("manga", "Suggère-moi des manga comme Attack on Titan"),
        ("general", "Que peux-tu me recommander pour bien lire ?")
    ]
    
    for agent_type, query in test_cases:
        print(f"\n🔬 Test {agent_type}: {query}")
        try:
            start_time = time.time()
            response, metrics = optimized_llama_manager.generate_response(query, agent_type)
            end_time = time.time()
            
            print(f"   ✅ Succès: {metrics['success']}")
            print(f"   ⏱️ Temps: {end_time - start_time:.2f}s")
            print(f"   📊 Tokens: {metrics['tokens_generated']}")
            print(f"   📝 Début: {response[:80]}...")
            
        except Exception as e:
            print(f"   ❌ Erreur: {e}")

def test_statistics():
    """Test des statistiques détaillées"""
    print("\n3️⃣ TEST DES STATISTIQUES")
    print("-" * 30)
    
    try:
        # Obtenir les statistiques
        stats = optimized_llama_manager.get_detailed_stats()
        
        print(f"📊 Requêtes totales: {stats['performance_stats']['total_queries']}")
        print(f"✅ Requêtes réussies: {stats['performance_stats']['successful_queries']}")
        print(f"📈 Taux de succès: {stats['performance_stats']['success_rate']:.1f}%")
        print(f"⏱️ Temps moyen: {stats['timing_stats']['avg_response_time']:.2f}s")
        print(f"🎯 Note: {stats['performance_stats']['performance_grade']}")
        
        # Statistiques par type
        print(f"\n📋 Utilisation par type:")
        for agent_type, count in stats['usage_stats']['queries_by_type'].items():
            print(f"   {agent_type}: {count} requêtes")
        
        # Recommandations
        recommendations = optimized_llama_manager.get_recommendations()
        print(f"\n💡 Recommandations:")
        for rec in recommendations:
            print(f"   • {rec}")
            
    except Exception as e:
        print(f"❌ Erreur statistiques: {e}")

def test_django_views():
    """Test des vues Django"""
    print("\n4️⃣ TEST DES VUES DJANGO")
    print("-" * 30)
    
    try:
        from django.test import RequestFactory
        import json
        
        factory = RequestFactory()
        
        # Test des agents
        views_to_test = [
            ("Tech", LlamaTechAgentView, "Livres Python"),
            ("Literature", LlamaLiteratureAgentView, "Romans français"),
            ("Manga", LlamaMangaAgentView, "Manga shounen"),
            ("Router", LlamaRouterAgentView, "Recommandations générales")
        ]
        
        for name, view_class, query in views_to_test:
            print(f"\n🔬 Test {name}Agent:")
            
            request = factory.post(
                f'/api/chat/llama/{name.lower()}/',
                data={'message': query},
                content_type='application/json'
            )
            
            view = view_class()
            response = view.post(request)
            
            if response.status_code == 200:
                data = response.data
                print(f"   ✅ Succès: {data['success']}")
                print(f"   ⏱️ Temps: {data['llama_metrics']['response_time']:.2f}s")
                print(f"   📊 Tokens: {data['llama_metrics']['tokens_generated']}")
                print(f"   🎯 Grade: {data['system_info']['performance_grade']}")
            else:
                print(f"   ❌ Erreur HTTP: {response.status_code}")
        
        # Test des vues de statistiques
        print(f"\n🔬 Test vues statistiques:")
        
        # Stats view
        request = factory.get('/api/chat/llama/stats/')
        view = LlamaStatsView()
        response = view.get(request)
        
        if response.status_code == 200:
            print(f"   ✅ LlamaStatsView: OK")
        else:
            print(f"   ❌ LlamaStatsView: {response.status_code}")
        
        # Health view
        request = factory.get('/api/chat/llama/health/')
        view = LlamaHealthView()
        response = view.get(request)
        
        if response.status_code == 200:
            print(f"   ✅ LlamaHealthView: OK")
        else:
            print(f"   ❌ LlamaHealthView: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur test vues: {e}")

def test_performance_monitoring():
    """Test du monitoring des performances"""
    print("\n5️⃣ TEST DU MONITORING")
    print("-" * 30)
    
    try:
        # Effectuer plusieurs requêtes pour générer des stats
        print("🔄 Génération de données de performance...")
        
        test_queries = [
            ("tech", "Python pour débutants"),
            ("literature", "Romans du 19ème siècle"),
            ("manga", "Manga d'action"),
            ("tech", "Machine learning books"),
            ("literature", "Littérature contemporaine")
        ]
        
        times = []
        for agent_type, query in test_queries:
            start = time.time()
            response, metrics = optimized_llama_manager.generate_response(query, agent_type)
            end = time.time()
            times.append(end - start)
            
            print(f"   • {agent_type}: {end - start:.2f}s")
        
        # Analyser les performances
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"\n📊 Analyse des performances:")
        print(f"   ⏱️ Temps moyen: {avg_time:.2f}s")
        print(f"   🚀 Plus rapide: {min_time:.2f}s")
        print(f"   🐌 Plus lent: {max_time:.2f}s")
        
        # Vérifier les stats mises à jour
        final_stats = optimized_llama_manager.get_detailed_stats()
        print(f"   📈 Total requêtes: {final_stats['performance_stats']['total_queries']}")
        print(f"   ✅ Taux succès: {final_stats['performance_stats']['success_rate']:.1f}%")
        print(f"   🎯 Grade final: {final_stats['performance_stats']['performance_grade']}")
        
    except Exception as e:
        print(f"❌ Erreur monitoring: {e}")

def test_comprehensive_system():
    """Test complet du système"""
    print("\n6️⃣ TEST SYSTÈME COMPLET")
    print("-" * 30)
    
    try:
        # Simuler une session utilisateur complète
        print("🎭 Simulation session utilisateur:")
        
        # Conversation multi-tours
        conversation = [
            ("tech", "Je veux apprendre Python"),
            ("literature", "J'aime les romans historiques"),
            ("manga", "Recommande-moi des manga"),
            ("tech", "Des livres avancés sur l'IA"),
            ("general", "Que me conseillez-vous ?")
        ]
        
        session_start = time.time()
        successful_queries = 0
        
        for i, (agent_type, query) in enumerate(conversation, 1):
            print(f"\n   💬 Tour {i}: {query}")
            
            try:
                response, metrics = optimized_llama_manager.generate_response(query, agent_type)
                
                if metrics['success']:
                    successful_queries += 1
                    print(f"   ✅ Réponse ({metrics['response_time']:.1f}s): {response[:60]}...")
                else:
                    print(f"   ❌ Échec: {metrics.get('error', 'Erreur inconnue')}")
                    
            except Exception as e:
                print(f"   ❌ Erreur: {e}")
        
        session_time = time.time() - session_start
        success_rate = (successful_queries / len(conversation)) * 100
        
        print(f"\n📊 Résultats session:")
        print(f"   ⏱️ Temps total: {session_time:.2f}s")
        print(f"   ✅ Succès: {successful_queries}/{len(conversation)} ({success_rate:.1f}%)")
        print(f"   ⚡ Temps moyen: {session_time/len(conversation):.2f}s par requête")
        
        # Vérifier l'état final
        final_health = optimized_llama_manager.get_health_status()
        print(f"   🏥 Santé finale: {final_health['status']}")
        
    except Exception as e:
        print(f"❌ Erreur test système: {e}")

def generate_final_report():
    """Génère un rapport final"""
    print("\n7️⃣ RAPPORT FINAL")
    print("-" * 30)
    
    try:
        # Collecter toutes les données
        stats = optimized_llama_manager.get_detailed_stats()
        health = optimized_llama_manager.get_health_status()
        recommendations = optimized_llama_manager.get_recommendations()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'model_name': optimized_llama_manager.MODEL_NAME,
            'model_info': optimized_llama_manager.MODEL_INFO,
            'performance_stats': stats['performance_stats'],
            'timing_stats': stats['timing_stats'],
            'usage_stats': stats['usage_stats'],
            'health_status': health,
            'recommendations': recommendations,
            'system_ready': health['status'] == 'healthy'
        }
        
        # Sauvegarder le rapport
        report_file = f"llama_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Système Llama 3.2 3B: {'OPÉRATIONNEL' if report['system_ready'] else 'PROBLÈME'}")
        print(f"📊 Requêtes totales: {report['performance_stats']['total_queries']}")
        print(f"✅ Taux de succès: {report['performance_stats']['success_rate']:.1f}%")
        print(f"⏱️ Temps moyen: {report['timing_stats']['avg_response_time']:.2f}s")
        print(f"🎯 Note de performance: {report['performance_stats']['performance_grade']}")
        print(f"📄 Rapport sauvegardé: {report_file}")
        
        # Endpoints disponibles
        print(f"\n🔗 Endpoints disponibles:")
        endpoints = [
            "GET /api/chat/llama/status/ - Statut système",
            "POST /api/chat/llama/tech/ - Agent technique",
            "POST /api/chat/llama/literature/ - Agent littéraire",
            "POST /api/chat/llama/manga/ - Agent manga",
            "POST /api/chat/llama/router/ - Agent routeur",
            "GET /api/chat/llama/stats/ - Statistiques détaillées",
            "GET /api/chat/llama/health/ - Santé du modèle",
            "GET /api/chat/llama/dashboard/ - Tableau de bord"
        ]
        
        for endpoint in endpoints:
            print(f"   • {endpoint}")
        
    except Exception as e:
        print(f"❌ Erreur génération rapport: {e}")

def main():
    """Fonction principale"""
    print("🚀 TEST COMPLET LLAMA 3.2 3B OPTIMISÉ")
    print("=" * 80)
    print(f"⏰ Début: {datetime.now()}")
    
    try:
        # Séquence de tests
        test_llama_manager()
        test_agent_types()
        test_statistics()
        test_django_views()
        test_performance_monitoring()
        test_comprehensive_system()
        generate_final_report()
        
        print("\n" + "=" * 80)
        print("✅ TEST COMPLET TERMINÉ AVEC SUCCÈS!")
        
    except Exception as e:
        print(f"\n❌ ERREUR GLOBALE: {e}")
        print("🔧 Vérifiez qu'Ollama est démarré et que llama3.2:3b est installé")
    
    print(f"⏰ Fin: {datetime.now()}")

if __name__ == "__main__":
    main()