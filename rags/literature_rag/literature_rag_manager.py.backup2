"""
Gestionnaire RAG pour les livres littéraires
"""
import logging
from typing import List, Dict, Any, Optional
from django.conf import settings
from apps.books.models import LiteratureBook
from rags.shared.embedding_manager import ChromaDBManager

logger = logging.getLogger(__name__)


class LiteratureRAGManager:
    """Gestionnaire RAG spécialisé pour les livres littéraires"""
    
    def __init__(self):
        self.chroma_path = settings.RAG_CONFIG['literature_chroma_path']
        self.collection_name = "literature_books"
        self.chroma_manager = ChromaDBManager(str(self.chroma_path))
        self.collection = None
        self._init_collection()
    
    def _init_collection(self):
        """Initialise la collection ChromaDB pour les livres littéraires"""
        try:
            self.collection = self.chroma_manager.create_collection(self.collection_name)
            logger.info(f"Collection {self.collection_name} initialisée")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation de la collection: {e}")
            raise
    
    def index_all_books(self, reset: bool = False):
        """Indexe tous les livres littéraires dans ChromaDB"""
        try:
            if reset:
                self.collection = self.chroma_manager.create_collection(
                    self.collection_name, reset=True
                )
            
            # Récupérer tous les livres littéraires
            books = LiteratureBook.objects.all()
            logger.info(f"Indexation de {books.count()} livres littéraires...")
            
            documents = []
            for book in books:
                # Construire le texte pour l'embedding
                text_content = self._build_book_text(book)
                
                # Préparer les métadonnées
                metadata = {
                    'book_id': book.id,
                    'title': book.title,
                    'authors': book.authors,
                    'isbn13': book.isbn13,
                    'average_rating': float(book.average_rating) if book.average_rating else 0.0,
                    'published_year': book.published_year or 0,
                    'categories': book.categories or '',
                    'reading_difficulty': book.reading_difficulty,
                    'themes': book.themes or '',
                    'genres': ','.join(book.genres.values_list('name', flat=True)),
                    'popularity_rating': float(book.popularity_rating) if book.popularity_rating else 0.0,
                    'popularity_score': book.popularity_score or 0,
                    'ratings_count': book.ratings_count or 0,
                    'votes_count': book.votes_count or 0,
                    'type': 'literature_book'
                }
                
                documents.append({
                    'id': f"literature_book_{book.id}",
                    'text': text_content,
                    'metadata': metadata
                })
            
            # Indexer par lots pour éviter les problèmes de mémoire
            batch_size = 100
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                self.chroma_manager.add_documents(self.collection, batch)
                logger.info(f"Lot {i//batch_size + 1} indexé ({len(batch)} livres)")
            
            logger.info(f"Indexation terminée: {len(documents)} livres littéraires indexés")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'indexation: {e}")
            raise
    
    def _build_book_text(self, book: LiteratureBook) -> str:
        """Construit le texte d'un livre pour l'embedding"""
        # Combiner titre, description, et métadonnées importantes
        text_parts = [
            f"Titre: {book.title}",
            f"Auteur(s): {book.authors}",
            f"Description: {book.description}",
        ]
        
        if book.categories:
            text_parts.append(f"Catégories: {book.categories}")
        
        if book.genres.exists():
            genres = ', '.join(book.genres.values_list('name', flat=True))
            text_parts.append(f"Genres: {genres}")
        
        if book.themes:
            text_parts.append(f"Thèmes: {book.themes}")
        
        text_parts.append(f"Difficulté de lecture: {book.get_reading_difficulty_display()}")
        
        if book.published_year:
            text_parts.append(f"Année de publication: {book.published_year}")
        
        # Informations de popularité
        if book.popularity_rating and book.popularity_rating >= 4.0:
            text_parts.append("Livre populaire")
        
        if book.average_rating and book.average_rating >= 4.5:
            text_parts.append("Très bien noté")
        
        return ' | '.join(text_parts)
    
    def search_books(self, query: str, user_preferences: Optional[Dict[str, Any]] = None,
                    n_results: int = 5) -> List[Dict[str, Any]]:
        """Recherche des livres littéraires basée sur une requête"""
        try:
            # Enrichir la requête avec les préférences utilisateur
            enhanced_query = self._enhance_query(query, user_preferences)
            
            # Rechercher dans ChromaDB avec un seuil équilibré pour les livres littéraires
            similarity_threshold = 0.58  # Seuil légèrement augmenté + filtrage qualité
            results = self.chroma_manager.search_similar(
                collection=self.collection,
                query=enhanced_query,
                n_results=n_results * 2,  # Chercher plus de résultats pour mieux filtrer
                similarity_threshold=similarity_threshold
            )
            
            # Formater les résultats
            formatted_results = []
            for i, metadata in enumerate(results['metadatas']):
                result = {
                    'book_id': metadata['book_id'],
                    'title': metadata['title'],
                    'authors': metadata['authors'],
                    'average_rating': metadata['average_rating'],
                    'reading_difficulty': metadata['reading_difficulty'],
                    'genres': metadata['genres'],
                    'categories': metadata['categories'],
                    'published_year': metadata['published_year'],
                    'popularity_rating': metadata.get('popularity_rating', 0.0),
                    'ratings_count': metadata.get('ratings_count', 0),
                    'similarity_score': 1 - results['distances'][i],  # Convertir distance en similarité
                    'matched_text': results['documents'][i][:200] + '...' if len(results['documents'][i]) > 200 else results['documents'][i]
                }
                formatted_results.append(result)
            
            # Filtrer et prioriser les livres populaires et bien notés
            filtered_results = self._filter_quality_books(formatted_results)
            
            # Limiter au nombre demandé
            final_results = filtered_results[:n_results]
            
            logger.info(f"Recherche terminée: {len(final_results)} livres trouvés (sur {len(formatted_results)} candidats)")
            return final_results
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche: {e}")
            return []
    
    def _filter_quality_books(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filtre et priorise les livres de qualité"""
        quality_books = []
        
        for result in results:
            rating = result.get('average_rating', 0.0)
            popularity = result.get('popularity_rating', 0.0)
            ratings_count = result.get('ratings_count', 0)
            
            # Critères de qualité (légèrement assouplis)
            is_well_rated = rating >= 3.3
            is_popular = popularity >= 2.5 or ratings_count >= 50
            
            # Accepter les livres qui respectent les critères de qualité
            if is_well_rated and is_popular:
                # Calculer un score de qualité combiné
                quality_score = (rating * 0.4) + (popularity * 0.3) + (min(ratings_count / 1000, 1.0) * 0.3)
                result['quality_score'] = quality_score
                quality_books.append(result)
        
        # Si pas assez de livres de qualité, accepter les livres bien notés même s'ils sont moins populaires
        if len(quality_books) < 3:
            for result in results:
                if result not in quality_books:
                    rating = result.get('average_rating', 0.0)
                    if rating >= 4.0:  # Seuil plus élevé pour les livres moins populaires
                        result['quality_score'] = rating * 0.5
                        quality_books.append(result)
        
        # Trier par score de qualité puis par similarité
        quality_books.sort(key=lambda x: (x.get('quality_score', 0), x.get('similarity_score', 0)), reverse=True)
        
        return quality_books
    
    def _enhance_query(self, query: str, user_preferences: Optional[Dict[str, Any]] = None) -> str:
        """Enrichit la requête avec extraction intelligente de genres et thèmes similaires"""
        import re
        
        # Dictionnaire des correspondances littéraires intelligentes
        literary_mappings = {
            # Séries populaires → genres/thèmes similaires
            r'\b(harry potter|hp)\b': 'fantasy magic young adult coming of age school adventure',
            r'\b(hunger games|suzanne collins)\b': 'dystopian young adult survival romance rebellion',
            r'\b(twilight|stephenie meyer)\b': 'paranormal romance vampire fantasy young adult',
            r'\b(game of thrones|asoiaf|george martin)\b': 'epic fantasy political intrigue medieval adult',
            r'\b(lord of the rings|tolkien|lotr)\b': 'high fantasy epic adventure magic medieval heroic',
            r'\b(star wars)\b': 'space opera science fiction adventure heroes',
            r'\b(stephen king)\b': 'horror supernatural thriller suspense',
            r'\b(agatha christie|hercule poirot)\b': 'mystery detective crime puzzle cozy mystery',
            r'\b(sherlock holmes|arthur conan doyle)\b': 'detective mystery crime investigation victorian',
            
            # Genres explicites
            r'\b(fantasy|fantastique)\b': 'fantasy magic adventure medieval mythology',
            r'\b(science fiction|sci-fi|sf)\b': 'science fiction space future technology dystopian',
            r'\b(romance)\b': 'romance love relationship contemporary historical',
            r'\b(thriller|suspense)\b': 'thriller suspense mystery crime psychological',
            r'\b(horror|horreur)\b': 'horror supernatural scary thriller dark',
            r'\b(mystery|mystère|police)\b': 'mystery detective crime investigation puzzle',
            r'\b(historical|historique)\b': 'historical fiction period drama war biography',
            r'\b(young adult|ado|adolescent)\b': 'young adult coming of age teen romance contemporary',
            
            # Thèmes et ambiances
            r'\b(magic|magie|magical)\b': 'fantasy magic supernatural paranormal wizards',
            r'\b(vampire|vampires)\b': 'paranormal romance vampire supernatural dark fantasy',
            r'\b(dystopian|dystopie)\b': 'dystopian science fiction future society rebellion',
            r'\b(war|guerre|world war)\b': 'historical fiction war military biography drama',
            r'\b(love|amour|romantic)\b': 'romance contemporary love relationship drama',
            r'\b(adventure|aventure)\b': 'adventure action quest journey exploration',
            
            # Intentions de lecture
            r'\b(terminer|fini|finished|similar|similaire|like|comme)\b': '',
            r'\b(style|genre|type)\b': '',
            r'\b(serie|series|saga)\b': '',
        }
        
        # Extraction intelligente des termes littéraires
        enhanced_query = query.lower()
        extracted_terms = []
        
        for pattern, literary_terms in literary_mappings.items():
            if re.search(pattern, enhanced_query, re.IGNORECASE):
                if literary_terms:  # Ignorer les patterns vides (mots à supprimer)
                    extracted_terms.append(literary_terms)
        
        # Si des termes littéraires sont trouvés, les utiliser
        if extracted_terms:
            enhanced_query = ' '.join(extracted_terms)
            # Éviter les doublons exacts du même livre en excluant les titres spécifiques
            enhanced_query = re.sub(r'\b(harry potter|hunger games|twilight)\b', '', enhanced_query, flags=re.IGNORECASE)
        else:
            # Fallback: si aucun terme littéraire détecté, suggérer des genres populaires
            enhanced_query = 'fiction contemporary popular bestseller'
        
        # Ajouter les préférences utilisateur
        if user_preferences:
            if 'preferred_genres' in user_preferences:
                genres = user_preferences['preferred_genres']
                if genres:
                    enhanced_query += f" {' '.join(genres)}"
            
            if 'preferred_reading_difficulty' in user_preferences:
                difficulty = user_preferences['preferred_reading_difficulty']
                if difficulty:
                    enhanced_query += f" {difficulty}"
            
            if 'preferred_themes' in user_preferences:
                themes = user_preferences['preferred_themes']
                if themes:
                    enhanced_query += f" {' '.join(themes)}"
            
            if 'favorite_authors' in user_preferences:
                authors = user_preferences['favorite_authors']
                if authors:
                    enhanced_query += f" {' '.join(authors)}"
        
        logger.info(f"Requête littéraire originale: '{query}' -> Requête enrichie: '{enhanced_query}'")
        return enhanced_query
    
    def get_book_recommendations(self, user_id: int, query: str, 
                               n_recommendations: int = 3) -> List[Dict[str, Any]]:
        """Génère des recommandations de livres littéraires pour un utilisateur"""
        try:
            # Récupérer les préférences utilisateur
            from apps.accounts.models import UserProfile
            try:
                user_profile = UserProfile.objects.get(user_id=user_id)
                user_preferences = {
                    'preferred_genres': [
                        genre.name for genre in user_profile.preferred_genres.all()
                    ],
                    'preferred_reading_difficulty': user_profile.preferred_reading_difficulty,
                    'preferred_themes': user_profile.preferred_themes.split(',') if user_profile.preferred_themes else [],
                    'favorite_authors': user_profile.favorite_authors.split(',') if user_profile.favorite_authors else []
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
                    book = LiteratureBook.objects.get(id=result['book_id'])
                    recommendation = {
                        'book': {
                            'id': book.id,
                            'title': book.title,
                            'authors': book.authors,
                            'description': book.description,
                            'average_rating': float(book.average_rating) if book.average_rating else 0.0,
                            'published_year': book.published_year,
                            'categories': book.categories,
                            'reading_difficulty': book.get_reading_difficulty_display(),
                            'themes': book.themes,
                            'thumbnail': book.thumbnail,
                        },
                        'similarity_score': result['similarity_score'],
                        'reason': self._generate_recommendation_reason(book, result, user_preferences)
                    }
                    recommendations.append(recommendation)
                except LiteratureBook.DoesNotExist:
                    continue
            
            logger.info(f"Recommandations générées: {len(recommendations)} livres")
            return recommendations
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération des recommandations: {e}")
            return []
    
    def _generate_recommendation_reason(self, book: LiteratureBook, search_result: Dict[str, Any],
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
        if book.average_rating and book.average_rating >= 4.5:
            reasons.append(f"Excellente note ({book.average_rating}/5)")
        elif book.average_rating and book.average_rating >= 4.0:
            reasons.append(f"Bien noté ({book.average_rating}/5)")
        
        if book.popularity_rating and book.popularity_rating >= 4.0:
            reasons.append("Livre populaire")
        
        if book.ratings_count and book.ratings_count > 1000:
            reasons.append("Très lu et commenté")
        
        # Correspondance avec les préférences
        if user_preferences:
            if user_preferences.get('preferred_genres'):
                book_genres = set(book.genres.values_list('name', flat=True))
                user_genres = set(user_preferences['preferred_genres'])
                if book_genres.intersection(user_genres):
                    common_genres = book_genres.intersection(user_genres)
                    reasons.append(f"Correspond à vos genres préférés: {', '.join(common_genres)}")
            
            if (user_preferences.get('preferred_reading_difficulty') and 
                book.reading_difficulty == user_preferences['preferred_reading_difficulty']):
                reasons.append(f"Difficulté {book.get_reading_difficulty_display()} comme souhaité")
            
            if user_preferences.get('favorite_authors'):
                for author in user_preferences['favorite_authors']:
                    if author.lower() in book.authors.lower():
                        reasons.append(f"Auteur que vous appréciez: {author}")
                        break
        
        # Période de publication
        if book.published_year:
            if book.published_year >= 2020:
                reasons.append("Publication récente")
            elif book.published_year >= 2000:
                reasons.append("Publication moderne")
            elif book.published_year >= 1950:
                reasons.append("Classique moderne")
            else:
                reasons.append("Classique de la littérature")
        
        return " | ".join(reasons)
    
    def get_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques de la collection"""
        try:
            stats = self.chroma_manager.get_collection_stats(self.collection)
            db_count = LiteratureBook.objects.count()
            
            return {
                'collection_name': self.collection_name,
                'indexed_books': stats.get('count', 0),
                'total_books_in_db': db_count,
                'sync_status': 'synchronized' if stats.get('count', 0) == db_count else 'out_of_sync'
            }
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des stats: {e}")
            return {'error': str(e)}