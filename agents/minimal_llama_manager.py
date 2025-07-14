"""
Gestionnaire Llama minimal pour éviter les blocages Django
Fichier: agents/minimal_llama_manager.py

Version ultra-simplifiée qui ne fait AUCUNE initialisation
"""
import logging
import time
import json
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class LlamaStats:
    """Statistiques simplifiées du modèle Llama"""
    total_queries: int = 0
    successful_queries: int = 0
    failed_queries: int = 0
    total_response_time: float = 0.0
    avg_response_time: float = 0.0
    
    def update_stats(self, response_time: float, success: bool, tokens: int, query_type: str):
        """Met à jour les statistiques après une requête"""
        self.total_queries += 1
        
        if success:
            self.successful_queries += 1
            self.total_response_time += response_time
            self.avg_response_time = self.total_response_time / self.successful_queries
        else:
            self.failed_queries += 1
    
    def get_success_rate(self) -> float:
        """Taux de succès en pourcentage"""
        if self.total_queries == 0:
            return 0.0
        return (self.successful_queries / self.total_queries) * 100
    
    def get_performance_grade(self) -> str:
        """Note de performance basée sur les statistiques"""
        success_rate = self.get_success_rate()
        
        if success_rate >= 95 and self.avg_response_time < 10:
            return "A+"
        elif success_rate >= 90 and self.avg_response_time < 15:
            return "A"
        elif success_rate >= 85 and self.avg_response_time < 20:
            return "B+"
        elif success_rate >= 80 and self.avg_response_time < 25:
            return "B"
        elif success_rate >= 70 and self.avg_response_time < 30:
            return "C+"
        elif success_rate >= 60:
            return "C"
        else:
            return "D"

class MinimalLlamaManager:
    """Gestionnaire Llama minimal - AUCUNE initialisation"""
    
    MODEL_NAME = "llama3.2:3b"
    MODEL_INFO = {
        "name": "Llama 3.2 3B",
        "size": "3B parameters",
        "ram_usage": "~6GB",
        "strengths": ["RAG", "Raisonnement", "Multilingue", "Équilibre performance/vitesse"],
        "optimal_for": ["Recommandations littéraires", "Analyse technique", "Conversations générales"],
        "language": "Français optimisé",
        "context_window": "4096 tokens",
        "speed": "Modéré (10-30s par requête)"
    }
    
    OPTIMAL_CONFIG = {
        "temperature": 0.7,
        "top_p": 0.9,
        "top_k": 40,
        "num_predict": 512,
        "repeat_penalty": 1.1,
        "seed": -1,
        "stop": ["</s>", "<|im_end|>"]
    }
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.client = None
        self.stats = LlamaStats()
        self._initialized = False
        
        # AUCUNE initialisation - tout est lazy
        logger.info("✅ MinimalLlamaManager créé (pas d'initialisation)")
    
    def _ensure_initialized(self):
        """Initialise seulement quand nécessaire"""
        if self._initialized:
            return
        
        try:
            # Import différé
            import ollama
            
            # Initialiser le client
            self.client = ollama.Client(host=self.base_url)
            self._initialized = True
            
            logger.info("✅ MinimalLlamaManager initialisé")
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation: {e}")
            raise
    
    def is_available(self) -> bool:
        """Vérifie si le service est disponible"""
        try:
            self._ensure_initialized()
            return self.client is not None
        except Exception:
            return False
    
    def generate_response(self, prompt: str, agent_type: str = "general") -> tuple[str, Dict[str, Any]]:
        """Génère une réponse avec Llama 3.2 3B"""
        if not self.is_available():
            return "❌ Service Llama non disponible", {
                'model_name': self.MODEL_NAME,
                'success': False,
                'error': 'Service non disponible',
                'response_time': 0.0,
                'agent_type': agent_type
            }
        
        start_time = time.time()
        success = False
        response = ""
        
        try:
            # Configuration simple
            config = self.OPTIMAL_CONFIG.copy()
            
            # Prompt simple
            simple_prompt = f"Réponds en français à cette question: {prompt}"
            
            # Appel au modèle
            response_obj = self.client.chat(
                model=self.MODEL_NAME,
                messages=[{
                    'role': 'user',
                    'content': simple_prompt
                }],
                options=config
            )
            
            # Extraire la réponse
            if 'message' in response_obj and 'content' in response_obj['message']:
                response = response_obj['message']['content']
                success = True
            else:
                response = str(response_obj)
            
            response_time = time.time() - start_time
            
            # Calculer les tokens (approximation)
            tokens = len(response.split())
            
            # Mettre à jour les statistiques
            self.stats.update_stats(response_time, success, tokens, agent_type)
            
            # Métriques de retour
            metrics = {
                'model_name': self.MODEL_NAME,
                'success': success,
                'response_time': response_time,
                'tokens_generated': tokens,
                'agent_type': agent_type,
                'config_used': config
            }
            
            logger.info(f"✅ Réponse générée en {response_time:.2f}s ({tokens} tokens)")
            return response, metrics
            
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"❌ Erreur génération: {e}")
            
            # Mettre à jour les stats d'échec
            self.stats.update_stats(response_time, False, 0, agent_type)
            
            metrics = {
                'model_name': self.MODEL_NAME,
                'success': False,
                'response_time': response_time,
                'error': str(e),
                'agent_type': agent_type
            }
            
            return f"❌ Erreur: {str(e)}", metrics
    
    def get_detailed_stats(self) -> Dict[str, Any]:
        """Retourne des statistiques détaillées"""
        return {
            "model_info": self.MODEL_INFO,
            "performance_stats": {
                "total_queries": self.stats.total_queries,
                "successful_queries": self.stats.successful_queries,
                "failed_queries": self.stats.failed_queries,
                "success_rate": self.stats.get_success_rate(),
                "performance_grade": self.stats.get_performance_grade()
            },
            "timing_stats": {
                "avg_response_time": self.stats.avg_response_time,
                "total_processing_time": self.stats.total_response_time
            },
            "system_info": {
                "model_name": self.MODEL_NAME,
                "config": self.OPTIMAL_CONFIG,
                "initialized": self._initialized
            }
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Vérifie l'état de santé du modèle"""
        try:
            if not self.is_available():
                return {
                    "status": "unavailable",
                    "model_available": False,
                    "error": "Service Ollama non disponible",
                    "last_check": datetime.now().isoformat()
                }
            
            return {
                "status": "healthy",
                "model_available": True,
                "last_check": datetime.now().isoformat(),
                "performance_grade": self.stats.get_performance_grade(),
                "success_rate": self.stats.get_success_rate()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "model_available": False,
                "error": str(e),
                "last_check": datetime.now().isoformat()
            }
    
    def get_recommendations(self) -> List[str]:
        """Génère des recommandations d'optimisation"""
        if not self.is_available():
            return ["Service Ollama non disponible - Démarrez ollama serve"]
        
        success_rate = self.stats.get_success_rate()
        avg_time = self.stats.avg_response_time
        
        recommendations = []
        
        if success_rate < 90:
            recommendations.append("Taux de succès faible - Vérifiez la stabilité d'Ollama")
        
        if avg_time > 30:
            recommendations.append("Temps de réponse lent - Considérez réduire num_predict")
        
        if avg_time < 5:
            recommendations.append("Très bonnes performances - Configuration optimale")
        
        if self.stats.total_queries < 10:
            recommendations.append("Peu de données - Effectuez plus de tests pour des stats fiables")
        
        if not recommendations:
            recommendations.append("Performances excellentes - Continuez ainsi !")
        
        return recommendations

# Instance globale minimal
minimal_llama_manager = MinimalLlamaManager()