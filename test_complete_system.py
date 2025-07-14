#!/usr/bin/env python3
"""
Script de test complet du système multi-modèles
Fichier: scripts/test_complete_system.py

Test complet de l'intégration des modèles Llama, Mistral et Gemma
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
from agents.multi_model_manager import multi_model_manager
from agents.model_evaluator import get_model_evaluator
from agents.langchain_agents.django_integration import django_langchain_bridge
from apps.chat.views_model_management import ModelStatusView, ModelEvaluationView

def test_multi_model_system():
    """Test complet du système multi-modèles"""
    print("🚀 TEST COMPLET DU SYSTÈME MULTI-MODÈLES")
    print("=" * 80)
    
    # 1. Test de base des modèles
    print("\n1️⃣ TEST DE BASE DES MODÈLES")
    print("-" * 50)
    
    models_to_test = ['llama3.2:3b', 'mistral:7b', 'gemma2:2b']
    test_query = "Recommande-moi des livres sur Python pour débutant"
    
    model_results = {}
    
    for model in models_to_test:
        print(f"\n🔬 Test du modèle: {model}")
        try:
            start_time = time.time()
            response, metrics = multi_model_manager.generate_response(
                test_query, model_name=model, agent_type="tech"
            )
            end_time = time.time()
            
            model_results[model] = {
                'success': metrics.get('success', False),
                'response_time': end_time - start_time,
                'response_length': len(response),
                'response_preview': response[:100] + "..." if len(response) > 100 else response
            }
            
            print(f"   ✅ Succès: {metrics.get('success', False)}")
            print(f"   ⏱️ Temps: {end_time - start_time:.2f}s")
            print(f"   📝 Réponse: {model_results[model]['response_preview']}")
            
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            model_results[model] = {'success': False, 'error': str(e)}
    
    # 2. Test d'évaluation comparative
    print("\n2️⃣ TEST D'ÉVALUATION COMPARATIVE")
    print("-" * 50)
    
    try:
        evaluator = get_model_evaluator(multi_model_manager)
        comparison_results = evaluator.compare_models(models_to_test)
        
        if 'best_model' in comparison_results:
            print(f"🏆 Meilleur modèle: {comparison_results['best_model']}")
            print(f"📊 Score: {comparison_results['best_score']:.3f}")
            
            print("\n📈 Classement:")
            for i, (model, metrics) in enumerate(comparison_results['ranking'], 1):
                print(f"   {i}. {model}: {metrics.overall_score:.3f}")
        else:
            print(f"❌ Erreur évaluation: {comparison_results.get('error', 'Erreur inconnue')}")
            
    except Exception as e:
        print(f"❌ Erreur évaluation comparative: {e}")
    
    # 3. Test de sélection automatique
    print("\n3️⃣ TEST DE SÉLECTION AUTOMATIQUE")
    print("-" * 50)
    
    agent_types = ['tech', 'literature', 'manga', 'general']
    
    for agent_type in agent_types:
        try:
            best_model = multi_model_manager.get_best_model_for_task(agent_type)
            print(f"🎯 Agent {agent_type}: {best_model}")
            
            # Test avec ce modèle
            test_queries = {
                'tech': "Livres sur le machine learning",
                'literature': "Romans français classiques",
                'manga': "Manga comme One Piece",
                'general': "Recommandations générales"
            }
            
            query = test_queries.get(agent_type, "Test général")
            response, metrics = multi_model_manager.generate_response(
                query, model_name=best_model, agent_type=agent_type
            )
            
            print(f"   ✅ Test réussi: {metrics.get('success', False)}")
            print(f"   ⏱️ Temps: {metrics.get('response_time', 0):.2f}s")
            
        except Exception as e:
            print(f"   ❌ Erreur {agent_type}: {e}")
    
    # 4. Test d'intégration LangChain
    print("\n4️⃣ TEST INTÉGRATION LANGCHAIN")
    print("-" * 50)
    
    try:
        bridge = django_langchain_bridge
        
        if bridge.is_available():
            print("✅ LangChain Bridge disponible")
            
            # Test des agents LangChain
            test_cases = [
                ("Recommande-moi des livres Python", "tech"),
                ("Romans de Victor Hugo", "literature"),
                ("Manga similaires à Naruto", "manga")
            ]
            
            for query, agent_type in test_cases:
                print(f"\n🧪 Test {agent_type}: {query}")
                try:
                    start_time = time.time()
                    
                    if agent_type == "tech":
                        response = bridge.get_manager().get_tech_recommendations(query)
                    elif agent_type == "literature":
                        response = bridge.get_manager().get_literature_recommendations(query)
                    elif agent_type == "manga":
                        response = bridge.get_manager().get_manga_recommendations(query)
                    
                    end_time = time.time()
                    
                    print(f"   ✅ Réponse reçue: {len(response)} caractères")
                    print(f"   ⏱️ Temps: {end_time - start_time:.2f}s")
                    print(f"   📝 Début: {response[:100]}...")
                    
                except Exception as e:
                    print(f"   ❌ Erreur: {e}")
        else:
            print("❌ LangChain Bridge non disponible")
            
    except Exception as e:
        print(f"❌ Erreur test LangChain: {e}")
    
    # 5. Test des vues Django
    print("\n5️⃣ TEST DES VUES DJANGO")
    print("-" * 50)
    
    try:
        # Simuler une requête GET pour le statut
        from django.test import RequestFactory
        factory = RequestFactory()
        
        # Test ModelStatusView
        print("🔬 Test ModelStatusView...")
        request = factory.get('/api/chat/models/status/')
        view = ModelStatusView()
        response = view.get(request)
        
        if response.status_code == 200:
            print("   ✅ ModelStatusView fonctionne")
            data = response.data
            print(f"   📊 Modèles disponibles: {len(data.get('available_models', []))}")
            print(f"   🏆 Meilleur modèle: {data.get('current_best_model', 'Unknown')}")
        else:
            print(f"   ❌ ModelStatusView erreur: {response.status_code}")
        
        # Test ModelEvaluationView
        print("\n🔬 Test ModelEvaluationView...")
        request = factory.get('/api/chat/models/evaluation/')
        view = ModelEvaluationView()
        response = view.get(request)
        
        if response.status_code == 200:
            print("   ✅ ModelEvaluationView fonctionne")
        else:
            print(f"   ❌ ModelEvaluationView erreur: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur test vues Django: {e}")
    
    # 6. Test de performance
    print("\n6️⃣ TEST DE PERFORMANCE")
    print("-" * 50)
    
    try:
        performance_results = {}
        test_queries = [
            "Recommande-moi des livres sur Python",
            "Quels sont les meilleurs romans ?",
            "Suggère-moi des manga"
        ]
        
        for model in models_to_test:
            print(f"\n⚡ Performance {model}:")
            times = []
            
            for query in test_queries:
                try:
                    start_time = time.time()
                    response, metrics = multi_model_manager.generate_response(
                        query, model_name=model
                    )
                    end_time = time.time()
                    times.append(end_time - start_time)
                    
                except Exception as e:
                    print(f"   ❌ Erreur: {e}")
                    times.append(float('inf'))
            
            if times:
                avg_time = sum(t for t in times if t != float('inf')) / len([t for t in times if t != float('inf')])
                performance_results[model] = avg_time
                print(f"   ⏱️ Temps moyen: {avg_time:.2f}s")
        
        # Classer par performance
        sorted_models = sorted(performance_results.items(), key=lambda x: x[1])
        print(f"\n🏆 Classement performance:")
        for i, (model, time) in enumerate(sorted_models, 1):
            print(f"   {i}. {model}: {time:.2f}s")
            
    except Exception as e:
        print(f"❌ Erreur test performance: {e}")
    
    # 7. Génération du rapport final
    print("\n7️⃣ RAPPORT FINAL")
    print("-" * 50)
    
    try:
        # Statut système
        system_status = multi_model_manager.get_system_status()
        print(f"📊 Système multi-modèles: {'✅ Actif' if system_status.get('ollama_available', False) else '❌ Inactif'}")
        print(f"🏆 Meilleur modèle actuel: {system_status.get('current_best_model', 'Non déterminé')}")
        print(f"🔄 Évaluation activée: {'✅ Oui' if system_status.get('evaluation_enabled', False) else '❌ Non'}")
        
        # Classement des modèles
        rankings = multi_model_manager.get_model_rankings()
        if rankings:
            print(f"\n📈 Top 3 modèles:")
            for i, model in enumerate(rankings[:3], 1):
                print(f"   {i}. {model['model_name']}: {model['overall_score']:.3f}")
                print(f"      📝 {model['description']}")
                print(f"      💾 RAM: {model['ram_usage']}")
        
        # Recommandations
        print(f"\n💡 Recommandations:")
        if system_status.get('ollama_available', False):
            print("   ✅ Système prêt pour la production")
            print("   📚 Testez les différents agents via l'interface web")
            print("   🔄 L'évaluation automatique optimisera les performances")
        else:
            print("   ❌ Démarrez Ollama: ollama serve")
            print("   📥 Installez les modèles: python scripts/setup_models.py")
        
    except Exception as e:
        print(f"❌ Erreur rapport final: {e}")
    
    print("\n" + "=" * 80)
    print("✅ TEST COMPLET TERMINÉ")
    print(f"⏰ Timestamp: {datetime.now()}")

def create_test_report():
    """Crée un rapport de test détaillé"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"complete_system_test_report_{timestamp}.json"
    
    try:
        # Collecter les données
        system_status = multi_model_manager.get_system_status()
        rankings = multi_model_manager.get_model_rankings()
        
        evaluator = get_model_evaluator(multi_model_manager)
        evaluation_report = evaluator.get_evaluation_report()
        
        # Créer le rapport
        report = {
            'timestamp': timestamp,
            'test_type': 'complete_system_test',
            'system_status': system_status,
            'model_rankings': rankings,
            'evaluation_report': evaluation_report,
            'recommendations': {
                'best_model': rankings[0]['model_name'] if rankings else None,
                'production_ready': system_status.get('ollama_available', False),
                'next_steps': [
                    "Démarrer l'application Django",
                    "Tester l'interface web",
                    "Configurer les modèles selon vos besoins"
                ]
            }
        }
        
        # Sauvegarder
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Rapport sauvegardé: {report_file}")
        
    except Exception as e:
        print(f"❌ Erreur création rapport: {e}")

if __name__ == "__main__":
    test_multi_model_system()
    create_test_report()