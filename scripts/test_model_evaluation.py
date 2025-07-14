#!/usr/bin/env python3
"""
Script de test et d'évaluation des modèles
Fichier: scripts/test_model_evaluation.py

Test et compare les modèles Llama, Mistral et Gemma
"""
import os
import sys
import logging
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

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_model_availability():
    """Test la disponibilité des modèles"""
    print("🔍 Vérification de la disponibilité des modèles...")
    print("=" * 60)
    
    status = multi_model_manager.get_system_status()
    print(f"📊 Statut système: {status}")
    
    # Test de chaque modèle
    test_models = ['llama3.2:3b', 'mistral:7b', 'gemma2:2b']
    
    for model in test_models:
        print(f"\n🧪 Test du modèle {model}...")
        try:
            response, metrics = multi_model_manager.generate_response(
                "Bonjour, peux-tu me recommander un livre sur Python ?",
                model_name=model
            )
            
            print(f"   ✅ Succès: {metrics['success']}")
            print(f"   ⏱️ Temps: {metrics['response_time']:.2f}s")
            print(f"   📝 Réponse: {response[:100]}...")
            
        except Exception as e:
            print(f"   ❌ Erreur: {e}")

def run_comprehensive_evaluation():
    """Lance une évaluation complète des modèles"""
    print("\n🧪 Évaluation complète des modèles...")
    print("=" * 60)
    
    evaluator = get_model_evaluator(multi_model_manager)
    
    # Tester chaque modèle
    models_to_test = ['llama3.2:3b', 'mistral:7b', 'gemma2:2b']
    
    for model in models_to_test:
        print(f"\n🔬 Évaluation détaillée: {model}")
        print("-" * 40)
        
        try:
            metrics = evaluator.evaluate_model_comprehensive(model)
            
            print(f"   🎯 Score global: {metrics.overall_score:.3f}")
            print(f"   📊 Pertinence RAG: {metrics.rag_relevance:.3f}")
            print(f"   💬 Qualité réponse: {metrics.response_quality:.3f}")
            print(f"   ⚡ Temps moyen: {metrics.response_time:.2f}s")
            print(f"   ✅ Précision: {metrics.accuracy:.3f}")
            print(f"   🔗 Cohérence: {metrics.coherence:.3f}")
            
        except Exception as e:
            print(f"   ❌ Erreur évaluation: {e}")

def run_comparative_analysis():
    """Compare les modèles et sélectionne le meilleur"""
    print("\n🏆 Analyse comparative des modèles...")
    print("=" * 60)
    
    evaluator = get_model_evaluator(multi_model_manager)
    
    try:
        comparison = evaluator.compare_models()
        
        if 'best_model' in comparison:
            print(f"🥇 Meilleur modèle: {comparison['best_model']}")
            print(f"📊 Score: {comparison['best_score']:.3f}")
            
            print("\n📈 Classement des modèles:")
            for i, (model, metrics) in enumerate(comparison['ranking'], 1):
                print(f"   {i}. {model}: {metrics.overall_score:.3f}")
                
                # Détails du modèle
                model_info = multi_model_manager.OPTIMAL_MODELS.get(model, {})
                print(f"      📝 {model_info.get('description', 'Pas de description')}")
                print(f"      💾 RAM: {model_info.get('ram_usage', 'Unknown')}")
                print(f"      🎯 Forces: {', '.join(model_info.get('strengths', []))}")
                print()
        
        else:
            print(f"❌ Erreur comparaison: {comparison.get('error', 'Erreur inconnue')}")
            
    except Exception as e:
        print(f"❌ Erreur analyse: {e}")

def test_specific_rag_scenarios():
    """Test des scénarios RAG spécifiques"""
    print("\n🎯 Test des scénarios RAG spécifiques...")
    print("=" * 60)
    
    scenarios = {
        'tech': [
            "Recommande-moi des livres pour apprendre Python",
            "Quels sont les meilleurs livres sur le machine learning ?"
        ],
        'literature': [
            "Je veux lire des romans de Victor Hugo",
            "Recommande-moi de la littérature française classique"
        ],
        'manga': [
            "Suggère-moi des manga comme Attack on Titan",
            "Quels sont les meilleurs manga seinen ?"
        ]
    }
    
    for scenario_type, queries in scenarios.items():
        print(f"\n📚 Scénario: {scenario_type.upper()}")
        print("-" * 30)
        
        for query in queries:
            print(f"\n💬 Query: {query}")
            
            # Tester avec le meilleur modèle pour ce type
            best_model = multi_model_manager.get_best_model_for_task(scenario_type)
            
            try:
                response, metrics = multi_model_manager.generate_response(
                    query, 
                    model_name=best_model,
                    agent_type=scenario_type
                )
                
                print(f"   🏆 Modèle utilisé: {best_model}")
                print(f"   ⏱️ Temps: {metrics['response_time']:.2f}s")
                print(f"   ✅ Succès: {metrics['success']}")
                print(f"   📝 Réponse: {response[:150]}...")
                
            except Exception as e:
                print(f"   ❌ Erreur: {e}")

def test_langchain_integration():
    """Test l'intégration avec LangChain"""
    print("\n🔗 Test intégration LangChain...")
    print("=" * 60)
    
    try:
        bridge = django_langchain_bridge
        
        if bridge.is_available():
            print("✅ LangChain Bridge disponible")
            
            # Test des différents agents
            test_queries = [
                ("Recommande-moi des livres Python", "tech"),
                ("Romans de science-fiction", "literature"),
                ("Manga comme Naruto", "manga")
            ]
            
            for query, expected_type in test_queries:
                print(f"\n🧪 Test {expected_type}: {query}")
                
                try:
                    if expected_type == "tech":
                        response = bridge.get_manager().get_tech_recommendations(query)
                    elif expected_type == "literature":
                        response = bridge.get_manager().get_literature_recommendations(query)
                    elif expected_type == "manga":
                        response = bridge.get_manager().get_manga_recommendations(query)
                    
                    print(f"   ✅ Réponse reçue: {len(response)} caractères")
                    print(f"   📝 Début: {response[:100]}...")
                    
                except Exception as e:
                    print(f"   ❌ Erreur: {e}")
        
        else:
            print("❌ LangChain Bridge non disponible")
            
    except Exception as e:
        print(f"❌ Erreur test intégration: {e}")

def save_evaluation_report():
    """Sauvegarde un rapport d'évaluation"""
    print("\n📊 Génération du rapport d'évaluation...")
    print("=" * 60)
    
    try:
        evaluator = get_model_evaluator(multi_model_manager)
        report = evaluator.get_evaluation_report()
        
        # Sauvegarder le rapport
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"model_evaluation_report_{timestamp}.json"
        
        import json
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Rapport sauvegardé: {report_file}")
        
        # Afficher le résumé
        if 'models' in report:
            print(f"\n📈 Résumé du rapport:")
            print(f"   📊 Modèles évalués: {report['total_models_evaluated']}")
            
            for model, info in report['models'].items():
                print(f"   🏆 {model}: Rang {info['rank']}, Score {info['overall_score']:.3f}")
                if info['strengths']:
                    print(f"      💪 Forces: {', '.join(info['strengths'])}")
                if info['weaknesses']:
                    print(f"      ⚠️ Faiblesses: {', '.join(info['weaknesses'])}")
                print(f"      💡 Recommandation: {info['recommendation']}")
                print()
        
    except Exception as e:
        print(f"❌ Erreur génération rapport: {e}")

def main():
    """Fonction principale"""
    print("🚀 Test et Évaluation des Modèles Multi-LLM")
    print("=" * 80)
    print(f"⏰ Début: {datetime.now()}")
    
    # 1. Test de disponibilité
    test_model_availability()
    
    # 2. Évaluation complète
    run_comprehensive_evaluation()
    
    # 3. Analyse comparative
    run_comparative_analysis()
    
    # 4. Test des scénarios RAG
    test_specific_rag_scenarios()
    
    # 5. Test intégration LangChain
    test_langchain_integration()
    
    # 6. Rapport final
    save_evaluation_report()
    
    print("\n" + "=" * 80)
    print("✅ Évaluation terminée!")
    print(f"⏰ Fin: {datetime.now()}")
    
    # Afficher les recommandations finales
    rankings = multi_model_manager.get_model_rankings()
    if rankings:
        print(f"\n🏆 Recommandation finale:")
        best = rankings[0]
        print(f"   🥇 Meilleur modèle: {best['model_name']}")
        print(f"   📊 Score: {best['overall_score']:.3f}")
        print(f"   🎯 Forces: {', '.join(best['strengths'])}")
        print(f"   💾 RAM: {best['ram_usage']}")
        print(f"   💡 {best['description']}")

if __name__ == "__main__":
    main()