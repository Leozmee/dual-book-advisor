"""
Gestionnaire pour Gemma-2-2b via Ollama
Fichier: agents/ollama_gemma_manager.py
"""
import logging
import ollama
import requests
from typing import List, Dict, Any, Optional
import time

logger = logging.getLogger(__name__)


class OllamaGemmaManager:
    """Gestionnaire pour Gemma-2-2b via Ollama"""
    
    def __init__(self, model_name: str = "gemma2:2b"):
        self.model_name = model_name
        self.client = None
        self.base_url = "http://localhost:11434"
        self._init_client()
    
    def _init_client(self):
        """Initialise le client Ollama"""
        try:
            logger.info(f"🚀 Initialisation Ollama avec {self.model_name}")
            
            # Vérifier que le service Ollama est démarré
            self._check_ollama_service()
            
            # Initialiser le client
            self.client = ollama.Client(host=self.base_url)
            
            # Vérifier que le modèle est disponible
            self._check_model_availability()
            
            logger.info("✅ Ollama Gemma initialisé avec succès")
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation Ollama: {e}")
            raise
    
    def _check_ollama_service(self):
        """Vérifie que le service Ollama est démarré"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code != 200:
                raise Exception("Service Ollama non accessible")
        except requests.exceptions.RequestException:
            raise Exception("Service Ollama non démarré. Lancez: 'ollama serve'")
    
    def _check_model_availability(self):
        """Vérifie que le modèle Gemma est disponible"""
        try:
            models_response = self.client.list()
            
            # Fix: vérifier la structure de la réponse
            if isinstance(models_response, dict) and 'models' in models_response:
                available_models = [model.get('name', '') for model in models_response['models']]
            else:
                # Fallback si la structure est différente
                available_models = []
            
            if self.model_name not in available_models:
                logger.warning(f"⚠️ Modèle {self.model_name} non trouvé dans {available_models}")
                logger.info("📥 Tentative de téléchargement...")
                try:
                    self.client.pull(self.model_name)
                    logger.info("✅ Modèle téléchargé")
                except Exception as pull_error:
                    logger.warning(f"⚠️ Téléchargement échoué: {pull_error}")
            else:
                logger.info(f"✅ Modèle {self.model_name} disponible")
            
        except Exception as e:
            logger.warning(f"⚠️ Vérification modèle échouée: {e}")
    
    def generate_response(self, prompt: str, temperature: float = 0.7, max_tokens: int = 512) -> str:
        """Génère une réponse avec Gemma via Ollama"""
        try:
            start_time = time.time()
            
            response = self.client.chat(
                model=self.model_name,
                messages=[
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                options={
                    'temperature': temperature,
                    'num_predict': max_tokens,
                    'top_p': 0.9,
                    'top_k': 40
                }
            )
            
            generation_time = time.time() - start_time
            logger.info(f"⚡ Génération Gemma en {generation_time:.2f}s")
            
            # Extraire le contenu de la réponse
            if 'message' in response and 'content' in response['message']:
                return response['message']['content']
            else:
                logger.warning("⚠️ Format de réponse inattendu")
                return str(response)
            
        except Exception as e:
            logger.error(f"❌ Erreur génération Ollama: {e}")
            return f"Erreur: {str(e)}"
    
    def generate_book_recommendation(self, query: str, books_context: str, agent_type: str = "literature") -> str:
        """Génère une recommandation de livre personnalisée"""
        try:
            # Créer un prompt adapté selon le type d'agent
            if agent_type == "tech":
                prompt = self._create_tech_prompt(query, books_context)
            elif agent_type == "manga":
                prompt = self._create_manga_prompt(query, books_context)
            else:  # literature
                prompt = self._create_literature_prompt(query, books_context)
            
            return self.generate_response(prompt, temperature=0.8, max_tokens=400)
            
        except Exception as e:
            logger.error(f"❌ Erreur recommandation: {e}")
            return "Erreur lors de la génération de recommandation"
    
    def _create_tech_prompt(self, query: str, books_context: str) -> str:
        """Crée un prompt pour les recommandations techniques"""
        return f"""Tu es un expert en livres techniques et programmation. 

Demande de l'utilisateur: "{query}"

Livres techniques disponibles:
{books_context}

Instructions:
- Génère une recommandation personnalisée et engageante
- Explique pourquoi ces livres correspondent à la demande
- Sois précis sur les technologies, le niveau de difficulté, et les bénéfices
- Utilise des emojis tech (🔧, 💻, 📚, ⭐)
- Reste concis mais informatif

Recommandation:"""
    
    def _create_literature_prompt(self, query: str, books_context: str) -> str:
        """Crée un prompt pour les recommandations littéraires"""
        return f"""Tu es un critique littéraire passionné et cultivé.

Demande de l'utilisateur: "{query}"

Livres littéraires disponibles:
{books_context}

Instructions:
- Génère une recommandation chaleureuse et érudite
- Explique les thèmes, le style, et pourquoi ces œuvres plairont
- Sois empathique et personnalise selon les goûts exprimés
- Utilise des emojis littéraires (📚, ✨, 💫, 📖)
- Évoque l'émotion et l'expérience de lecture

Recommandation:"""
    
    def _create_manga_prompt(self, query: str, books_context: str) -> str:
        """Crée un prompt pour les recommandations manga"""
        return f"""Tu es un otaku expert en manga et anime, passionné et connaisseur.

Demande de l'utilisateur: "{query}"

Mangas disponibles:
{books_context}

Instructions:
- Génère une recommandation enthousiaste et précise
- Explique les genres, l'histoire, les personnages
- Utilise le vocabulaire otaku approprié (shounen, seinen, etc.)
- Montre ta passion pour les mangas
- Utilise des emojis manga/anime (🎌, 🗾, ⚔️, 🌸, 🔥)
- Compare avec d'autres mangas connus si pertinent

Recommandation:"""
    
    def health_check(self) -> Dict[str, Any]:
        """Vérifie l'état du service Ollama et du modèle"""
        try:
            # Test de base
            test_response = self.generate_response("Bonjour", max_tokens=50)
            
            # Obtenir les infos du modèle
            models = self.client.list()
            model_info = None
            for model in models['models']:
                if model['name'] == self.model_name:
                    model_info = model
                    break
            
            return {
                "status": "healthy",
                "service": "ollama",
                "model": self.model_name,
                "base_url": self.base_url,
                "model_size": model_info.get('size', 'Unknown') if model_info else 'Unknown',
                "test_response": test_response[:100],
                "available_models": [m['name'] for m in models['models']]
            }
            
        except Exception as e:
            return {
                "status": "error",
                "service": "ollama",
                "model": self.model_name,
                "error": str(e)
            }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Obtient les informations du modèle"""
        try:
            models = self.client.list()
            for model in models['models']:
                if model['name'] == self.model_name:
                    return {
                        "name": model['name'],
                        "size": model.get('size', 'Unknown'),
                        "digest": model.get('digest', 'Unknown'),
                        "modified_at": model.get('modified_at', 'Unknown')
                    }
            return {"error": f"Modèle {self.model_name} non trouvé"}
        except Exception as e:
            return {"error": str(e)}


class GemmaAgentManager:
    """Gestionnaire d'agents utilisant Gemma via Ollama"""
    
    def __init__(self):
        self.gemma = OllamaGemmaManager()
        self.tech_rag = None
        self.literature_rag = None
        self.manga_rag = None
        self._init_rag_managers()
    
    def _init_rag_managers(self):
        """Initialise les gestionnaires RAG"""
        try:
            from rags.tech_rag.tech_rag_manager import TechRAGManager
            from rags.literature_rag.literature_rag_manager import LiteratureRAGManager
            
            self.tech_rag = TechRAGManager()
            self.literature_rag = LiteratureRAGManager()
            
            # Manga RAG (à créer plus tard)
            try:
                from rags.manga_rag.manga_rag_manager import MangaRAGManager
                self.manga_rag = MangaRAGManager()
                logger.info("✅ Manga RAG Manager chargé")
            except ImportError:
                logger.warning("⚠️ Manga RAG Manager non encore créé")
            
            logger.info("✅ RAG managers initialisés")
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation RAG: {e}")
    
    def get_tech_recommendations(self, query: str, user_id: int = 1) -> str:
        """Génère des recommandations techniques avec Gemma"""
        try:
            if not self.tech_rag:
                return "🔧 Service technique temporairement indisponible."
            
            start_time = time.time()
            
            # Obtenir des livres via RAG
            recommendations = self.tech_rag.get_book_recommendations(
                user_id=user_id,
                query=query,
                n_recommendations=3
            )
            
            if not recommendations:
                return "🔧 Aucun livre technique trouvé pour cette requête."
            
            # Préparer le contexte pour Gemma
            books_context = self._format_tech_context(recommendations)
            
            # Générer la réponse avec Gemma
            gemma_response = self.gemma.generate_book_recommendation(
                query=query,
                books_context=books_context,
                agent_type="tech"
            )
            
            processing_time = time.time() - start_time
            
            return f"🔧 **Recommandations Techniques (Gemma-2-2b)**\n\n{gemma_response}\n\n⚡ Traitement en {processing_time:.1f}s"
            
        except Exception as e:
            logger.error(f"❌ Erreur recommandations tech: {e}")
            return "🔧 Erreur lors de la génération des recommandations techniques."
    
    def get_literature_recommendations(self, query: str, user_id: int = 1) -> str:
        """Génère des recommandations littéraires avec Gemma (SANS manga)"""
        try:
            if not self.literature_rag:
                return "📚 Service littéraire temporairement indisponible."
            
            start_time = time.time()
            
            # Obtenir des livres via RAG (filtrer les mangas)
            recommendations = self.literature_rag.get_book_recommendations(
                user_id=user_id,
                query=query,
                n_recommendations=3
            )
            
            # Filtrer les mangas des résultats
            filtered_recommendations = self._filter_out_manga(recommendations)
            
            if not filtered_recommendations:
                return "📚 Aucun livre littéraire (non-manga) trouvé pour cette requête."
            
            # Préparer le contexte pour Gemma
            books_context = self._format_literature_context(filtered_recommendations)
            
            # Générer la réponse avec Gemma
            gemma_response = self.gemma.generate_book_recommendation(
                query=query,
                books_context=books_context,
                agent_type="literature"
            )
            
            processing_time = time.time() - start_time
            
            return f"📚 **Recommandations Littéraires (Gemma-2-2b)**\n\n{gemma_response}\n\n⚡ Traitement en {processing_time:.1f}s"
            
        except Exception as e:
            logger.error(f"❌ Erreur recommandations littérature: {e}")
            return "📚 Erreur lors de la génération des recommandations littéraires."
    
    def get_manga_recommendations(self, query: str, user_id: int = 1) -> str:
        """Génère des recommandations manga avec Gemma"""
        try:
            start_time = time.time()
            
            if self.manga_rag:
                # Utiliser le RAG manga dédié
                manga_results = self.manga_rag.search_manga(query, n_results=5)
            else:
                # Fallback: chercher dans les données littéraires
                manga_results = self._search_manga_fallback(query)
            
            if not manga_results:
                return "🎌 Aucun manga trouvé pour cette requête."
            
            # Préparer le contexte pour Gemma
            manga_context = self._format_manga_context(manga_results)
            
            # Générer la réponse avec Gemma
            gemma_response = self.gemma.generate_book_recommendation(
                query=query,
                books_context=manga_context,
                agent_type="manga"
            )
            
            processing_time = time.time() - start_time
            
            return f"🎌 **Recommandations Manga (Gemma-2-2b)**\n\n{gemma_response}\n\n⚡ Traitement en {processing_time:.1f}s"
            
        except Exception as e:
            logger.error(f"❌ Erreur recommandations manga: {e}")
            return "🎌 Erreur lors de la génération des recommandations manga."
    
    def _filter_out_manga(self, recommendations: List[Dict]) -> List[Dict]:
        """Filtre les mangas des recommandations littéraires"""
        filtered = []
        manga_keywords = ['manga', 'anime', 'shounen', 'shoujo', 'seinen', 'josei', 'manhua', 'manhwa']
        
        for rec in recommendations:
            book = rec['book']
            title_lower = book['title'].lower()
            desc_lower = book['description'].lower()
            categories_lower = book.get('categories', '').lower()
            
            # Vérifier si c'est un manga
            is_manga = any(keyword in title_lower or keyword in desc_lower or keyword in categories_lower 
                          for keyword in manga_keywords)
            
            if not is_manga:
                filtered.append(rec)
        
        return filtered
    
    def _search_manga_fallback(self, query: str) -> List[Dict]:
        """Recherche manga de fallback dans les données littéraires"""
        try:
            from apps.books.models import LiteratureBook
            
            # Chercher des livres qui semblent être des mangas
            manga_keywords = ['manga', 'anime', 'shounen', 'shoujo', 'seinen', 'josei']
            
            manga_books = LiteratureBook.objects.none()
            for keyword in manga_keywords:
                manga_books = manga_books | LiteratureBook.objects.filter(
                    categories__icontains=keyword
                ) | LiteratureBook.objects.filter(
                    description__icontains=keyword
                ) | LiteratureBook.objects.filter(
                    title__icontains=keyword
                )
            
            # Convertir en format manga
            results = []
            for book in manga_books.distinct()[:5]:
                results.append({
                    'title': book.title,
                    'description': book.description,
                    'rating': float(book.average_rating) if book.average_rating else 0.0,
                    'year': book.published_year,
                    'tags': book.categories,
                    'cover': book.thumbnail or ''
                })
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Erreur recherche manga fallback: {e}")
            return []
    
    def _format_tech_context(self, recommendations: List[Dict]) -> str:
        """Formate le contexte technique pour Gemma"""
        context = ""
        for i, rec in enumerate(recommendations, 1):
            book = rec['book']
            context += f"{i}. {book['title']} par {book['author']}\n"
            context += f"   Note: {book['rating']}/5, Prix: ${book['price']}\n"
            context += f"   Description: {book['description'][:150]}...\n\n"
        return context
    
    def _format_literature_context(self, recommendations: List[Dict]) -> str:
        """Formate le contexte littéraire pour Gemma"""
        context = ""
        for i, rec in enumerate(recommendations, 1):
            book = rec['book']
            context += f"{i}. {book['title']} de {book['authors']}\n"
            context += f"   Note: {book['average_rating']}/5, Année: {book['published_year']}\n"
            context += f"   Description: {book['description'][:150]}...\n\n"
        return context
    
    def _format_manga_context(self, manga_list: List[Dict]) -> str:
        """Formate le contexte manga pour Gemma"""
        context = ""
        for i, manga in enumerate(manga_list, 1):
            context += f"{i}. {manga['title']}\n"
            context += f"   Note: {manga['rating']}/5, Année: {manga['year']}\n"
            context += f"   Genres: {manga['tags']}\n"
            context += f"   Description: {manga['description'][:150]}...\n\n"
        return context
    
    def route_query(self, query: str) -> str:
        """Route une requête vers l'agent approprié"""
        query_lower = query.lower()
        
        # Détection manga (priorité haute)
        manga_keywords = ['manga', 'anime', 'naruto', 'one piece', 'dragon ball', 'attack on titan', 
                         'death note', 'fullmetal', 'bleach', 'demon slayer', 'tokyo ghoul',
                         'shounen', 'shoujo', 'seinen', 'josei', 'manhua', 'manhwa', 'otaku']
        
        # Détection technique
        tech_keywords = ['python', 'javascript', 'java', 'programming', 'code', 'development',
                        'web', 'mobile', 'data science', 'machine learning', 'ai']
        
        manga_score = sum(1 for keyword in manga_keywords if keyword in query_lower)
        tech_score = sum(1 for keyword in tech_keywords if keyword in query_lower)
        
        if manga_score > 0:
            return self.get_manga_recommendations(query)
        elif tech_score > 0:
            return self.get_tech_recommendations(query)
        else:
            return self.get_literature_recommendations(query)
    
    def health_check(self) -> Dict[str, Any]:
        """Vérifie l'état de tous les composants"""
        return {
            "gemma": self.gemma.health_check(),
            "tech_rag": "available" if self.tech_rag else "unavailable",
            "literature_rag": "available" if self.literature_rag else "unavailable",
            "manga_rag": "available" if self.manga_rag else "unavailable"
        }