"""
Agents simples pour les recommandations de livres
"""
import logging
import time
from typing import List, Dict, Any, Optional
from django.conf import settings

logger = logging.getLogger(__name__)


class SimpleAgentManager:
    """Gestionnaire simple pour les agents de recommandation"""
    
    def __init__(self):
        self.tech_rag = None
        self.literature_rag = None
        self._init_rag_managers()
    
    def _init_rag_managers(self):
        """Initialise les gestionnaires RAG"""
        try:
            from rags.tech_rag.tech_rag_manager import TechRAGManager
            from rags.literature_rag.literature_rag_manager import LiteratureRAGManager
            
            self.tech_rag = TechRAGManager()
            self.literature_rag = LiteratureRAGManager()
            logger.info("✅ Gestionnaires RAG initialisés")
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation RAG: {e}")
    
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
    
    def route_query(self, query: str) -> str:
        """Route une requête vers l'agent approprié"""
        import re
        
        query_lower = query.lower()
        logger.info(f"🔍 Route query called with: '{query}'")
        
        # Mots-clés techniques
        tech_keywords = [
            'python', 'javascript', 'java', 'c#', 'csharp', 'php', 'ruby', 'go',
            'programming', 'programmation', 'développement', 'development',
            'web', 'mobile', 'app', 'application', 'software', 'logiciel',
            'machine learning', 'data science', 'ai', 'intelligence artificielle',
            'algorithm', 'algorithme', 'code', 'coding', 'framework',
            'database', 'base de données', 'api', 'backend', 'frontend'
        ]
        
        # Mots-clés littéraires
        lit_keywords = [
            'roman', 'novel', 'livre', 'book', 'auteur', 'author', 'écrivain',
            'littérature', 'literature', 'fiction', 'poetry', 'poésie',
            'histoire', 'story', 'récit', 'narrative', 'classique', 'classic',
            'genre', 'style', 'oeuvre', 'work', 'masterpiece', 'chef-d\'oeuvre',
            'comme', 'similaire', 'similar', 'aimé', 'recommandation', 'films'
        ]
        
        # Noms d'auteurs connus
        known_authors = [
            'tolstoy', 'tolstoï', 'stephen king', 'murakami', 'shakespeare',
            'hugo', 'camus', 'sartre', 'proust', 'zola', 'balzac', 'dickens',
            'hemingway', 'orwell', 'kafka', 'dostoyevsky', 'chekhov'
        ]
        
        # Score pour déterminer le type
        tech_score = sum(1 for keyword in tech_keywords if keyword in query_lower)
        lit_score = sum(1 for keyword in lit_keywords if keyword in query_lower)
        author_score = sum(1 for author in known_authors if author in query_lower)
        
        # Si auteur détecté, c'est littéraire
        if author_score > 0:
            return self.get_literature_recommendations(query)
        
        # Sinon, utiliser les scores
        if tech_score > lit_score:
            return self.get_tech_recommendations(query)
        elif lit_score > 0:
            return self.get_literature_recommendations(query)
        else:
            # Par défaut, essayer les deux et retourner le meilleur
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
        """Génère des recommandations techniques avec nombre dynamique"""
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
            logger.error(f"Erreur dans get_tech_recommendations: {e}")
            return "🔧 Désolé, j'ai rencontré un problème technique. Essayez de préciser votre domaine d'intérêt (Python, JavaScript, etc.)."
    
    def get_literature_recommendations(self, query: str, user_id: int = 1) -> str:
        """Point d'entrée principal - utilise l'agent intelligent"""
        return self.get_literature_recommendations_intelligent(query, user_id)
    
    def get_literature_recommendations_intelligent(self, query: str, user_id: int = 1) -> str:
        """Version intelligente qui comprend les requêtes complexes"""
        try:
            import re
            from apps.books.models import LiteratureBook
            
            start_time = time.time()
            query_lower = query.lower()
            logger.info(f"📚 Literature intelligent called with: '{query}'")
            
            # Analyser la requête
            analysis = self._analyze_literature_query(query_lower)
            logger.info(f"📊 Analyse de la requête '{query}': {analysis}")
            
            if analysis['type'] == 'similarity_request':
                # Demande de recommandations similaires (ex: "10 films comme Harry Potter")
                books = self._get_books_similar_to(analysis['reference'], analysis['count'])
                if books:
                    response = f"📚 **{analysis['count']} livres comme {analysis['reference'].title()}**\n\n"
                    
                    for i, book in enumerate(books, 1):
                        response += f"{i}. **{book.title}** de {book.authors}\n"
                        if book.average_rating:
                            response += f"   ⭐ Note: {book.average_rating}/5"
                        if book.published_year:
                            response += f" | 📅 {book.published_year}"
                        response += "\n"
                        if book.description:
                            desc = book.description[:100] + "..." if len(book.description) > 100 else book.description
                            response += f"   📖 {desc}\n"
                        response += "\n"
                    
                    processing_time = time.time() - start_time
                    response += f"⚡ Recherche en {processing_time:.1f}s"
                    return response
                else:
                    return f"💔 Désolé, je n'ai pas trouvé de livres similaires à {analysis['reference']} dans ma base"
            
            elif analysis['type'] == 'list_request':
                # Demande de liste (ex: "10 livres de fantasy")
                books = self._get_books_by_genre(analysis['genre'], analysis['count'])
                if books:
                    response = f"📚 **{analysis['count']} Livres {analysis['genre'].title()}**\n\n"
                    
                    for i, book in enumerate(books, 1):
                        response += f"{i}. **{book.title}** de {book.authors}\n"
                        if book.average_rating:
                            response += f"   ⭐ Note: {book.average_rating}/5"
                        if book.published_year:
                            response += f" | 📅 {book.published_year}"
                        response += "\n"
                        if book.description:
                            desc = book.description[:100] + "..." if len(book.description) > 100 else book.description
                            response += f"   📖 {desc}\n"
                        response += "\n"
                    
                    processing_time = time.time() - start_time
                    response += f"⚡ Recherche en {processing_time:.1f}s"
                    return response
                else:
                    return f"💔 Désolé, je n'ai pas trouvé de livres {analysis['genre']} dans ma base"
            
            elif analysis['type'] == 'author_works':
                # Demande d'œuvres d'auteur
                books = self._get_books_by_author(analysis['author'])
                if books:
                    response = f"📚 **Œuvres de {analysis['author'].title()}**\n\n"
                    
                    for i, book in enumerate(books[:10], 1):
                        response += f"{i}. **{book.title}**\n"
                        if book.average_rating:
                            response += f"   ⭐ Note: {book.average_rating}/5"
                        if book.published_year:
                            response += f" | 📅 {book.published_year}"
                        response += "\n\n"
                    
                    processing_time = time.time() - start_time
                    response += f"⚡ Recherche en {processing_time:.1f}s"
                    return response
                else:
                    return f"💔 Aucune œuvre de {analysis['author'].title()} trouvée dans ma base"
            
            else:
                # Requête générale - utiliser le RAG original
                return self._get_literature_recommendations_original(query, user_id)
        
        except Exception as e:
            logger.error(f"Erreur agent intelligent: {e}")
            return self._get_literature_recommendations_original(query, user_id)
    
    def _analyze_literature_query(self, query_lower: str) -> dict:
        """Analyse intelligente des requêtes littéraires"""
        import re
        
        analysis = {
            'type': 'general',
            'genre': None,
            'author': None,
            'count': 10,
            'reference': None
        }
        
        # Détecter les demandes de recommandations similaires
        similarity_patterns = [
            r'(?:donne.{0,20}moi|liste.{0,10}|trouve.{0,10})?\s*(\d+)\s+(?:livres?|films?|oeuvres?)\s+comme\s+(.+)',
            r'(\d+)\s+(?:livres?|films?|oeuvres?)\s+similaires?\s+(?:à|au)\s+(.+)',
            r'(?:livres?|films?|oeuvres?)\s+comme\s+(.+)',
            r'similaires?\s+(?:à|au)\s+(.+)',
            r'j[\'\s]*ai\s+(?:bien\s+)?aimé\s+([^,]+),?\s+(?:donne|recommande).{0,20}moi\s+(?:(\d+|un|deux|trois|quatre|cinq|six|sept|huit|neuf|dix|onze|douze|treize|quatorze|quinze|seize|dix-sept|dix-huit|dix-neuf|vingt)\s+)?(?:livres?|films?|oeuvres?)',
            r'(?:donne|recommande).{0,20}moi\s+(?:(\d+|un|deux|trois|quatre|cinq|six|sept|huit|neuf|dix|onze|douze|treize|quatorze|quinze|seize|dix-sept|dix-huit|dix-neuf|vingt)\s+)?(?:livres?|films?|oeuvres?)',
        ]
        
        for pattern in similarity_patterns:
            match = re.search(pattern, query_lower)
            if match:
                analysis['type'] = 'similarity_request'
                groups = match.groups()
                
                # Gérer les différents ordres de groupes
                if len(groups) >= 2:
                    # Trouver le nombre et la référence
                    count_found = False
                    for group in groups:
                        if group and group.isdigit():
                            analysis['count'] = min(int(group), 20)  # Max 20 livres
                            count_found = True
                        elif group and self._is_french_number(group):
                            analysis['count'] = min(self._convert_french_number(group), 20)
                            count_found = True
                        elif group and not group.isdigit() and not self._is_french_number(group):
                            analysis['reference'] = group.strip()
                    
                    # Si pas de nombre trouvé, utiliser la valeur par défaut
                    if not count_found:
                        analysis['count'] = 10
                        
                elif len(groups) == 1:
                    analysis['reference'] = groups[0].strip()
                
                # Nettoyer la référence
                if analysis['reference']:
                    # Enlever les mots de liaison et la ponctuation
                    analysis['reference'] = analysis['reference'].replace(',', '').strip()
                
                break
        
        # Détecter les demandes de listes par genre
        list_patterns = [
            r'(?:donne.{0,20}moi|liste.{0,10}|trouve.{0,10})?\s*(\d+)\s+livres?\s+de\s+(\w+)',
            r'(\d+)\s+livres?\s+de\s+(\w+)',
            r'livres?\s+de\s+(fantasy|science fiction|romance|thriller|horror|mystery)',
        ]
        
        if analysis['type'] == 'general':  # Only check if not already similarity
            for pattern in list_patterns:
                match = re.search(pattern, query_lower)
                if match:
                    analysis['type'] = 'list_request'
                    groups = match.groups()
                    if len(groups) >= 2 and groups[0].isdigit():
                        analysis['count'] = min(int(groups[0]), 20)  # Max 20 livres
                        analysis['genre'] = groups[1]
                    elif len(groups) == 1:
                        analysis['genre'] = groups[0]
                    break
        
        # Mapping des genres français vers anglais
        genre_mapping = {
            'fantasy': 'Fantasy',
            'fantastique': 'Fantasy',
            'science fiction': 'Science Fiction',
            'sci-fi': 'Science Fiction',
            'romance': 'Romance',
            'thriller': 'Thriller',
            'horreur': 'Horror',
            'horror': 'Horror',
            'mystery': 'Mystery',
            'policier': 'Mystery',
            'young adult': 'Young Adult',
            'ado': 'Young Adult',
            'classique': 'Classics',
            'historic': 'Historical Fiction',
            'historique': 'Historical Fiction',
        }
        
        if analysis['genre'] and analysis['genre'] in genre_mapping:
            analysis['genre'] = genre_mapping[analysis['genre']]
        
        # Détecter les demandes d'auteur - SEULEMENT si pas déjà une requête de similarité
        if analysis['type'] == 'general':
            author_patterns = [
                r'(?:livres?|oeuvres?|romans?)\s+de\s+([a-zA-Z\s]+?)(?:\s|$)',
                r'([a-zA-Z\s]+?)\s+(?:livres?|oeuvres?|romans?)',
            ]
            
            for pattern in author_patterns:
                match = re.search(pattern, query_lower)
                if match:
                    author = match.group(1).strip()
                    # Vérifier que ce n'est pas un genre ou des mots de demande
                    excluded_words = [
                        'fantasy', 'science fiction', 'romance', 'thriller', 'horror',
                        'recommande moi', 'donne moi', 'trouve moi', 'deux', 'trois', 'quatre'
                    ]
                    if not any(excluded in author.lower() for excluded in excluded_words):
                        analysis['type'] = 'author_works'
                        analysis['author'] = author
                        break
        
        return analysis
    
    def _is_french_number(self, text: str) -> bool:
        """Vérifie si le texte est un nombre en français"""
        if not text:
            return False
        french_numbers = [
            'un', 'deux', 'trois', 'quatre', 'cinq', 'six', 'sept', 'huit', 'neuf', 'dix',
            'onze', 'douze', 'treize', 'quatorze', 'quinze', 'seize', 'dix-sept', 'dix-huit', 'dix-neuf', 'vingt'
        ]
        return text.lower().strip() in french_numbers
    
    def _convert_french_number(self, text: str) -> int:
        """Convertit un nombre français en entier"""
        if not text:
            return 10
        
        french_to_int = {
            'un': 1, 'deux': 2, 'trois': 3, 'quatre': 4, 'cinq': 5,
            'six': 6, 'sept': 7, 'huit': 8, 'neuf': 9, 'dix': 10,
            'onze': 11, 'douze': 12, 'treize': 13, 'quatorze': 14, 'quinze': 15,
            'seize': 16, 'dix-sept': 17, 'dix-huit': 18, 'dix-neuf': 19, 'vingt': 20
        }
        
        return french_to_int.get(text.lower().strip(), 10)
    
    def _get_books_by_genre(self, genre: str, count: int = 10):
        """Récupère des livres par genre"""
        from apps.books.models import LiteratureBook
        
        if not genre:
            return []
        
        # Recherche par catégories
        books = list(LiteratureBook.objects.filter(
            categories__icontains=genre
        ).order_by('-average_rating')[:count * 2])
        
        if not books:
            # Recherche par description
            books = list(LiteratureBook.objects.filter(
                description__icontains=genre.lower()
            ).order_by('-average_rating')[:count * 2])
        
        # Filtrer les livres bien notés
        good_books = [book for book in books if book.average_rating and book.average_rating >= 3.5]
        
        if len(good_books) >= count:
            return good_books[:count]
        else:
            return books[:count]
    
    def _get_books_by_author(self, author: str):
        """Récupère des livres par auteur"""
        from apps.books.models import LiteratureBook
        
        if not author:
            return []
        
        return list(LiteratureBook.objects.filter(
            authors__icontains=author
        ).order_by('-average_rating')[:15])
    
    def _get_books_similar_to(self, reference: str, count: int = 10):
        """Récupère des livres similaires à une référence en utilisant le RAG"""
        from apps.books.models import LiteratureBook
        
        if not reference:
            return []
        
        try:
            # D'abord essayer de trouver le livre de référence dans la base
            reference_book = None
            reference_lower = reference.lower()
            
            # Chercher par titre exact ou partiel
            possible_books = LiteratureBook.objects.filter(
                title__icontains=reference
            )[:5]  # Prendre les 5 premiers matches
            
            for book in possible_books:
                if reference_lower in book.title.lower():
                    reference_book = book
                    break
            
            if reference_book:
                # Utiliser les catégories et description du livre de référence
                search_query = f"{reference_book.categories} {reference_book.description[:200]}"
                logger.info(f"Livre de référence trouvé: {reference_book.title}")
            else:
                # Utiliser la référence directement pour la recherche RAG
                search_query = f"{reference} similar books like"
                logger.info(f"Livre de référence non trouvé, utilisation directe: {reference}")
            
            # Utiliser le RAG pour trouver des livres similaires
            if self.literature_rag:
                recommendations = self.literature_rag.get_book_recommendations(
                    user_id=1,
                    query=search_query,
                    n_recommendations=count
                )
                
                if recommendations:
                    # Convertir les recommandations RAG en objets LiteratureBook
                    similar_books = []
                    for rec in recommendations:
                        book_data = rec['book']
                        try:
                            # Chercher le livre dans la base par titre
                            book_obj = LiteratureBook.objects.filter(
                                title__icontains=book_data['title']
                            ).first()
                            if book_obj:
                                similar_books.append(book_obj)
                        except Exception as e:
                            logger.warning(f"Erreur conversion livre RAG: {e}")
                            continue
                    
                    if similar_books:
                        return similar_books[:count]
            
            # Fallback: recherche par mots-clés si le RAG ne fonctionne pas
            return self._get_books_by_keywords_fallback(reference, count)
            
        except Exception as e:
            logger.error(f"Erreur dans _get_books_similar_to: {e}")
            return self._get_books_by_keywords_fallback(reference, count)
    
    def _get_books_by_keywords_fallback(self, reference: str, count: int = 10):
        """Méthode de fallback pour trouver des livres similaires"""
        from apps.books.models import LiteratureBook
        
        # Mappings pour les références populaires (livres + mangas/anime)
        reference_mappings = {
            # Livres classiques
            'harry potter': ['fantasy', 'magic', 'adventure', 'young adult', 'wizard', 'school'],
            'lord of the rings': ['fantasy', 'adventure', 'epic', 'tolkien', 'middle earth'],
            'game of thrones': ['fantasy', 'epic', 'political', 'dark fantasy', 'medieval'],
            'twilight': ['romance', 'vampire', 'young adult', 'paranormal'],
            'hunger games': ['dystopian', 'young adult', 'survival', 'adventure'],
            'sherlock holmes': ['mystery', 'detective', 'crime', 'victorian', 'investigation'],
            'agatha christie': ['mystery', 'detective', 'crime', 'murder', 'investigation'],
            'stephen king': ['horror', 'thriller', 'supernatural', 'suspense'],
            
            # Mangas/Anime populaires
            'naruto': ['adventure', 'action', 'martial arts', 'friendship', 'ninja', 'coming of age'],
            'one piece': ['adventure', 'friendship', 'pirates', 'action', 'comedy', 'treasure'],
            'dragon ball': ['martial arts', 'adventure', 'action', 'tournament', 'power'],
            'attack on titan': ['dark', 'action', 'military', 'survival', 'dystopian'],
            'death note': ['psychological', 'thriller', 'supernatural', 'mystery', 'crime'],
            'fullmetal alchemist': ['adventure', 'military', 'alchemy', 'brotherhood', 'philosophy'],
            'bleach': ['supernatural', 'action', 'spirits', 'sword fighting', 'afterlife'],
            'my hero academia': ['superhero', 'school', 'coming of age', 'action', 'friendship'],
            'demon slayer': ['action', 'supernatural', 'family', 'revenge', 'martial arts'],
            'tokyo ghoul': ['dark', 'supernatural', 'horror', 'transformation', 'identity'],
            'cowboy bebop': ['space', 'bounty hunters', 'jazz', 'noir', 'action'],
            'spirited away': ['fantasy', 'coming of age', 'magic', 'adventure', 'spirits'],
            'princess mononoke': ['fantasy', 'nature', 'conflict', 'spirituality', 'adventure'],
        }
        
        # Chercher des mots-clés pour cette référence
        keywords = []
        reference_lower = reference.lower()
        
        for ref_key, ref_keywords in reference_mappings.items():
            if ref_key in reference_lower:
                keywords.extend(ref_keywords)
                break
        
        # Si pas de mapping spécifique, utiliser des mots-clés génériques
        if not keywords:
            keywords = [reference.lower(), 'fantasy', 'adventure', 'fiction']
        
        # Rechercher des livres avec ces mots-clés
        books = []
        for keyword in keywords:
            # Recherche dans les catégories
            category_books = list(LiteratureBook.objects.filter(
                categories__icontains=keyword
            ).order_by('-average_rating')[:count * 2])
            
            # Recherche dans les descriptions
            desc_books = list(LiteratureBook.objects.filter(
                description__icontains=keyword
            ).order_by('-average_rating')[:count * 2])
            
            books.extend(category_books + desc_books)
        
        # Éliminer les doublons et trier par note
        seen_titles = set()
        unique_books = []
        for book in books:
            if book.title not in seen_titles and book.average_rating and book.average_rating >= 3.5:
                seen_titles.add(book.title)
                unique_books.append(book)
        
        # Trier par note décroissante
        unique_books.sort(key=lambda b: b.average_rating or 0, reverse=True)
        
        return unique_books[:count]
    
    def _get_literature_recommendations_original(self, query: str, user_id: int = 1) -> str:
        """Version originale pour les requêtes générales"""
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
            
            processing_time = time.time() - start_time
            
            if recommendations:
                response = "📚 **Recommandations Littéraires**\n\n"
                
                for i, rec in enumerate(recommendations, 1):
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
            logger.error(f"Erreur dans RAG original: {e}")
            return "📚 Désolé, j'ai rencontré un problème."
    
    def _generate_tech_fallback(self, query: str) -> str:
        """Génère une réponse de fallback pour les requêtes techniques"""
        _ = query  # Unused parameter
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
        _ = query  # Unused parameter
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
    
    def get_agent_response(self, query: str, agent_type: str = "router") -> str:
        """Interface unifiée pour obtenir une réponse d'agent"""
        try:
            if agent_type == "router":
                return self.route_query(query)
            elif agent_type == "tech":
                return self.get_tech_recommendations(query)
            elif agent_type == "literature":
                return self.get_literature_recommendations(query)
            else:
                return "🤖 Type d'agent non reconnu. Utilisez: 'router', 'tech', ou 'literature'"
                
        except Exception as e:
            logger.error(f"Erreur dans get_agent_response: {e}")
            return f"🤖 Erreur: {str(e)}"