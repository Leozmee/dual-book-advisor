"""
Vues Django pour la gestion des modèles
Fichier: apps/chat/views_model_management.py

Interface web pour gérer et évaluer les modèles
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
import logging
import time
import json
from typing import Dict, Any

from agents.multi_model_manager import multi_model_manager
from agents.model_evaluator import get_model_evaluator
from agents.langchain_agents.django_integration import django_langchain_bridge

logger = logging.getLogger(__name__)

class ModelStatusView(APIView):
    """Vue pour afficher le statut des modèles"""
    
    permission_classes = []
    
    def get(self, request):
        """Retourne le statut de tous les modèles"""
        try:
            # Statut du système multi-modèles
            system_status = multi_model_manager.get_system_status()
            
            # Classement des modèles
            rankings = multi_model_manager.get_model_rankings()
            
            # Statut LangChain
            langchain_status = django_langchain_bridge.get_status()
            
            response_data = {
                'timestamp': time.time(),
                'system_status': system_status,
                'model_rankings': rankings,
                'langchain_status': langchain_status,
                'available_models': list(multi_model_manager.OPTIMAL_MODELS.keys()),
                'current_best_model': system_status.get('current_best_model'),
                'evaluation_enabled': system_status.get('evaluation_enabled', False)
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Erreur statut modèles: {e}")
            return Response({
                'error': str(e),
                'timestamp': time.time()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ModelEvaluationView(APIView):
    """Vue pour évaluer les modèles"""
    
    permission_classes = []
    
    def post(self, request):
        """Lance l'évaluation des modèles"""
        try:
            models_to_evaluate = request.data.get('models', None)
            
            if not models_to_evaluate:
                models_to_evaluate = multi_model_manager.preferred_models
            
            logger.info(f"Lancement évaluation modèles: {models_to_evaluate}")
            
            # Obtenir l'évaluateur
            evaluator = get_model_evaluator(multi_model_manager)
            
            # Lancer l'évaluation
            start_time = time.time()
            comparison_results = evaluator.compare_models(models_to_evaluate)
            evaluation_time = time.time() - start_time
            
            # Générer le rapport
            report = evaluator.get_evaluation_report()
            
            response_data = {
                'success': True,
                'evaluation_time': evaluation_time,
                'models_evaluated': len(models_to_evaluate),
                'comparison_results': comparison_results,
                'report': report,
                'timestamp': time.time()
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Erreur évaluation modèles: {e}")
            return Response({
                'success': False,
                'error': str(e),
                'timestamp': time.time()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get(self, request):
        """Retourne les résultats de la dernière évaluation"""
        try:
            evaluator = get_model_evaluator(multi_model_manager)
            report = evaluator.get_evaluation_report()
            
            return Response({
                'success': True,
                'report': report,
                'timestamp': time.time()
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Erreur récupération évaluation: {e}")
            return Response({
                'success': False,
                'error': str(e),
                'timestamp': time.time()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ModelSwitchView(APIView):
    """Vue pour changer de modèle"""
    
    permission_classes = []
    
    def post(self, request):
        """Bascule vers un modèle spécifique ou le meilleur modèle"""
        try:
            model_name = request.data.get('model_name')
            agent_type = request.data.get('agent_type', 'general')
            auto_select = request.data.get('auto_select', False)
            
            if auto_select:
                # Sélection automatique du meilleur modèle
                best_model = multi_model_manager.get_best_model_for_task(agent_type)
                
                if best_model:
                    # Mettre à jour le bridge LangChain
                    bridge = django_langchain_bridge
                    if bridge.is_available():
                        # Reconfigurer le bridge avec le nouveau modèle
                        bridge._graph_manager.model_name = best_model
                        bridge._graph_manager.llm = bridge._graph_manager._create_llm()
                        
                        return Response({
                            'success': True,
                            'switched_to': best_model,
                            'agent_type': agent_type,
                            'auto_selected': True,
                            'message': f'Basculé vers le meilleur modèle: {best_model}'
                        }, status=status.HTTP_200_OK)
                    else:
                        return Response({
                            'success': False,
                            'error': 'LangChain bridge non disponible'
                        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
                else:
                    return Response({
                        'success': False,
                        'error': 'Aucun modèle optimal trouvé'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            elif model_name:
                # Basculer vers un modèle spécifique
                if model_name not in multi_model_manager.OPTIMAL_MODELS:
                    return Response({
                        'success': False,
                        'error': f'Modèle {model_name} non supporté',
                        'available_models': list(multi_model_manager.OPTIMAL_MODELS.keys())
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Mettre à jour le bridge LangChain
                bridge = django_langchain_bridge
                if bridge.is_available():
                    old_model = bridge._graph_manager.model_name
                    bridge._graph_manager.model_name = model_name
                    bridge._graph_manager.llm = bridge._graph_manager._create_llm()
                    
                    return Response({
                        'success': True,
                        'switched_from': old_model,
                        'switched_to': model_name,
                        'auto_selected': False,
                        'message': f'Basculé vers {model_name}'
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({
                        'success': False,
                        'error': 'LangChain bridge non disponible'
                    }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
            else:
                return Response({
                    'success': False,
                    'error': 'Paramètre model_name ou auto_select requis'
                }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Erreur changement modèle: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ModelBenchmarkView(APIView):
    """Vue pour lancer des benchmarks de modèles"""
    
    permission_classes = []
    
    def post(self, request):
        """Lance un benchmark comparatif"""
        try:
            test_type = request.data.get('test_type', 'comprehensive')
            models = request.data.get('models', multi_model_manager.preferred_models)
            
            logger.info(f"Lancement benchmark {test_type} pour modèles: {models}")
            
            start_time = time.time()
            
            if test_type == 'comprehensive':
                # Benchmark complet
                evaluator = get_model_evaluator(multi_model_manager)
                results = evaluator.compare_models(models)
                
            elif test_type == 'speed':
                # Test de vitesse uniquement
                results = self._run_speed_benchmark(models)
                
            elif test_type == 'quality':
                # Test de qualité uniquement
                results = self._run_quality_benchmark(models)
                
            else:
                return Response({
                    'success': False,
                    'error': f'Type de test {test_type} non supporté'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            benchmark_time = time.time() - start_time
            
            return Response({
                'success': True,
                'test_type': test_type,
                'models_tested': models,
                'benchmark_time': benchmark_time,
                'results': results,
                'timestamp': time.time()
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Erreur benchmark: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _run_speed_benchmark(self, models):
        """Benchmark de vitesse"""
        test_query = "Recommande-moi des livres sur Python"
        results = {}
        
        for model in models:
            try:
                times = []
                for _ in range(3):  # 3 essais
                    start_time = time.time()
                    response, metrics = multi_model_manager.generate_response(
                        test_query, model_name=model
                    )
                    times.append(time.time() - start_time)
                
                results[model] = {
                    'avg_time': sum(times) / len(times),
                    'min_time': min(times),
                    'max_time': max(times),
                    'times': times
                }
                
            except Exception as e:
                results[model] = {'error': str(e)}
        
        return results
    
    def _run_quality_benchmark(self, models):
        """Benchmark de qualité"""
        test_queries = [
            "Recommande-moi des livres sur Python pour débutant",
            "Quels sont les meilleurs romans de science-fiction ?",
            "Suggère-moi des manga comme Attack on Titan"
        ]
        
        results = {}
        
        for model in models:
            model_results = []
            
            for query in test_queries:
                try:
                    response, metrics = multi_model_manager.generate_response(
                        query, model_name=model
                    )
                    
                    # Évaluation basique de la qualité
                    quality_score = min(1.0, len(response) / 200.0)
                    
                    model_results.append({
                        'query': query,
                        'response_length': len(response),
                        'quality_score': quality_score,
                        'success': metrics.get('success', False)
                    })
                    
                except Exception as e:
                    model_results.append({
                        'query': query,
                        'error': str(e)
                    })
            
            # Calculer la moyenne
            successful_results = [r for r in model_results if 'quality_score' in r]
            avg_quality = sum(r['quality_score'] for r in successful_results) / len(successful_results) if successful_results else 0
            
            results[model] = {
                'avg_quality_score': avg_quality,
                'success_rate': len(successful_results) / len(test_queries),
                'detailed_results': model_results
            }
        
        return results

class ModelConfigView(APIView):
    """Vue pour configurer les modèles"""
    
    permission_classes = []
    
    def get(self, request):
        """Retourne la configuration des modèles"""
        try:
            config = {
                'optimal_models': multi_model_manager.OPTIMAL_MODELS,
                'preferred_models': multi_model_manager.preferred_models,
                'evaluation_enabled': multi_model_manager.evaluation_enabled,
                'base_url': multi_model_manager.base_url,
                'current_best_model': multi_model_manager.current_best_model
            }
            
            return Response(config, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Erreur configuration: {e}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        """Met à jour la configuration des modèles"""
        try:
            # Mettre à jour les modèles préférés
            if 'preferred_models' in request.data:
                multi_model_manager.preferred_models = request.data['preferred_models']
            
            # Activer/désactiver l'évaluation
            if 'evaluation_enabled' in request.data:
                multi_model_manager.evaluation_enabled = request.data['evaluation_enabled']
            
            # Réinitialiser les performances si demandé
            if request.data.get('reset_performance_data', False):
                multi_model_manager.reset_performance_data()
            
            return Response({
                'success': True,
                'message': 'Configuration mise à jour',
                'current_config': {
                    'preferred_models': multi_model_manager.preferred_models,
                    'evaluation_enabled': multi_model_manager.evaluation_enabled
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Erreur mise à jour config: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ModelHealthView(APIView):
    """Vue pour vérifier la santé des modèles"""
    
    permission_classes = []
    
    def get(self, request):
        """Vérifie la santé de tous les modèles"""
        try:
            health_results = {}
            
            for model_name in multi_model_manager.preferred_models:
                try:
                    start_time = time.time()
                    response, metrics = multi_model_manager.generate_response(
                        "Test de santé", model_name=model_name
                    )
                    response_time = time.time() - start_time
                    
                    health_results[model_name] = {
                        'status': 'healthy' if metrics.get('success', False) else 'unhealthy',
                        'response_time': response_time,
                        'response_length': len(response),
                        'last_check': time.time()
                    }
                    
                except Exception as e:
                    health_results[model_name] = {
                        'status': 'error',
                        'error': str(e),
                        'last_check': time.time()
                    }
            
            # Statut global
            healthy_models = [model for model, health in health_results.items() if health['status'] == 'healthy']
            overall_status = 'healthy' if len(healthy_models) > 0 else 'unhealthy'
            
            return Response({
                'overall_status': overall_status,
                'healthy_models': healthy_models,
                'total_models': len(multi_model_manager.preferred_models),
                'health_details': health_results,
                'timestamp': time.time()
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Erreur vérification santé: {e}")
            return Response({
                'overall_status': 'error',
                'error': str(e),
                'timestamp': time.time()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)