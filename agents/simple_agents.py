"""
Agents simplifiés pour les recommandations de livres
"""
import logging
from typing import Dict, Any, Optional
from rags.tech_rag.tech_rag_manager import TechRAGManager
from rags.literature_rag.literature_rag_manager import LiteratureRAGManager

logger = logging.getLogger(__name__)


class SimpleAgentManager:
    """Gestionnaire d'agents simplifiés pour les recommandations"""
    
    def __init__(self):
        try:
            self.tech_rag = TechRAGManager()
            self.literature_rag = LiteratureRAGManager()
            self.rag_available = True
        except Exception as e:
            logger.warning(f"RAG non disponible, utilisation fallback: {e}")
            self.tech_rag = None
            self.literature_rag = None
            self.rag_available = False
    
    def get_tech_recommendations(self, query: str, user_id: int = 1) -> str:
        """Obtient des recommandations techniques"""
        try:
            if not self.rag_available:
                return self._get_fallback_tech_recommendations(query)
            
            recommendations = self.tech_rag.get_book_recommendations(
                user_id=user_id,
                query=query,
                n_recommendations=3
            )
            
            if not recommendations:
                # Si RAG ne trouve rien, utiliser le fallback
                return self._get_fallback_tech_recommendations(query)
            
            result = "🔧 **Agent Technique**\n\n"
            for i, rec in enumerate(recommendations, 1):
                book = rec['book']
                result += f"**{i}. {book['title']}**\n"
                result += f"👤 Auteur: {book.get('author', 'Auteur inconnu')}\n"
                result += f"⭐ Note: {book.get('rating', 'N/A')}/5\n"
                result += f"📊 Pertinence: {rec['similarity_score']:.0%}\n"
                result += f"💡 {rec['reason']}\n"
                if book.get('description'):
                    desc = book['description'][:150] + "..." if len(book['description']) > 150 else book['description']
                    result += f"📖 {desc}\n"
                result += "\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur agent technique: {e}")
            return f"🔧 **Agent Technique**\n\nErreur: {str(e)}"
    
    def get_literature_recommendations(self, query: str, user_id: int = 1) -> str:
        """Obtient des recommandations littéraires"""
        try:
            if not self.rag_available:
                return self._get_fallback_literature_recommendations(query)
            
            recommendations = self.literature_rag.get_book_recommendations(
                user_id=user_id,
                query=query,
                n_recommendations=3
            )
            
            if not recommendations:
                # Si RAG ne trouve rien, utiliser le fallback
                return self._get_fallback_literature_recommendations(query)
            
            result = "📚 **Agent Littéraire**\n\n"
            for i, rec in enumerate(recommendations, 1):
                book = rec['book']
                result += f"**{i}. {book['title']}**\n"
                result += f"👤 Auteur: {book.get('authors', 'Auteur inconnu')}\n"
                result += f"⭐ Note: {book.get('average_rating', 'N/A')}/5\n"
                if book.get('published_year'):
                    result += f"📅 {book['published_year']}\n"
                result += f"📊 Pertinence: {rec['similarity_score']:.0%}\n"
                result += f"💡 {rec['reason']}\n"
                if book.get('description'):
                    desc = book['description'][:150] + "..." if len(book['description']) > 150 else book['description']
                    result += f"📖 {desc}\n"
                result += "\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur agent littéraire: {e}")
            return f"📚 **Agent Littéraire**\n\nErreur: {str(e)}"
    
    def route_query(self, query: str, user_id: int = 1) -> str:
        """Route automatiquement la requête vers l'agent approprié"""
        query_lower = query.lower()
        
        # Mots-clés techniques
        tech_keywords = [
            'python', 'java', 'javascript', 'c#', 'c++', 'php', 'ruby', 'go', 'rust',
            'programmation', 'programming', 'code', 'coding', 'développement', 'development',
            'web', 'mobile', 'app', 'application', 'data', 'machine learning', 'ai',
            'blockchain', 'cybersécurité', 'security', 'réseau', 'network', 'cloud'
        ]
        
        # Mots-clés littéraires
        literature_keywords = [
            'roman', 'livre', 'book', 'histoire', 'story', 'auteur', 'author',
            'fantasy', 'science fiction', 'romance', 'thriller', 'mystery',
            'fiction', 'littérature', 'literature', 'novel', 'harry potter',
            'twilight', 'game of thrones', 'série', 'saga'
        ]
        
        tech_score = sum(1 for keyword in tech_keywords if keyword in query_lower)
        lit_score = sum(1 for keyword in literature_keywords if keyword in query_lower)
        
        if tech_score > lit_score:
            return self.get_tech_recommendations(query, user_id)
        elif lit_score > tech_score:
            return self.get_literature_recommendations(query, user_id)
        else:
            # Requête ambiguë, proposer les deux
            return f"""🤖 **Agent de Routage**

Votre requête pourrait concerner les livres techniques ou littéraires.

**Spécialisations disponibles:**
- 🔧 **Livres techniques**: Programmation, développement, data science, technologies
- 📚 **Livres littéraires**: Romans, fiction, genres littéraires, auteurs

**Exemples de requêtes:**
- "Je veux apprendre Python" → Agent technique
- "J'ai adoré Harry Potter, que me conseillez-vous ?" → Agent littéraire
- "Un livre sur le JavaScript" → Agent technique
- "Des romans fantastiques" → Agent littéraire

**Votre requête**: "{query}"

Pourriez-vous préciser si vous cherchez des livres techniques ou littéraires ?"""
    
    def get_agent_response(self, query: str, agent_type: str = "router", user_id: int = 1) -> str:
        """Interface unifiée pour tous les agents"""
        try:
            if agent_type == "router":
                return self.route_query(query, user_id)
            elif agent_type == "tech":
                return self.get_tech_recommendations(query, user_id)
            elif agent_type == "literature":
                return self.get_literature_recommendations(query, user_id)
            else:
                return "❌ Type d'agent non reconnu. Utilisez: 'router', 'tech', ou 'literature'"
        
        except Exception as e:
            logger.error(f"Erreur agent {agent_type}: {e}")
            return f"❌ Erreur: {str(e)}"
    
    def _get_fallback_tech_recommendations(self, query: str) -> str:
        """Recommandations techniques sans RAG (fallback)"""
        from apps.books.models import TechBook
        
        # Recherche simple par mots-clés
        query_lower = query.lower()
        books = TechBook.objects.all()
        
        # Filtrage basique
        from django.db.models import Q
        
        if 'javascript' in query_lower or 'js' in query_lower:
            books = books.filter(
                Q(title__icontains='javascript') |
                Q(tech_categories__icontains='javascript')
            )
        elif 'python' in query_lower:
            books = books.filter(
                Q(title__icontains='python') |
                Q(tech_categories__icontains='python')
            )
        elif 'c#' in query_lower or 'csharp' in query_lower or 'c sharp' in query_lower:
            books = books.filter(
                Q(title__icontains='c#') |
                Q(title__icontains='csharp') |
                Q(tech_categories__icontains='c#') |
                Q(programming_languages__name__icontains='c#')
            )
        elif 'java' in query_lower and 'javascript' not in query_lower:
            books = books.filter(
                Q(title__icontains='java') |
                Q(tech_categories__icontains='java')
            )
        elif 'web' in query_lower or 'html' in query_lower or 'css' in query_lower:
            books = books.filter(tech_categories__icontains='web')
        elif 'apprendre' in query_lower or 'learn' in query_lower or 'débutant' in query_lower:
            books = books.filter(difficulty_level='beginner')
        else:
            # Prendre les mieux notés par défaut
            books = books.filter(rating__gte=4.0)
        
        books = books.order_by('-rating')[:3]
        
        if not books.exists():
            return "🔧 **Agent Technique** (Mode Simple)\n\nAucun livre trouvé. Essayez 'JavaScript', 'Python', 'C#', etc."
        
        result = "🔧 **Agent Technique** (Mode Simple)\n\n"
        for i, book in enumerate(books, 1):
            result += f"**{i}. {book.title}**\n"
            result += f"👤 Auteur: {book.author}\n"
            result += f"⭐ Note: {book.rating}/5\n"
            result += f"💰 Prix: ${book.price}\n"
            if book.description:
                desc = book.description[:150] + "..." if len(book.description) > 150 else book.description
                result += f"📖 {desc}\n"
            result += "\n"
        
        return result
    
    def _get_fallback_literature_recommendations(self, query: str) -> str:
        """Recommandations littéraires sans RAG (fallback)"""
        from apps.books.models import LiteratureBook
        
        # Recherche simple par mots-clés
        query_lower = query.lower()
        books = LiteratureBook.objects.all()
        
        # Filtrage basique amélioré
        if 'harry potter' in query_lower:
            # Chercher des livres fantasy jeunesse populaires
            books = books.filter(categories__icontains='fantasy').filter(
                average_rating__gte=4.0
            ).filter(popularity_rating__gte=4.0)
        elif 'fantasy' in query_lower or 'fantastique' in query_lower:
            books = books.filter(categories__icontains='fantasy').filter(
                average_rating__gte=4.0
            )
        elif 'romance' in query_lower:
            books = books.filter(categories__icontains='romance').filter(
                average_rating__gte=4.0
            )
        elif 'science fiction' in query_lower or 'sci-fi' in query_lower or 'sf' in query_lower:
            books = books.filter(categories__icontains='science fiction').filter(
                average_rating__gte=4.0
            )
        elif 'thriller' in query_lower or 'mystery' in query_lower or 'suspense' in query_lower:
            books = books.filter(categories__icontains='mystery').filter(
                average_rating__gte=4.0
            )
        elif 'young adult' in query_lower or 'ado' in query_lower or 'jeunesse' in query_lower:
            books = books.filter(categories__icontains='young adult').filter(
                average_rating__gte=4.0
            )
        elif 'classique' in query_lower or 'classic' in query_lower:
            books = books.filter(published_year__lt=1980).filter(
                average_rating__gte=4.2
            )
        else:
            # Prendre les plus populaires et mieux notés
            books = books.filter(average_rating__gte=4.2).filter(
                popularity_rating__gte=4.0
            )
        
        books = books.order_by('-average_rating')[:3]
        
        if not books.exists():
            return "📚 **Agent Littéraire** (Mode Simple)\n\nAucun livre trouvé. Essayez 'fantasy', 'romance', 'Harry Potter', etc."
        
        result = "📚 **Agent Littéraire** (Mode Simple)\n\n"
        for i, book in enumerate(books, 1):
            result += f"**{i}. {book.title}**\n"
            result += f"👤 Auteur: {book.authors}\n"
            result += f"⭐ Note: {book.average_rating}/5\n"
            if book.published_year:
                result += f"📅 {book.published_year}\n"
            if book.description:
                desc = book.description[:150] + "..." if len(book.description) > 150 else book.description
                result += f"📖 {desc}\n"
            result += "\n"
        
        return result