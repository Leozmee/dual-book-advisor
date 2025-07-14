"""
Évaluateur de Modèles pour RAG
Fichier: agents/model_evaluator.py

Évalue automatiquement les modèles sur des critères spécifiques au RAG
"""
import logging
import time
import json
import os
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import threading

logger = logging.getLogger(__name__)

@dataclass
class EvaluationMetrics:
    """Métriques d'évaluation d'un modèle"""
    model_name: str
    rag_relevance: float  # Pertinence des réponses RAG
    response_quality: float  # Qualité de la réponse
    response_time: float  # Temps de réponse
    accuracy: float  # Précision des informations
    coherence: float  # Cohérence du texte
    completeness: float  # Complétude de la réponse
    language_quality: float  # Qualité du français
    overall_score: float  # Score global

class ModelEvaluator:
    """Évaluateur automatique de modèles"""
    
    # Jeux de tests pour différents domaines
    TEST_QUERIES = {
        'tech': [
            "Recommande-moi des livres sur Python pour débutant",
            "Quels sont les meilleurs livres sur le machine learning ?",
            "Je veux apprendre le développement web, par où commencer ?",
            "Livres sur les algorithmes et structures de données",
            "Ressources pour apprendre Django et Flask"
        ],
        'literature': [
            "Recommande-moi des romans de Victor Hugo",
            "Quels sont les meilleurs livres de science-fiction ?",
            "Je cherche des romans historiques français",
            "Livres sur la littérature du 19ème siècle",
            "Œuvres de littérature contemporaine française"
        ],
        'manga': [
            "Recommande-moi des manga comme Naruto",
            "Quels sont les meilleurs manga de science-fiction ?",
            "Je cherche des manga seinen pour adultes",
            "Manga similaires à Attack on Titan",
            "Bandes dessinées françaises populaires"
        ],
        'factual': [
            "Qui est l'auteur des Misérables ?",
            "Quand a été publié Notre-Dame de Paris ?",
            "Qui a écrit Les Enfants du Capitaine Grant ?",
            "Quel est le genre littéraire de Jules Verne ?",
            "Combien de tomes a Le Seigneur des Anneaux ?"
        ]
    }
    
    # Réponses attendues pour les questions factuelles
    EXPECTED_ANSWERS = {
        "Qui est l'auteur des Misérables ?": "Victor Hugo",
        "Quand a été publié Notre-Dame de Paris ?": "1831",
        "Qui a écrit Les Enfants du Capitaine Grant ?": "Jules Verne",
        "Quel est le genre littéraire de Jules Verne ?": "science-fiction",
        "Combien de tomes a Le Seigneur des Anneaux ?": "trois"
    }
    
    def __init__(self, multi_model_manager):
        self.multi_model_manager = multi_model_manager
        self.evaluation_results = {}
        self.evaluation_history = []
        self._load_evaluation_history()
    
    def _load_evaluation_history(self):
        """Charge l'historique des évaluations"""
        try:
            history_file = os.path.join(os.path.dirname(__file__), 'evaluation_history.json')
            if os.path.exists(history_file):
                with open(history_file, 'r') as f:
                    self.evaluation_history = json.load(f)
        except Exception as e:
            logger.warning(f"⚠️ Erreur chargement historique: {e}")
    
    def _save_evaluation_history(self):
        """Sauvegarde l'historique des évaluations"""
        try:
            history_file = os.path.join(os.path.dirname(__file__), 'evaluation_history.json')
            with open(history_file, 'w') as f:
                json.dump(self.evaluation_history, f, indent=2)
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde historique: {e}")
    
    def evaluate_model_comprehensive(self, model_name: str) -> EvaluationMetrics:
        """Évaluation complète d'un modèle"""
        logger.info(f"🧪 Évaluation complète du modèle {model_name}")
        
        start_time = time.time()
        
        # Résultats par catégorie
        category_results = {}
        
        for category, queries in self.TEST_QUERIES.items():
            category_results[category] = self._evaluate_category(model_name, category, queries)
        
        # Calculer les métriques globales
        metrics = self._calculate_comprehensive_metrics(model_name, category_results)
        
        total_time = time.time() - start_time
        logger.info(f"✅ Évaluation {model_name} terminée en {total_time:.2f}s")
        
        # Sauvegarder les résultats
        self._save_evaluation_result(model_name, metrics, category_results)
        
        return metrics
    
    def _evaluate_category(self, model_name: str, category: str, queries: List[str]) -> Dict[str, Any]:
        """Évalue un modèle sur une catégorie spécifique"""
        results = {
            'category': category,
            'total_queries': len(queries),
            'successful_queries': 0,
            'avg_response_time': 0.0,
            'avg_quality_score': 0.0,
            'responses': []
        }
        
        total_time = 0
        total_quality = 0
        
        for query in queries:
            try:
                start_time = time.time()
                response, metrics = self.multi_model_manager.generate_response(
                    query, model_name, category
                )
                response_time = time.time() - start_time
                
                if metrics.get('success', False):
                    results['successful_queries'] += 1
                    
                    # Évaluer la qualité de la réponse
                    quality_score = self._evaluate_response_quality(
                        query, response, category
                    )
                    
                    total_time += response_time
                    total_quality += quality_score
                    
                    results['responses'].append({
                        'query': query,
                        'response_length': len(response),
                        'response_time': response_time,
                        'quality_score': quality_score,
                        'success': True
                    })
                else:
                    results['responses'].append({
                        'query': query,
                        'success': False,
                        'error': metrics.get('error', 'Unknown error')
                    })
                    
            except Exception as e:
                logger.error(f"❌ Erreur évaluation query '{query}': {e}")
                results['responses'].append({
                    'query': query,
                    'success': False,
                    'error': str(e)
                })
        
        # Calculer les moyennes
        if results['successful_queries'] > 0:
            results['avg_response_time'] = total_time / results['successful_queries']
            results['avg_quality_score'] = total_quality / results['successful_queries']
        
        return results
    
    def _evaluate_response_quality(self, query: str, response: str, category: str) -> float:
        """Évalue la qualité d'une réponse"""
        score = 0.0
        
        # Critères de base
        if len(response) > 50:
            score += 0.2  # Longueur minimum
        
        if len(response) > 200:
            score += 0.1  # Réponse détaillée
        
        # Critères spécifiques à la catégorie
        if category == 'tech':
            score += self._evaluate_tech_response(query, response)
        elif category == 'literature':
            score += self._evaluate_literature_response(query, response)
        elif category == 'manga':
            score += self._evaluate_manga_response(query, response)
        elif category == 'factual':
            score += self._evaluate_factual_response(query, response)
        
        # Critères généraux
        score += self._evaluate_language_quality(response)
        score += self._evaluate_coherence(response)
        
        return min(1.0, score)
    
    def _evaluate_tech_response(self, query: str, response: str) -> float:
        """Évalue une réponse technique"""
        score = 0.0
        tech_keywords = ['python', 'javascript', 'java', 'livre', 'programmation', 'code']
        
        response_lower = response.lower()
        
        # Présence de mots-clés techniques
        keyword_count = sum(1 for keyword in tech_keywords if keyword in response_lower)
        score += min(0.3, keyword_count * 0.1)
        
        # Mentions de livres spécifiques
        if any(word in response_lower for word in ['titre', 'auteur', 'édition']):
            score += 0.2
        
        # Structure de recommandation
        if '1.' in response or '2.' in response or '-' in response:
            score += 0.1
        
        return score
    
    def _evaluate_literature_response(self, query: str, response: str) -> float:
        """Évalue une réponse littéraire"""
        score = 0.0
        lit_keywords = ['roman', 'auteur', 'littérature', 'œuvre', 'récit', 'histoire']
        
        response_lower = response.lower()
        
        # Présence de mots-clés littéraires
        keyword_count = sum(1 for keyword in lit_keywords if keyword in response_lower)
        score += min(0.3, keyword_count * 0.1)
        
        # Mentions d'auteurs célèbres
        famous_authors = ['hugo', 'verne', 'dumas', 'zola', 'balzac', 'camus']
        author_count = sum(1 for author in famous_authors if author in response_lower)
        score += min(0.2, author_count * 0.1)
        
        # Qualité descriptive
        if any(word in response_lower for word in ['style', 'thème', 'époque']):
            score += 0.1
        
        return score
    
    def _evaluate_manga_response(self, query: str, response: str) -> float:
        """Évalue une réponse manga"""
        score = 0.0
        manga_keywords = ['manga', 'anime', 'shounen', 'seinen', 'auteur', 'série']
        
        response_lower = response.lower()
        
        # Présence de mots-clés manga
        keyword_count = sum(1 for keyword in manga_keywords if keyword in response_lower)
        score += min(0.3, keyword_count * 0.1)
        
        # Mentions de manga populaires
        popular_manga = ['naruto', 'one piece', 'dragon ball', 'attack on titan']
        manga_count = sum(1 for manga in popular_manga if manga in response_lower)
        score += min(0.2, manga_count * 0.1)
        
        # Informations sur le genre
        if any(word in response_lower for word in ['genre', 'type', 'style']):
            score += 0.1
        
        return score
    
    def _evaluate_factual_response(self, query: str, response: str) -> float:
        """Évalue une réponse factuelle"""
        score = 0.0
        
        # Vérifier si la réponse contient l'information attendue
        if query in self.EXPECTED_ANSWERS:
            expected = self.EXPECTED_ANSWERS[query].lower()
            if expected in response.lower():
                score += 0.5  # Réponse correcte
        
        # Réponse concise (bonus pour les réponses factuelles)
        if len(response) < 200:
            score += 0.2
        
        # Présence d'informations spécifiques
        if any(word in response.lower() for word in ['auteur', 'année', 'publié']):
            score += 0.1
        
        return score
    
    def _evaluate_language_quality(self, response: str) -> float:
        """Évalue la qualité de la langue française"""
        score = 0.0
        
        # Vérification basique du français
        french_indicators = ['le', 'la', 'les', 'un', 'une', 'de', 'du', 'des', 'et', 'est']
        french_count = sum(1 for word in french_indicators if word in response.lower())
        
        if french_count >= 5:
            score += 0.1
        
        # Absence de mots anglais (sauf termes techniques)
        english_words = ['the', 'and', 'is', 'are', 'book', 'author', 'this', 'that']
        english_count = sum(1 for word in english_words if word in response.lower())
        
        if english_count == 0:
            score += 0.05
        
        return score
    
    def _evaluate_coherence(self, response: str) -> float:
        """Évalue la cohérence du texte"""
        score = 0.0
        
        # Présence de structure
        if any(marker in response for marker in ['1.', '2.', '-', '•']):
            score += 0.05
        
        # Longueur raisonnable
        if 100 <= len(response) <= 800:
            score += 0.05
        
        # Présence de phrases complètes
        if response.count('.') >= 2:
            score += 0.05
        
        return score
    
    def _calculate_comprehensive_metrics(self, model_name: str, category_results: Dict) -> EvaluationMetrics:
        """Calcule les métriques complètes"""
        total_queries = sum(r['total_queries'] for r in category_results.values())
        successful_queries = sum(r['successful_queries'] for r in category_results.values())
        
        # Moyennes pondérées
        avg_response_time = 0
        avg_quality_score = 0
        
        for category, results in category_results.items():
            if results['successful_queries'] > 0:
                weight = results['successful_queries'] / max(successful_queries, 1)
                avg_response_time += results['avg_response_time'] * weight
                avg_quality_score += results['avg_quality_score'] * weight
        
        # Calculs spécifiques
        accuracy = successful_queries / max(total_queries, 1)
        rag_relevance = avg_quality_score * 0.8  # Basé sur la qualité des réponses
        coherence = avg_quality_score * 0.9  # Cohérence incluse dans la qualité
        completeness = min(1.0, avg_quality_score + 0.1)  # Bonus pour complétude
        language_quality = 0.8  # Estimation basique (à améliorer)
        
        # Score global
        overall_score = (
            rag_relevance * 0.3 +
            avg_quality_score * 0.25 +
            accuracy * 0.2 +
            coherence * 0.15 +
            (1 / max(avg_response_time, 0.1)) * 0.1
        )
        
        return EvaluationMetrics(
            model_name=model_name,
            rag_relevance=rag_relevance,
            response_quality=avg_quality_score,
            response_time=avg_response_time,
            accuracy=accuracy,
            coherence=coherence,
            completeness=completeness,
            language_quality=language_quality,
            overall_score=overall_score
        )
    
    def _save_evaluation_result(self, model_name: str, metrics: EvaluationMetrics, category_results: Dict):
        """Sauvegarde les résultats d'évaluation"""
        result = {
            'model_name': model_name,
            'timestamp': datetime.now().isoformat(),
            'metrics': {
                'rag_relevance': metrics.rag_relevance,
                'response_quality': metrics.response_quality,
                'response_time': metrics.response_time,
                'accuracy': metrics.accuracy,
                'coherence': metrics.coherence,
                'completeness': metrics.completeness,
                'language_quality': metrics.language_quality,
                'overall_score': metrics.overall_score
            },
            'category_results': category_results
        }
        
        self.evaluation_results[model_name] = result
        self.evaluation_history.append(result)
        self._save_evaluation_history()
    
    def compare_models(self, model_names: List[str] = None) -> Dict[str, Any]:
        """Compare plusieurs modèles"""
        if not model_names:
            model_names = self.multi_model_manager.preferred_models
        
        logger.info(f"🔄 Comparaison des modèles: {model_names}")
        
        comparison_results = {}
        
        for model_name in model_names:
            try:
                metrics = self.evaluate_model_comprehensive(model_name)
                comparison_results[model_name] = metrics
            except Exception as e:
                logger.error(f"❌ Erreur évaluation {model_name}: {e}")
                comparison_results[model_name] = None
        
        # Classer les résultats
        valid_results = {k: v for k, v in comparison_results.items() if v is not None}
        
        if valid_results:
            best_model = max(valid_results.items(), key=lambda x: x[1].overall_score)
            
            return {
                'best_model': best_model[0],
                'best_score': best_model[1].overall_score,
                'results': comparison_results,
                'ranking': sorted(valid_results.items(), key=lambda x: x[1].overall_score, reverse=True)
            }
        
        return {'error': 'Aucun modèle évalué avec succès'}
    
    def get_evaluation_report(self) -> Dict[str, Any]:
        """Génère un rapport d'évaluation"""
        if not self.evaluation_results:
            return {'error': 'Aucune évaluation disponible'}
        
        report = {
            'total_models_evaluated': len(self.evaluation_results),
            'evaluation_timestamp': datetime.now().isoformat(),
            'models': {}
        }
        
        # Classer les modèles par score
        sorted_models = sorted(
            self.evaluation_results.items(),
            key=lambda x: x[1]['metrics']['overall_score'],
            reverse=True
        )
        
        for model_name, result in sorted_models:
            report['models'][model_name] = {
                'rank': len(report['models']) + 1,
                'overall_score': result['metrics']['overall_score'],
                'strengths': self._identify_strengths(result),
                'weaknesses': self._identify_weaknesses(result),
                'recommendation': self._generate_recommendation(result)
            }
        
        return report
    
    def _identify_strengths(self, result: Dict) -> List[str]:
        """Identifie les forces d'un modèle"""
        strengths = []
        metrics = result['metrics']
        
        if metrics['response_time'] < 2.0:
            strengths.append("Temps de réponse rapide")
        
        if metrics['accuracy'] > 0.8:
            strengths.append("Haute précision")
        
        if metrics['rag_relevance'] > 0.7:
            strengths.append("Excellente pertinence RAG")
        
        if metrics['coherence'] > 0.8:
            strengths.append("Réponses cohérentes")
        
        return strengths
    
    def _identify_weaknesses(self, result: Dict) -> List[str]:
        """Identifie les faiblesses d'un modèle"""
        weaknesses = []
        metrics = result['metrics']
        
        if metrics['response_time'] > 5.0:
            weaknesses.append("Temps de réponse lent")
        
        if metrics['accuracy'] < 0.6:
            weaknesses.append("Précision faible")
        
        if metrics['rag_relevance'] < 0.5:
            weaknesses.append("Pertinence RAG insuffisante")
        
        if metrics['language_quality'] < 0.7:
            weaknesses.append("Qualité de langue à améliorer")
        
        return weaknesses
    
    def _generate_recommendation(self, result: Dict) -> str:
        """Génère une recommandation pour un modèle"""
        metrics = result['metrics']
        overall_score = metrics['overall_score']
        
        if overall_score > 0.8:
            return "Excellent choix pour toutes les tâches"
        elif overall_score > 0.6:
            return "Bon modèle avec quelques améliorations possibles"
        elif overall_score > 0.4:
            return "Modèle moyen, approprié pour des tâches spécifiques"
        else:
            return "Modèle nécessitant des améliorations significatives"
    
    def benchmark_models_async(self, model_names: List[str] = None, callback=None):
        """Lance l'évaluation des modèles en arrière-plan"""
        def run_benchmark():
            try:
                results = self.compare_models(model_names)
                if callback:
                    callback(results)
                logger.info("✅ Benchmark terminé")
            except Exception as e:
                logger.error(f"❌ Erreur benchmark: {e}")
                if callback:
                    callback({'error': str(e)})
        
        thread = threading.Thread(target=run_benchmark)
        thread.daemon = True
        thread.start()
        
        return thread

# Instance globale d'évaluation
model_evaluator = None

def get_model_evaluator(multi_model_manager):
    """Retourne l'instance globale d'évaluation"""
    global model_evaluator
    if model_evaluator is None:
        model_evaluator = ModelEvaluator(multi_model_manager)
    return model_evaluator