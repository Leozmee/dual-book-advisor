"""
Gestionnaire Optimisé pour Llama 3.2 3B
Fichier: agents/optimized_llama_manager.py

Gestionnaire simplifié uniquement pour Llama 3.2 3B avec statistiques détaillées
"""
import logging
import time
import json
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import ollama

logger = logging.getLogger(__name__)

@dataclass
class LlamaStats:
    """Statistiques détaillées du modèle Llama 3.2 3B"""
    total_queries: int = 0
    successful_queries: int = 0
    failed_queries: int = 0
    total_response_time: float = 0.0
    avg_response_time: float = 0.0
    fastest_response: float = float('inf')
    slowest_response: float = 0.0
    total_tokens_generated: int = 0
    avg_tokens_per_response: float = 0.0
    queries_by_type: Dict[str, int] = None
    daily_usage: Dict[str, int] = None
    last_reset: str = None
    
    def __post_init__(self):
        if self.queries_by_type is None:
            self.queries_by_type = {"tech": 0, "literature": 0, "manga": 0, "general": 0}
        if self.daily_usage is None:
            self.daily_usage = {}
        if self.last_reset is None:
            self.last_reset = datetime.now().isoformat()
    
    def update_stats(self, response_time: float, success: bool, tokens: int, query_type: str):
        """Met à jour les statistiques après une requête"""
        self.total_queries += 1
        
        if success:
            self.successful_queries += 1
            self.total_response_time += response_time
            self.avg_response_time = self.total_response_time / self.successful_queries
            
            if response_time < self.fastest_response:
                self.fastest_response = response_time
            if response_time > self.slowest_response:
                self.slowest_response = response_time
            
            self.total_tokens_generated += tokens
            self.avg_tokens_per_response = self.total_tokens_generated / self.successful_queries
        else:
            self.failed_queries += 1
        
        # Comptage par type
        if query_type in self.queries_by_type:
            self.queries_by_type[query_type] += 1
        
        # Usage quotidien
        today = datetime.now().strftime("%Y-%m-%d")
        if today not in self.daily_usage:
            self.daily_usage[today] = 0
        self.daily_usage[today] += 1
        
        # Nettoyer les données anciennes (garder 30 jours)
        if len(self.daily_usage) > 30:
            sorted_dates = sorted(self.daily_usage.keys())
            for old_date in sorted_dates[:-30]:
                del self.daily_usage[old_date]
    
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

class OptimizedLlamaManager:
    """Gestionnaire optimisé pour Llama 3.2 3B uniquement"""
    
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
    
    # Configuration optimale pour Llama 3.2 3B
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
        self.stats_file = os.path.join(os.path.dirname(__file__), 'llama_stats.json')
        
        # Initialiser le client
        self._init_client()
        
        # Charger les statistiques
        self._load_stats()
        
        logger.info(f"✅ OptimizedLlamaManager initialisé avec {self.MODEL_NAME}")
    
    def _init_client(self):
        """Initialise le client Ollama"""
        try:
            self.client = ollama.Client(host=self.base_url)
            
            # Vérifier la disponibilité du modèle
            self._check_model_availability()
            
            logger.info(f"✅ Client Ollama connecté - {self.MODEL_NAME} prêt")
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation Ollama: {e}")
            raise
    
    def _check_model_availability(self):
        """Vérifie que Llama 3.2 3B est disponible"""
        try:
            models_response = self.client.list()
            available_models = []
            
            if hasattr(models_response, 'models'):
                for model in models_response.models:
                    model_name = getattr(model, 'model', getattr(model, 'name', ''))
                    available_models.append(model_name)
            
            if self.MODEL_NAME not in available_models:
                logger.warning(f"⚠️ Modèle {self.MODEL_NAME} non trouvé")
                logger.info("📥 Téléchargement automatique...")
                self.client.pull(self.MODEL_NAME)
                logger.info("✅ Modèle téléchargé")
            else:
                logger.info(f"✅ Modèle {self.MODEL_NAME} disponible")
                
        except Exception as e:
            logger.error(f"❌ Erreur vérification modèle: {e}")
            raise
    
    def _load_stats(self):
        """Charge les statistiques depuis le fichier"""
        try:
            if os.path.exists(self.stats_file):
                with open(self.stats_file, 'r') as f:
                    data = json.load(f)
                    self.stats = LlamaStats(**data)
                logger.info(f"📊 Statistiques chargées: {self.stats.total_queries} requêtes")
            else:
                logger.info("📊 Nouvelles statistiques initialisées")
        except Exception as e:
            logger.warning(f"⚠️ Erreur chargement stats: {e}")
            self.stats = LlamaStats()
    
    def _save_stats(self):
        """Sauvegarde les statistiques"""
        try:
            with open(self.stats_file, 'w') as f:
                json.dump(asdict(self.stats), f, indent=2)
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde stats: {e}")
    
    def generate_response(self, prompt: str, agent_type: str = "general") -> tuple[str, Dict[str, Any]]:
        """
        Génère une réponse optimisée avec Llama 3.2 3B
        
        Args:
            prompt: Le prompt à traiter
            agent_type: Type d'agent (tech, literature, manga, general)
            
        Returns:
            Tuple[response, metrics]
        """
        start_time = time.time()
        success = False
        response = ""
        
        try:
            # Configuration spécifique par type d'agent
            config = self._get_agent_config(agent_type)
            
            # Appel au modèle
            response_obj = self.client.chat(
                model=self.MODEL_NAME,
                messages=[{
                    'role': 'user',
                    'content': self._enhance_prompt(prompt, agent_type)
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
            self._save_stats()
            
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
            self._save_stats()
            
            metrics = {
                'model_name': self.MODEL_NAME,
                'success': False,
                'response_time': response_time,
                'error': str(e),
                'agent_type': agent_type
            }
            
            return f"❌ Erreur: {str(e)}", metrics
    
    def _get_agent_config(self, agent_type: str) -> Dict[str, Any]:
        """Retourne la configuration optimale pour un type d'agent"""
        base_config = self.OPTIMAL_CONFIG.copy()
        
        if agent_type == "tech":
            # Configuration pour les questions techniques
            base_config.update({
                "temperature": 0.6,  # Plus déterministe
                "num_predict": 600,  # Réponses plus détaillées
                "top_k": 50
            })
        elif agent_type == "literature":
            # Configuration pour la littérature
            base_config.update({
                "temperature": 0.8,  # Plus créatif
                "num_predict": 500,
                "top_p": 0.95
            })
        elif agent_type == "manga":
            # Configuration pour manga/comics
            base_config.update({
                "temperature": 0.75,
                "num_predict": 400,
                "top_k": 45
            })
        
        return base_config
    
    def _enhance_prompt(self, prompt: str, agent_type: str) -> str:
        """Améliore le prompt selon le type d'agent"""
        
        system_prompts = {
            "tech": """Tu es un expert français en livres techniques et programmation. 
Réponds EXCLUSIVEMENT en français. Génère des recommandations personnalisées et professionnelles.
Explique pourquoi ces livres correspondent à la demande. Sois précis sur les technologies et le niveau.""",
            
            "literature": """Tu es un critique littéraire français passionné et cultivé.
Réponds EXCLUSIVEMENT en français. Génère des recommandations chaleureuses et érudites.
Explique les thèmes, le style, et pourquoi ces œuvres plairont. Évoque l'émotion et l'expérience de lecture.""",
            
            "manga": """Tu es un expert français passionné de manga, anime et bandes dessinées.
Réponds EXCLUSIVEMENT en français. Génère des recommandations enthousiastes mais professionnelles.
Explique les genres, l'histoire, les personnages. Utilise les termes français appropriés.""",
            
            "general": """Tu es un bibliothécaire français expert en recommandations.
Réponds EXCLUSIVEMENT en français. Génère des recommandations pertinentes et bien structurées.
Adapte ton style selon le type de contenu demandé."""
        }
        
        system_prompt = system_prompts.get(agent_type, system_prompts["general"])
        
        return f"{system_prompt}\n\nDemande de l'utilisateur: {prompt}\n\nRéponse en français:"
    
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
                "fastest_response": self.stats.fastest_response if self.stats.fastest_response != float('inf') else 0,
                "slowest_response": self.stats.slowest_response,
                "total_processing_time": self.stats.total_response_time
            },
            "usage_stats": {
                "total_tokens_generated": self.stats.total_tokens_generated,
                "avg_tokens_per_response": self.stats.avg_tokens_per_response,
                "queries_by_type": self.stats.queries_by_type,
                "daily_usage": self.stats.daily_usage
            },
            "system_info": {
                "model_name": self.MODEL_NAME,
                "config": self.OPTIMAL_CONFIG,
                "last_reset": self.stats.last_reset,
                "stats_file": self.stats_file
            }
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Vérifie l'état de santé du modèle"""
        try:
            # Test rapide
            start_time = time.time()
            test_response = self.client.chat(
                model=self.MODEL_NAME,
                messages=[{'role': 'user', 'content': 'Bonjour'}],
                options={'num_predict': 50}
            )
            response_time = time.time() - start_time
            
            success = 'message' in test_response
            
            return {
                "status": "healthy" if success else "unhealthy",
                "model_available": success,
                "test_response_time": response_time,
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
    
    def reset_stats(self):
        """Remet à zéro les statistiques"""
        self.stats = LlamaStats()
        self._save_stats()
        logger.info("🔄 Statistiques réinitialisées")
    
    def get_recommendations(self) -> List[str]:
        """Génère des recommandations d'optimisation"""
        recommendations = []
        
        success_rate = self.stats.get_success_rate()
        avg_time = self.stats.avg_response_time
        
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

# Instance globale
optimized_llama_manager = OptimizedLlamaManager()