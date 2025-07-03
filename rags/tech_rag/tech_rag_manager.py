"""
Gestionnaire RAG pour les livres techniques
"""
import logging
from typing import List, Dict, Any, Optional
from django.conf import settings
from apps.books.models import TechBook
from rags.shared.embedding_manager import ChromaDBManager

logger = logging.getLogger(__name__)


class TechRAGManager:
    """Gestionnaire RAG spécialisé pour les livres techniques"""
    
    def __init__(self):
        self.chroma_path = settings.RAG_CONFIG['tech_chroma_path']
        self.collection_name = "tech_books"
        self.chroma_manager = ChromaDBManager(str(self.chroma_path))
        self.collection = None
        self._init_collection()
    
    def _init_collection(self):
        """Initialise la collection ChromaDB pour les livres techniques"""
        try:
            self.collection = self.chroma_manager.create_collection(self.collection_name)
            logger.info(f"Collection {self.collection_name} initialisée")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation de la collection: {e}")
            raise
    
    def index_all_books(self, reset: bool = False):
        """Indexe tous les livres techniques dans ChromaDB"""
        try:
            if reset:
                self.collection = self.chroma_manager.create_collection(
                    self.collection_name, reset=True
                )
            
            # Récupérer tous les livres techniques
            books = TechBook.objects.all()
            logger.info(f"Indexation de {books.count()} livres techniques...")
            
            documents = []
            for book in books:
                # Construire le texte pour l'embedding
                text_content = self._build_book_text(book)
                
                # Préparer les métadonnées
                metadata = {
                    'book_id': book.id,
                    'title': book.title,
                    'author': book.author,
                    'isbn13': book.isbn13 or '',
                    'rating': float(book.rating) if book.rating else 0.0,
                    'difficulty_level': book.difficulty_level,
                    'tech_categories': book.tech_categories,
                    'programming_languages': ','.join(
                        book.programming_languages.values_list('name', flat=True)
                    ),
                    'best_seller': book.best_seller,
                    'top_rated': book.top_rated,
                    'price': float(book.price) if book.price else 0.0,
                    'type': 'tech_book'
                }
                
                documents.append({
                    'id': f"tech_book_{book.id}",
                    'text': text_content,
                    'metadata': metadata
                })
            
            # Indexer par lots pour éviter les problèmes de mémoire
            batch_size = 100
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                self.chroma_manager.add_documents(self.collection, batch)
                logger.info(f"Lot {i//batch_size + 1} indexé ({len(batch)} livres)")
            
            logger.info(f"Indexation terminée: {len(documents)} livres techniques indexés")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'indexation: {e}")
            raise
    
    def _build_book_text(self, book: TechBook) -> str:
        """Construit le texte d'un livre pour l'embedding"""
        # Combiner titre, description, et métadonnées importantes
        text_parts = [
            f"Titre: {book.title}",
            f"Auteur: {book.author}",
            f"Description: {book.description}",
        ]
        
        if book.tech_categories:
            text_parts.append(f"Catégories: {book.tech_categories}")
        
        if book.programming_languages.exists():
            languages = ', '.join(book.programming_languages.values_list('name', flat=True))
            text_parts.append(f"Langages de programmation: {languages}")
        
        text_parts.append(f"Niveau: {book.get_difficulty_level_display()}")
        
        if book.best_seller:
            text_parts.append("Best-seller")
        
        if book.top_rated:
            text_parts.append("Très bien noté")
        
        return ' | '.join(text_parts)
    
    def search_books(self, query: str, user_preferences: Optional[Dict[str, Any]] = None,
                    n_results: int = 5) -> List[Dict[str, Any]]:
        """Recherche des livres techniques basée sur une requête"""
        try:
            # Enrichir la requête avec les préférences utilisateur
            enhanced_query = self._enhance_query(query, user_preferences)
            
            # Rechercher dans ChromaDB
            similarity_threshold = settings.RAG_CONFIG.get('similarity_threshold', 0.7)
            results = self.chroma_manager.search_similar(
                collection=self.collection,
                query=enhanced_query,
                n_results=n_results,
                similarity_threshold=similarity_threshold
            )
            
            # Formater les résultats
            formatted_results = []
            for i, metadata in enumerate(results['metadatas']):
                result = {
                    'book_id': metadata['book_id'],
                    'title': metadata['title'],
                    'author': metadata['author'],
                    'rating': metadata['rating'],
                    'difficulty_level': metadata['difficulty_level'],
                    'programming_languages': metadata['programming_languages'],
                    'similarity_score': 1 - results['distances'][i],  # Convertir distance en similarité
                    'matched_text': results['documents'][i][:200] + '...' if len(results['documents'][i]) > 200 else results['documents'][i]
                }
                formatted_results.append(result)
            
            logger.info(f"Recherche terminée: {len(formatted_results)} livres trouvés")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche: {e}")
            return []
    
    def _enhance_query(self, query: str, user_preferences: Optional[Dict[str, Any]] = None) -> str:
        """Enrichit la requête avec extraction intelligente des termes techniques et adaptation contextuelle"""
        import re
        
        # Dictionnaire des correspondances intelligentes - uniquement pour les intentions techniques claires
        tech_mappings = {
            # Langages de programmation
            r'\b(python|py)\b': 'Python programming',
            r'\b(javascript|js|node)\b': 'JavaScript programming',
            r'\b(java)\b': 'Java programming',
            r'\b(c#|csharp|c sharp)\b': 'C# programming',
            r'\b(c\+\+|cpp)\b': 'C++ programming',
            r'\b(php)\b': 'PHP programming',
            r'\b(ruby)\b': 'Ruby programming',
            r'\b(go|golang)\b': 'Go programming',
            r'\b(rust)\b': 'Rust programming',
            r'\b(swift)\b': 'Swift programming',
            r'\b(kotlin)\b': 'Kotlin programming',
            
            # Domaines techniques explicites
            r'\b(web development|développement web)\b': 'web development',
            r'\b(mobile development|développement mobile)\b': 'mobile development',
            r'\b(game development|développement jeu)\b': 'game development',
            r'\b(data science|science des données)\b': 'data science',
            r'\b(machine learning|ml|ai|intelligence artificielle)\b': 'machine learning',
            r'\b(cybersécurité|cybersecurity|sécurité informatique)\b': 'cybersecurity',
            r'\b(réseau informatique|network|networking)\b': 'networking',
            r'\b(cloud computing|cloud|nuage)\b': 'cloud computing',
            r'\b(blockchain|crypto)\b': 'blockchain',
            
            # Intentions d'apprentissage techniques
            r'\b(apprendre.*(python|java|c#|csharp|javascript|programmation))\b': 'beginner programming',
            r'\b(learn.*(python|java|c#|csharp|javascript|programming))\b': 'beginner programming',
            r'\b(débutant\s+(en\s+)?(programmation|coding))\b': 'beginner programming',
            r'\b(beginner\s+(programming|coding))\b': 'beginner programming',
            r'\b(avancé\s+(en\s+)?(programmation|coding))\b': 'advanced programming',
            r'\b(advanced\s+(programming|coding))\b': 'advanced programming',
        }
        
        # Contextes spécialisés - uniquement si intention technique claire
        specialized_tech_mappings = {
            r'\b(programmation\s+(audio|musique|music))\b': 'audio programming music software',
            r'\b(audio\s+(programming|development))\b': 'audio programming music software',
            r'\b(sport\s+(analytics|data|programming))\b': 'sports analytics fitness apps health tech',
            r'\b(fitness\s+(app|software|development))\b': 'sports analytics fitness apps health tech',
            r'\b(programmation\s+(graphique|image))\b': 'image processing computer graphics',
            r'\b(computer\s+(graphics|vision))\b': 'image processing computer graphics',
            r'\b(video\s+(processing|programming))\b': 'video processing multimedia programming',
            r'\b(financial\s+(programming|software))\b': 'financial programming trading algorithms',
            r'\b(trading\s+(algorithms|bot))\b': 'financial programming trading algorithms',
            r'\b(educational\s+(technology|software))\b': 'educational technology programming',
            r'\b(restaurant\s+(management\s+)?(software|system))\b': 'restaurant management software food tech',
        }
        
        # Extraction intelligente des termes techniques
        enhanced_query = query.lower()
        extracted_terms = []
        
        # D'abord, chercher les termes techniques explicites
        for pattern, tech_term in tech_mappings.items():
            if re.search(pattern, enhanced_query, re.IGNORECASE):
                extracted_terms.append(tech_term)
        
        # Ensuite, chercher les contextes spécialisés (uniquement si intention technique claire)
        if not extracted_terms:  # Seulement si aucun terme technique explicite trouvé
            for pattern, tech_term in specialized_tech_mappings.items():
                if re.search(pattern, enhanced_query, re.IGNORECASE):
                    extracted_terms.append(tech_term)
        
        # Si des termes techniques sont trouvés, les utiliser
        if extracted_terms:
            enhanced_query = ' '.join(extracted_terms)
        else:
            # Fallback: Conserver la requête originale si aucun terme technique détecté
            # Ne pas forcer une requête technique si l'utilisateur n'en a pas l'intention
            enhanced_query = query
        
        # Ajouter les préférences utilisateur
        if user_preferences:
            if 'preferred_programming_languages' in user_preferences:
                languages = user_preferences['preferred_programming_languages']
                if languages:
                    enhanced_query += f" {' '.join(languages)}"
            
            if 'preferred_tech_difficulty' in user_preferences:
                difficulty = user_preferences['preferred_tech_difficulty']
                if difficulty:
                    enhanced_query += f" {difficulty}"
            
            if 'preferred_tech_categories' in user_preferences:
                categories = user_preferences['preferred_tech_categories']
                if categories:
                    enhanced_query += f" {' '.join(categories)}"
        
        logger.info(f"Requête originale: '{query}' -> Requête enrichie: '{enhanced_query}'")
        return enhanced_query
    
    def get_book_recommendations(self, user_id: int, query: str, 
                               n_recommendations: int = 3) -> List[Dict[str, Any]]:
        """Génère des recommandations de livres techniques pour un utilisateur"""
        try:
            # Récupérer les préférences utilisateur
            from apps.accounts.models import UserProfile
            try:
                user_profile = UserProfile.objects.get(user_id=user_id)
                user_preferences = {
                    'preferred_programming_languages': [
                        lang.name for lang in user_profile.preferred_programming_languages.all()
                    ],
                    'preferred_tech_difficulty': user_profile.preferred_tech_difficulty,
                    'preferred_tech_categories': user_profile.preferred_tech_categories.split(',') if user_profile.preferred_tech_categories else []
                }
            except UserProfile.DoesNotExist:
                user_preferences = None
            
            # Rechercher des livres
            results = self.search_books(
                query=query,
                user_preferences=user_preferences,
                n_results=n_recommendations
            )
            
            # Enrichir avec les données complètes des livres
            recommendations = []
            for result in results:
                try:
                    book = TechBook.objects.get(id=result['book_id'])
                    recommendation = {
                        'book': {
                            'id': book.id,
                            'title': book.title,
                            'author': book.author,
                            'description': book.description,
                            'rating': float(book.rating) if book.rating else 0.0,
                            'price': float(book.price) if book.price else 0.0,
                            'difficulty_level': book.get_difficulty_level_display(),
                            'best_seller': book.best_seller,
                            'top_rated': book.top_rated,
                        },
                        'similarity_score': result['similarity_score'],
                        'reason': self._generate_recommendation_reason(book, result, user_preferences)
                    }
                    recommendations.append(recommendation)
                except TechBook.DoesNotExist:
                    continue
            
            logger.info(f"Recommandations générées: {len(recommendations)} livres")
            return recommendations
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération des recommandations: {e}")
            return []
    
    def _generate_recommendation_reason(self, book: TechBook, search_result: Dict[str, Any],
                                      user_preferences: Optional[Dict[str, Any]] = None) -> str:
        """Génère une explication pour la recommandation"""
        reasons = []
        
        # Score de similarité
        similarity_score = search_result['similarity_score']
        if similarity_score > 0.9:
            reasons.append("Correspond parfaitement à votre recherche")
        elif similarity_score > 0.8:
            reasons.append("Très pertinent pour votre recherche")
        else:
            reasons.append("Pertinent pour votre recherche")
        
        # Qualité du livre
        if book.best_seller:
            reasons.append("Best-seller")
        if book.top_rated:
            reasons.append("Très bien noté")
        if book.rating and book.rating >= 4.5:
            reasons.append(f"Excellente note ({book.rating}/5)")
        
        # Correspondance avec les préférences
        if user_preferences:
            if user_preferences.get('preferred_programming_languages'):
                book_languages = set(book.programming_languages.values_list('name', flat=True))
                user_languages = set(user_preferences['preferred_programming_languages'])
                if book_languages.intersection(user_languages):
                    common_languages = book_languages.intersection(user_languages)
                    reasons.append(f"Correspond à vos langages préférés: {', '.join(common_languages)}")
            
            if (user_preferences.get('preferred_tech_difficulty') and 
                book.difficulty_level == user_preferences['preferred_tech_difficulty']):
                reasons.append(f"Niveau {book.get_difficulty_level_display()} comme souhaité")
        
        return " | ".join(reasons)
    
    def get_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques de la collection"""
        try:
            stats = self.chroma_manager.get_collection_stats(self.collection)
            db_count = TechBook.objects.count()
            
            return {
                'collection_name': self.collection_name,
                'indexed_books': stats.get('count', 0),
                'total_books_in_db': db_count,
                'sync_status': 'synchronized' if stats.get('count', 0) == db_count else 'out_of_sync'
            }
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des stats: {e}")
            return {'error': str(e)}