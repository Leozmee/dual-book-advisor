"""
Gestionnaire pour Gemma-2-2b via Ollama
Fichier: agents/ollama_gemma_manager.py
"""
import logging
import ollama
import requests
from typing import List, Dict, Any, Optional
import time
import re

logger = logging.getLogger(__name__)

# Import du service d'images
try:
    from .cover_image_service import cover_service
    COVER_SERVICE_AVAILABLE = True
    logger.info("✅ Cover Image Service disponible dans Gemma Manager")
except ImportError as e:
    COVER_SERVICE_AVAILABLE = False
    logger.warning(f"⚠️ Cover Image Service non disponible dans Gemma Manager: {e}")

# Import de Wikipedia
try:
    import wikipedia
    wikipedia.set_lang("fr")
    WIKIPEDIA_AVAILABLE = True
    logger.info("✅ Wikipedia disponible dans Gemma Manager")
except ImportError as e:
    WIKIPEDIA_AVAILABLE = False
    logger.warning(f"⚠️ Wikipedia non disponible dans Gemma Manager: {e}")


class OllamaGemmaManager:
    """Gestionnaire pour Gemma-2-2b via Ollama"""
    
    def __init__(self, model_name: str = "gemma2:2b", use_cover_images: bool = True):
        self.model_name = model_name
        self.client = None
        self.base_url = "http://localhost:11434"
        self.use_cover_images = use_cover_images and COVER_SERVICE_AVAILABLE
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
            
            # Fix: gérer la structure d'objet Ollama
            available_models = []
            if hasattr(models_response, 'models'):
                # C'est un objet ListResponse avec attribut models
                for model in models_response.models:
                    if hasattr(model, 'model'):
                        available_models.append(model.model)
                    elif hasattr(model, 'name'):
                        available_models.append(model.name)
            elif isinstance(models_response, dict) and 'models' in models_response:
                # Fallback pour structure dict
                available_models = [model.get('name', '') for model in models_response['models']]
            
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
    
    def generate_factual_response(self, query: str, book_info: str) -> str:
        """Génère une réponse factuelle"""
        try:
            prompt = self._create_factual_prompt(query, book_info)
            return self.generate_response(prompt, temperature=0.3, max_tokens=200)
        except Exception as e:
            logger.error(f"❌ Erreur réponse factuelle: {e}")
            return "Erreur lors de la génération de la réponse factuelle"
    
    def _create_tech_prompt(self, query: str, books_context: str) -> str:
        """Crée un prompt pour les recommandations techniques EN FRANÇAIS"""
        return f"""Tu es un expert français en livres techniques et programmation. 

Demande de l'utilisateur: "{query}"

Livres techniques disponibles:
{books_context}

IMPORTANT - Instructions strictes:
- Réponds EXCLUSIVEMENT en français
- Génère une recommandation personnalisée et professionnelle
- Explique pourquoi ces livres correspondent à la demande
- Sois précis sur les technologies, le niveau de difficulté, et les bénéfices
- Reste concis mais informatif
- N'utilise AUCUN mot anglais sauf les noms de technologies (Python, JavaScript, etc.)

Recommandation en français:"""
    
    def _create_literature_prompt(self, query: str, books_context: str) -> str:
        """Crée un prompt pour les recommandations littéraires EN FRANÇAIS"""
        return f"""Tu es un critique littéraire français passionné et cultivé.

Demande de l'utilisateur: "{query}"

Livres littéraires disponibles:
{books_context}

IMPORTANT - Instructions strictes:
- Réponds EXCLUSIVEMENT en français
- Génère une recommandation chaleureuse et érudite
- Explique les thèmes, le style, et pourquoi ces œuvres plairont
- Sois empathique et personnalise selon les goûts exprimés
- Évoque l'émotion et l'expérience de lecture
- Utilise un français élégant et littéraire

Recommandation en français:"""
    
    def _create_manga_prompt(self, query: str, books_context: str) -> str:
        """Crée un prompt pour les recommandations manga/comics EN FRANÇAIS"""
        return f"""Tu es un expert français passionné de manga, anime et bandes dessinées.

Demande de l'utilisateur: "{query}"

Contenu disponible (mangas/comics/BD):
{books_context}

IMPORTANT - Instructions strictes:
- Réponds EXCLUSIVEMENT en français
- Tu es un passionné français de la culture manga/BD 
- Génère une recommandation enthousiaste mais en français correct
- Explique les genres, l'histoire, les personnages
- Utilise les termes français appropriés : "bande dessinée", "manga", "comics"
- Tu peux mentionner les termes japonais (shounen, seinen, etc.) 
- Compare avec d'autres œuvres connues si pertinent
- Reste professionnel et informatif, pas trop familier

Recommandation en français:"""
    
    def _create_factual_prompt(self, query: str, book_info: str) -> str:
        """Crée un prompt pour les réponses factuelles EN FRANÇAIS"""
        return f"""Tu es un bibliothécaire français expert en littérature.

Question de l'utilisateur: "{query}"

Informations sur le livre:
{book_info}

IMPORTANT - Instructions strictes:
- Réponds EXCLUSIVEMENT en français
- Donne une réponse factuelle précise et concise
- Si c'est une question sur l'auteur, donne le nom de l'auteur clairement
- Ajoute des informations contextuelles pertinentes (année, genre, etc.)
- Utilise un français correct et professionnel
- Sois informatif mais concis
- Ne fais pas de recommandations, réponds juste à la question posée

Réponse factuelle en français:"""
    
    def health_check(self) -> Dict[str, Any]:
        """Vérifie l'état du service Ollama et du modèle"""
        try:
            # Test de base
            test_response = self.generate_response("Bonjour", max_tokens=50)
            
            # Obtenir les infos du modèle
            models = self.client.list()
            model_info = None
            available_models = []
            
            if hasattr(models, 'models'):
                # Structure d'objet Ollama
                for model in models.models:
                    model_name = getattr(model, 'model', getattr(model, 'name', ''))
                    available_models.append(model_name)
                    if model_name == self.model_name:
                        model_info = {
                            'size': getattr(model, 'size', 'Unknown'),
                            'digest': getattr(model, 'digest', 'Unknown'),
                            'modified_at': str(getattr(model, 'modified_at', 'Unknown'))
                        }
            elif isinstance(models, dict) and 'models' in models:
                # Fallback pour structure dict
                for model in models['models']:
                    model_name = model.get('name', '')
                    available_models.append(model_name)
                    if model_name == self.model_name:
                        model_info = model
            
            return {
                "status": "healthy",
                "service": "ollama",
                "model": self.model_name,
                "base_url": self.base_url,
                "model_size": model_info.get('size', 'Unknown') if model_info else 'Unknown',
                "test_response": test_response[:100] if test_response else "No response",
                "available_models": available_models
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
            
            if hasattr(models, 'models'):
                # Structure d'objet Ollama
                for model in models.models:
                    model_name = getattr(model, 'model', getattr(model, 'name', ''))
                    if model_name == self.model_name:
                        return {
                            "name": model_name,
                            "size": getattr(model, 'size', 'Unknown'),
                            "digest": getattr(model, 'digest', 'Unknown'),
                            "modified_at": str(getattr(model, 'modified_at', 'Unknown'))
                        }
            elif isinstance(models, dict) and 'models' in models:
                # Fallback pour structure dict
                for model in models['models']:
                    if model.get('name', '') == self.model_name:
                        return {
                            "name": model.get('name', ''),
                            "size": model.get('size', 'Unknown'),
                            "digest": model.get('digest', 'Unknown'),
                            "modified_at": model.get('modified_at', 'Unknown')
                        }
            
            return {"error": f"Modèle {self.model_name} non trouvé"}
        except Exception as e:
            return {"error": str(e)}


class GemmaAgentManager:
    """Gestionnaire d'agents utilisant Gemma via Ollama"""
    
    def __init__(self, use_cover_images: bool = True):
        self.gemma = OllamaGemmaManager(use_cover_images=use_cover_images)
        self.tech_rag = None
        self.literature_rag = None
        self.manga_rag = None
        self.use_cover_images = use_cover_images and COVER_SERVICE_AVAILABLE
        self._init_rag_managers()
    
    def _init_rag_managers(self):
        """Initialise les gestionnaires RAG"""
        try:
            from rags.tech_rag.tech_rag_manager import TechRAGManager
            from rags.literature_rag.literature_rag_manager import LiteratureRAGManager
            
            self.tech_rag = TechRAGManager()
            self.literature_rag = LiteratureRAGManager()
            
            # Manga RAG unifié
            try:
                from rags.manga_rag.manga_rag_manager import MangaRAGManager
                self.manga_rag = MangaRAGManager()
                logger.info("✅ Manga RAG Manager unifié chargé")
            except ImportError:
                logger.warning("⚠️ Manga RAG Manager non disponible")
            
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
            
            # Enrichir avec des images de couverture si activé
            if self.use_cover_images:
                gemma_response = self._enrich_response_with_images(gemma_response, recommendations, 'tech')
            
            processing_time = time.time() - start_time
            
            return f"🔧 **Recommandations Techniques (Gemma-2-2b)**\n\n{gemma_response}\n\n⚡ Traitement en {processing_time:.1f}s"
            
        except Exception as e:
            logger.error(f"❌ Erreur recommandations tech: {e}")
            return "🔧 Erreur lors de la génération des recommandations techniques."
    
    def get_literature_recommendations(self, query: str, user_id: int = 1) -> str:
        """Génère des recommandations littéraires avec Gemma (SANS manga/comics)"""
        try:
            if not self.literature_rag:
                return "📚 Service littéraire temporairement indisponible."
            
            start_time = time.time()
            
            # Obtenir des livres via RAG (filtrer les mangas/comics)
            recommendations = self.literature_rag.get_book_recommendations(
                user_id=user_id,
                query=query,
                n_recommendations=3
            )
            
            # Filtrer les mangas/comics des résultats
            filtered_recommendations = self._filter_out_manga_comics(recommendations)
            
            if not filtered_recommendations:
                return "📚 Aucun livre littéraire (non-manga/comics) trouvé pour cette requête."
            
            # Préparer le contexte pour Gemma
            books_context = self._format_literature_context(filtered_recommendations)
            
            # Générer la réponse avec Gemma
            gemma_response = self.gemma.generate_book_recommendation(
                query=query,
                books_context=books_context,
                agent_type="literature"
            )
            
            # Enrichir avec des images de couverture si activé
            if self.use_cover_images:
                gemma_response = self._enrich_response_with_images(gemma_response, filtered_recommendations, 'literature')
            
            processing_time = time.time() - start_time
            
            return f"📚 **Recommandations Littéraires (Gemma-2-2b)**\n\n{gemma_response}\n\n⚡ Traitement en {processing_time:.1f}s"
            
        except Exception as e:
            logger.error(f"❌ Erreur recommandations littérature: {e}")
            return "📚 Erreur lors de la génération des recommandations littéraires."
    
    def get_manga_recommendations(self, query: str, user_id: int = 1) -> str:
        """Génère des recommandations manga/comics avec Gemma"""
        try:
            start_time = time.time()
            
            if self.manga_rag:
                # Utiliser le RAG manga/comics unifié
                content_results = self.manga_rag.search_content(query, n_results=5)
            else:
                # Fallback: chercher dans les données littéraires
                content_results = self._search_manga_comics_fallback(query)
            
            if not content_results:
                return "🎌 Aucun manga/comics trouvé pour cette requête."
            
            # Préparer le contexte pour Gemma
            content_context = self._format_manga_comics_context(content_results)
            
            # Générer la réponse avec Gemma
            gemma_response = self.gemma.generate_book_recommendation(
                query=query,
                books_context=content_context,
                agent_type="manga"
            )
            
            # Enrichir avec des images de couverture si activé
            if self.use_cover_images:
                gemma_response = self._enrich_response_with_images(gemma_response, content_results, 'manga')
            
            processing_time = time.time() - start_time
            
            return f"🎌 **Recommandations Manga/Comics (Gemma-2-2b)**\n\n{gemma_response}\n\n⚡ Traitement en {processing_time:.1f}s"
            
        except Exception as e:
            logger.error(f"❌ Erreur recommandations manga/comics: {e}")
            return "🎌 Erreur lors de la génération des recommandations manga/comics."
    
    def _enrich_response_with_images(self, response: str, recommendations: List[Dict], content_type: str) -> str:
        """Enrichit une réponse Gemma avec des images de couverture"""
        if not self.use_cover_images or not COVER_SERVICE_AVAILABLE:
            return response
        
        try:
            logger.info(f"🖼️ Enrichissement Gemma avec images pour {len(recommendations)} recommandations ({content_type})")
            
            enriched_response = response
            
            for rec in recommendations:
                # Extraire les informations selon le type de contenu
                if content_type == 'tech':
                    book = rec.get('book', {})
                    title = book.get('title', '')
                    author = book.get('author', '')
                    search_type = 'book'
                elif content_type == 'literature':
                    book = rec.get('book', {})
                    title = book.get('title', '')
                    author = book.get('authors', '')
                    search_type = 'book'
                elif content_type == 'manga':
                    # Pour le manga, le format peut être différent
                    if 'content' in rec:
                        content = rec.get('content', {})
                        title = content.get('title', '')
                        author = content.get('author', '')
                    else:
                        # Format alternatif
                        title = rec.get('title', '')
                        author = rec.get('author', '')
                    search_type = 'manga'
                else:
                    continue
                
                if not title:
                    continue
                
                # Rechercher l'image de couverture
                cover_url = cover_service.get_cover_image(title, author, search_type)
                
                if cover_url:
                    logger.info(f"✅ Image trouvée pour: {title}")
                    
                    # Insérer l'image avant la mention du titre dans la réponse
                    # Chercher le titre dans la réponse (avec différents formats possibles)
                    title_patterns = [
                        f"**{title}**",
                        f"*{title}*",
                        title
                    ]
                    
                    image_tag = f"📸 ![{title}]({cover_url})\n\n"
                    
                    for pattern in title_patterns:
                        if pattern in enriched_response and image_tag not in enriched_response:
                            # Insérer l'image juste avant la première occurrence du titre
                            enriched_response = enriched_response.replace(pattern, f"{image_tag}{pattern}", 1)
                            break
                else:
                    logger.info(f"❌ Aucune image trouvée pour: {title}")
            
            return enriched_response
            
        except Exception as e:
            logger.error(f"❌ Erreur enrichissement images: {e}")
            return response
    
    def get_factual_response(self, query: str, book_info: str) -> str:
        """Génère une réponse factuelle avec Gemma EN FRANÇAIS"""
        try:
            # Générer la réponse avec Gemma
            gemma_response = self.gemma.generate_factual_response(query, book_info)
            
            return f"📚 **Réponse (Gemma-2-2b)**\n\n{gemma_response}"
            
        except Exception as e:
            logger.error(f"❌ Erreur réponse factuelle: {e}")
            return "📚 Erreur lors de la génération de la réponse factuelle."
    
    def _filter_out_manga_comics(self, recommendations: List[Dict]) -> List[Dict]:
        """Filtre les mangas/comics des recommandations littéraires"""
        filtered = []
        exclusion_keywords = [
            'manga', 'anime', 'shounen', 'shoujo', 'seinen', 'josei', 'manhua', 'manhwa',
            'comics', 'bd', 'bande dessinée', 'superhéros', 'superman', 'batman', 'marvel', 'dc'
        ]
        
        for rec in recommendations:
            book = rec['book']
            title_lower = book['title'].lower()
            desc_lower = book['description'].lower()
            categories_lower = book.get('categories', '').lower()
            
            # Vérifier si c'est un manga/comics
            is_manga_comics = any(keyword in title_lower or keyword in desc_lower or keyword in categories_lower 
                                for keyword in exclusion_keywords)
            
            if not is_manga_comics:
                filtered.append(rec)
        
        return filtered
    
    def _search_manga_comics_fallback(self, query: str) -> List[Dict]:
        """Recherche manga/comics de fallback dans les données littéraires"""
        try:
            from apps.books.models import LiteratureBook
            
            # Chercher des livres qui semblent être des mangas/comics
            keywords = ['manga', 'anime', 'shounen', 'shoujo', 'seinen', 'josei', 'comics', 'bd']
            
            books = LiteratureBook.objects.none()
            for keyword in keywords:
                books = books | LiteratureBook.objects.filter(
                    categories__icontains=keyword
                ) | LiteratureBook.objects.filter(
                    description__icontains=keyword
                ) | LiteratureBook.objects.filter(
                    title__icontains=keyword
                )
            
            # Convertir en format unifié
            results = []
            for book in books.distinct()[:5]:
                results.append({
                    'title': book.title,
                    'description': book.description,
                    'rating': float(book.average_rating) if book.average_rating else 0.0,
                    'year': book.published_year,
                    'tags': book.categories,
                    'cover': book.thumbnail or '',
                    'author': book.authors,
                    'source_type': 'literature_fallback'
                })
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Erreur recherche manga/comics fallback: {e}")
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
    
    def _format_manga_comics_context(self, content_list: List[Dict]) -> str:
        """Formate le contexte manga/comics pour Gemma"""
        context = ""
        for i, content in enumerate(content_list, 1):
            context += f"{i}. {content['title']}\n"
            if 'author' in content and content['author']:
                context += f"   Auteur: {content['author']}\n"
            context += f"   Note: {content['rating']}/5"
            if 'year' in content and content['year']:
                context += f", Année: {content['year']}"
            context += f"\n   Genres: {content.get('tags', 'Non spécifié')}\n"
            context += f"   Description: {content['description'][:150]}...\n\n"
        return context
    
    def route_query(self, query: str) -> str:
        """Route une requête vers l'agent approprié avec détection factuelle"""
        query_lower = query.lower()
        
        # PRIORITÉ 1: Questions factuelles (comme "qui est l'auteur de...")
        if self._detect_factual_query(query_lower):
            return self._handle_factual_query_with_gemma(query)
        
        # PRIORITÉ 2: Détection manga/comics (mais pas littérature classique)
        manga_comics_keywords = [
            'manga', 'anime', 'naruto', 'one piece', 'dragon ball', 'attack on titan', 
            'death note', 'fullmetal', 'bleach', 'demon slayer', 'tokyo ghoul',
            'shounen', 'shoujo', 'seinen', 'josei', 'manhua', 'manhwa', 'otaku',
            'comics', 'bd', 'bande dessinée', 'superman', 'batman', 'marvel', 'dc',
            'tintin', 'astérix', 'superhéros'
        ]
        
        # PRIORITÉ 3: Détection technique
        tech_keywords = [
            'python', 'javascript', 'java', 'programming', 'code', 'development',
            'web', 'mobile', 'data science', 'machine learning', 'ai'
        ]
        
        # Détection intelligente de littérature vs manga/tech
        # Utiliser des patterns plus généraux au lieu de listes hardcodées
        literature_indicators = [
            'roman', 'livre', 'littérature', 'auteur', 'écrivain', 'poète',
            'œuvre', 'qui a écrit', 'auteur de'
        ]
        
        manga_score = sum(1 for keyword in manga_comics_keywords if keyword in query_lower)
        tech_score = sum(1 for keyword in tech_keywords if keyword in query_lower)
        literature_score = sum(1 for keyword in literature_indicators if keyword in query_lower)
        
        # Routage intelligent basé sur les scores ET la détection factuelle
        if manga_score > tech_score and manga_score > literature_score:
            return self.get_manga_recommendations(query)
        elif tech_score > literature_score and tech_score > manga_score:
            return self.get_tech_recommendations(query)
        else:
            # Par défaut, littérature (gère aussi les questions factuelles via Wikipedia)
            return self.get_literature_recommendations(query)
    
    def _detect_factual_query(self, query_lower: str) -> bool:
        """Détecte si c'est une question factuelle"""
        factual_patterns = [
            'qui est', 'who is', 'quel est', 'what is',
            'auteur de', 'author of', 'écrit par', 'written by',
            'quand', 'when', 'où', 'where', 'comment', 'how'
        ]
        return any(pattern in query_lower for pattern in factual_patterns)
    
    def _search_wikipedia(self, query: str) -> Dict[str, str]:
        """Recherche universelle sur Wikipedia"""
        if not WIKIPEDIA_AVAILABLE:
            return None
            
        try:
            # Nettoyer la requête pour Wikipedia
            clean_query = query.lower()
            # Extraire le titre du livre si c'est une question d'auteur
            if "qui a écrit" in clean_query or "auteur de" in clean_query:
                # Extraire le titre entre guillemets ou après "auteur de"
                import re
                patterns = [
                    r'qui\s+a\s+écrit\s+"([^"]+)"',
                    r'qui\s+a\s+écrit\s+([^?]+)',
                    r'auteur\s+de\s+"([^"]+)"',
                    r'auteur\s+de\s+([^?]+)'
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, clean_query)
                    if match:
                        title = match.group(1).strip()
                        break
                else:
                    title = clean_query
            else:
                title = clean_query
                
            # Rechercher sur Wikipedia (français)
            search_results = wikipedia.search(title, results=3)
            if not search_results:
                return None
                
            # Essayer le premier résultat
            page = wikipedia.page(search_results[0])
            
            # Extraire les informations pertinentes
            summary = page.summary[:300]
            
            # Essayer d'extraire l'auteur de la page
            content = page.content[:1000].lower()
            
            # Patterns pour détecter l'auteur
            author_patterns = [
                r'(?:roman|livre|œuvre|novel|book)\s+(?:de|d\'|par|by)\s+([A-ZÀ-Ÿ][a-zA-ZÀ-ÿ\s\-\'\.]+)',
                r'(?:écrit|écrite|written)\s+par\s+([A-ZÀ-Ÿ][a-zA-ZÀ-ÿ\s\-\'\.]+)',
                r'([A-ZÀ-Ÿ][a-zA-ZÀ-ÿ\s\-\'\.]+)\s+(?:est|is)\s+(?:un|une|l\')?(?:auteur|écrivain|romancier)'
            ]
            
            author = None
            for pattern in author_patterns:
                match = re.search(pattern, content)
                if match:
                    author = match.group(1).strip()
                    # Nettoyer l'auteur (enlever les mots en trop)
                    stop_words = ['le', 'la', 'les', 'un', 'une', 'des', 'du', 'de', 'est', 'dans', 'pour', 'avec']
                    author_words = author.split()
                    if author_words[-1].lower() in stop_words:
                        author = ' '.join(author_words[:-1])
                    break
            
            return {
                'title': page.title,
                'author': author,
                'summary': summary,
                'url': page.url
            }
            
        except Exception as e:
            logger.error(f"Erreur recherche Wikipedia: {e}")
            return None

    def _handle_factual_query_with_gemma(self, query: str) -> str:
        """Gère les questions factuelles avec Gemma - VERSION UNIVERSELLE avec Wikipedia"""
        try:
            # 1. D'abord essayer le RAG littéraire
            if self.literature_rag:
                title = self._extract_book_title(query)
                if title:
                    results = self.literature_rag.search_books(query=title, n_results=1)
                    if results:
                        book = results[0]
                        book_info = f"""Titre: {book['title']}
Auteur(s): {book['authors']}
Année de publication: {book.get('published_year', 'Non spécifiée')}
Note moyenne: {book['average_rating']}/5
Description: {book['description'][:200]}..."""
                        
                        return self.get_factual_response(query, book_info)
            
            # 2. Ensuite essayer Wikipedia (UNIVERSEL)
            wiki_result = self._search_wikipedia(query)
            if wiki_result and wiki_result.get('author'):
                
                # Réponse courte et directe pour les questions d'auteur
                if "qui a écrit" in query.lower() or "auteur de" in query.lower():
                    return f"**{wiki_result['author']}** a écrit {wiki_result['title']}."
                
                # Réponse plus complète pour d'autres questions
                book_info = f"""Titre: {wiki_result['title']}
Auteur: {wiki_result['author']}
Description: {wiki_result['summary']}"""
                
                return self.get_factual_response(query, book_info)
            
            # 3. Si Wikipedia ne trouve pas l'auteur, essayer une recherche générale
            elif wiki_result:
                return f"📚 J'ai trouvé des informations sur **{wiki_result['title']}** : {wiki_result['summary'][:150]}..."
            
            # 4. Si rien n'est trouvé
            return "📚 Je n'ai pas trouvé d'information spécifique sur cette question. Pouvez-vous reformuler ou préciser le titre de l'œuvre ?"
            
        except Exception as e:
            logger.error(f"Erreur gestion question factuelle: {e}")
            return "📚 Erreur lors du traitement de votre question."
    
    def _extract_book_title(self, query: str) -> str:
        """Extrait le titre du livre de la question"""
        patterns = [
            r'auteur de\s+(.+?)(?:\?|$)',
            r'author of\s+(.+?)(?:\?|$)',
            r'écrit\s+(.+?)(?:\?|$)',
            r'"([^"]+)"',
            r'«([^»]+)»'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return ""
    
    def health_check(self) -> Dict[str, Any]:
        """Vérifie l'état de tous les composants"""
        return {
            "gemma": self.gemma.health_check(),
            "tech_rag": "available" if self.tech_rag else "unavailable",
            "literature_rag": "available" if self.literature_rag else "unavailable",
            "manga_rag": "available" if self.manga_rag else "unavailable"
        }