"""
Service de recherche d'images de couvertures pour les livres, mangas et comics
Fichier: agents/cover_image_service.py
"""
import logging
import requests
import time
from typing import Dict, Optional, List
from urllib.parse import quote_plus
import re

logger = logging.getLogger(__name__)


class CoverImageService:
    """Service pour récupérer les images de couvertures"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'DualBookAdvisor/1.0 (Educational Project)'
        })
        
        # Cache simple en mémoire
        self._cache = {}
        
        # Rate limiting
        self._last_request_time = {}
        self._min_interval = {
            'google_books': 0.1,  # 10 requêtes par seconde max
            'open_library': 0.2,  # 5 requêtes par seconde max
            'anilist': 0.5        # 2 requêtes par seconde max
        }
    
    def get_cover_image(self, title: str, author: str = "", content_type: str = "book") -> Optional[str]:
        """
        Récupère l'URL de l'image de couverture avec stratégies optimisées par agent
        
        Args:
            title: Titre de l'œuvre
            author: Auteur/créateur (optionnel)
            content_type: Type de contenu ("book", "manga", "comics")
        
        Returns:
            URL de l'image ou None
        """
        try:
            # Créer une clé de cache
            cache_key = f"{content_type}:{title.lower()}:{author.lower()}"
            
            # Vérifier le cache
            if cache_key in self._cache:
                logger.info(f"📸 Image trouvée en cache pour: {title}")
                return self._cache[cache_key]
            
            # Nettoyer les titres pour la recherche
            clean_title = self._clean_title(title)
            clean_author = self._clean_author(author)
            
            logger.info(f"🔍 Recherche d'image pour: {clean_title} par {clean_author} (type: {content_type})")
            
            # Stratégies optimisées selon l'agent
            image_url = None
            
            if content_type == "manga":
                # AGENT MANGA: AniList en priorité absolue pour les mangas japonais
                logger.info("🎌 Stratégie manga: AniList prioritaire")
                image_url = self._search_anilist(clean_title, "MANGA")
                # Pas de fallback - AniList est la source de référence pour les mangas
            
            elif content_type == "comics":
                # AGENT MANGA/COMICS: AniList puis Google Books pour comics/BD
                logger.info("🦸 Stratégie comics: AniList puis Google Books")
                image_url = self._search_anilist(clean_title, "MANGA")  # Peut contenir des webtoons/manhwa
                if not image_url:
                    image_url = self._search_google_books(clean_title, clean_author, "comics")
            
            else:  # books/literature
                # AGENT LITTERATURE: Google Books puis Open Library (PAS d'AniList)
                logger.info("📚 Stratégie littérature: Google Books puis Open Library")
                image_url = self._search_google_books(clean_title, clean_author, "book")
                if not image_url:
                    image_url = self._search_open_library(clean_title, clean_author)
                # AniList exclu pour éviter les contaminations manga/anime
            
            # Mettre en cache le résultat
            self._cache[cache_key] = image_url
            
            if image_url:
                logger.info(f"✅ Image trouvée: {image_url[:100]}...")
            else:
                logger.warning(f"❌ Aucune image trouvée pour: {title}")
            
            return image_url
            
        except Exception as e:
            logger.error(f"❌ Erreur recherche image pour {title}: {e}")
            return None
    
    def _clean_title(self, title: str) -> str:
        """Nettoie le titre pour la recherche"""
        if not title:
            return ""
        
        # Supprimer les caractères spéciaux et normaliser
        clean = re.sub(r'[^\w\s-]', ' ', title)
        clean = re.sub(r'\s+', ' ', clean).strip()
        
        # Supprimer les parties communes qui polluent la recherche
        patterns_to_remove = [
            r'\b(tome|volume|vol|chapter|chapitre)\s*\d+\b',
            r'\b(série|series|saga)\b',
            r'\b(edition|édition)\b',
            r'\([^)]*\)',  # Tout entre parenthèses
        ]
        
        for pattern in patterns_to_remove:
            clean = re.sub(pattern, ' ', clean, flags=re.IGNORECASE)
        
        return re.sub(r'\s+', ' ', clean).strip()
    
    def _clean_author(self, author: str) -> str:
        """Nettoie le nom de l'auteur"""
        if not author:
            return ""
        
        # Prendre seulement le premier auteur si plusieurs
        clean = author.split(',')[0].split(';')[0].strip()
        
        # Supprimer les titres et suffixes
        clean = re.sub(r'\b(dr|prof|mr|mrs|ms|phd|jr|sr)\b\.?', '', clean, flags=re.IGNORECASE)
        
        return clean.strip()
    
    def _wait_for_rate_limit(self, service: str):
        """Respecte le rate limiting"""
        current_time = time.time()
        last_time = self._last_request_time.get(service, 0)
        min_interval = self._min_interval.get(service, 1.0)
        
        time_since_last = current_time - last_time
        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            time.sleep(sleep_time)
        
        self._last_request_time[service] = time.time()
    
    def _search_google_books(self, title: str, author: str = "", book_type: str = "book") -> Optional[str]:
        """Recherche via Google Books API"""
        try:
            self._wait_for_rate_limit('google_books')
            
            # Construire la requête
            query_parts = [title]
            if author:
                query_parts.append(f"inauthor:{author}")
            
            query = " ".join(query_parts)
            
            url = "https://www.googleapis.com/books/v1/volumes"
            params = {
                'q': query,
                'maxResults': 5,
                'fields': 'items(volumeInfo(title,authors,imageLinks))'
            }
            
            logger.debug(f"🔍 Google Books query: {query}")
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            items = data.get('items', [])
            
            for item in items:
                volume_info = item.get('volumeInfo', {})
                image_links = volume_info.get('imageLinks', {})
                
                # Préférer les images de haute qualité
                for size in ['extraLarge', 'large', 'medium', 'thumbnail']:
                    if size in image_links:
                        image_url = image_links[size]
                        # Forcer HTTPS
                        image_url = image_url.replace('http://', 'https://')
                        logger.info(f"📚 Google Books trouvé ({size}): {volume_info.get('title', 'N/A')}")
                        return image_url
            
            logger.info(f"📚 Google Books: Aucune image trouvée pour {title}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Erreur Google Books pour {title}: {e}")
            return None
    
    def _search_open_library(self, title: str, author: str = "") -> Optional[str]:
        """Recherche via Open Library"""
        try:
            self._wait_for_rate_limit('open_library')
            
            # Recherche de livre
            url = "https://openlibrary.org/search.json"
            params = {
                'title': title,
                'author': author,
                'limit': 5,
                'fields': 'key,title,author_name,cover_i'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            docs = data.get('docs', [])
            
            for doc in docs:
                cover_i = doc.get('cover_i')
                if cover_i:
                    # URL de l'image de couverture (Large size)
                    image_url = f"https://covers.openlibrary.org/b/id/{cover_i}-L.jpg"
                    logger.info(f"📖 Open Library trouvé: {doc.get('title', 'N/A')}")
                    return image_url
            
            logger.info(f"📖 Open Library: Aucune image trouvée pour {title}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Erreur Open Library pour {title}: {e}")
            return None
    
    def _search_anilist(self, title: str, media_type: str = "MANGA") -> Optional[str]:
        """Recherche via AniList GraphQL API optimisée pour mangas/anime"""
        try:
            self._wait_for_rate_limit('anilist')
            
            # GraphQL query optimisée pour AniList
            query = """
            query ($search: String, $type: MediaType) {
                Page(page: 1, perPage: 8) {
                    media(search: $search, type: $type, sort: [POPULARITY_DESC, SCORE_DESC]) {
                        title {
                            romaji
                            english
                            native
                        }
                        coverImage {
                            extraLarge
                            large
                            medium
                        }
                        popularity
                        averageScore
                        genres
                        format
                    }
                }
            }
            """
            
            variables = {
                'search': title,
                'type': media_type
            }
            
            url = 'https://graphql.anilist.co'
            payload = {
                'query': query,
                'variables': variables
            }
            
            logger.debug(f"🎌 AniList query pour: {title} (type: {media_type})")
            response = self.session.post(url, json=payload, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            media_list = data.get('data', {}).get('Page', {}).get('media', [])
            
            # Trier par pertinence (popularité + score)
            for media in media_list:
                cover_image = media.get('coverImage', {})
                title_info = media.get('title', {})
                popularity = media.get('popularity', 0)
                score = media.get('averageScore', 0)
                
                # Vérifier la qualité du match (avec sécurité contre None)
                romaji_title = (title_info.get('romaji') or '').lower()
                english_title = (title_info.get('english') or '').lower()
                native_title = (title_info.get('native') or '').lower()
                search_title = title.lower()
                
                # Score de correspondance simple
                match_score = 0
                if search_title in romaji_title or romaji_title in search_title:
                    match_score += 3
                if search_title in english_title or english_title in search_title:
                    match_score += 3
                if search_title in native_title or native_title in search_title:
                    match_score += 2
                
                # Accepter si bon match, très populaire, ou au moins un match partiel
                if match_score >= 2 or popularity > 50000 or match_score >= 1:
                    # Préférer les images de haute qualité
                    for size in ['extraLarge', 'large', 'medium']:
                        if cover_image.get(size):
                            image_url = cover_image[size]
                            matched_title = title_info.get('romaji') or title_info.get('english') or 'N/A'
                            logger.info(f"🎌 AniList trouvé ({size}): {matched_title} (score: {score}, pop: {popularity})")
                            return image_url
            
            logger.info(f"🎌 AniList: Aucune image pertinente trouvée pour {title}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Erreur AniList pour {title}: {e}")
            return None
    
    def get_multiple_covers(self, items: List[Dict]) -> List[Dict]:
        """
        Récupère les images pour une liste d'œuvres
        
        Args:
            items: Liste de dictionnaires avec 'title', 'author', 'type'
        
        Returns:
            Liste enrichie avec 'cover_image_url'
        """
        enriched_items = []
        
        for item in items:
            title = item.get('title', '')
            author = item.get('author', item.get('authors', ''))
            content_type = item.get('type', 'book')
            
            # Récupérer l'image
            cover_url = self.get_cover_image(title, author, content_type)
            
            # Ajouter l'URL de l'image à l'item
            enriched_item = item.copy()
            enriched_item['cover_image_url'] = cover_url
            
            enriched_items.append(enriched_item)
            
            # Petit délai pour éviter de surcharger les APIs
            time.sleep(0.1)
        
        return enriched_items
    
    def health_check(self) -> Dict[str, bool]:
        """Vérifie la disponibilité des services"""
        services = {}
        
        # Test Google Books
        try:
            response = self.session.get(
                "https://www.googleapis.com/books/v1/volumes?q=test&maxResults=1", 
                timeout=5
            )
            services['google_books'] = response.status_code == 200
        except:
            services['google_books'] = False
        
        # Test Open Library
        try:
            response = self.session.get(
                "https://openlibrary.org/search.json?title=test&limit=1", 
                timeout=5
            )
            services['open_library'] = response.status_code == 200
        except:
            services['open_library'] = False
        
        # Test AniList
        try:
            response = self.session.post(
                "https://graphql.anilist.co",
                json={'query': '{ Page(page: 1, perPage: 1) { media(type: MANGA) { id } } }'},
                timeout=5
            )
            services['anilist'] = response.status_code == 200
        except:
            services['anilist'] = False
        
        return services
    
    def clear_cache(self):
        """Vide le cache"""
        self._cache.clear()
        logger.info("🗑️ Cache d'images vidé")
    
    def get_cache_stats(self) -> Dict:
        """Statistiques du cache"""
        return {
            'cached_items': len(self._cache),
            'cache_keys': list(self._cache.keys())[:10]  # Premiers 10 pour debug
        }


# Instance globale du service
cover_service = CoverImageService()