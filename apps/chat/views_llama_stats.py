"""
Vues Django pour les statistiques Llama 3.2 3B
Fichier: apps/chat/views_llama_stats.py

Interface web pour monitoring et statistiques détaillées du modèle Llama
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any

from agents.minimal_llama_manager import minimal_llama_manager

logger = logging.getLogger(__name__)

class LlamaStatsView(APIView):
    """Vue pour les statistiques détaillées de Llama 3.2 3B"""
    
    permission_classes = []
    
    def get(self, request):
        """Retourne les statistiques complètes du modèle"""
        try:
            stats = minimal_llama_manager.get_detailed_stats()
            
            # Ajouter des métriques calculées
            stats['computed_metrics'] = self._compute_additional_metrics(stats)
            
            return Response({
                'success': True,
                'timestamp': datetime.now().isoformat(),
                'stats': stats
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Erreur récupération stats: {e}")
            return Response({
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _compute_additional_metrics(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """Calcule des métriques supplémentaires"""
        perf_stats = stats.get('performance_stats', {})
        timing_stats = stats.get('timing_stats', {})
        usage_stats = stats.get('usage_stats', {})
        
        # Métriques de performance
        total_queries = perf_stats.get('total_queries', 0)
        success_rate = perf_stats.get('success_rate', 0)
        avg_time = timing_stats.get('avg_response_time', 0)
        
        # Calculs
        queries_per_day = self._calculate_queries_per_day(usage_stats.get('daily_usage', {}))
        efficiency_score = self._calculate_efficiency_score(success_rate, avg_time)
        usage_trend = self._calculate_usage_trend(usage_stats.get('daily_usage', {}))
        
        return {
            'queries_per_day': queries_per_day,
            'efficiency_score': efficiency_score,
            'usage_trend': usage_trend,
            'estimated_tokens_per_minute': self._estimate_tokens_per_minute(timing_stats, usage_stats),
            'peak_usage_day': self._get_peak_usage_day(usage_stats.get('daily_usage', {})),
            'performance_category': self._get_performance_category(success_rate, avg_time)
        }
    
    def _calculate_queries_per_day(self, daily_usage: Dict[str, int]) -> float:
        """Calcule la moyenne de requêtes par jour"""
        if not daily_usage:
            return 0.0
        
        total_queries = sum(daily_usage.values())
        days_count = len(daily_usage)
        
        return total_queries / days_count if days_count > 0 else 0.0
    
    def _calculate_efficiency_score(self, success_rate: float, avg_time: float) -> float:
        """Calcule un score d'efficacité (0-100)"""
        if avg_time == 0:
            return 0.0
        
        # Score basé sur le taux de succès et la vitesse
        time_score = max(0, 100 - (avg_time - 5) * 2)  # Pénalité après 5s
        success_score = success_rate
        
        return (time_score + success_score) / 2
    
    def _calculate_usage_trend(self, daily_usage: Dict[str, int]) -> str:
        """Calcule la tendance d'utilisation"""
        if len(daily_usage) < 2:
            return "insufficient_data"
        
        # Prendre les 7 derniers jours
        sorted_dates = sorted(daily_usage.keys())[-7:]
        values = [daily_usage[date] for date in sorted_dates]
        
        if len(values) < 2:
            return "stable"
        
        # Calculer la tendance
        first_half = sum(values[:len(values)//2])
        second_half = sum(values[len(values)//2:])
        
        if second_half > first_half * 1.2:
            return "increasing"
        elif second_half < first_half * 0.8:
            return "decreasing"
        else:
            return "stable"
    
    def _estimate_tokens_per_minute(self, timing_stats: Dict, usage_stats: Dict) -> float:
        """Estime le nombre de tokens par minute"""
        avg_time = timing_stats.get('avg_response_time', 0)
        avg_tokens = usage_stats.get('avg_tokens_per_response', 0)
        
        if avg_time == 0:
            return 0.0
        
        return (avg_tokens / avg_time) * 60  # tokens par minute
    
    def _get_peak_usage_day(self, daily_usage: Dict[str, int]) -> Dict[str, Any]:
        """Trouve le jour avec le plus d'utilisation"""
        if not daily_usage:
            return {"date": None, "queries": 0}
        
        max_date = max(daily_usage.items(), key=lambda x: x[1])
        return {"date": max_date[0], "queries": max_date[1]}
    
    def _get_performance_category(self, success_rate: float, avg_time: float) -> str:
        """Catégorise la performance"""
        if success_rate >= 95 and avg_time < 10:
            return "excellent"
        elif success_rate >= 90 and avg_time < 15:
            return "very_good"
        elif success_rate >= 85 and avg_time < 20:
            return "good"
        elif success_rate >= 80 and avg_time < 25:
            return "average"
        elif success_rate >= 70:
            return "below_average"
        else:
            return "poor"

class LlamaHealthView(APIView):
    """Vue pour vérifier la santé du modèle Llama"""
    
    permission_classes = []
    
    def get(self, request):
        """Vérifie l'état de santé du modèle"""
        try:
            health_status = minimal_llama_manager.get_health_status()
            
            # Ajouter des informations supplémentaires
            health_status['recommendations'] = minimal_llama_manager.get_recommendations()
            health_status['model_info'] = minimal_llama_manager.MODEL_INFO
            
            return Response({
                'success': True,
                'health': health_status,
                'timestamp': datetime.now().isoformat()
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Erreur vérification santé: {e}")
            return Response({
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LlamaTestView(APIView):
    """Vue pour tester le modèle Llama"""
    
    permission_classes = []
    
    def post(self, request):
        """Lance un test du modèle"""
        try:
            test_type = request.data.get('test_type', 'quick')
            agent_type = request.data.get('agent_type', 'general')
            custom_prompt = request.data.get('prompt', None)
            
            if test_type == 'quick':
                # Test rapide
                prompt = custom_prompt or "Bonjour, peux-tu me recommander un livre ?"
                response, metrics = minimal_llama_manager.generate_response(prompt, agent_type)
                
                return Response({
                    'success': True,
                    'test_type': 'quick',
                    'prompt': prompt,
                    'response': response,
                    'metrics': metrics,
                    'timestamp': datetime.now().isoformat()
                }, status=status.HTTP_200_OK)
                
            elif test_type == 'comprehensive':
                # Test complet
                test_results = self._run_comprehensive_test()
                
                return Response({
                    'success': True,
                    'test_type': 'comprehensive',
                    'results': test_results,
                    'timestamp': datetime.now().isoformat()
                }, status=status.HTTP_200_OK)
                
            else:
                return Response({
                    'success': False,
                    'error': f'Type de test non supporté: {test_type}'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Erreur test Llama: {e}")
            return Response({
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _run_comprehensive_test(self) -> Dict[str, Any]:
        """Lance un test complet du modèle"""
        test_cases = [
            {
                'agent_type': 'tech',
                'prompt': 'Recommande-moi des livres pour apprendre Python',
                'expected_keywords': ['python', 'programmation', 'livre']
            },
            {
                'agent_type': 'literature',
                'prompt': 'Suggère-moi des romans français classiques',
                'expected_keywords': ['roman', 'français', 'classique']
            },
            {
                'agent_type': 'manga',
                'prompt': 'Recommande-moi des manga comme Naruto',
                'expected_keywords': ['manga', 'naruto', 'anime']
            },
            {
                'agent_type': 'general',
                'prompt': 'Que peux-tu me recommander à lire ?',
                'expected_keywords': ['livre', 'lecture', 'recommandation']
            }
        ]
        
        results = []
        total_time = 0
        successful_tests = 0
        
        for test_case in test_cases:
            try:
                start_time = time.time()
                response, metrics = minimal_llama_manager.generate_response(
                    test_case['prompt'],
                    test_case['agent_type']
                )
                test_time = time.time() - start_time
                total_time += test_time
                
                # Vérifier les mots-clés
                response_lower = response.lower()
                keywords_found = [
                    keyword for keyword in test_case['expected_keywords']
                    if keyword in response_lower
                ]
                
                success = metrics['success'] and len(keywords_found) > 0
                if success:
                    successful_tests += 1
                
                results.append({
                    'agent_type': test_case['agent_type'],
                    'prompt': test_case['prompt'],
                    'response_length': len(response),
                    'response_time': test_time,
                    'success': success,
                    'keywords_found': keywords_found,
                    'metrics': metrics
                })
                
            except Exception as e:
                results.append({
                    'agent_type': test_case['agent_type'],
                    'prompt': test_case['prompt'],
                    'success': False,
                    'error': str(e)
                })
        
        return {
            'total_tests': len(test_cases),
            'successful_tests': successful_tests,
            'success_rate': (successful_tests / len(test_cases)) * 100,
            'total_time': total_time,
            'avg_time_per_test': total_time / len(test_cases),
            'detailed_results': results
        }

class LlamaConfigView(APIView):
    """Vue pour la configuration du modèle Llama"""
    
    permission_classes = []
    
    def get(self, request):
        """Retourne la configuration actuelle"""
        try:
            config_info = {
                'model_info': minimal_llama_manager.MODEL_INFO,
                'optimal_config': minimal_llama_manager.OPTIMAL_CONFIG,
                'model_name': minimal_llama_manager.MODEL_NAME,
                'base_url': minimal_llama_manager.base_url,
                'stats_file': minimal_llama_manager.stats_file
            }
            
            return Response({
                'success': True,
                'config': config_info,
                'timestamp': datetime.now().isoformat()
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Erreur récupération config: {e}")
            return Response({
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LlamaResetStatsView(APIView):
    """Vue pour réinitialiser les statistiques"""
    
    permission_classes = []
    
    def post(self, request):
        """Remet à zéro les statistiques"""
        try:
            # Vérification de sécurité
            confirm = request.data.get('confirm', False)
            if not confirm:
                return Response({
                    'success': False,
                    'error': 'Confirmation requise pour réinitialiser les statistiques'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Sauvegarder les anciennes stats
            old_stats = minimal_llama_manager.get_detailed_stats()
            
            # Réinitialiser
            minimal_llama_manager.reset_stats()
            
            return Response({
                'success': True,
                'message': 'Statistiques réinitialisées avec succès',
                'old_stats_summary': {
                    'total_queries': old_stats['performance_stats']['total_queries'],
                    'success_rate': old_stats['performance_stats']['success_rate'],
                    'avg_response_time': old_stats['timing_stats']['avg_response_time']
                },
                'timestamp': datetime.now().isoformat()
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Erreur reset stats: {e}")
            return Response({
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LlamaDashboardView(APIView):
    """Vue pour le tableau de bord complet"""
    
    permission_classes = []
    
    def get(self, request):
        """Retourne toutes les informations pour le dashboard"""
        try:
            # Collecter toutes les données
            stats = minimal_llama_manager.get_detailed_stats()
            health = minimal_llama_manager.get_health_status()
            recommendations = minimal_llama_manager.get_recommendations()
            
            # Calculer des métriques pour le dashboard
            dashboard_data = {
                'overview': {
                    'model_name': minimal_llama_manager.MODEL_NAME,
                    'status': health['status'],
                    'performance_grade': stats['performance_stats']['performance_grade'],
                    'total_queries': stats['performance_stats']['total_queries'],
                    'success_rate': stats['performance_stats']['success_rate'],
                    'avg_response_time': stats['timing_stats']['avg_response_time']
                },
                'detailed_stats': stats,
                'health_check': health,
                'recommendations': recommendations,
                'quick_actions': [
                    {
                        'name': 'Test rapide',
                        'endpoint': '/api/chat/llama/test/',
                        'method': 'POST',
                        'description': 'Lance un test rapide du modèle'
                    },
                    {
                        'name': 'Vérifier santé',
                        'endpoint': '/api/chat/llama/health/',
                        'method': 'GET',
                        'description': 'Vérifie l\'état de santé du modèle'
                    },
                    {
                        'name': 'Réinitialiser stats',
                        'endpoint': '/api/chat/llama/reset-stats/',
                        'method': 'POST',
                        'description': 'Remet à zéro les statistiques'
                    }
                ]
            }
            
            return Response({
                'success': True,
                'dashboard': dashboard_data,
                'timestamp': datetime.now().isoformat()
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Erreur dashboard: {e}")
            return Response({
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)