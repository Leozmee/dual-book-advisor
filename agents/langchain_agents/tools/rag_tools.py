"""
RAG Tools - Interface LangChain avec vos systèmes RAG existants
Fichier: agents/langchain_agents/tools/rag_tools.py
"""
from typing import List, Dict, Any, Optional
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
import logging

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
            
            # Obtenir des recommandations
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
            
            # Obtenir des recommandations
            recommendations = manga_rag.get_content_recommendations(
                user_id=user_id,
                query=query,
                n_recommendations=n_results,
                content_type=content_type
            )
            
            # Formater pour LangChain
            formatted_results = []
            for rec in recommendations:
                content = rec['content']
                formatted_results.append({
                    'id': content['id'],
                    'title': content['title'],
                    'description': content['description'],
                    'rating': content['rating'],
                    'author': content.get('author', ''),
                    'year': content.get('year', 0),
                    'tags': content.get('tags', ''),
                    'cover': content.get('cover', ''),
                    'publisher': content.get('publisher', ''),
                    'content_type': content['type'],
                    'similarity_score': rec['similarity_score'],
                    'reason': rec['reason'],
                    'type': 'manga_content'
                })
            
            logger.info(f"Manga search: '{query}' ({content_type}) → {len(formatted_results)} résultats")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Erreur recherche manga: {e}")
            # Fallback vers recherche littéraire si le RAG manga n'est pas disponible
            return self._fallback_manga_search(query, n_results)
    
    def _fallback_manga_search(self, query: str, n_results: int) -> List[Dict[str, Any]]:
        """Fallback si le RAG manga n'est pas disponible"""
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
            for book in books.distinct()[:n_results]:
                results.append({
                    'id': f"fallback_{book.id}",
                    'title': book.title,
                    'description': book.description,
                    'rating': float(book.average_rating) if book.average_rating else 0.0,
                    'author': book.authors,
                    'year': book.published_year or 0,
                    'tags': book.categories,
                    'cover': book.thumbnail or '',
                    'content_type': 'literature_fallback',
                    'similarity_score': 0.5,
                    'reason': 'Fallback depuis base littéraire',
                    'type': 'manga_content'
                })
            
            logger.info(f"Manga fallback: '{query}' → {len(results)} résultats")
            return results
            
        except Exception as e:
            logger.error(f"Erreur fallback manga: {e}")
            return []
    
    def _arun(self, query: str, n_results: int = 3, content_type: str = "all", user_id: int = 1):
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
    
    def __init__(self):
        super().__init__()
        self.tech_tool = TechBookSearchTool()
        self.literature_tool = LiteratureBookSearchTool()
        self.manga_tool = MangaContentSearchTool()
    
    def _run(self, query: str, n_results: int = 3, user_id: int = 1) -> List[Dict[str, Any]]:
        """Execute une recherche combinée"""
        try:
            all_results = []
            
            # Recherche dans chaque domaine
            tech_results = self.tech_tool._run(query, max(1, n_results // 3), user_id)
            lit_results = self.literature_tool._run(query, max(1, n_results // 3), user_id)
            manga_results = self.manga_tool._run(query, max(1, n_results // 3), "all", user_id)
            
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