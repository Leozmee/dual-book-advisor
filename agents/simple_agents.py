"""
Agents simples pour les recommandations de livres
Avec intégration Gemma et séparation manga/littérature
"""
import logging
import time
from typing import List, Dict, Any, Optional
from django.conf import settings

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


class SimpleAgentManager:
    """Gestionnaire simple pour les agents de recommandation"""
    
    def __init__(self, use_gemma: bool = True):
        self.tech_rag = None
        self.literature_rag = None
        self.manga_rag = None
        
        # Configuration Gemma
        self.use_gemma = use_gemma and GEMMA_AVAILABLE
        self.gemma_manager = None
        
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
            
            # Essayer d'initialiser le RAG manga
            try:
                from rags.manga_rag.manga_rag_manager import MangaRAGManager
                self.manga_rag = MangaRAGManager()
                logger.info("✅ Gestionnaire RAG manga initialisé")
            except ImportError:
                logger.warning("⚠️ RAG manga non disponible (normal si pas encore créé)")
            
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
        """Détecte si une requête concerne des mangas"""
        query_lower = query.lower()
        
        manga_keywords = [
            # Mangas populaires
            'manga', 'anime', 'naruto', 'one piece', 'dragon ball', 'attack on titan',
            'death note', 'fullmetal alchemist', 'bleach', 'demon slayer', 'tokyo ghoul',
            'my hero academia', 'cowboy bebop', 'spirited away', 'princess mononoke',
            'akira', 'ghost in the shell', 'sailor moon', 'fruits basket',
            
            # Genres manga
            'shounen', 'shoujo', 'seinen', 'josei', 'manhua', 'manhwa', 
            'isekai', 'mecha', 'slice of life',
            
            # Termes généraux
            'otaku', 'anime', 'manga japonais', 'bande dessinée japonaise'
        ]
        
        return any(keyword in query_lower for keyword in manga_keywords)
    
    def route_query(self, query: str) -> str:
        """Route une requête vers l'agent approprié avec détection manga prioritaire"""
        import re
        
        query_lower = query.lower()
        logger.info(f"🔍 Route query called with: '{query}'")
        
        # PRIORITÉ 1: Détection manga (nouvelle logique)
        if self.detect_manga_query(query):
            logger.info("🎌 Détection manga - routage vers agent manga")
            return self.get_manga_recommendations(query)
        
        # PRIORITÉ 2: Mots-clés techniques
        tech_keywords = [
            'python', 'javascript', 'java', 'c#', 'csharp', 'php', 'ruby', 'go',
            'programming', 'programmation', 'développement', 'development',
            'web', 'mobile', 'app', 'application', 'software', 'logiciel',
            'machine learning', 'data science', 'ai', 'intelligence artificielle',
            'algorithm', 'algorithme', 'code', 'coding', 'framework',
            'database', 'base de données', 'api', 'backend', 'frontend'
        ]
        
        # PRIORITÉ 3: Mots-clés littéraires (SANS manga)
        lit_keywords = [
            'roman', 'novel', 'livre', 'book', 'auteur', 'author', 'écrivain',
            'littérature', 'literature', 'fiction', 'poetry', 'poésie',
            'histoire', 'story', 'récit', 'narrative', 'classique', 'classic',
            'genre', 'style', 'oeuvre', 'work', 'masterpiece', 'chef-d\'oeuvre',
            'comme', 'similaire', 'similar', 'aimé', 'recommandation'
        ]
        
        # Noms d'auteurs connus (littérature classique)
        known_authors = [
            'tolstoy', 'tolstoï', 'stephen king', 'murakami', 'shakespeare',
            'hugo', 'camus', 'sartre', 'proust', 'zola', 'balzac', 'dickens',
            'hemingway', 'orwell', 'kafka', 'dostoyevsky', 'chekhov'
        ]
        
        # Score pour déterminer le type
        tech_score = sum(1 for keyword in tech_keywords if keyword in query_lower)
        lit_score = sum(1 for keyword in lit_keywords if keyword in query_lower)
        author_score = sum(1 for author in known_authors if author in query_lower)
        
        # Si auteur classique détecté, c'est littéraire
        if author_score > 0:
            logger.info("📚 Détection auteur classique - routage vers agent littéraire")
            return self.get_literature_recommendations(query)
        
        # Sinon, utiliser les scores
        if tech_score > lit_score:
            logger.info("🔧 Détection technique - routage vers agent technique")
            return self.get_tech_recommendations(query)
        elif lit_score > 0:
            logger.info("📚 Détection littéraire - routage vers agent littéraire")
            return self.get_literature_recommendations(query)
        else:
            # Par défaut, essayer les deux et retourner le meilleur
            logger.info("🤔 Requête ambiguë - test des deux agents")
            return self._get_best_recommendation(query)
    
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
        """Génère des recommandations techniques avec Gemma ou fallback"""
        try:
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
        """Génère des recommandations littéraires (SANS manga) avec Gemma ou fallback"""
        try:
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
        """Génère des recommandations manga avec Gemma ou fallback"""
        try:
            # Essayer avec Gemma d'abord
            if self.use_gemma and self.gemma_manager:
                logger.info("🤖 Utilisation de Gemma pour recommandations manga")
                return self.gemma_manager.get_manga_recommendations(query, user_id)
            
            # Fallback vers méthode simple
            logger.info("🔄 Fallback vers méthode manga simple")
            return self._get_manga_fallback(query)
            
        except Exception as e:
            logger.error(f"❌ Erreur manga recommendations: {e}")
            return self._get_manga_fallback(query)
    
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
                response = f"🔧 **Recommandations Techniques**\n\n"
                
                for i, rec in enumerate(recommendations, 1):
                    book = rec['book']
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
        """Méthode littéraire originale (SANS manga)"""
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
            
            # NOUVEAU: Filtrer les mangas des résultats littéraires
            filtered_recommendations = self._filter_out_manga_from_literature(recommendations)
            
            processing_time = time.time() - start_time
            
            if filtered_recommendations:
                response = "📚 **Recommandations Littéraires**\n\n"
                
                for i, rec in enumerate(filtered_recommendations, 1):
                    book = rec['book']
                    response += f"{i}. **{book['title']}** de {book['authors']}\n"
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
        """Filtre les mangas des recommandations littéraires"""
        if not recommendations:
            return recommendations
        
        filtered = []
        manga_keywords = ['manga', 'anime', 'shounen', 'shoujo', 'seinen', 'josei', 'manhua', 'manhwa', 'otaku']
        
        for rec in recommendations:
            book = rec['book']
            title_lower = book['title'].lower()
            desc_lower = book['description'].lower()
            categories_lower = book.get('categories', '').lower()
            authors_lower = book.get('authors', '').lower()
            
            # Vérifier si c'est un manga
            is_manga = any(keyword in title_lower or keyword in desc_lower or 
                          keyword in categories_lower or keyword in authors_lower
                          for keyword in manga_keywords)
            
            if not is_manga:
                filtered.append(rec)
        
        logger.info(f"📚 Filtrage manga: {len(recommendations)} → {len(filtered)} livres littéraires")
        return filtered
    
    def _get_manga_fallback(self, query: str) -> str:
        """Méthode de fallback pour les mangas quand Gemma n'est pas disponible"""
        return f"""🎌 **Recommandations Manga**

Je détecte que vous cherchez des mangas !

**Votre recherche:** "{query}"

Pour de meilleures recommandations manga, le système Gemma avec RAG dédié est recommandé.

**Suggestions générales basées sur votre requête:**

🔥 **Si vous aimez l'action/aventure:**
- Naruto : Ninja, amitié, persévérance
- One Piece : Pirates, aventure, camaraderie
- Dragon Ball : Arts martiaux, tournois, dépassement de soi

⚔️ **Si vous aimez les histoires sombres:**
- Attack on Titan : Survie, humanité, mystère
- Tokyo Ghoul : Transformation, identité, surnaturel
- Death Note : Psychologique, moral, justice

🌸 **Si vous aimez les émotions:**
- Your Name : Romance, surnaturel, destin
- Spirited Away : Famille, croissance, magie

💡 **Pour des recommandations personnalisées avec Gemma:**
1. Installez Ollama et Gemma 2B
2. Activez le système Gemma dans l'application
3. Profitez de recommandations intelligentes !

🎯 **Précisez votre recherche:** Genre (shounen, seinen, romance), thème (action, school life), ou manga de référence."""
    
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
    
    def get_system_status(self) -> Dict[str, Any]:
        """Obtient le statut du système"""
        status = {
            "simple_agents": "active",
            "gemma_available": GEMMA_AVAILABLE,
            "gemma_active": self.use_gemma,
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
    
    # ===============================
    # MÉTHODES HÉRITÉES (gardées pour compatibilité)
    # ===============================
    
    def get_literature_recommendations_intelligent(self, query: str, user_id: int = 1) -> str:
        """Méthode héritée - redirige vers la nouvelle logique"""
        return self.get_literature_recommendations(query, user_id)
    
    # Garder toutes les autres méthodes privées existantes pour la compatibilité...
    # (toutes les méthodes _analyze_literature_query, _get_books_by_genre, etc.)
    
    def _analyze_literature_query(self, query_lower: str) -> dict:
        """Analyse intelligente des requêtes littéraires (méthode héritée)"""
        # Garder la logique existante mais ajouter la détection manga
        import re
        
        analysis = {
            'type': 'general',
            'genre': None,
            'author': None,
            'count': 10,
            'reference': None
        }
        
        # Si c'est détecté comme manga, marquer spécialement
        if self.detect_manga_query(query_lower):
            analysis['type'] = 'manga_request'
            return analysis
        
        # Resto de la logique existante...
        # (garder tout le code existant de _analyze_literature_query)
        
        return analysis