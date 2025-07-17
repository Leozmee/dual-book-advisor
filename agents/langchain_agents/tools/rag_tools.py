"""
RAG Tools - Interface LangChain avec vos systèmes RAG existants
Fichier: agents/langchain_agents/tools/rag_tools.py
"""
from typing import List, Dict, Any, Optional
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
import logging
import wikipedia

logger = logging.getLogger(__name__)

# Modèles Pydantic pour les entrées des outils
class BookSearchInput(BaseModel):
    """Input schema pour la recherche de livres"""
    query: str = Field(description="Requête de recherche")
    n_results: int = Field(description="Nombre de résultats souhaités", default=3)
    user_id: int = Field(description="ID de l'utilisateur", default=1)

class ContentSearchInput(BaseModel):
    """Input schema pour la recherche de contenu manga/comics"""
    query: str = Field(description="Requête de recherche")
    n_results: int = Field(description="Nombre de résultats souhaités", default=3)
    content_type: str = Field(description="Type de contenu: 'manga', 'comics', ou 'all'", default="all")
    user_id: int = Field(description="ID de l'utilisateur", default=1)

class WikipediaSearchInput(BaseModel):
    """Input schema pour la recherche Wikipedia"""
    query: str = Field(description="Terme à rechercher sur Wikipedia (auteur, titre d'œuvre, etc.)")
    language: str = Field(description="Langue de recherche: 'fr' ou 'en'", default="fr")

class TechBookSearchTool(BaseTool):
    """Outil de recherche dans les livres techniques"""
    
    name: str = "tech_book_search"
    description: str = """
    Recherche des livres techniques basée sur une requête.
    Utilise le système RAG technique existant pour trouver des livres de programmation,
    data science, développement web, etc.
    """
    args_schema: type[BaseModel] = BookSearchInput
    
    def _run(self, query: str, n_results: int = 3, user_id: int = 1) -> List[Dict[str, Any]]:
        """Execute la recherche technique"""
        try:
            # Import dynamique pour éviter les dépendances circulaires
            from rags.tech_rag.tech_rag_manager import TechRAGManager
            
            tech_rag = TechRAGManager()
            
            # Obtenir des recommandations
            recommendations = tech_rag.get_book_recommendations(
                user_id=user_id,
                query=query,
                n_recommendations=n_results
            )
            
            # Formater pour LangChain
            formatted_results = []
            for rec in recommendations:
                book = rec['book']
                formatted_results.append({
                    'id': book['id'],
                    'title': book['title'],
                    'author': book['author'],
                    'description': book['description'],
                    'rating': book['rating'],
                    'price': book['price'],
                    'difficulty_level': book['difficulty_level'],
                    'similarity_score': rec['similarity_score'],
                    'reason': rec['reason'],
                    'type': 'tech_book'
                })
            
            logger.info(f"Tech search: '{query}' → {len(formatted_results)} résultats")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Erreur recherche tech: {e}")
            return []
    
    def _arun(self, query: str, n_results: int = 3, user_id: int = 1):
        """Version asynchrone (non implémentée pour l'instant)"""
        raise NotImplementedError("Async version not implemented")

class LiteratureBookSearchTool(BaseTool):
    """Outil de recherche dans la littérature (sans manga)"""
    
    name: str = "literature_book_search"
    description: str = """
    Recherche des livres littéraires basée sur une requête.
    Utilise le système RAG littéraire pour trouver romans, classiques, fiction.
    EXCLUT automatiquement les mangas et comics.
    """
    args_schema: type[BaseModel] = BookSearchInput
    
    def _run(self, query: str, n_results: int = 3, user_id: int = 1) -> List[Dict[str, Any]]:
        """Execute la recherche littéraire"""
        try:
            from rags.literature_rag.literature_rag_manager import LiteratureRAGManager
            
            lit_rag = LiteratureRAGManager()
            
            # Détecter d'abord si c'est une recherche de titre d'œuvre (priorité)
            title_search = self._detect_title_search(query)
            # Puis détecter si c'est une recherche d'auteur spécifique
            author_name = self._detect_author_search(query) if not title_search else None
            
            if title_search:
                # Recherche par titre avec fallback Wikipedia
                recommendations = self._search_by_title(title_search, n_results, user_id)
            elif author_name:
                # Recherche directe par auteur dans la base de données
                recommendations = self._search_by_author(author_name, n_results, user_id)
            else:
                # Recherche RAG normale
                recommendations = lit_rag.get_book_recommendations(
                    user_id=user_id,
                    query=query,
                    n_recommendations=n_results
                )
            
            # Filtrer les mangas/comics (logique de votre système)
            filtered_recommendations = self._filter_out_manga_comics(recommendations)
            
            # Formater pour LangChain
            formatted_results = []
            for rec in filtered_recommendations:
                book = rec['book']
                formatted_results.append({
                    'id': book['id'],
                    'title': book['title'],
                    'authors': book['authors'],
                    'description': book['description'],
                    'average_rating': book['average_rating'],
                    'published_year': book.get('published_year'),
                    'categories': book.get('categories'),
                    'similarity_score': rec['similarity_score'],
                    'reason': rec['reason'],
                    'type': 'literature_book'
                })
            
            logger.info(f"Literature search: '{query}' → {len(formatted_results)} résultats")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Erreur recherche littérature: {e}")
            return []
    
    def _filter_out_manga_comics(self, recommendations: List[Dict]) -> List[Dict]:
        """Filtre les mangas/comics (logique de votre système actuel)"""
        if not recommendations:
            return recommendations
        
        filtered = []
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
            
            # Vérifier si c'est un manga/comics
            is_manga_comics = any(keyword in title_lower or keyword in desc_lower or 
                                keyword in categories_lower or keyword in authors_lower
                                for keyword in exclusion_keywords)
            
            if not is_manga_comics:
                filtered.append(rec)
        
        logger.info(f"Filtrage manga/comics: {len(recommendations)} → {len(filtered)} livres littéraires")
        return filtered
    
    def _detect_author_search(self, query: str) -> str:
        """Détecte si la requête concerne une recherche d'auteur"""
        import re
        
        query_lower = query.lower().strip()
        
        # Patterns de recherche d'auteur avec groupes de capture
        author_patterns = [
            # Patterns explicites avec mots-clés
            r'(?:œuvres?|romans?|livres?|books?)\s+(?:de|d\'|par|by)\s+([a-zA-ZÀ-ÿ\s\-\'\.]+)',
            r'recommande.*(?:de|d\'|par|by)\s+([a-zA-ZÀ-ÿ\s\-\'\.]+)',
            r'(?:donne|donnez)\s+(?:moi|nous)\s+(?:des|les)\s+(?:œuvres?|romans?|livres?)\s+(?:de|d\'|par)\s+([a-zA-ZÀ-ÿ\s\-\'\.]+)',
            r'auteur\s+([a-zA-ZÀ-ÿ\s\-\'\.]+)',
            r'écrivain\s+([a-zA-ZÀ-ÿ\s\-\'\.]+)',
            r'écrit\s+par\s+([a-zA-ZÀ-ÿ\s\-\'\.]+)',
            r'written\s+by\s+([a-zA-ZÀ-ÿ\s\-\'\.]+)',
            
            # Patterns pour noms complets (prénom + nom) - mais pas les phrases avec mots-clés
            r'^([a-zA-ZÀ-ÿ]+\s+[a-zA-ZÀ-ÿ]+(?:\s+[a-zA-ZÀ-ÿ]+)*)\s*$',
            
            # Patterns pour noms avec particules
            r'^([a-zA-ZÀ-ÿ]+\s+(?:de|du|van|von|da|di)\s+[a-zA-ZÀ-ÿ]+)\s*$',
        ]
        
        for pattern in author_patterns:
            match = re.search(pattern, query_lower)
            if match:
                author_name = match.group(1).strip()
                # Vérifier que le nom fait au moins 3 caractères et contient des lettres
                if len(author_name) >= 3 and re.search(r'[a-zA-ZÀ-ÿ]', author_name):
                    # Exclure les phrases qui contiennent des mots-clés de recherche de titre
                    excluded_words = ['qui', 'a', 'écrit', 'wrote', 'written', 'est', 'what', 'comment', 'pourquoi', 'when', 'where', 'how']
                    if not any(word in author_name.lower() for word in excluded_words):
                        return author_name
        
        return None
    
    def _detect_title_search(self, query: str) -> str:
        """Détecte si la requête concerne une recherche de titre d'œuvre"""
        import re
        
        query_lower = query.lower().strip()
        
        # Patterns de recherche de titre
        title_patterns = [
            # "qui a écrit X" - extraire le titre X
            r'qui\s+a\s+écrit\s+["\']?([^"\']+)["\']?',
            r'qui\s+a\s+écrit\s+(.+)',
            
            # "auteur de X" - extraire le titre X
            r'auteur\s+de\s+["\']?([^"\']+)["\']?',
            r'who\s+wrote\s+["\']?([^"\']+)["\']?',
            r'author\s+of\s+["\']?([^"\']+)["\']?',
            
            # Patterns avec guillemets ou références explicites
            r'livre\s+["\']([^"\']+)["\']',
            r'roman\s+["\']([^"\']+)["\']',
            r'œuvre\s+["\']([^"\']+)["\']',
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, query_lower)
            if match:
                title = match.group(1).strip()
                # Nettoyer le titre
                title = re.sub(r'\s+', ' ', title)  # Normaliser les espaces
                title = title.strip('.,!?;:')  # Supprimer la ponctuation finale
                
                # Vérifier que le titre fait au moins 3 caractères et contient des lettres
                if len(title) >= 3 and re.search(r'[a-zA-ZÀ-ÿ]', title):
                    return title
        
        return None
    
    def _search_by_author(self, author_name: str, n_results: int, user_id: int) -> List[Dict]:
        """Recherche directe par auteur dans la base de données"""
        try:
            from apps.books.models import LiteratureBook
            
            # Recherche flexible par auteur
            books = LiteratureBook.objects.filter(
                authors__icontains=author_name
            ).order_by('-average_rating', '-published_year')[:n_results]
            
            # Convertir en format RAG
            recommendations = []
            for book in books:
                recommendations.append({
                    'book': {
                        'id': book.id,
                        'title': book.title,
                        'authors': book.authors,
                        'description': book.description or '',
                        'average_rating': float(book.average_rating) if book.average_rating else 0.0,
                        'published_year': book.published_year,
                        'categories': book.categories or '',
                        'thumbnail': book.thumbnail or ''
                    },
                    'similarity_score': 0.9,  # Score élevé pour match direct d'auteur
                    'reason': f'Livre de {author_name}'
                })
            
            logger.info(f"Recherche directe auteur '{author_name}': {len(recommendations)} livres trouvés")
            return recommendations
            
        except Exception as e:
            logger.error(f"Erreur recherche auteur '{author_name}': {e}")
            return []
    
    def _search_by_title(self, title: str, n_results: int, user_id: int) -> List[Dict]:
        """Recherche par titre avec fallback Wikipedia pour trouver l'auteur"""
        try:
            from apps.books.models import LiteratureBook
            from rags.literature_rag.literature_rag_manager import LiteratureRAGManager
            
            # Étape 1: Recherche directe par titre dans la base de données
            books = LiteratureBook.objects.filter(
                title__icontains=title
            ).order_by('-average_rating', '-published_year')[:n_results]
            
            if books:
                # Convertir en format RAG
                recommendations = []
                for book in books:
                    recommendations.append({
                        'book': {
                            'id': book.id,
                            'title': book.title,
                            'authors': book.authors,
                            'description': book.description or '',
                            'average_rating': float(book.average_rating) if book.average_rating else 0.0,
                            'published_year': book.published_year,
                            'categories': book.categories or '',
                            'thumbnail': book.thumbnail or ''
                        },
                        'similarity_score': 0.95,  # Score très élevé pour match direct de titre
                        'reason': f'Correspondance exacte du titre "{title}"'
                    })
                
                logger.info(f"Recherche directe titre '{title}': {len(recommendations)} livres trouvés")
                
                # Filtrer les mangas/comics AVANT de retourner
                filtered_recommendations = self._filter_out_manga_comics(recommendations)
                
                # Si après filtrage il reste des livres, les retourner
                if filtered_recommendations:
                    logger.info(f"Après filtrage: {len(filtered_recommendations)} livres valides")
                    return filtered_recommendations
                else:
                    logger.info(f"Tous les livres filtrés comme manga/comics, passage à Wikipedia")
                    # Continuer vers l'étape Wikipedia
            
            # Étape 2: Utiliser Wikipedia pour trouver l'auteur
            logger.info(f"Aucun résultat direct pour '{title}', utilisation de Wikipedia")
            wikipedia_tool = WikipediaSearchTool()
            
            # Stratégie multi-recherche Wikipedia
            search_queries = [
                title,  # Recherche directe du titre
                f"{title} roman",  # Titre + "roman"
                f"{title} livre",  # Titre + "livre"
                f"{title} auteur",  # Titre + "auteur"
            ]
            
            author_from_wiki = None
            successful_query = None
            
            for query in search_queries:
                try:
                    logger.info(f"Tentative Wikipedia avec: '{query}'")
                    wiki_result = wikipedia_tool._run(query, language="fr")
                    
                    if wiki_result.get('success'):
                        logger.info(f"Wikipedia succès pour '{query}': {wiki_result.get('title')}")
                        
                        # Essayer d'extraire l'auteur
                        author_from_wiki = self._extract_author_from_wikipedia(wiki_result)
                        
                        if author_from_wiki:
                            successful_query = query
                            logger.info(f"Auteur trouvé: {author_from_wiki}")
                            break
                        else:
                            logger.info(f"Aucun auteur extrait de '{query}'")
                    else:
                        logger.info(f"Wikipedia échec pour '{query}': {wiki_result.get('message', 'Unknown error')}")
                        
                except Exception as e:
                    logger.error(f"Erreur Wikipedia pour '{query}': {e}")
                    continue
            
            # Si un auteur a été trouvé, rechercher ses livres
            if author_from_wiki:
                logger.info(f"Auteur trouvé sur Wikipedia: {author_from_wiki}")
                # Rechercher les livres de cet auteur
                author_books = self._search_by_author(author_from_wiki, n_results, user_id)
                
                if author_books:
                    # Modifier la raison pour indiquer l'origine Wikipedia
                    for book in author_books:
                        book['reason'] = f'Auteur de "{title}" trouvé sur Wikipedia via "{successful_query}": {author_from_wiki}'
                    return author_books
                
                # Si pas d'auteur extrait, essayer la recherche en anglais
                if wiki_result.get('other_languages'):
                    english_title = self._find_english_title(wiki_result)
                    if english_title and english_title != title:
                        logger.info(f"Titre anglais trouvé: {english_title}")
                        # Rechercher avec le titre anglais
                        english_books = LiteratureBook.objects.filter(
                            title__icontains=english_title
                        ).order_by('-average_rating', '-published_year')[:n_results]
                        
                        if english_books:
                            recommendations = []
                            for book in english_books:
                                recommendations.append({
                                    'book': {
                                        'id': book.id,
                                        'title': book.title,
                                        'authors': book.authors,
                                        'description': book.description or '',
                                        'average_rating': float(book.average_rating) if book.average_rating else 0.0,
                                        'published_year': book.published_year,
                                        'categories': book.categories or '',
                                        'thumbnail': book.thumbnail or ''
                                    },
                                    'similarity_score': 0.9,
                                    'reason': f'Correspondance titre anglais "{english_title}" pour "{title}"'
                                })
                            
                            logger.info(f"Recherche titre anglais '{english_title}': {len(recommendations)} livres trouvés")
                            return recommendations
            
            # Étape 3: Fallback vers recherche RAG normale
            logger.info(f"Fallback vers recherche RAG pour '{title}'")
            lit_rag = LiteratureRAGManager()
            recommendations = lit_rag.get_book_recommendations(
                user_id=user_id,
                query=title,
                n_recommendations=n_results
            )
            
            # Modifier la raison pour indiquer que c'est un fallback
            for rec in recommendations:
                rec['reason'] = f'Recherche sémantique pour "{title}"'
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Erreur recherche titre '{title}': {e}")
            return []
    
    def _extract_author_from_wikipedia(self, wiki_result: Dict) -> str:
        """Extrait l'auteur depuis un résultat Wikipedia"""
        try:
            import re
            
            summary = wiki_result.get('summary', '')
            # Note: variable 'title' non utilisée, supprimée pour éviter les warnings
            
            # Patterns pour extraire l'auteur
            author_patterns = [
                r'(?:roman|livre|œuvre|novel|book)\s+(?:de|d\'|par|by)\s+([A-ZÀ-Ÿ][a-zA-ZÀ-ÿ\s\-\'\.]+)',
                r'(?:écrit|écrite|written)\s+par\s+([A-ZÀ-Ÿ][a-zA-ZÀ-ÿ\s\-\'\.]+)',
                r'([A-ZÀ-Ÿ][a-zA-ZÀ-ÿ\s\-\'\.]+)\s+(?:est|is)\s+(?:un|une|a|an)\s+(?:écrivain|auteur|novelist|writer)',
                r'L\'auteur\s+([A-ZÀ-Ÿ][a-zA-ZÀ-ÿ\s\-\'\.]+)',
                r'([A-ZÀ-Ÿ][a-zA-ZÀ-ÿ]{2,}\s+[A-ZÀ-Ÿ][a-zA-ZÀ-ÿ]{2,}(?:\s+[A-ZÀ-Ÿ][a-zA-ZÀ-ÿ]{2,})*)',  # Nom prénom
            ]
            
            for pattern in author_patterns:
                match = re.search(pattern, summary)
                if match:
                    author = match.group(1).strip()
                    # Nettoyer l'auteur
                    author = re.sub(r'\s+', ' ', author)
                    author = author.strip('.,!?;:()[]{}')
                    
                    # Vérifier que c'est un nom valide
                    if len(author) >= 3 and ' ' in author and not any(word in author.lower() for word in ['est', 'est', 'qui', 'que', 'cette', 'cette']):
                        return author
            
            return None
            
        except Exception as e:
            logger.error(f"Erreur extraction auteur Wikipedia: {e}")
            return None
    
    def _find_english_title(self, wiki_result: Dict) -> str:
        """Trouve le titre anglais depuis un résultat Wikipedia"""
        try:
            # Méthode simple - peut être améliorée
            other_languages = wiki_result.get('other_languages', {})
            
            # Chercher dans les langues alternatives
            for lang, title in other_languages.items():
                if 'english' in lang.lower() or 'en' in lang.lower():
                    return title
            
            # Si pas trouvé, essayer une recherche Wikipedia en anglais
            title = wiki_result.get('title', '')
            if title:
                wikipedia_tool = WikipediaSearchTool()
                english_result = wikipedia_tool._run(title, language="en")
                
                if english_result.get('success'):
                    return english_result.get('title', '')
            
            return None
            
        except Exception as e:
            logger.error(f"Erreur recherche titre anglais: {e}")
            return None
    
    def _arun(self, query: str, n_results: int = 3, user_id: int = 1):
        """Version asynchrone (non implémentée pour l'instant)"""
        raise NotImplementedError("Async version not implemented")

class MangaContentSearchTool(BaseTool):
    """Outil de recherche dans les mangas et comics"""
    
    name: str = "manga_content_search"
    description: str = """
    Recherche des mangas, anime et comics/BD basée sur une requête.
    Utilise le système RAG manga unifié pour trouver du contenu japonais et occidental.
    """
    args_schema: type[BaseModel] = ContentSearchInput
    
    def _run(self, query: str, n_results: int = 3, content_type: str = "all", user_id: int = 1) -> List[Dict[str, Any]]:
        """Execute la recherche manga/comics"""
        try:
            from rags.manga_rag.manga_rag_manager import MangaRAGManager
            
            manga_rag = MangaRAGManager()
            
            # Utiliser la nouvelle méthode search_content avec détection d'auteur
            search_results = manga_rag.search_content(
                query=query,
                n_results=n_results,
                content_type=content_type
            )
            
            # Formater et filtrer les résultats
            formatted_results = []
            for result in search_results:
                # Filtrer les résultats avec un score de similarité très faible
                similarity_score = result.get('similarity_score', 0)
                if similarity_score < 0.3:  # Seuil minimum de pertinence
                    continue
                    
                formatted_results.append({
                    'id': result.get('doc_id', ''),
                    'title': result.get('title', ''),
                    'description': result.get('description', ''),
                    'rating': result.get('rating', 0),
                    'author': result.get('author', ''),
                    'year': result.get('year', 0),
                    'tags': result.get('tags', ''),
                    'cover': result.get('cover', ''),
                    'publisher': result.get('publisher', ''),
                    'content_type': result.get('source_type', 'unknown'),
                    'similarity_score': similarity_score,
                    'reason': f"Correspondance: {result.get('matched_text', '')[:100]}...",
                    'type': 'manga_content'
                })
            
            # Trier par score de similarité décroissant
            formatted_results.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            logger.info(f"Manga search: '{query}' ({content_type}) → {len(formatted_results)} résultats")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Erreur recherche manga: {e}")
            # Retourner une liste vide au lieu d'un fallback vers la littérature
            return []
    
    def _fallback_manga_search(self, query: str, n_results: int) -> List[Dict[str, Any]]:
        """Fallback désactivé - retourne une liste vide"""
        logger.warning("Fallback manga désactivé - utilise uniquement le RAG manga dédié")
        return []
    
    def _arun(self, query: str, n_results: int = 3, content_type: str = "all", user_id: int = 1):
        """Version asynchrone (non implémentée pour l'instant)"""
        raise NotImplementedError("Async version not implemented")

class WikipediaSearchTool(BaseTool):
    """Outil de recherche Wikipedia pour information complémentaire"""
    
    name: str = "wikipedia_search"
    description: str = """
    Recherche des informations sur Wikipedia pour des auteurs, œuvres littéraires, ou contexte culturel.
    Utilise cet outil UNIQUEMENT quand :
    - Le RAG littéraire ne trouve pas d'information sur un auteur ou une œuvre
    - L'utilisateur demande des informations biographiques sur un auteur
    - Il faut trouver la correspondance entre un titre français et anglais
    - Il faut du contexte historique ou culturel sur une œuvre
    - Il faut trouver l'auteur d'une oeuvre si elle n est pas dans le RAG
    """
    args_schema: type[BaseModel] = WikipediaSearchInput
    
    def _run(self, query: str, language: str = "fr") -> Dict[str, Any]:
        """Execute la recherche Wikipedia"""
        try:
            # Configurer la langue
            wikipedia.set_lang(language)
            
            # Rechercher les pages
            search_results = wikipedia.search(query, results=3)
            
            if not search_results:
                return {
                    'success': False,
                    'message': f"Aucun résultat Wikipedia trouvé pour '{query}' en {language}",
                    'suggestions': []
                }
            
            # Prendre le premier résultat le plus pertinent
            try:
                page = wikipedia.page(search_results[0])
                
                # Extraire les informations principales
                summary = wikipedia.summary(search_results[0], sentences=3)
                
                # Détecter si c'est un auteur ou une œuvre
                info_type = self._detect_info_type(page.title, summary)
                
                result = {
                    'success': True,
                    'title': page.title,
                    'summary': summary,
                    'url': page.url,
                    'type': info_type,
                    'language': language,
                    'other_languages': self._get_other_language_titles(page) if info_type == 'work' else None
                }
                
                # Ajouter informations spécifiques selon le type
                if info_type == 'author':
                    result['author_info'] = self._extract_author_info(page.content)
                elif info_type == 'work':
                    result['work_info'] = self._extract_work_info(page.content)
                
                logger.info(f"Wikipedia search: '{query}' ({language}) → {info_type} trouvé")
                return result
                
            except wikipedia.exceptions.DisambiguationError as e:
                # Plusieurs résultats possibles
                return {
                    'success': True,
                    'title': f"Plusieurs résultats pour '{query}'",
                    'summary': f"Plusieurs pages Wikipedia trouvées. Options: {', '.join(e.options[:5])}",
                    'type': 'disambiguation',
                    'language': language,
                    'options': e.options[:5]
                }
                
            except wikipedia.exceptions.PageError:
                # Page non trouvée, essayer le deuxième résultat
                if len(search_results) > 1:
                    try:
                        page = wikipedia.page(search_results[1])
                        summary = wikipedia.summary(search_results[1], sentences=3)
                        info_type = self._detect_info_type(page.title, summary)
                        
                        return {
                            'success': True,
                            'title': page.title,
                            'summary': summary,
                            'url': page.url,
                            'type': info_type,
                            'language': language
                        }
                    except:
                        pass
                
                return {
                    'success': False,
                    'message': f"Page Wikipedia non trouvée pour '{query}'",
                    'suggestions': search_results
                }
                
        except Exception as e:
            logger.error(f"Erreur Wikipedia search: {e}")
            return {
                'success': False,
                'message': f"Erreur lors de la recherche Wikipedia: {str(e)}",
                'suggestions': []
            }
    
    def _detect_info_type(self, title: str, summary: str) -> str:
        """Détecte si c'est un auteur, une œuvre, ou autre"""
        title_lower = title.lower()
        summary_lower = summary.lower()
        
        # Indicateurs d'auteur
        author_indicators = ['écrivain', 'auteur', 'romancier', 'poète', 'novelist', 'writer', 'author']
        if any(indicator in summary_lower for indicator in author_indicators):
            return 'author'
        
        # Indicateurs d'œuvre
        work_indicators = ['roman', 'livre', 'novel', 'book', 'œuvre', 'work', 'récit', 'story']
        if any(indicator in summary_lower for indicator in work_indicators):
            return 'work'
        
        return 'other'
    
    def _extract_author_info(self, content: str) -> Dict[str, Any]:
        """Extrait les informations d'auteur"""
        info = {}
        
        # Extraire les dates de naissance/mort (basique)
        import re
        birth_death_pattern = r'(\d{4})\s*[-–]\s*(\d{4}|\w+)'
        match = re.search(birth_death_pattern, content)
        if match:
            info['birth_year'] = match.group(1)
            info['death_year'] = match.group(2) if match.group(2).isdigit() else None
        
        # Extraire les œuvres principales (premiers paragraphes)
        works_section = content[:1000]  # Premiers 1000 caractères
        info['biography_excerpt'] = works_section
        
        return info
    
    def _extract_work_info(self, content: str) -> Dict[str, Any]:
        """Extrait les informations d'œuvre"""
        info = {}
        
        # Extraire l'année de publication
        import re
        year_pattern = r'publié en (\d{4})|published in (\d{4})|(\d{4})'
        match = re.search(year_pattern, content)
        if match:
            info['publication_year'] = match.group(1) or match.group(2) or match.group(3)
        
        # Extraire le genre
        genre_patterns = ['roman', 'novel', 'poésie', 'poetry', 'théâtre', 'theater', 'essai', 'essay']
        for pattern in genre_patterns:
            if pattern in content.lower():
                info['genre'] = pattern
                break
        
        return info
    
    def _get_other_language_titles(self, page) -> Dict[str, str]:
        """Obtient les titres dans d'autres langues"""
        try:
            # Obtenir les liens vers d'autres langues
            other_langs = {}
            if hasattr(page, 'links'):
                # Basique - peut être amélioré
                for link in page.links[:10]:  # Limite pour éviter trop de traitement
                    if 'english' in link.lower() or 'français' in link.lower():
                        other_langs[link] = link
            return other_langs
        except:
            return {}
    
    def _arun(self, query: str, language: str = "fr"):
        """Version asynchrone (non implémentée pour l'instant)"""
        raise NotImplementedError("Async version not implemented")

class CombinedSearchTool(BaseTool):
    """Outil de recherche combinée pour cas ambigus"""
    
    name: str = "combined_search"
    description: str = """
    Recherche combinée dans tous les domaines (tech, littérature, manga).
    Utilisé pour les requêtes ambiguës où le type n'est pas clairement déterminé.
    """
    args_schema: type[BaseModel] = BookSearchInput
    
    def _run(self, query: str, n_results: int = 3, user_id: int = 1) -> List[Dict[str, Any]]:
        """Execute une recherche combinée"""
        try:
            all_results = []
            
            # Créer les outils dynamiquement pour éviter les problèmes Pydantic
            tech_tool = TechBookSearchTool()
            lit_tool = LiteratureBookSearchTool()
            manga_tool = MangaContentSearchTool()
            
            # Recherche dans chaque domaine
            tech_results = tech_tool._run(query, max(1, n_results // 3), user_id)
            lit_results = lit_tool._run(query, max(1, n_results // 3), user_id)
            manga_results = manga_tool._run(query, max(1, n_results // 3), "all", user_id)
            
            # Combiner et trier par score de similarité
            all_results.extend(tech_results)
            all_results.extend(lit_results)
            all_results.extend(manga_results)
            
            # Trier par score de similarité
            all_results.sort(key=lambda x: x.get('similarity_score', 0), reverse=True)
            
            # Retourner les meilleurs résultats
            final_results = all_results[:n_results]
            
            logger.info(f"Combined search: '{query}' → {len(final_results)} résultats")
            return final_results
            
        except Exception as e:
            logger.error(f"Erreur recherche combinée: {e}")
            return []
    
    def _arun(self, query: str, n_results: int = 3, user_id: int = 1):
        """Version asynchrone (non implémentée pour l'instant)"""
        raise NotImplementedError("Async version not implemented")

# Factory pour créer les outils facilement
class RAGToolsFactory:
    """Factory pour créer et gérer les outils RAG"""
    
    @staticmethod
    def create_all_tools() -> List[BaseTool]:
        """Crée tous les outils RAG disponibles"""
        return [
            TechBookSearchTool(),
            LiteratureBookSearchTool(),
            MangaContentSearchTool(),
            CombinedSearchTool()
        ]
    
    @staticmethod
    def get_tool_by_agent_type(agent_type: str) -> BaseTool:
        """Retourne l'outil approprié selon le type d'agent"""
        tool_mapping = {
            "tech": TechBookSearchTool(),
            "literature": LiteratureBookSearchTool(),
            "manga": MangaContentSearchTool()
        }
        
        return tool_mapping.get(agent_type, CombinedSearchTool())
    
    @staticmethod
    def get_wikipedia_tool() -> BaseTool:
        """Retourne l'outil Wikipedia"""
        return WikipediaSearchTool()
    
    @staticmethod
    def test_all_tools(test_queries: Dict[str, str] = None):
        """Test basique de tous les outils"""
        if test_queries is None:
            test_queries = {
                "tech": "apprendre Python",
                "literature": "romans de Tolstoï", 
                "manga": "manga comme Naruto"
            }
        
        tools = RAGToolsFactory.create_all_tools()
        
        for tool in tools:
            agent_type = tool.name.split('_')[0]  # tech, literature, manga, combined
            query = test_queries.get(agent_type, "test query")
            
            try:
                results = tool._run(query, n_results=2)
                print(f"✅ {tool.name}: {len(results)} résultats pour '{query}'")
                
                if results:
                    print(f"   Premier résultat: {results[0].get('title', 'Titre inconnu')}")
                
            except Exception as e:
                print(f"❌ {tool.name}: Erreur - {e}")

# Utilitaires pour le formatage des résultats
class ResultFormatter:
    """Utilitaires pour formater les résultats des outils RAG"""
    
    @staticmethod
    def format_for_llm(results: List[Dict[str, Any]], agent_type: str) -> str:
        """Formate les résultats pour être utilisés dans un prompt LLM"""
        if not results:
            return f"Aucun résultat trouvé pour cette requête {agent_type}."
        
        formatted_text = f"Résultats de recherche {agent_type}:\n\n"
        
        for i, result in enumerate(results, 1):
            formatted_text += f"{i}. **{result['title']}**\n"
            
            # Formatage spécifique selon le type
            if result['type'] == 'tech_book':
                formatted_text += f"   Auteur: {result['author']}\n"
                formatted_text += f"   Note: {result['rating']}/5 | Prix: ${result['price']}\n"
                formatted_text += f"   Niveau: {result['difficulty_level']}\n"
            
            elif result['type'] == 'literature_book':
                formatted_text += f"   Auteur(s): {result['authors']}\n"
                formatted_text += f"   Note: {result['average_rating']}/5"
                if result.get('published_year'):
                    formatted_text += f" | Publié: {result['published_year']}"
                formatted_text += "\n"
            
            elif result['type'] == 'manga_content':
                if result.get('author'):
                    formatted_text += f"   Auteur: {result['author']}\n"
                formatted_text += f"   Note: {result['rating']}/5"
                if result.get('year') and result['year'] > 0:
                    formatted_text += f" | Année: {result['year']}"
                formatted_text += f"\n   Type: {result['content_type']}\n"
                if result.get('tags'):
                    formatted_text += f"   Genres: {result['tags']}\n"
            
            # Informations communes
            formatted_text += f"   Pertinence: {result['similarity_score']:.1%}\n"
            formatted_text += f"   Raison: {result['reason']}\n"
            formatted_text += f"   Description: {result['description'][:150]}...\n\n"
        
        return formatted_text
    
    @staticmethod
    def format_for_api(results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Formate les résultats pour l'API JSON"""
        return {
            "success": True,
            "count": len(results),
            "results": results
        }
    
    @staticmethod
    def extract_titles_list(results: List[Dict[str, Any]]) -> List[str]:
        """Extrait juste la liste des titres"""
        return [result.get('title', 'Titre inconnu') for result in results]

# Validation des outils
def validate_rag_systems():
    """Valide que tous les systèmes RAG sont accessibles"""
    validation_results = {
        "tech_rag": False,
        "literature_rag": False,
        "manga_rag": False
    }
    
    # Test Tech RAG
    try:
        from rags.tech_rag.tech_rag_manager import TechRAGManager
        tech_rag = TechRAGManager()
        validation_results["tech_rag"] = True
        logger.info("✅ Tech RAG accessible")
    except Exception as e:
        logger.error(f"❌ Tech RAG inaccessible: {e}")
    
    # Test Literature RAG
    try:
        from rags.literature_rag.literature_rag_manager import LiteratureRAGManager
        lit_rag = LiteratureRAGManager()
        validation_results["literature_rag"] = True
        logger.info("✅ Literature RAG accessible")
    except Exception as e:
        logger.error(f"❌ Literature RAG inaccessible: {e}")
    
    # Test Manga RAG
    try:
        from rags.manga_rag.manga_rag_manager import MangaRAGManager
        manga_rag = MangaRAGManager()
        validation_results["manga_rag"] = True
        logger.info("✅ Manga RAG accessible")
    except Exception as e:
        logger.error(f"❌ Manga RAG inaccessible: {e}")
    
    return validation_results

if __name__ == "__main__":
    # Test des outils
    print("🔧 Test des outils RAG...")
    validate_rag_systems()
    RAGToolsFactory.test_all_tools()