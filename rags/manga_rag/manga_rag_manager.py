"""
Gestionnaire RAG unifié pour les mangas et comics/BD
Fichier: rags/manga_rag/manga_rag_manager.py
"""
import logging
from typing import List, Dict, Any, Optional
from django.conf import settings
from pathlib import Path
import pandas as pd
import ast
import time
from rags.shared.embedding_manager import ChromaDBManager

logger = logging.getLogger(__name__)


class MangaRAGManager:
    """Gestionnaire RAG unifié pour mangas japonais et comics/BD françaises"""
    
    def __init__(self):
        self.chroma_path = Path(settings.BASE_DIR) / 'rags' / 'manga_rag' / 'chroma_db'
        
        # Deux sources de données
        self.manga_data_path = Path(settings.BASE_DIR) / 'rags' / 'manga_rag' / 'data' / 'manga_data.csv'
        self.comics_data_path = Path(settings.BASE_DIR) / 'rags' / 'manga_rag' / 'data' / 'albums_from_seen_clean.csv'
        
        self.collection_name = "manga_comics_collection"
        self.chroma_manager = ChromaDBManager(str(self.chroma_path))
        self.collection = None
        self._init_collection()
    
    def _init_collection(self):
        """Initialise la collection ChromaDB pour mangas et comics"""
        try:
            # Créer le dossier s'il n'existe pas
            self.chroma_path.mkdir(parents=True, exist_ok=True)
            
            self.collection = self.chroma_manager.create_collection(self.collection_name)
            logger.info(f"Collection manga/comics {self.collection_name} initialisée")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation de la collection manga/comics: {e}")
            raise
    
    def load_manga_data(self) -> pd.DataFrame:
        """Charge les données manga japonais depuis le CSV"""
        try:
            if not self.manga_data_path.exists():
                logger.warning(f"Fichier manga japonais non trouvé: {self.manga_data_path}")
                return pd.DataFrame()
            
            # Lire le CSV manga avec gestion d'erreurs
            df = pd.read_csv(
                self.manga_data_path,
                encoding='utf-8',
                quotechar='"',
                escapechar='\\',
                on_bad_lines='skip'
            )
            
            # Nettoyer les données
            df = df.fillna('')
            
            # Nettoyer la colonne tags si elle contient des listes Python
            if 'tags' in df.columns:
                df['tags'] = df['tags'].apply(self._clean_tags_column)
            
            # Ajouter une colonne pour identifier le type
            df['source_type'] = 'manga_japonais'
            
            logger.info(f"📊 {len(df)} mangas japonais chargés depuis {self.manga_data_path}")
            return df
            
        except Exception as e:
            logger.error(f"Erreur chargement manga data: {e}")
            return pd.DataFrame()
    
    def load_comics_data(self) -> pd.DataFrame:
        """Charge les données comics/BD françaises depuis le CSV"""
        try:
            if not self.comics_data_path.exists():
                logger.warning(f"Fichier comics non trouvé: {self.comics_data_path}")
                return pd.DataFrame()
            
            # Lire le CSV comics avec la structure spécifique
            df = pd.read_csv(
                self.comics_data_path,
                encoding='utf-8',
                quotechar='"',
                escapechar='\\',
                on_bad_lines='skip'
            )
            
            # Nettoyer les données
            df = df.fillna('')
            
            # Normaliser les colonnes pour correspondre au format manga
            comics_normalized = pd.DataFrame()
            comics_normalized['title'] = df.get('titre', '')
            comics_normalized['description'] = df.get('synopsis', '')
            comics_normalized['rating'] = pd.to_numeric(df.get('note', 0), errors='coerce').fillna(0)
            comics_normalized['year'] = 0  # Pas d'année dans les comics
            comics_normalized['tags'] = df.get('genre', '') + ', ' + df.get('publisher', '')
            comics_normalized['cover'] = ''  # Pas de cover dans les comics
            comics_normalized['author'] = df.get('auteur', '')
            comics_normalized['publisher'] = df.get('publisher', '')
            comics_normalized['nb_notes'] = pd.to_numeric(df.get('nb_notes', 0), errors='coerce').fillna(0)
            comics_normalized['source_type'] = 'comics_bd'
            
            logger.info(f"📊 {len(comics_normalized)} comics/BD chargés depuis {self.comics_data_path}")
            return comics_normalized
            
        except Exception as e:
            logger.error(f"Erreur chargement comics data: {e}")
            return pd.DataFrame()
    
    def load_all_data(self) -> pd.DataFrame:
        """Charge et combine toutes les données (mangas + comics)"""
        try:
            manga_df = self.load_manga_data()
            comics_df = self.load_comics_data()
            
            # Combiner les deux DataFrames
            all_data = []
            
            if not manga_df.empty:
                all_data.append(manga_df)
            
            if not comics_df.empty:
                all_data.append(comics_df)
            
            if all_data:
                combined_df = pd.concat(all_data, ignore_index=True, sort=False)
                logger.info(f"📊 Total combiné: {len(combined_df)} entrées ({len(manga_df)} mangas + {len(comics_df)} comics)")
                return combined_df
            else:
                logger.warning("Aucune donnée manga/comics trouvée")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Erreur lors de la combinaison des données: {e}")
            return pd.DataFrame()
    
    def _clean_tags_column(self, tags_str):
        """Nettoie la colonne tags qui contient des listes Python"""
        if not tags_str or tags_str == '':
            return 'Manga'
        
        try:
            # Si c'est déjà une liste Python en string, l'évaluer
            if tags_str.startswith('[') and tags_str.endswith(']'):
                tags_list = ast.literal_eval(tags_str)
                return ', '.join(tags_list)
            else:
                # Si c'est déjà une string simple
                return str(tags_str)
        except:
            # En cas d'erreur, nettoyer manuellement
            clean_tags = tags_str.replace('[', '').replace(']', '').replace("'", "").replace('"', '')
            return clean_tags
    
    def index_all_content(self, reset: bool = False):
        """Indexe tous les mangas et comics dans ChromaDB"""
        try:
            if reset:
                self.collection = self.chroma_manager.create_collection(
                    self.collection_name, reset=True
                )
            
            # Charger toutes les données combinées
            all_data = self.load_all_data()
            
            if all_data.empty:
                logger.warning("Aucune donnée manga/comics à indexer")
                return
            
            logger.info(f"Indexation de {len(all_data)} entrées manga/comics...")
            
            documents = []
            for index, row in all_data.iterrows():
                try:
                    # Construire le texte pour l'embedding selon le type
                    if row.get('source_type') == 'comics_bd':
                        text_content = self._build_comics_text(row)
                        doc_id = f"comics_{index}"
                        doc_type = 'comics'
                    else:
                        text_content = self._build_manga_text(row)
                        doc_id = f"manga_{index}"
                        doc_type = 'manga'
                    
                    # Préparer les métadonnées unifiées
                    metadata = {
                        'doc_id': doc_id,
                        'title': str(row.get('title', '')).strip()[:500],
                        'description': str(row.get('description', '')).strip()[:1000],
                        'rating': float(row.get('rating', 0)) if pd.notna(row.get('rating')) else 0.0,
                        'year': int(row.get('year', 0)) if pd.notna(row.get('year')) and row.get('year', 0) > 0 else 0,
                        'tags': str(row.get('tags', '')).strip()[:300],
                        'cover': str(row.get('cover', '')).strip(),
                        'author': str(row.get('author', '')).strip()[:300],
                        'publisher': str(row.get('publisher', '')).strip()[:200],
                        'nb_notes': int(row.get('nb_notes', 0)) if pd.notna(row.get('nb_notes')) else 0,
                        'source_type': row.get('source_type', 'unknown'),
                        'type': doc_type
                    }
                    
                    documents.append({
                        'id': doc_id,
                        'text': text_content,
                        'metadata': metadata
                    })
                    
                except Exception as e:
                    logger.warning(f"Erreur traitement ligne {index}: {e}")
                    continue
            
            if documents:
                # Indexer par lots
                batch_size = 50
                for i in range(0, len(documents), batch_size):
                    batch = documents[i:i + batch_size]
                    self.chroma_manager.add_documents(self.collection, batch)
                    logger.info(f"Lot {i//batch_size + 1} indexé ({len(batch)} entrées)")
                
                logger.info(f"✅ Indexation terminée: {len(documents)} entrées indexées")
            else:
                logger.warning("Aucun document à indexer")
                
        except Exception as e:
            logger.error(f"Erreur lors de l'indexation: {e}")
            raise
    
    # Conserver l'ancienne méthode pour compatibilité
    def index_all_manga(self, reset: bool = False):
        """Alias pour compatibilité - indexe tout le contenu"""
        return self.index_all_content(reset)
    
    def _build_manga_text(self, manga_row) -> str:
        """Construit le texte d'un manga japonais pour l'embedding"""
        text_parts = []
        
        # Titre
        title = str(manga_row.get('title', '')).strip()
        if title:
            text_parts.append(f"Titre: {title}")
        
        # Description
        description = str(manga_row.get('description', '')).strip()
        if description:
            text_parts.append(f"Description: {description}")
        
        # Tags/Genres
        tags = str(manga_row.get('tags', '')).strip()
        if tags:
            text_parts.append(f"Genres: {tags}")
        
        # Année
        year = manga_row.get('year')
        if year and pd.notna(year):
            try:
                year_int = int(float(year))
                if 1900 <= year_int <= 2025:
                    text_parts.append(f"Année: {year_int}")
            except:
                pass
        
        # Note
        rating = manga_row.get('rating')
        if rating and pd.notna(rating):
            try:
                rating_float = float(rating)
                if rating_float >= 4.0:
                    text_parts.append("Très bien noté")
                elif rating_float >= 3.5:
                    text_parts.append("Bien noté")
            except:
                pass
        
        # Ajouter des mots-clés manga
        text_parts.append("Manga japonais anime otaku bande dessinée")
        
        return ' | '.join(text_parts)
    
    def _build_comics_text(self, comics_row) -> str:
        """Construit le texte d'un comic/BD pour l'embedding"""
        text_parts = []
        
        # Titre
        title = str(comics_row.get('title', '')).strip()
        if title:
            text_parts.append(f"Titre: {title}")
        
        # Auteur
        author = str(comics_row.get('author', '')).strip()
        if author:
            text_parts.append(f"Auteur: {author}")
        
        # Description/Synopsis
        description = str(comics_row.get('description', '')).strip()
        if description:
            text_parts.append(f"Synopsis: {description}")
        
        # Tags/Genres
        tags = str(comics_row.get('tags', '')).strip()
        if tags:
            text_parts.append(f"Genre: {tags}")
        
        # Éditeur
        publisher = str(comics_row.get('publisher', '')).strip()
        if publisher:
            text_parts.append(f"Éditeur: {publisher}")
        
        # Note
        rating = comics_row.get('rating')
        if rating and pd.notna(rating):
            try:
                rating_float = float(rating)
                if rating_float >= 4.0:
                    text_parts.append("Très bien noté")
                elif rating_float >= 3.5:
                    text_parts.append("Bien noté")
            except:
                pass
        
        # Ajouter des mots-clés comics/BD
        text_parts.append("comics bande dessinée BD album graphique français")
        
        return ' | '.join(text_parts)
    
    def search_content(self, query: str, n_results: int = 5, content_type: str = 'all') -> List[Dict[str, Any]]:
        """Recherche dans mangas et/ou comics selon le type demandé"""
        try:
            # Enrichir la requête selon le type de contenu
            enhanced_query = self._enhance_unified_query(query, content_type)
            
            # Recherche dans ChromaDB avec seuil permissif
            similarity_threshold = 0.1
            results = self.chroma_manager.search_similar(
                collection=self.collection,
                query=enhanced_query,
                n_results=n_results * 3,  # Plus de candidats pour filtrer
                similarity_threshold=similarity_threshold
            )
            
            # Formater les résultats
            formatted_results = []
            for i, metadata in enumerate(results['metadatas']):
                # Filtrer par type si demandé
                if content_type != 'all':
                    if content_type == 'manga' and metadata.get('source_type') != 'manga_japonais':
                        continue
                    elif content_type == 'comics' and metadata.get('source_type') != 'comics_bd':
                        continue
                
                result = {
                    'doc_id': metadata['doc_id'],
                    'title': metadata['title'],
                    'description': metadata['description'],
                    'rating': metadata['rating'],
                    'year': metadata['year'],
                    'tags': metadata['tags'],
                    'cover': metadata.get('cover', ''),
                    'author': metadata.get('author', ''),
                    'publisher': metadata.get('publisher', ''),
                    'nb_notes': metadata.get('nb_notes', 0),
                    'source_type': metadata.get('source_type', 'unknown'),
                    'similarity_score': 1 - results['distances'][i],
                    'matched_text': results['documents'][i][:200] + '...' if len(results['documents'][i]) > 200 else results['documents'][i]
                }
                formatted_results.append(result)
            
            # Trier par score et note
            formatted_results.sort(key=lambda x: (x['similarity_score'], x['rating']), reverse=True)
            
            logger.info(f"Recherche terminée: {len(formatted_results)} résultats trouvés (type: {content_type})")
            return formatted_results[:n_results]
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche: {e}")
            return []
    
    # Conserver l'ancienne méthode pour compatibilité
    def search_manga(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Alias pour compatibilité - recherche dans tout le contenu"""
        return self.search_content(query, n_results, 'all')
    
    def _enhance_unified_query(self, query: str, content_type: str = 'all') -> str:
        """Enrichit la requête pour mangas et comics"""
        import re
        
        query_lower = query.lower()
        enhanced_parts = [query]
        
        # Détection automatique du type si pas spécifié
        auto_detected_type = self._detect_content_type(query_lower)
        if content_type == 'all':
            content_type = auto_detected_type
        
        # Mappings pour mangas japonais
        manga_mappings = {
            r'\b(naruto)\b': 'ninja village hidden leaf Uzumaki Sasuke Sakura action adventure friendship',
            r'\b(one piece)\b': 'pirate treasure Luffy Straw Hat Grand Line adventure comedy action',
            r'\b(dragon ball)\b': 'Goku martial arts power tournament Saiyan energy blast adventure',
            r'\b(attack on titan|shingeki no kyojin)\b': 'titan wall humanity survival military dark action',
            r'\b(death note)\b': 'Light Yagami L psychological thriller supernatural detective',
            r'\b(shounen)\b': 'action adventure friendship tournament power young male',
            r'\b(shoujo)\b': 'romance emotion relationship school young female',
            r'\b(seinen)\b': 'mature adult psychological complex dark realistic',
        }
        
        # Mappings pour comics/BD
        comics_mappings = {
            r'\b(superman|batman|wonder woman)\b': 'superhero DC comics cape costume hero villain',
            r'\b(spider-man|spiderman|x-men)\b': 'Marvel superhero mutant web slinger comic book',
            r'\b(tintin|astérix|lucky luke)\b': 'bande dessinée française classique aventure humour',
            r'\b(comics|bd|bande dessinée)\b': 'comics bande dessinée album graphique',
            r'\b(superhéros|super-héros)\b': 'superhero comic book cape costume power',
            r'\b(marvel|dc)\b': 'superhero comic book universe hero villain',
        }
        
        # Appliquer les mappings selon le type
        found_match = False
        
        if content_type in ['all', 'manga']:
            for pattern, expansion in manga_mappings.items():
                if re.search(pattern, query_lower, re.IGNORECASE):
                    enhanced_parts.append(expansion)
                    found_match = True
                    break
        
        if content_type in ['all', 'comics'] and not found_match:
            for pattern, expansion in comics_mappings.items():
                if re.search(pattern, query_lower, re.IGNORECASE):
                    enhanced_parts.append(expansion)
                    found_match = True
                    break
        
        # Si aucune correspondance spécifique
        if not found_match:
            if content_type == 'manga':
                enhanced_parts.append('manga anime Japanese comic otaku')
            elif content_type == 'comics':
                enhanced_parts.append('comics bande dessinée BD album graphique français')
            else:
                enhanced_parts.append('manga anime comics bande dessinée')
        
        # Requêtes de similarité
        if any(word in query_lower for word in ['comme', 'similar', 'similaire', 'aimé', 'like']):
            enhanced_parts.append('similar recommendation suggest same genre style')
        
        return f"{query} {' '.join(enhanced_parts)}"
    
    def _detect_content_type(self, query_lower: str) -> str:
        """Détecte automatiquement le type de contenu recherché"""
        # Indicateurs manga
        manga_indicators = ['manga', 'anime', 'otaku', 'shounen', 'shoujo', 'seinen', 'naruto', 'one piece', 'dragon ball']
        # Indicateurs comics
        comics_indicators = ['comics', 'bd', 'bande dessinée', 'superhéros', 'superman', 'batman', 'marvel', 'dc', 'tintin', 'astérix']
        
        manga_score = sum(1 for indicator in manga_indicators if indicator in query_lower)
        comics_score = sum(1 for indicator in comics_indicators if indicator in query_lower)
        
        if manga_score > comics_score:
            return 'manga'
        elif comics_score > manga_score:
            return 'comics'
        else:
            return 'all'
    
    def get_content_recommendations(self, user_id: int, query: str, n_recommendations: int = 3, content_type: str = 'all') -> List[Dict[str, Any]]:
        """Génère des recommandations pour mangas et/ou comics"""
        try:
            start_time = time.time()
            
            # Rechercher du contenu
            results = self.search_content(
                query=query,
                n_results=n_recommendations,
                content_type=content_type
            )
            
            # Enrichir avec des raisons de recommandation
            recommendations = []
            for result in results:
                # Adapter la structure selon le type de source
                if result['source_type'] == 'comics_bd':
                    content_data = {
                        'id': result['doc_id'],
                        'title': result['title'],
                        'description': result['description'],
                        'rating': result['rating'],
                        'author': result['author'],
                        'publisher': result['publisher'],
                        'tags': result['tags'],
                        'nb_notes': result['nb_notes'],
                        'type': 'comics'
                    }
                else:
                    content_data = {
                        'id': result['doc_id'],
                        'title': result['title'],
                        'description': result['description'],
                        'rating': result['rating'],
                        'year': result['year'],
                        'tags': result['tags'],
                        'cover': result['cover'],
                        'type': 'manga'
                    }
                
                recommendation = {
                    'content': content_data,
                    'similarity_score': result['similarity_score'],
                    'reason': self._generate_unified_recommendation_reason(result, query)
                }
                recommendations.append(recommendation)
            
            processing_time = time.time() - start_time
            logger.info(f"Recommandations générées en {processing_time:.2f}s: {len(recommendations)} résultats")
            return recommendations
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération des recommandations: {e}")
            return []
    
    # Conserver l'ancienne méthode pour compatibilité
    def get_manga_recommendations(self, user_id: int, query: str, n_recommendations: int = 3) -> List[Dict[str, Any]]:
        """Alias pour compatibilité"""
        return self.get_content_recommendations(user_id, query, n_recommendations, 'all')
    
    def _generate_unified_recommendation_reason(self, result: Dict[str, Any], query: str) -> str:
        """Génère une explication pour la recommandation (manga ou comics)"""
        reasons = []
        
        # Score de similarité
        similarity_score = result['similarity_score']
        if similarity_score > 0.9:
            reasons.append("Correspond parfaitement à votre recherche")
        elif similarity_score > 0.7:
            reasons.append("Très pertinent pour votre recherche")
        else:
            reasons.append("Recommandé pour vous")
        
        # Qualité
        rating = result['rating']
        if rating >= 4.5:
            reasons.append(f"Excellente note ({rating}/5)")
        elif rating >= 4.0:
            reasons.append(f"Très bien noté ({rating}/5)")
        elif rating >= 3.5:
            reasons.append(f"Bien noté ({rating}/5)")
        
        # Type spécifique
        source_type = result.get('source_type', '')
        if source_type == 'comics_bd':
            reasons.append("Comics/BD française")
            # Popularité pour comics
            nb_notes = result.get('nb_notes', 0)
            if nb_notes > 100:
                reasons.append("Populaire auprès des lecteurs")
        else:
            reasons.append("Manga japonais")
            # Année pour mangas
            year = result.get('year', 0)
            if year and year >= 2015:
                reasons.append("Manga récent")
            elif year and year >= 2000:
                reasons.append("Manga moderne")
        
        # Tags/Genres
        tags = result.get('tags', '').lower()
        if 'action' in tags:
            reasons.append("Plein d'action")
        if 'aventure' in tags or 'adventure' in tags:
            reasons.append("Aventure captivante")
        if 'humour' in tags or 'comedy' in tags:
            reasons.append("Moments drôles")
        
        return " | ".join(reasons)
    
    def get_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques de la collection unifiée"""
        try:
            stats = self.chroma_manager.get_collection_stats(self.collection)
            
            # Charger les données pour compter
            manga_df = self.load_manga_data()
            comics_df = self.load_comics_data()
            
            manga_count = len(manga_df) if not manga_df.empty else 0
            comics_count = len(comics_df) if not comics_df.empty else 0
            total_csv_count = manga_count + comics_count
            
            return {
                'collection_name': self.collection_name,
                'indexed_total': stats.get('count', 0),
                'manga_in_csv': manga_count,
                'comics_in_csv': comics_count,
                'total_in_csv': total_csv_count,
                'sync_status': 'synchronized' if stats.get('count', 0) == total_csv_count else 'out_of_sync',
                'manga_data_path': str(self.manga_data_path),
                'comics_data_path': str(self.comics_data_path),
                'chroma_path': str(self.chroma_path)
            }
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des stats: {e}")
            return {'error': str(e)}
    
    def health_check(self) -> Dict[str, Any]:
        """Vérifie l'état du système manga/comics RAG"""
        try:
            # Test de recherche basique sur les deux types
            manga_test = self.search_content("naruto", n_results=1, content_type='manga')
            comics_test = self.search_content("superman", n_results=1, content_type='comics')
            
            return {
                "status": "healthy" if (manga_test or comics_test) else "warning",
                "collection_accessible": True,
                "manga_data_exists": self.manga_data_path.exists(),
                "comics_data_exists": self.comics_data_path.exists(),
                "manga_test_results": len(manga_test),
                "comics_test_results": len(comics_test),
                "stats": self.get_stats()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "collection_accessible": False,
                "manga_data_exists": self.manga_data_path.exists(),
                "comics_data_exists": self.comics_data_path.exists()
            }