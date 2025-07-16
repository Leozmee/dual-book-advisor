"""
Agents simples pour les recommandations de livres
Avec intégration Gemma et séparation manga/comics/littérature
"""
import logging
import time
from typing import List, Dict, Any, Optional
from django.conf import settings
from typing import List, Dict, Any
import re

# Import conditionnel de Gemma
try:
    from .ollama_gemma_manager import GemmaAgentManager
    GEMMA_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("✅ Gemma Manager disponible")
except ImportError as e:
    GEMMA_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning(f"⚠️ Gemma Manager non disponible: {e}")

# Import du service d'images
try:
    from .cover_image_service import cover_service
    COVER_SERVICE_AVAILABLE = True
    logger.info("✅ Cover Image Service disponible")
except ImportError as e:
    COVER_SERVICE_AVAILABLE = False
    logger.warning(f"⚠️ Cover Image Service non disponible: {e}")


class SimpleAgentManager:
    """Gestionnaire simple pour les agents de recommandation"""
    
    def __init__(self, use_gemma: bool = True, use_cover_images: bool = True):
        self.tech_rag = None
        self.literature_rag = None
        self.manga_rag = None
        
        # Configuration Gemma
        self.use_gemma = use_gemma and GEMMA_AVAILABLE
        self.gemma_manager = None
        
        # Configuration images de couverture
        self.use_cover_images = use_cover_images and COVER_SERVICE_AVAILABLE
        
        # Initialiser les composants
        self._init_rag_managers()
        if self.use_gemma:
            self._init_gemma_manager()
    
    def _init_rag_managers(self):
        """Initialise les gestionnaires RAG"""
        try:
            from rags.tech_rag.tech_rag_manager import TechRAGManager
            from rags.literature_rag.literature_rag_manager import LiteratureRAGManager
            
            self.tech_rag = TechRAGManager()
            self.literature_rag = LiteratureRAGManager()
            logger.info("✅ Gestionnaires RAG tech/littéraire initialisés")
            
            # Essayer d'initialiser le RAG manga/comics unifié
            try:
                from rags.manga_rag.manga_rag_manager import MangaRAGManager
                self.manga_rag = MangaRAGManager()
                logger.info("✅ Gestionnaire RAG manga/comics unifié initialisé")
            except ImportError:
                logger.warning("⚠️ RAG manga/comics non disponible (normal si pas encore créé)")
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation RAG: {e}")
    
    def _init_gemma_manager(self):
        """Initialise le gestionnaire Gemma"""
        try:
            self.gemma_manager = GemmaAgentManager()
            logger.info("✅ Gemma Agent Manager initialisé")
        except Exception as e:
            logger.error(f"❌ Erreur init Gemma: {e}")
            self.use_gemma = False
    
    def expand_query(self, query: str) -> str:
        """Enrichit une requête pour améliorer la recherche sémantique"""
        query_lower = query.lower()
        expanded_parts = [query]
        
        # Dictionnaire de traduction (version simplifiée intégrée)
        translations = {
            # Auteurs littéraires
            'tolstoy': 'Leo Tolstoy War Peace Anna Karenina Russian literature classic',
            'tolstoï': 'Leo Tolstoy War Peace Anna Karenina Russian literature classic',
            'stephen king': 'Stephen King horror thriller It Shining Carrie Salem',
            'murakami': 'Haruki Murakami Norwegian Wood Kafka Shore Japanese literature',
            'victor hugo': 'Victor Hugo Les Misérables Hunchback Notre Dame French classic',
            'shakespeare': 'William Shakespeare Hamlet Romeo Juliet Macbeth English',
            'camus': 'Albert Camus Stranger Plague Myth Sisyphus existentialism',
            
            # Genres littéraires
            'romans': 'novels fiction literature story narrative',
            'fantasy': 'fantasy magic adventure fiction magical worlds',
            'science fiction': 'science fiction sci-fi futuristic space technology',
            'thriller': 'thriller suspense mystery crime psychological',
            'romance': 'romance love relationship contemporary historical',
            
            # Technique
            'python': 'Python programming language development beginner advanced',
            'javascript': 'JavaScript web development frontend backend Node.js',
            'c#': 'C# CSharp .NET Microsoft programming Windows development',
            'java': 'Java programming language enterprise development Android',
            'web développement': 'web development HTML CSS JavaScript frontend backend',
            'machine learning': 'machine learning AI artificial intelligence data science',
            'data science': 'data science analysis statistics Python R visualization',
            
            # Manga/Comics
            'manga': 'manga anime Japanese comic otaku shounen seinen',
            'comics': 'comics superhero graphic novel DC Marvel',
            'bd': 'bande dessinée comics album français',
            'superhéros': 'superhero comics cape costume power hero',
            
            # Intentions
            'apprendre': 'learn beginner tutorial introduction guide',
            'débutant': 'beginner introductory basic fundamentals getting started',
            'avancé': 'advanced expert professional deep dive comprehensive',
            'recommandation': 'recommendation suggest similar like comparable',
            'oeuvres principales': 'main works major novels best books masterpieces',
        }
        
        # Recherche de termes à enrichir
        for key, expansion in translations.items():
            if key.lower() in query_lower:
                expanded_parts.append(expansion)
                break  # Prendre la première correspondance principale
        
        # Ajout de synonymes contextuels
        if any(word in query_lower for word in ['livre', 'book', 'ouvrage']):
            expanded_parts.append('book literature reading')
        
        if any(word in query_lower for word in ['recommandation', 'suggestion', 'conseil']):
            expanded_parts.append('recommendation suggest similar')
        
        return ' '.join(expanded_parts)
    
    def _extract_requested_count(self, query: str) -> int:
        """Extrait le nombre de recommandations demandé dans la requête"""
        import re
        
        query_lower = query.lower()
        
        # Patterns pour détecter le nombre
        patterns = [
            r'donne.{0,20}moi\s+(\d+)\s+(?:livres?|recommandations?)',
            r'(\d+)\s+(?:livres?|recommandations?)',
            r'(un|une|deux|trois|quatre|cinq|six|sept|huit|neuf|dix)\s+(?:livres?|recommandations?)',
        ]
        
        # Mapping français vers nombres
        french_numbers = {
            'un': 1, 'une': 1, 'deux': 2, 'trois': 3, 'quatre': 4, 'cinq': 5,
            'six': 6, 'sept': 7, 'huit': 8, 'neuf': 9, 'dix': 10
        }
        
        for pattern in patterns:
            match = re.search(pattern, query_lower)
            if match:
                number_str = match.group(1)
                
                # Si c'est un chiffre
                if number_str.isdigit():
                    return min(int(number_str), 10)  # Max 10 recommandations
                
                # Si c'est un nombre en français
                if number_str in french_numbers:
                    return french_numbers[number_str]
        
        # Par défaut, retourner 3 recommandations
        return 3
    
    def detect_manga_query(self, query: str) -> bool:
        """Détecte si une requête concerne des mangas OU comics/BD"""
        query_lower = query.lower()
        
        # Mots-clés mangas japonais
        manga_keywords = [
            'manga', 'anime', 'naruto', 'one piece', 'dragon ball', 'attack on titan',
            'death note', 'fullmetal alchemist', 'bleach', 'demon slayer', 'tokyo ghoul',
            'my hero academia', 'cowboy bebop', 'spirited away', 'princess mononoke',
            'akira', 'ghost in the shell', 'sailor moon', 'fruits basket',
            'shounen', 'shoujo', 'seinen', 'josei', 'manhua', 'manhwa', 
            'isekai', 'mecha', 'slice of life', 'otaku'
        ]
        
        # Mots-clés comics/BD françaises  
        comics_keywords = [
            'comics', 'bd', 'bande dessinée', 'bande-dessinée', 'album',
            'superman', 'batman', 'spider-man', 'spiderman', 'wonder woman',
            'x-men', 'avengers', 'justice league', 'marvel', 'dc',
            'tintin', 'astérix', 'lucky luke', 'gaston', 'spirou',
            'superhéros', 'super-héros', 'héros', 'vilain',
            'comics français', 'bd française', 'album graphique'
        ]
        
        all_keywords = manga_keywords + comics_keywords
        return any(keyword in query_lower for keyword in all_keywords)
    
    def detect_content_type(self, query: str) -> str:
        """Détecte spécifiquement si c'est manga, comics, ou les deux"""
        query_lower = query.lower()
        
        # Indicateurs manga japonais
        manga_indicators = [
            'manga', 'anime', 'otaku', 'shounen', 'shoujo', 'seinen', 
            'naruto', 'one piece', 'dragon ball', 'akira', 'ghibli',
            'japonais', 'japon', 'asia'
        ]
        
        # Indicateurs comics/BD
        comics_indicators = [
            'comics', 'bd', 'bande dessinée', 'superhéros', 'superman', 
            'batman', 'marvel', 'dc', 'tintin', 'astérix', 'album',
            'français', 'france', 'européen', 'américain'
        ]
        
        manga_score = sum(1 for indicator in manga_indicators if indicator in query_lower)
        comics_score = sum(1 for indicator in comics_indicators if indicator in query_lower)
        
        if manga_score > comics_score:
            return 'manga'
        elif comics_score > manga_score:
            return 'comics'
        else:
            return 'all'  # Les deux ou indéterminé
    
    def route_query(self, query: str) -> str:
        """Route une requête vers l'agent approprié - VERSION SIMPLIFIÉE"""
        
        query_lower = query.lower()
        logger.info(f"🔍 Route query called with: '{query}'")
        
        # 🎯 ROUTAGE SIMPLIFIÉ: Chaque agent gère ses propres questions factuelles
        
        # PRIORITÉ 1: Détection manga/comics
        if self.detect_manga_query(query):
            logger.info("🎌🦸 Routage vers agent manga/comics")
            return self.get_manga_recommendations(query)
        
        # PRIORITÉ 2: Mots-clés techniques (détection par mots entiers)
        tech_keywords = [
            'python', 'javascript', 'java', 'c#', 'csharp', 'php', 'ruby', 'go',
            'programming', 'programmation', 'développement', 'development',
            'web', 'mobile', 'app', 'application', 'software', 'logiciel',
            'machine learning', 'data science', 'intelligence artificielle',
            'algorithm', 'algorithme', 'code', 'coding', 'framework',
            'database', 'base de données', 'api', 'backend', 'frontend'
        ]
        
        # Mots-clés techniques spéciaux nécessitant une détection par mots entiers
        word_boundary_keywords = ['ai', 'app', 'code', 'api', 'go']
        
        # Mots-clés techniques qui peuvent être des sous-chaînes (comme "web" dans "website")
        substring_keywords = ['web']
        
        tech_score = 0
        
        # Détection standard pour la plupart des mots-clés
        for keyword in tech_keywords:
            if keyword not in word_boundary_keywords and keyword not in substring_keywords and keyword in query_lower:
                tech_score += 1
                logger.info(f"🔧 Mot-clé technique détecté: '{keyword}'")
        
        # Détection par mots entiers pour les mots-clés ambigus
        import re
        for keyword in word_boundary_keywords:
            if keyword in tech_keywords:  # Vérifier que le mot-clé est dans la liste
                # Utiliser \b pour les frontières de mots
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, query_lower):
                    tech_score += 1
                    logger.info(f"🔧 Mot-clé technique (frontière) détecté: '{keyword}'")
        
        # Détection par sous-chaînes pour les mots-clés techniques spéciaux
        for keyword in substring_keywords:
            if keyword in tech_keywords and keyword in query_lower:
                tech_score += 1
                logger.info(f"🔧 Mot-clé technique (sous-chaîne) détecté: '{keyword}'")
        
        if tech_score > 0:
            logger.info("🔧 Routage vers agent technique")
            return self.get_tech_recommendations(query)
        
        # PRIORITÉ 3: Par défaut, agent littéraire (gérera ses propres questions factuelles)
        else:
            logger.info("📚 Routage vers agent littéraire")
            return self.get_literature_recommendations(query)
        
    def detect_factual_query(self, query: str) -> bool:
        """Détecte si c'est une question factuelle plutôt qu'une demande de recommandation"""
        
        query_lower = query.lower()
        
        # Patterns pour questions factuelles
        factual_patterns = [
            r'\b(qui est|who is|quel est|what is)\b',
            r'\b(auteur de|author of|écrit par|written by)\b',
            r'\b(quand|when|où|where|comment|how|pourquoi|why)\b',
            r'\b(définition|definition|signification|meaning)\b',
            r'\b(c\'est quoi|what\'s|qu\'est-ce que)\b'
        ]
        
        return any(re.search(pattern, query_lower) for pattern in factual_patterns)

    def detect_classic_literature_query(self, query: str) -> bool:
        """Détecte les questions sur la littérature classique"""
        
        query_lower = query.lower()
        
        # Œuvres classiques connues
        classic_works = [
            'les enfants du capitaine grant', 'vingt mille lieues sous les mers',
            'le tour du monde en 80 jours', 'voyage au centre de la terre',
            'les misérables', 'notre-dame de paris', 'le comte de monte-cristo',
            'les trois mousquetaires', 'madame bovary', 'germinal',
            'guerre et paix', 'anna karénine', 'crime et châtiment',
            'hamlet', 'roméo et juliette', 'macbeth',
            'l\'étranger', 'la peste', 'le mythe de sisyphe'
        ]
        
        # Auteurs classiques
        classic_authors = [
            'jules verne', 'victor hugo', 'alexandre dumas',
            'gustave flaubert', 'émile zola', 'léon tolstoï',
            'fiodor dostoïevski', 'william shakespeare', 'albert camus',
            'jean-paul sartre', 'marcel proust', 'honoré de balzac'
        ]
        
        all_classics = classic_works + classic_authors
        
        return any(classic in query_lower for classic in all_classics)

    def get_factual_literature_response(self, query: str) -> str:
        """Répond aux questions factuelles sur la littérature"""
        try:
            # Extraire le titre de l'œuvre de la question
            title = self._extract_book_title_from_query(query)
            
            if title:
                # Rechercher dans le RAG littéraire
                if self.literature_rag:
                    results = self.literature_rag.search_books(
                        query=title,
                        n_results=3
                    )
                    
                    if results:
                        # Prendre le premier résultat le plus pertinent
                        best_match = results[0]
                        
                        # Construire une réponse factuelle
                        if "auteur" in query.lower() or "author" in query.lower():
                            return f"📚 {best_match['title']} a été écrit par {best_match['authors']}.\n\n" \
                                f"📖 Publié en {best_match.get('published_year', 'date inconnue')}\n" \
                                f"⭐ Note moyenne: {best_match['average_rating']}/5\n" \
                                f"📝 {best_match['description'][:200]}..."
                        
                        elif "quand" in query.lower() or "when" in query.lower():
                            return f"📚 {best_match['title']} a été publié en {best_match.get('published_year', 'date inconnue')} par {best_match['authors']}."
                        
                        else:
                            # Réponse générale
                            return f"📚 {best_match['title']}\n\n" \
                                f"✍️ Auteur: {best_match['authors']}\n" \
                                f"📅 Publié: {best_match.get('published_year', 'Date inconnue')}\n" \
                                f"⭐ Note: {best_match['average_rating']}/5\n\n" \
                                f"📖 {best_match['description'][:300]}..."
            
            # Si pas trouvé dans le RAG, réponse de fallback avec info connue
            if "les enfants du capitaine grant" in query.lower():
                return """📚 Les Enfants du capitaine Grant

    ✍️ Auteur: Jules Verne (1828-1905)
    📅 Publié: 1867-1868
    📖 Genre: Roman d'aventures, littérature jeunesse

    🌍 Résumé: Roman d'aventures où les enfants du capitaine Grant partent à la recherche de leur père disparu. L'expédition les mène autour du monde, de l'Amérique du Sud à l'Australie en passant par l'océan Pacifique.

    📚 Autres œuvres de Jules Verne:
    - Vingt mille lieues sous les mers
    - Le Tour du monde en 80 jours  
    - Voyage au centre de la Terre

    💡 Pour des recommandations similaires, demandez: "livres comme Jules Verne" ou "romans d'aventure classiques"."""
            
            return self._get_factual_fallback_response(query)
            
        except Exception as e:
            logger.error(f"Erreur dans get_factual_literature_response: {e}")
            return self._get_factual_fallback_response(query)

    def _extract_book_title_from_query(self, query: str) -> str:
        """Extrait le titre du livre de la question"""
        import re
        
        # Patterns pour extraire le titre
        patterns = [
            r'auteur de\s+["\']?([^"\'?]+)["\']?',
            r'author of\s+["\']?([^"\'?]+)["\']?',
            r'écrit\s+["\']?([^"\'?]+)["\']?',
            r'written\s+["\']?([^"\'?]+)["\']?',
            r'livre\s+["\']?([^"\'?]+)["\']?',
            r'book\s+["\']?([^"\'?]+)["\']?',
            r'["\']([^"\'?]+)["\']'  # Titre entre guillemets
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                title = match.group(1).strip()
                # Nettoyer le titre
                title = re.sub(r'\s+', ' ', title)
                return title
        
        return ""

    def _get_factual_fallback_response(self, query: str) -> str:
        """Réponse de fallback pour questions factuelles"""
        return f"""📚 **Question sur la littérature**

    Je n'ai pas trouvé d'information précise sur "{query}" dans ma base de données.

    💡 **Suggestions:**
    - Vérifiez l'orthographe du titre ou de l'auteur
    - Essayez une formulation différente
    - Pour "Les Enfants du Capitaine Grant" : c'est une œuvre de **Jules Verne** (1868)

    🔍 **Autres questions que je peux traiter:**
    - "Qui est l'auteur de [titre]"
    - "Quand a été publié [titre]" 
    - "Livres similaires à [titre]"

    Pour des recommandations de livres, demandez plutôt:
    - "Livres comme Jules Verne"
    - "Romans d'aventure classiques"
    """

    def handle_factual_query(self, query: str) -> str:
        """Gère les questions factuelles générales"""
        query_lower = query.lower()
        
        # Questions techniques
        if any(word in query_lower for word in ['python', 'javascript', 'programming', 'code']):
            return "🔧 Pour les questions techniques, essayez plutôt: 'livres pour apprendre Python' ou 'ressources JavaScript'"
        
        # Questions littéraires générales
        elif any(word in query_lower for word in ['livre', 'auteur', 'roman', 'littérature']):
            return self.get_factual_literature_response(query)
        
        # Autres questions
        else:
            return """❓ Question factuelle détectée

    Je suis spécialisé dans les recommandations de livres. Pour des questions factuelles:

    📚 Littérature: "Qui est l'auteur de [titre]"
    🔧 Technique: "Livres pour apprendre [technologie]"
    🎌 Manga/Comics: "Recommandations manga action"

    💡 Reformulez votre question en demande de recommandation pour une meilleure réponse !"""

    def _get_best_recommendation(self, query: str) -> str:
        """Essaie les deux agents et retourne le meilleur résultat"""
        try:
            tech_response = self.get_tech_recommendations(query)
            lit_response = self.get_literature_recommendations(query)
            
            # Simple heuristique : préférer celui qui a trouvé des livres
            if "aucun livre" in tech_response.lower() and "aucun livre" not in lit_response.lower():
                return f"📚 **Agent Littéraire**\n\n{lit_response}"
            elif "aucun livre" in lit_response.lower() and "aucun livre" not in tech_response.lower():
                return f"🔧 **Agent Technique**\n\n{tech_response}"
            else:
                # Par défaut, littéraire pour les requêtes ambiguës
                return f"📚 **Agent Littéraire**\n\n{lit_response}"
                
        except Exception as e:
            logger.error(f"Erreur dans _get_best_recommendation: {e}")
            return "🤖 Désolé, je rencontre des difficultés techniques. Pouvez-vous reformuler votre question ?"
    
    def get_tech_recommendations(self, query: str, user_id: int = 1) -> str:
        """Génère des recommandations techniques avec gestion des questions factuelles"""
        try:
            # ✨ NOUVEAU: Vérifier si c'est une question factuelle technique
            if self.detect_factual_query(query):
                logger.info("❓ Question factuelle technique détectée")
                return self._handle_tech_factual_query(query, user_id)
            
            # Logique de recommandation existante...
            # Essayer avec Gemma d'abord
            if self.use_gemma and self.gemma_manager:
                logger.info("🤖 Utilisation de Gemma pour recommandations techniques")
                return self.gemma_manager.get_tech_recommendations(query, user_id)
            
            # Fallback vers la méthode originale
            logger.info("🔄 Fallback vers méthode technique originale")
            return self._get_tech_recommendations_original(query, user_id)
            
        except Exception as e:
            logger.error(f"❌ Erreur tech recommendations: {e}")
            return self._get_tech_recommendations_original(query, user_id)

    def get_literature_recommendations(self, query: str, user_id: int = 1) -> str:
        """Génère des recommandations littéraires avec gestion des questions factuelles"""
        try:
            # ✨ NOUVEAU: Vérifier si c'est une question factuelle littéraire
            if self.detect_factual_query(query):
                logger.info("❓ Question factuelle littéraire détectée")
                return self._handle_literature_factual_query(query, user_id)
            
            # Logique de recommandation existante...
            # Essayer avec Gemma d'abord
            if self.use_gemma and self.gemma_manager:
                logger.info("🤖 Utilisation de Gemma pour recommandations littéraires")
                return self.gemma_manager.get_literature_recommendations(query, user_id)
            
            # Fallback vers la méthode originale
            logger.info("🔄 Fallback vers méthode littéraire originale")
            return self._get_literature_recommendations_original(query, user_id)
            
        except Exception as e:
            logger.error(f"❌ Erreur literature recommendations: {e}")
            return self._get_literature_recommendations_original(query, user_id)

    def get_manga_recommendations(self, query: str, user_id: int = 1) -> str:
        """Génère des recommandations manga/comics avec gestion des questions factuelles"""
        try:
            # ✨ NOUVEAU: Vérifier si c'est une question factuelle manga/comics
            if self.detect_factual_query(query):
                logger.info("❓ Question factuelle manga/comics détectée")
                return self._handle_manga_factual_query(query, user_id)
            
            # Logique de recommandation existante...
            content_type = self.detect_content_type(query)
            
            # Essayer avec Gemma d'abord
            if self.use_gemma and self.gemma_manager:
                logger.info(f"🤖 Utilisation de Gemma pour recommandations manga/comics (type: {content_type})")
                return self.gemma_manager.get_manga_recommendations(query, user_id)
            
            # Fallback vers méthode avec le nouveau RAG unifié
            logger.info(f"🔄 Fallback vers méthode manga/comics (type: {content_type})")
            return self._get_manga_comics_recommendations(query, user_id, content_type)
            
        except Exception as e:
            logger.error(f"❌ Erreur manga/comics recommendations: {e}")
            return self._get_manga_fallback(query)

    
    def _get_manga_comics_recommendations(self, query: str, user_id: int = 1, content_type: str = 'all') -> str:
        """Méthode de recommandation unifiée manga/comics"""
        try:
            if not self.manga_rag:
                return "🎌 Service manga/comics temporairement indisponible."
            
            start_time = time.time()
            
            # Utiliser la nouvelle méthode unifiée
            recommendations = self.manga_rag.get_content_recommendations(
                user_id=user_id,
                query=query,
                n_recommendations=3,
                content_type=content_type
            )
            
            processing_time = time.time() - start_time
            
            if recommendations:
                # Enrichir avec des images de couverture
                recommendations = self._enrich_recommendations_with_images(recommendations, content_type)
                
                # Titre selon le type détecté
                if content_type == 'manga':
                    title = "🎌 **Recommandations Manga**"
                elif content_type == 'comics':
                    title = "🦸 **Recommandations Comics/BD**"
                else:
                    title = "🎌🦸 **Recommandations Manga & Comics**"
                
                response = f"{title}\n\n"
                
                for i, rec in enumerate(recommendations, 1):
                    content = rec['content']
                    content_type_icon = "🎌" if content['type'] == 'manga' else "🦸"
                    
                    # Ajouter l'image de couverture si disponible
                    if rec.get('cover_image_url'):
                        response += f"📸 ![{content['title']}]({rec['cover_image_url']})\n\n"
                    
                    response += f"{i}. {content_type_icon} **{content['title']}**\n"
                    
                    # Affichage adapté selon le type
                    if content['type'] == 'manga':
                        if 'year' in content and content['year'] > 0:
                            response += f"   📅 Année: {content['year']} | "
                        response += f"⭐ Note: {content['rating']}/5\n"
                    else:  # comics
                        if 'author' in content and content['author']:
                            response += f"   ✍️ Auteur: {content['author']} | "
                        response += f"⭐ Note: {content['rating']}/5\n"
                    
                    response += f"   📊 Pertinence: {rec['similarity_score']:.1%}\n"
                    response += f"   💡 {rec['reason']}\n"
                    response += f"   📖 {content['description'][:120]}...\n\n"
                
                response += f"⚡ Recherche en {processing_time:.1f}s"
                return response
            else:
                return self._generate_manga_comics_fallback(query, content_type)
                
        except Exception as e:
            logger.error(f"Erreur dans _get_manga_comics_recommendations: {e}")
            return "🎌 Désolé, j'ai rencontré un problème. Pouvez-vous reformuler votre demande ?"
    
    def _generate_manga_comics_fallback(self, query: str, content_type: str = 'all') -> str:
        """Génère une réponse de fallback adaptée au type de contenu"""
        
        if content_type == 'manga':
            return f"""🎌 **Recommandations Manga**

Je n'ai pas trouvé de correspondance exacte pour "{query}", mais voici quelques suggestions :

🔥 **Mangas d'action populaires:**
- Naruto : Ninja, amitié, persévérance
- One Piece : Pirates, aventure, camaraderie  
- Dragon Ball : Arts martiaux, dépassement de soi

⚔️ **Mangas plus sombres:**
- Attack on Titan : Survie, humanité, mystère
- Tokyo Ghoul : Transformation, identité
- Death Note : Psychologique, moral

🌸 **Mangas émotionnels:**
- Your Name : Romance, surnaturel
- Spirited Away : Famille, magie

💡 **Précisez votre recherche:** Genre (shounen, seinen), thème (école, action), ou manga de référence."""
        
        elif content_type == 'comics':
            return f"""🦸 **Recommandations Comics/BD**

Je n'ai pas trouvé de correspondance exacte pour "{query}", mais voici des suggestions :

🦸‍♂️ **Comics de super-héros:**
- Superman : Héros classique, espoir, justice
- Batman : Sombre, détective, Gotham
- Spider-Man : Responsabilité, humour, New York

🇫🇷 **BD françaises classiques:**
- Tintin : Aventure, voyage, mystère
- Astérix : Humour, histoire, Gaule
- Lucky Luke : Western, humour, cowboys

📚 **BD d'auteur:**
- Albums graphiques contemporains
- Bandes dessinées d'aventure

💡 **Précisez votre recherche:** Type (superhéros, BD française), thème (aventure, humour), ou série de référence."""
        
        else:  # 'all'
            return f"""🎌🦸 **Recommandations Manga & Comics**

Je n'ai pas trouvé de correspondance exacte pour "{query}", mais voici des suggestions :

🎌 **Côté Manga:**
- Naruto, One Piece, Dragon Ball (action)
- Studio Ghibli (émotionnel)
- Death Note (psychologique)

🦸 **Côté Comics/BD:**
- Superman, Batman (super-héros)
- Tintin, Astérix (BD française)
- Marvel, DC (univers partagés)

💡 **Précisez votre recherche:**
- "manga comme naruto" → mangas japonais
- "comics superman" → comics/super-héros  
- "bd française" → bandes dessinées françaises
- "histoire d'action" → les deux types"""
    
    def _get_tech_recommendations_original(self, query: str, user_id: int = 1) -> str:
        """Méthode technique originale"""
        try:
            if not self.tech_rag:
                return "🔧 Service technique temporairement indisponible."
            
            start_time = time.time()
            
            # Extraire le nombre demandé de la requête
            requested_count = self._extract_requested_count(query)
            
            # Expansion de la requête
            expanded_query = self.expand_query(query)
            logger.info(f"Requête technique enrichie: '{query}' → '{expanded_query}'")
            logger.info(f"Nombre de recommandations demandé: {requested_count}")
            
            # Recherche avec le nombre demandé
            recommendations = self.tech_rag.get_book_recommendations(
                user_id=user_id,
                query=expanded_query,
                n_recommendations=requested_count
            )
            
            processing_time = time.time() - start_time
            
            if recommendations:
                # Enrichir avec des images de couverture
                recommendations = self._enrich_recommendations_with_images(recommendations, 'tech')
                
                response = f"🔧 **Recommandations Techniques**\n\n"
                
                for i, rec in enumerate(recommendations, 1):
                    book = rec['book']
                    
                    # Ajouter l'image de couverture si disponible
                    if rec.get('cover_image_url'):
                        response += f"📸 ![{book['title']}]({rec['cover_image_url']})\n\n"
                    
                    response += f"{i}. **{book['title']}** par {book['author']}\n"
                    response += f"   ⭐ Note: {book['rating']}/5"
                    if book['price'] > 0:
                        response += f" | 💰 ${book['price']}"
                    response += f"\n   📊 Pertinence: {rec['similarity_score']:.1%}\n"
                    response += f"   💡 {rec['reason']}\n"
                    response += f"   📖 {book['description'][:120]}...\n\n"
                
                response += f"⚡ Recherche en {processing_time:.1f}s"
                return response
            else:
                return self._generate_tech_fallback(query)
                
        except Exception as e:
            logger.error(f"Erreur dans get_tech_recommendations_original: {e}")
            return "🔧 Désolé, j'ai rencontré un problème technique. Essayez de préciser votre domaine d'intérêt (Python, JavaScript, etc.)."
    
    def _get_literature_recommendations_original(self, query: str, user_id: int = 1) -> str:
        """Méthode littéraire originale (SANS manga/comics)"""
        try:
            if not self.literature_rag:
                return "📚 Service littéraire temporairement indisponible."
            
            start_time = time.time()
            
            # Expansion de la requête
            expanded_query = self.expand_query(query)
            logger.info(f"Requête littéraire enrichie: '{query}' → '{expanded_query}'")
            
            # Recherche avec seuil plus bas
            recommendations = self.literature_rag.get_book_recommendations(
                user_id=user_id,
                query=expanded_query,
                n_recommendations=3
            )
            
            # NOUVEAU: Filtrer les mangas/comics des résultats littéraires
            filtered_recommendations = self._filter_out_manga_from_literature(recommendations)
            
            processing_time = time.time() - start_time
            
            if filtered_recommendations:
                # Enrichir avec des images de couverture
                filtered_recommendations = self._enrich_recommendations_with_images(filtered_recommendations, 'literature')
                
                response = "📚 Recommandations Littéraires\n\n"
                
                for i, rec in enumerate(filtered_recommendations, 1):
                    book = rec['book']
                    
                    # Ajouter l'image de couverture si disponible
                    if rec.get('cover_image_url'):
                        response += f"📸 ![{book['title']}]({rec['cover_image_url']})\n\n"
                    
                    response += f"{i}. {book['title']} de {book['authors']}\n"
                    response += f"   ⭐ Note: {book['average_rating']}/5"
                    if book['published_year']:
                        response += f" | 📅 {book['published_year']}"
                    response += f"\n   📊 Pertinence: {rec['similarity_score']:.1%}\n"
                    response += f"   💡 {rec['reason']}\n"
                    response += f"   📖 {book['description'][:120]}...\n\n"
                
                response += f"⚡ Recherche en {processing_time:.1f}s"
                return response
            else:
                return self._generate_literature_fallback(query)
                
        except Exception as e:
            logger.error(f"Erreur dans get_literature_recommendations_original: {e}")
            return "📚 Désolé, j'ai rencontré un problème."
    
    def _filter_out_manga_from_literature(self, recommendations: List[Dict]) -> List[Dict]:
        """Filtre les mangas/comics des recommandations littéraires"""
        if not recommendations:
            return recommendations
        
        filtered = []
        # Étendre les mots-clés pour inclure les comics/BD
        exclusion_keywords = [
            'manga', 'anime', 'shounen', 'shoujo', 'seinen', 'josei', 'manhua', 'manhwa', 'otaku',
            'comics', 'bd', 'bande dessinée', 'superhéros', 'superman', 'batman', 'marvel', 'dc',
            'tintin', 'astérix', 'album graphique'
        ]
        
        for rec in recommendations:
            book = rec['book']
            title_lower = book['title'].lower()
            desc_lower = book['description'].lower()
            categories_lower = book.get('categories', '').lower()
            authors_lower = book.get('authors', '').lower()
            
            # Vérifier si c'est un manga ou comics
            is_manga_comics = any(keyword in title_lower or keyword in desc_lower or 
                                keyword in categories_lower or keyword in authors_lower
                                for keyword in exclusion_keywords)
            
            if not is_manga_comics:
                filtered.append(rec)
        
        logger.info(f"📚 Filtrage manga/comics: {len(recommendations)} → {len(filtered)} livres littéraires")
        return filtered
    
    def _get_manga_fallback(self, query: str) -> str:
        """Méthode de fallback pour les mangas/comics quand Gemma n'est pas disponible"""
        content_type = self.detect_content_type(query)
        return self._generate_manga_comics_fallback(query, content_type)
    
    def _generate_tech_fallback(self, query: str) -> str:
        """Génère une réponse de fallback pour les requêtes techniques"""
        return """🔧 **Recommandations Techniques**

Je n'ai pas trouvé de correspondance exacte, mais voici quelques suggestions :

📚 **Langages populaires :**
- Python : Idéal pour débuter, data science, IA
- JavaScript : Développement web, applications
- Java : Applications entreprise, Android
- C# : Développement Windows, .NET

💡 **Précisez votre recherche :**
- "Apprendre Python débutant"
- "Développement web JavaScript"
- "Machine learning Python"
- "Programmation mobile"

Reformulez votre question avec un langage ou domaine spécifique !"""
    
    def _generate_literature_fallback(self, query: str) -> str:
        """Génère une réponse de fallback pour les requêtes littéraires"""
        return """📚 **Recommandations Littéraires**

Je n'ai pas trouvé de correspondance exacte, mais voici des suggestions :

👥 **Auteurs populaires :**
- Fiction : Stephen King, Murakami, Orwell
- Classiques : Tolstoï, Hugo, Shakespeare
- Contemporain : Elena Ferrante, Michel Houellebecq

📖 **Genres populaires :**
- Fantasy : Tolkien, Brandon Sanderson
- Science-fiction : Isaac Asimov, Philip K. Dick
- Thriller : Agatha Christie, Gillian Flynn

💡 **Précisez votre recherche :**
- "Romans de Tolstoï"
- "Livres comme Harry Potter"
- "Auteurs français contemporains"

Dites-moi quel auteur ou genre vous intéresse !"""
    
    # ===============================
    # INTERFACE UNIFIÉE
    # ===============================
    
    def get_agent_response(self, query: str, agent_type: str = "router") -> str:
        """Interface unifiée pour obtenir une réponse d'agent"""
        try:
            if agent_type == "router":
                return self.route_query(query)
            elif agent_type == "tech":
                return self.get_tech_recommendations(query)
            elif agent_type == "literature":
                return self.get_literature_recommendations(query)
            elif agent_type == "manga":
                return self.get_manga_recommendations(query)
            else:
                return "🤖 Type d'agent non reconnu. Utilisez: 'router', 'tech', 'literature', ou 'manga'"
                
        except Exception as e:
            logger.error(f"Erreur dans get_agent_response: {e}")
            return f"🤖 Erreur: {str(e)}"
    
    def get_agent_response_with_gemma(self, query: str, agent_type: str = "router") -> str:
        """Interface pour forcer l'utilisation de Gemma si disponible"""
        try:
            if self.use_gemma and self.gemma_manager:
                logger.info(f"🤖 Force utilisation de Gemma pour: {agent_type}")
                
                if agent_type == "router":
                    return self.gemma_manager.route_query(query)
                elif agent_type == "tech":
                    return self.gemma_manager.get_tech_recommendations(query)
                elif agent_type == "literature":
                    return self.gemma_manager.get_literature_recommendations(query)
                elif agent_type == "manga":
                    return self.gemma_manager.get_manga_recommendations(query)
                else:
                    return "🤖 Type d'agent non reconnu"
            else:
                # Fallback vers les méthodes existantes
                logger.info(f"🔄 Gemma non disponible, fallback pour: {agent_type}")
                return self.get_agent_response(query, agent_type)
                
        except Exception as e:
            logger.error(f"❌ Erreur Gemma, fallback: {e}")
            return self.get_agent_response(query, agent_type)
    
    def _enrich_recommendations_with_images(self, recommendations: List[Dict], content_type: str) -> List[Dict]:
        """Enrichit les recommandations avec des images de couverture"""
        if not self.use_cover_images or not recommendations:
            return recommendations
        
        try:
            logger.info(f"🖼️ Enrichissement avec images pour {len(recommendations)} recommandations ({content_type})")
            
            for rec in recommendations:
                # Extraire les informations selon le type de contenu
                if content_type == 'tech':
                    book = rec.get('book', {})
                    title = book.get('title', '')
                    author = book.get('author', '')
                elif content_type == 'literature':
                    book = rec.get('book', {})
                    title = book.get('title', '')
                    author = book.get('authors', '')
                elif content_type in ['manga', 'comics']:
                    content = rec.get('content', {})
                    title = content.get('title', '')
                    author = content.get('author', '')
                    # Déterminer le type spécifique pour l'API
                    if content.get('type') == 'manga':
                        api_content_type = 'manga'
                    else:
                        api_content_type = 'comics'
                else:
                    continue
                
                # Récupérer l'image de couverture avec la stratégie optimisée
                if title:
                    # Déterminer le type d'API à utiliser selon l'agent
                    if content_type == 'tech':
                        api_type = 'book'  # Agent technique = Google Books + Open Library
                    elif content_type == 'literature':
                        api_type = 'book'  # Agent littérature = Google Books + Open Library
                    elif content_type in ['manga', 'comics']:
                        api_type = api_content_type  # Agent manga/comics = AniList prioritaire
                    else:
                        api_type = 'book'
                    
                    cover_url = cover_service.get_cover_image(
                        title=title,
                        author=author,
                        content_type=api_type
                    )
                    
                    # Ajouter l'URL à la recommandation
                    rec['cover_image_url'] = cover_url
                    
                    if cover_url:
                        logger.info(f"✅ Image trouvée pour: {title}")
                    else:
                        logger.info(f"❌ Aucune image pour: {title}")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Erreur enrichissement images: {e}")
            return recommendations

    def get_system_status(self) -> Dict[str, Any]:
        """Obtient le statut du système"""
        status = {
            "simple_agents": "active",
            "gemma_available": GEMMA_AVAILABLE,
            "gemma_active": self.use_gemma,
            "cover_service_available": COVER_SERVICE_AVAILABLE,
            "cover_service_active": self.use_cover_images,
            "tech_rag": "available" if self.tech_rag else "unavailable",
            "literature_rag": "available" if self.literature_rag else "unavailable",
            "manga_rag": "available" if self.manga_rag else "unavailable"
        }
        
        if self.use_gemma and self.gemma_manager:
            try:
                status["gemma_health"] = self.gemma_manager.health_check()
            except Exception as e:
                status["gemma_health"] = {"error": str(e)}
        
        return status
    
    
    def _handle_tech_factual_query(self, query: str, user_id: int = 1) -> str:
        """Gère les questions factuelles techniques"""
        try:
            if not self.tech_rag:
                return "🔧 Service technique temporairement indisponible."
            
            # Extraire le titre du livre technique
            title = self._extract_book_title_from_query(query)
            
            if title:
                # Rechercher dans le RAG technique
                results = self.tech_rag.search_books(
                    query=title,
                    n_results=3
                )
                
                if results:
                    # Prendre le meilleur résultat
                    best_match = results[0]
                    
                    # Construire une réponse factuelle
                    if "auteur" in query.lower() or "author" in query.lower():
                        if self.use_gemma and self.gemma_manager:
                            # Utiliser Gemma pour une réponse naturelle
                            book_info = f"""Titre: {best_match['title']}
    Auteur: {best_match['author']}
    Note: {best_match['rating']}/5
    Prix: ${best_match['price']}
    Description: {best_match['matched_text']}"""
                            
                            return self.gemma_manager.get_factual_response(query, book_info)
                        else:
                            return f"🔧 **{best_match['title']}** a été écrit par **{best_match['author']}**.\n\n" \
                                f"📊 Note: {best_match['rating']}/5 | 💰 Prix: ${best_match['price']}\n" \
                                f"📖 {best_match['matched_text'][:200]}..."
                    
                    elif "quand" in query.lower() or "when" in query.lower():
                        return f"🔧 **{best_match['title']}** par {best_match['author']} - Informations techniques disponibles."
                    
                    else:
                        # Réponse générale
                        return f"🔧 **{best_match['title']}**\n\n" \
                            f"✍️ Auteur: {best_match['author']}\n" \
                            f"⭐ Note: {best_match['rating']}/5\n" \
                            f"💰 Prix: ${best_match['price']}\n\n" \
                            f"📖 {best_match['matched_text'][:300]}..."
            
            # Si pas trouvé dans le RAG technique
            return "🔧 Je n'ai pas trouvé ce livre technique dans ma base de données. Essayez une formulation différente ou vérifiez l'orthographe."
            
        except Exception as e:
            logger.error(f"Erreur dans _handle_tech_factual_query: {e}")
            return "🔧 Erreur lors du traitement de votre question technique."

    def _handle_literature_factual_query(self, query: str, user_id: int = 1) -> str:
        """Gère les questions factuelles littéraires"""
        try:
            if not self.literature_rag:
                return "📚 Service littéraire temporairement indisponible."
            
            # Extraire le titre du livre
            title = self._extract_book_title_from_query(query)
            
            if title:
                # Rechercher dans le RAG littéraire
                results = self.literature_rag.search_books(
                    query=title,
                    n_results=3
                )
                
                if results:
                    # Prendre le meilleur résultat
                    best_match = results[0]
                    
                    # Construire une réponse factuelle
                    if "auteur" in query.lower() or "author" in query.lower():
                        if self.use_gemma and self.gemma_manager:
                            # Utiliser Gemma pour une réponse naturelle
                            book_info = f"""Titre: {best_match['title']}
    Auteur(s): {best_match['authors']}
    Année de publication: {best_match.get('published_year', 'Non spécifiée')}
    Note moyenne: {best_match['average_rating']}/5
    Description: {best_match['matched_text']}"""
                            
                            return self.gemma_manager.get_factual_response(query, book_info)
                        else:
                            return f"📚 **{best_match['title']}** a été écrit par **{best_match['authors']}**.\n\n" \
                                f"📅 Publié en {best_match.get('published_year', 'date inconnue')}\n" \
                                f"⭐ Note moyenne: {best_match['average_rating']}/5\n" \
                                f"📖 {best_match['matched_text'][:200]}..."
                    
                    elif "quand" in query.lower() or "when" in query.lower():
                        return f"📚 **{best_match['title']}** a été publié en **{best_match.get('published_year', 'date inconnue')}** par {best_match['authors']}."
                    
                    else:
                        # Réponse générale
                        return f"📚 **{best_match['title']}**\n\n" \
                            f"✍️ Auteur(s): {best_match['authors']}\n" \
                            f"📅 Publié: {best_match.get('published_year', 'Date inconnue')}\n" \
                            f"⭐ Note: {best_match['average_rating']}/5\n\n" \
                            f"📖 {best_match['matched_text'][:300]}..."
            
            # Fallbacks pour les classiques connus
            return self._get_literature_factual_fallback(query)
            
        except Exception as e:
            logger.error(f"Erreur dans _handle_literature_factual_query: {e}")
            return self._get_literature_factual_fallback(query)

    def _handle_manga_factual_query(self, query: str, user_id: int = 1) -> str:
        """Gère les questions factuelles manga/comics"""
        try:
            if not self.manga_rag:
                return "🎌 Service manga/comics temporairement indisponible."
            
            # Extraire le titre de l'œuvre
            title = self._extract_book_title_from_query(query)
            
            if title:
                # Rechercher dans le RAG manga/comics
                results = self.manga_rag.search_content(
                    query=title,
                    n_results=3
                )
                
                if results:
                    # Prendre le meilleur résultat
                    best_match = results[0]
                    
                    # Construire une réponse factuelle
                    if "auteur" in query.lower() or "author" in query.lower():
                        author = best_match.get('author', 'Auteur non spécifié')
                        
                        if self.use_gemma and self.gemma_manager:
                            # Utiliser Gemma pour une réponse naturelle
                            content_info = f"""Titre: {best_match['title']}
    Auteur: {author}
    Note: {best_match['rating']}/5
    Genres: {best_match['tags']}
    Description: {best_match['description']}"""
                            
                            return self.gemma_manager.get_factual_response(query, content_info)
                        else:
                            content_type_icon = "🎌" if best_match.get('source_type') == 'manga_japonais' else "🦸"
                            return f"{content_type_icon} **{best_match['title']}** a été créé par **{author}**.\n\n" \
                                f"⭐ Note: {best_match['rating']}/5\n" \
                                f"🏷️ Genres: {best_match['tags']}\n" \
                                f"📖 {best_match['description'][:200]}..."
                    
                    else:
                        # Réponse générale
                        content_type_icon = "🎌" if best_match.get('source_type') == 'manga_japonais' else "🦸"
                        author = best_match.get('author', 'Auteur non spécifié')
                        return f"{content_type_icon} **{best_match['title']}**\n\n" \
                            f"✍️ Auteur: {author}\n" \
                            f"⭐ Note: {best_match['rating']}/5\n" \
                            f"🏷️ Genres: {best_match['tags']}\n\n" \
                            f"📖 {best_match['description'][:300]}..."
            
            # Si pas trouvé, fallback
            return "🎌 Je n'ai pas trouvé ce manga/comics dans ma base de données. Essayez une formulation différente ou vérifiez l'orthographe."
            
        except Exception as e:
            logger.error(f"Erreur dans _handle_manga_factual_query: {e}")
            return "🎌 Erreur lors du traitement de votre question manga/comics."

    def _extract_book_title_from_query(self, query: str) -> str:
        """Extrait le titre du livre de la question"""
        import re
        
        # Patterns pour extraire le titre
        patterns = [
            r'auteur de\s+(.+?)(?:\?|$)',
            r'author of\s+(.+?)(?:\?|$)',
            r'écrit\s+(.+?)(?:\?|$)',
            r'written\s+(.+?)(?:\?|$)',
            r'créé\s+(.+?)(?:\?|$)',
            r'created\s+(.+?)(?:\?|$)',
            r'"([^"]+)"',
            r'«([^»]+)»',
            r'est\s+(.+?)(?:\?|$)',
            r'is\s+(.+?)(?:\?|$)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                title = match.group(1).strip()
                # Nettoyer le titre
                title = re.sub(r'\s+', ' ', title)
                # Supprimer les mots de liaison
                title = re.sub(r'\b(le|la|les|the|a|an)\b', '', title, flags=re.IGNORECASE).strip()
                return title
        
        return ""

    def _get_literature_factual_fallback(self, query: str) -> str:
        """Fallback pour les questions factuelles littéraires"""
        # Fallbacks pour les classiques connus
        query_lower = query.lower()
        
        if "lord of the rings" in query_lower or "seigneur des anneaux" in query_lower:
            return """📚 **The Lord of the Rings** (Le Seigneur des Anneaux)

    ✍️ **Auteur: J.R.R. Tolkien** (John Ronald Reuel Tolkien)
    📅 **Publié:** 1954-1955
    📖 **Genre:** Fantasy épique

    🌍 **À propos:** Œuvre majeure de la fantasy moderne, cette trilogie suit Frodon Baggins dans sa quête pour détruire l'Anneau Unique. Tolkien a créé un univers complet avec ses langues, cultures et histoires.

    💡 **Pour des recommandations similaires, demandez:** "livres comme Tolkien" ou "fantasy épique"."""
        
        elif "harry potter" in query_lower:
            return """📚 **Harry Potter**

    ✍️ **Auteur: J.K. Rowling** (Joanne Kathleen Rowling)
    📅 **Publié:** 1997-2007
    📖 **Genre:** Fantasy jeunesse

    ⚡ **À propos:** Série de sept romans suivant le jeune sorcier Harry Potter à l'école de Poudlard. L'une des séries les plus populaires de tous les temps.

    💡 **Pour des recommandations similaires:** "livres comme Harry Potter" ou "fantasy jeunesse"."""
        
        else:
            return f"""📚 **Question sur la littérature**

    Je n'ai pas trouvé d'information précise sur "{query}" dans ma base de données littéraire.

    💡 **Suggestions:**
    - Vérifiez l'orthographe du titre ou de l'auteur
    - Essayez une formulation différente
    - Utilisez des guillemets pour le titre exact

    🔍 **Exemples de questions que je peux traiter:**
    - "Qui est l'auteur de Harry Potter"
    - "Quand a été publié Le Seigneur des Anneaux"

    Pour des recommandations de livres, demandez plutôt:
    - "Livres comme Tolkien"
    - "Romans de fantasy épique" """

    # ===============================
    # MÉTHODES HÉRITÉES (gardées pour compatibilité)
    # ===============================
    
    def get_literature_recommendations_intelligent(self, query: str, user_id: int = 1) -> str:
        """Méthode héritée - redirige vers la nouvelle logique"""
        return self.get_literature_recommendations(query, user_id)
    
    def _analyze_literature_query(self, query_lower: str) -> dict:
        """Analyse intelligente des requêtes littéraires (méthode héritée)"""
        # Garder la logique existante mais ajouter la détection manga/comics
        import re
        
        analysis = {
            'type': 'general',
            'genre': None,
            'author': None,
            'count': 10,
            'reference': None
        }
        
        # Si c'est détecté comme manga/comics, marquer spécialement
        if self.detect_manga_query(query_lower):
            analysis['type'] = 'manga_comics_request'
            return analysis
        
        # Détection du type de requête littéraire
        if re.search(r'\b(comme|similar|similaire|aimé|loved|enjoyed)\b', query_lower):
            analysis['type'] = 'similarity'
            # Extraire la référence
            ref_match = re.search(r'(?:comme|similar to|similaire à)\s+(.+?)(?:\s|$)', query_lower)
            if ref_match:
                analysis['reference'] = ref_match.group(1).strip()
        
        # Détection du genre
        genres = {
            'fantasy': r'\b(fantasy|fantastique|magic|magie|dragon|wizard|sorcier)\b',
            'science_fiction': r'\b(science fiction|sci-fi|sf|futur|space|espace)\b',
            'romance': r'\b(romance|amour|love|romantic)\b',
            'thriller': r'\b(thriller|suspense|mystery|mystère|police)\b',
            'horror': r'\b(horror|horreur|scary|effrayant|peur)\b',
            'classic': r'\b(classic|classique|great works|chef.*oeuvre)\b'
        }
        
        for genre, pattern in genres.items():
            if re.search(pattern, query_lower):
                analysis['genre'] = genre
                break
        
        # Détection d'auteur
        authors = {
            'stephen_king': r'\bstephen king\b',
            'murakami': r'\bmurakami\b',
            'tolkien': r'\btolkien\b',
            'shakespeare': r'\bshakespeare\b',
            'hugo': r'\bvictor hugo\b',
            'camus': r'\bcamus\b'
        }
        
        for author, pattern in authors.items():
            if re.search(pattern, query_lower):
                analysis['author'] = author
                break
        
        # Détection du nombre
        count_match = re.search(r'(\d+)\s*(?:livres?|books?|recommandations?)', query_lower)
        if count_match:
            analysis['count'] = min(int(count_match.group(1)), 20)
        
        return analysis
    
    def _get_books_by_genre(self, genre: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Récupère des livres par genre (méthode héritée)"""
        try:
            from apps.books.models import LiteratureBook
            
            genre_queries = {
                'fantasy': LiteratureBook.objects.filter(
                    categories__icontains='Fantasy'
                ).exclude(
                    categories__icontains='Manga'  # Exclure les mangas
                ),
                'science_fiction': LiteratureBook.objects.filter(
                    categories__icontains='Science Fiction'
                ).exclude(
                    categories__icontains='Manga'
                ),
                'romance': LiteratureBook.objects.filter(
                    categories__icontains='Romance'
                ).exclude(
                    categories__icontains='Manga'
                ),
                'thriller': LiteratureBook.objects.filter(
                    categories__icontains='Thriller'
                ).exclude(
                    categories__icontains='Manga'
                ),
                'classic': LiteratureBook.objects.filter(
                    published_year__lt=1950
                ).exclude(
                    categories__icontains='Manga'
                )
            }
            
            query = genre_queries.get(genre, LiteratureBook.objects.exclude(
                categories__icontains='Manga'
            ))
            
            books = query.filter(average_rating__gte=3.5).order_by('-average_rating')[:limit]
            
            return [
                {
                    'id': book.id,
                    'title': book.title,
                    'authors': book.authors,
                    'rating': float(book.average_rating) if book.average_rating else 0.0,
                    'description': book.description,
                    'published_year': book.published_year,
                    'categories': book.categories
                }
                for book in books
            ]
            
        except Exception as e:
            logger.error(f"Erreur _get_books_by_genre: {e}")
            return []
    
    def _get_books_by_author(self, author: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Récupère des livres par auteur (méthode héritée)"""
        try:
            from apps.books.models import LiteratureBook
            
            author_mappings = {
                'stephen_king': 'Stephen King',
                'murakami': 'Haruki Murakami',
                'tolkien': 'J.R.R. Tolkien',
                'shakespeare': 'William Shakespeare',
                'hugo': 'Victor Hugo',
                'camus': 'Albert Camus'
            }
            
            author_name = author_mappings.get(author, author)
            
            books = LiteratureBook.objects.filter(
                authors__icontains=author_name
            ).exclude(
                categories__icontains='Manga'  # Exclure les mangas
            ).order_by('-average_rating')[:limit]
            
            return [
                {
                    'id': book.id,
                    'title': book.title,
                    'authors': book.authors,
                    'rating': float(book.average_rating) if book.average_rating else 0.0,
                    'description': book.description,
                    'published_year': book.published_year,
                    'categories': book.categories
                }
                for book in books
            ]
            
        except Exception as e:
            logger.error(f"Erreur _get_books_by_author: {e}")
            return []
    
    def _get_similar_books(self, reference: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Trouve des livres similaires à une référence (méthode héritée)"""
        try:
            if self.literature_rag:
                # Utiliser le RAG pour les recommandations similaires
                recommendations = self.literature_rag.get_book_recommendations(
                    user_id=1,
                    query=f"livres comme {reference}",
                    n_recommendations=limit
                )
                
                # Filtrer les mangas/comics
                filtered_recommendations = self._filter_out_manga_from_literature(recommendations)
                
                return [
                    {
                        'id': rec['book']['id'],
                        'title': rec['book']['title'],
                        'authors': rec['book']['authors'],
                        'rating': rec['book']['average_rating'],
                        'description': rec['book']['description'],
                        'published_year': rec['book'].get('published_year'),
                        'categories': rec['book'].get('categories', ''),
                        'similarity_score': rec['similarity_score'],
                        'reason': rec['reason']
                    }
                    for rec in filtered_recommendations
                ]
            else:
                # Fallback vers recherche simple par titre
                from apps.books.models import LiteratureBook
                
                books = LiteratureBook.objects.filter(
                    title__icontains=reference
                ).exclude(
                    categories__icontains='Manga'
                ).order_by('-average_rating')[:limit]
                
                return [
                    {
                        'id': book.id,
                        'title': book.title,
                        'authors': book.authors,
                        'rating': float(book.average_rating) if book.average_rating else 0.0,
                        'description': book.description,
                        'published_year': book.published_year,
                        'categories': book.categories
                    }
                    for book in books
                ]
                
        except Exception as e:
            logger.error(f"Erreur _get_similar_books: {e}")
            return []
    
    def _format_literature_response(self, books: List[Dict[str, Any]], query: str, 
                                  processing_time: float = 0) -> str:
        """Formate la réponse littéraire (méthode héritée)"""
        if not books:
            return self._generate_literature_fallback(query)
        
        response = "📚 **Recommandations Littéraires**\n\n"
        
        for i, book in enumerate(books, 1):
            response += f"{i}. **{book['title']}** de {book['authors']}\n"
            response += f"   ⭐ Note: {book['rating']}/5"
            
            if book.get('published_year'):
                response += f" | 📅 {book['published_year']}"
            
            if book.get('similarity_score'):
                response += f"\n   📊 Pertinence: {book['similarity_score']:.1%}"
            
            if book.get('reason'):
                response += f"\n   💡 {book['reason']}"
            
            response += f"\n   📖 {book['description'][:120]}...\n\n"
        
        if processing_time > 0:
            response += f"⚡ Recherche en {processing_time:.1f}s"
        
        return response
    
