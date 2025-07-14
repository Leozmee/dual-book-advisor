"""
Gestionnaire Multi-Modèles avec Évaluation Automatique
Fichier: agents/multi_model_manager.py

Supporte: Llama 3.2, Mistral 7B, Gemma 2B avec évaluation des performances
"""
import logging
import time
import json
import os
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class ModelPerformance:
    """Métriques de performance d'un modèle"""
    model_name: str
    avg_response_time: float
    avg_quality_score: float
    success_rate: float
    total_queries: int
    rag_relevance_score: float
    memory_usage: float
    
    def get_overall_score(self) -> float:
        """Calcule un score global pondéré"""
        # Pondération: qualité 40%, temps 30%, succès 20%, relevance 10%
        return (
            self.avg_quality_score * 0.4 +
            (1 / max(self.avg_response_time, 0.1)) * 0.3 +
            self.success_rate * 0.2 +
            self.rag_relevance_score * 0.1
        )

class MultiModelManager:
    """Gestionnaire multi-modèles avec évaluation automatique"""
    
    # Modèles optimaux pour RAG avec leurs configurations
    OPTIMAL_MODELS = {
        'llama3.2:3b': {
            'provider': 'ollama',
            'description': 'Llama 3.2 3B - Équilibre performance/vitesse',
            'config': {
                'temperature': 0.6,
                'max_tokens': 512,
                'top_p': 0.8,
                'top_k': 40,
                'num_predict': 512
            },
            'strengths': ['RAG', 'Raisonnement', 'Multilingue'],
            'ram_usage': '6GB'
        },
        'mistral:7b': {
            'provider': 'ollama',
            'description': 'Mistral 7B - Excellent pour RAG et analyse',
            'config': {
                'temperature': 0.7,
                'max_tokens': 600,
                'top_p': 0.9,
                'top_k': 50,
                'num_predict': 600
            },
            'strengths': ['RAG', 'Analyse', 'Précision'],
            'ram_usage': '8GB'
        },
        'gemma2:2b': {
            'provider': 'ollama',
            'description': 'Gemma 2B - Rapide et efficace',
            'config': {
                'temperature': 0.7,
                'max_tokens': 400,
                'top_p': 0.9,
                'top_k': 40,
                'num_predict': 400
            },
            'strengths': ['Vitesse', 'Efficacité', 'Légèreté'],
            'ram_usage': '4GB'
        },
        'llama3.2:1b': {
            'provider': 'ollama',
            'description': 'Llama 3.2 1B - Ultra-rapide',
            'config': {
                'temperature': 0.6,
                'max_tokens': 300,
                'top_p': 0.8,
                'top_k': 40,
                'num_predict': 300
            },
            'strengths': ['Vitesse', 'Légèreté', 'Efficacité'],
            'ram_usage': '2GB'
        },
        'mistral:instruct': {
            'provider': 'ollama',
            'description': 'Mistral Instruct - Optimisé pour instructions',
            'config': {
                'temperature': 0.7,
                'max_tokens': 500,
                'top_p': 0.9,
                'top_k': 50,
                'num_predict': 500
            },
            'strengths': ['Instructions', 'RAG', 'Précision'],
            'ram_usage': '8GB'
        }
    }
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.performances: Dict[str, ModelPerformance] = {}
        self.current_best_model = None
        self.evaluation_enabled = os.getenv('MODEL_EVALUATION_ENABLED', 'true').lower() == 'true'
        self.preferred_models = os.getenv('PREFERRED_MODELS', 'llama3.2:3b,mistral:7b,gemma2:2b').split(',')
        
        # Clients pour chaque provider
        self.clients = {}
        self._init_clients()
        
        # Charger les performances sauvegardées
        self._load_performance_data()
        
        # Vérifier et télécharger les modèles
        self._ensure_models_available()
    
    def _init_clients(self):
        """Initialise les clients pour chaque provider"""
        try:
            import ollama
            self.clients['ollama'] = ollama.Client(host=self.base_url)
            logger.info("✅ Client Ollama initialisé")
        except ImportError:
            logger.warning("⚠️ Client Ollama non disponible")
    
    def _ensure_models_available(self):
        """Vérifie et télécharge les modèles nécessaires"""
        if 'ollama' not in self.clients:
            return
            
        try:
            # Obtenir la liste des modèles installés
            models_response = self.clients['ollama'].list()
            available_models = []
            
            if hasattr(models_response, 'models'):
                for model in models_response.models:
                    model_name = getattr(model, 'model', getattr(model, 'name', ''))
                    available_models.append(model_name)
            
            # Télécharger les modèles manquants
            for model_name in self.preferred_models:
                if model_name not in available_models:
                    logger.info(f"📥 Téléchargement du modèle {model_name}...")
                    try:
                        self.clients['ollama'].pull(model_name)
                        logger.info(f"✅ Modèle {model_name} téléchargé")
                    except Exception as e:
                        logger.warning(f"⚠️ Échec téléchargement {model_name}: {e}")
                else:
                    logger.info(f"✅ Modèle {model_name} déjà disponible")
                    
        except Exception as e:
            logger.error(f"❌ Erreur vérification modèles: {e}")
    
    def _load_performance_data(self):
        """Charge les données de performance depuis un fichier"""
        try:
            perf_file = os.path.join(os.path.dirname(__file__), 'model_performances.json')
            if os.path.exists(perf_file):
                with open(perf_file, 'r') as f:
                    data = json.load(f)
                    
                for model_name, perf_data in data.items():
                    self.performances[model_name] = ModelPerformance(**perf_data)
                
                # Déterminer le meilleur modèle
                if self.performances:
                    self.current_best_model = max(
                        self.performances.items(),
                        key=lambda x: x[1].get_overall_score()
                    )[0]
                    logger.info(f"🏆 Meilleur modèle actuel: {self.current_best_model}")
                
        except Exception as e:
            logger.warning(f"⚠️ Erreur chargement performances: {e}")
    
    def _save_performance_data(self):
        """Sauvegarde les données de performance"""
        try:
            perf_file = os.path.join(os.path.dirname(__file__), 'model_performances.json')
            data = {}
            
            for model_name, performance in self.performances.items():
                data[model_name] = {
                    'model_name': performance.model_name,
                    'avg_response_time': performance.avg_response_time,
                    'avg_quality_score': performance.avg_quality_score,
                    'success_rate': performance.success_rate,
                    'total_queries': performance.total_queries,
                    'rag_relevance_score': performance.rag_relevance_score,
                    'memory_usage': performance.memory_usage
                }
            
            with open(perf_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde performances: {e}")
    
    def generate_response(self, 
                         prompt: str, 
                         model_name: str = None,
                         agent_type: str = "general") -> Tuple[str, Dict[str, Any]]:
        """
        Génère une réponse avec le modèle spécifié ou le meilleur disponible
        
        Args:
            prompt: Le prompt à traiter
            model_name: Nom du modèle (optionnel, utilise le meilleur si None)
            agent_type: Type d'agent (tech, literature, manga, general)
            
        Returns:
            Tuple[response, metrics]
        """
        # Choisir le modèle
        if model_name is None:
            model_name = self.get_best_model_for_task(agent_type)
        
        if model_name not in self.OPTIMAL_MODELS:
            raise ValueError(f"Modèle {model_name} non supporté")
        
        model_config = self.OPTIMAL_MODELS[model_name]
        provider = model_config['provider']
        
        if provider not in self.clients:
            raise ValueError(f"Provider {provider} non disponible")
        
        # Générer la réponse
        start_time = time.time()
        success = False
        response = ""
        metrics = {}
        
        try:
            if provider == 'ollama':
                response = self._generate_ollama_response(model_name, prompt, model_config)
            
            response_time = time.time() - start_time
            success = True
            
            # Calculer les métriques
            metrics = {
                'model_name': model_name,
                'response_time': response_time,
                'success': success,
                'prompt_length': len(prompt),
                'response_length': len(response),
                'agent_type': agent_type
            }
            
            # Mettre à jour les performances si l'évaluation est activée
            if self.evaluation_enabled:
                self._update_performance_metrics(model_name, response_time, success, response, prompt)
            
            logger.info(f"✅ {model_name} réponse générée en {response_time:.2f}s")
            return response, metrics
            
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"❌ Erreur {model_name}: {e}")
            
            # Mettre à jour les performances d'échec
            if self.evaluation_enabled:
                self._update_performance_metrics(model_name, response_time, False, "", prompt)
            
            metrics = {
                'model_name': model_name,
                'response_time': response_time,
                'success': False,
                'error': str(e),
                'agent_type': agent_type
            }
            
            return f"Erreur {model_name}: {str(e)}", metrics
    
    def _generate_ollama_response(self, model_name: str, prompt: str, model_config: Dict) -> str:
        """Génère une réponse via Ollama"""
        client = self.clients['ollama']
        config = model_config['config']
        
        response = client.chat(
            model=model_name,
            messages=[{'role': 'user', 'content': prompt}],
            options={
                'temperature': config.get('temperature', 0.7),
                'num_predict': config.get('num_predict', 400),
                'top_p': config.get('top_p', 0.9),
                'top_k': config.get('top_k', 40)
            }
        )
        
        if 'message' in response and 'content' in response['message']:
            return response['message']['content']
        else:
            return str(response)
    
    def _update_performance_metrics(self, model_name: str, response_time: float, 
                                   success: bool, response: str, prompt: str):
        """Met à jour les métriques de performance"""
        if model_name not in self.performances:
            self.performances[model_name] = ModelPerformance(
                model_name=model_name,
                avg_response_time=response_time,
                avg_quality_score=0.5,
                success_rate=1.0 if success else 0.0,
                total_queries=1,
                rag_relevance_score=0.5,
                memory_usage=0.0
            )
        else:
            perf = self.performances[model_name]
            
            # Mise à jour des moyennes
            total = perf.total_queries
            perf.avg_response_time = (perf.avg_response_time * total + response_time) / (total + 1)
            perf.success_rate = (perf.success_rate * total + (1.0 if success else 0.0)) / (total + 1)
            perf.total_queries += 1
            
            # Calculer un score de qualité basique
            if success and response:
                quality_score = min(1.0, len(response) / 200.0)  # Score basé sur la longueur
                perf.avg_quality_score = (perf.avg_quality_score * total + quality_score) / (total + 1)
                
                # Score de relevance RAG (basique)
                relevance_score = 0.8 if len(response) > 100 else 0.5
                perf.rag_relevance_score = (perf.rag_relevance_score * total + relevance_score) / (total + 1)
        
        # Sauvegarder les données
        self._save_performance_data()
        
        # Mettre à jour le meilleur modèle
        self._update_best_model()
    
    def _update_best_model(self):
        """Met à jour le modèle avec les meilleures performances"""
        if not self.performances:
            return
            
        best_model = max(
            self.performances.items(),
            key=lambda x: x[1].get_overall_score()
        )[0]
        
        if best_model != self.current_best_model:
            logger.info(f"🏆 Nouveau meilleur modèle: {best_model} (remplace {self.current_best_model})")
            self.current_best_model = best_model
    
    def get_best_model_for_task(self, agent_type: str = "general") -> str:
        """Retourne le meilleur modèle pour un type de tâche"""
        # Recommandations par type de tâche
        task_preferences = {
            'tech': ['mistral:7b', 'llama3.2:3b', 'gemma2:2b'],
            'literature': ['llama3.2:3b', 'mistral:7b', 'gemma2:2b'],
            'manga': ['llama3.2:3b', 'gemma2:2b', 'mistral:7b'],
            'general': ['llama3.2:3b', 'mistral:7b', 'gemma2:2b']
        }
        
        preferred = task_preferences.get(agent_type, task_preferences['general'])
        
        # Si on a des données de performance, utiliser le meilleur
        if self.current_best_model and self.current_best_model in preferred:
            return self.current_best_model
        
        # Sinon, utiliser le premier disponible dans les préférences
        for model in preferred:
            if model in self.preferred_models:
                return model
        
        # Fallback
        return self.preferred_models[0] if self.preferred_models else 'gemma2:2b'
    
    def evaluate_all_models(self, test_queries: List[str] = None) -> Dict[str, Dict]:
        """Évalue tous les modèles disponibles"""
        if not test_queries:
            test_queries = [
                "Recommande-moi un livre sur Python pour débutant",
                "Quels sont les meilleurs romans de science-fiction ?",
                "Suggère-moi des manga comme Attack on Titan",
                "Explique-moi les concepts de base du machine learning"
            ]
        
        results = {}
        
        for model_name in self.preferred_models:
            if model_name not in self.OPTIMAL_MODELS:
                continue
                
            logger.info(f"🧪 Évaluation du modèle {model_name}...")
            model_results = []
            
            for query in test_queries:
                try:
                    response, metrics = self.generate_response(query, model_name)
                    model_results.append({
                        'query': query,
                        'response': response[:100] + "..." if len(response) > 100 else response,
                        'metrics': metrics
                    })
                except Exception as e:
                    model_results.append({
                        'query': query,
                        'error': str(e),
                        'metrics': {'success': False}
                    })
            
            results[model_name] = {
                'results': model_results,
                'performance': self.performances.get(model_name, None)
            }
        
        return results
    
    def get_model_rankings(self) -> List[Dict]:
        """Retourne le classement des modèles"""
        rankings = []
        
        for model_name, performance in self.performances.items():
            model_info = self.OPTIMAL_MODELS.get(model_name, {})
            rankings.append({
                'model_name': model_name,
                'overall_score': performance.get_overall_score(),
                'response_time': performance.avg_response_time,
                'quality_score': performance.avg_quality_score,
                'success_rate': performance.success_rate,
                'total_queries': performance.total_queries,
                'description': model_info.get('description', ''),
                'strengths': model_info.get('strengths', []),
                'ram_usage': model_info.get('ram_usage', 'Unknown')
            })
        
        # Trier par score global
        rankings.sort(key=lambda x: x['overall_score'], reverse=True)
        return rankings
    
    def get_system_status(self) -> Dict[str, Any]:
        """Retourne le statut du système multi-modèles"""
        return {
            'available_models': list(self.OPTIMAL_MODELS.keys()),
            'preferred_models': self.preferred_models,
            'current_best_model': self.current_best_model,
            'evaluation_enabled': self.evaluation_enabled,
            'total_performances': len(self.performances),
            'ollama_available': 'ollama' in self.clients,
            'base_url': self.base_url
        }
    
    def reset_performance_data(self):
        """Remet à zéro les données de performance"""
        self.performances = {}
        self.current_best_model = None
        self._save_performance_data()
        logger.info("🔄 Données de performance réinitialisées")

# Instance globale
multi_model_manager = MultiModelManager()