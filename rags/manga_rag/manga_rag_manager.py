"""
Gestionnaire RAG complet spécialisé pour les mangas
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
    """Gestionnaire RAG spécialisé pour les mangas"""
    
    def __init__(self):
        self.chroma_path = Path(settings.BASE_DIR) / 'rags' / 'manga_rag' / 'chroma_db'
        self.data_path = Path(settings.BASE_DIR) / 'rags' / 'manga_rag' / 'data' / 'manga_data.csv'
        self.collection_name = "manga_collection"
        self.chroma_manager = ChromaDBManager(str(self.chroma_path))
        self.collection = None
        self._init_collection()
    
    def _init_collection(self):
        """Initialise la collection ChromaDB pour les mangas"""
        try:
            # Créer le dossier s'il n'existe pas
            self.chroma_path.mkdir(parents=True, exist_ok=True)
            
            self.collection = self.chroma_manager.create_collection(self.collection_name)
            logger.info(f"Collection manga {self.collection_name} initialisée")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation de la collection manga: {e}")
            raise
    
    def load_manga_data(self) -> pd.DataFrame:
        """Charge les données manga depuis le CSV"""
        try:
            if not self.data_path.exists():
                logger.error(f"Fichier manga non trouvé: {self.data_path}")
                return pd.DataFrame()
            
            # Lire le CSV manga avec gestion d'erreurs
            df = pd.read_csv(
                self.data_path,
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
            
            logger.info(f"📊 {len(df)} mangas chargés depuis {self.data_path}")
            return df
            
        except Exception as e:
            logger.error(f"Erreur chargement manga data: {e}")
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
    
    def index_all_manga(self, reset: bool = False):
        """Indexe tous les mangas dans ChromaDB"""
        try:
            if reset:
                self.collection = self.chroma_manager.create_collection(
                    self.collection_name, reset=True
                )
            
            # Charger les données manga
            manga_df = self.load_manga_data()
            
            if manga_df.empty:
                logger.warning("Aucune donnée manga à indexer")
                return
            
            logger.info(f"Indexation de {len(manga_df)} mangas...")
            
            documents = []
            for index, row in manga_df.iterrows():
                try:
                    # Construire le texte pour l'embedding
                    text_content = self._build_manga_text(row)
                    
                    # Préparer les métadonnées
                    metadata = {
                        'manga_id': f"manga_{index}",
                        'title': str(row.get('title', '')).strip()[:500],
                        'description': str(row.get('description', '')).strip()[:1000],
                        'rating': float(row.get('rating', 0)) if row.get('rating') else 0.0,
                        'year': int(row.get('year', 0)) if row.get('year') else 0,
                        'tags': str(row.get('tags', '')).strip()[:300],
                        'cover': str(row.get('cover', '')).strip(),
                        'type': 'manga'
                    }
                    
                    documents.append({
                        'id': f"manga_{index}",
                        'text': text_content,
                        'metadata': metadata
                    })
                    
                except Exception as e:
                    logger.warning(f"Erreur traitement manga ligne {index}: {e}")
                    continue
            
            if documents:
                # Indexer par lots
                batch_size = 50
                for i in range(0, len(documents), batch_size):
                    batch = documents[i:i + batch_size]
                    self.chroma_manager.add_documents(self.collection, batch)
                    logger.info(f"Lot manga {i//batch_size + 1} indexé ({len(batch)} mangas)")
                
                logger.info(f"✅ Indexation terminée: {len(documents)} mangas indexés")
            else:
                logger.warning("Aucun document manga à indexer")
                
        except Exception as e:
            logger.error(f"Erreur lors de l'indexation manga: {e}")
            raise
    
    def _build_manga_text(self, manga_row) -> str:
        """Construit le texte d'un manga pour l'embedding"""
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
        if year:
            try:
                year_int = int(float(year))
                if 1900 <= year_int <= 2025:
                    text_parts.append(f"Année: {year_int}")
            except:
                pass
        
        # Note
        rating = manga_row.get('rating')
        if rating:
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
    
    def search_manga(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Recherche des mangas basée sur une requête"""
        try:
            # Enrichir la requête pour les mangas
            enhanced_query = self._enhance_manga_query(query)
            
            # Recherche dans ChromaDB avec seuil très permissif pour les mangas
            similarity_threshold = 0.1  # Seuil très permissif pour capturer plus de mangas
            results = self.chroma_manager.search_similar(
                collection=self.collection,
                query=enhanced_query,
                n_results=n_results * 2,  # Chercher plus pour filtrer
                similarity_threshold=similarity_threshold
            )
            
            # Formater les résultats
            formatted_results = []
            for i, metadata in enumerate(results['metadatas']):
                result = {
                    'manga_id': metadata['manga_id'],
                    'title': metadata['title'],
                    'description': metadata['description'],
                    'rating': metadata['rating'],
                    'year': metadata['year'],
                    'tags': metadata['tags'],
                    'cover': metadata['cover'],
                    'similarity_score': 1 - results['distances'][i],
                    'matched_text': results['documents'][i][:200] + '...' if len(results['documents'][i]) > 200 else results['documents'][i]
                }
                formatted_results.append(result)
            
            # Trier par score et note
            formatted_results.sort(key=lambda x: (x['similarity_score'], x['rating']), reverse=True)
            
            logger.info(f"Recherche manga terminée: {len(formatted_results)} mangas trouvés")
            return formatted_results[:n_results]
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche manga: {e}")
            return []
    
    def _enhance_manga_query(self, query: str) -> str:
        """Enrichit la requête pour améliorer la recherche manga"""
        import re
        
        query_lower = query.lower()
        enhanced_parts = [query]
        
        # Mappings spécifiques aux mangas populaires
        manga_mappings = {
            # Mangas shounen populaires
            r'\b(naruto)\b': 'ninja village hidden leaf Uzumaki Sasuke Sakura action adventure friendship',
            r'\b(one piece)\b': 'pirate treasure Luffy Straw Hat Grand Line adventure comedy action',
            r'\b(dragon ball)\b': 'Goku martial arts power tournament Saiyan energy blast adventure',
            r'\b(attack on titan|shingeki no kyojin)\b': 'titan wall humanity survival military dark action',
            r'\b(death note)\b': 'Light Yagami L psychological thriller supernatural detective',
            r'\b(fullmetal alchemist)\b': 'Edward Elric alchemy military conspiracy adventure brotherhood',
            r'\b(bleach)\b': 'Ichigo soul reaper hollow spiritual sword fighting supernatural',
            r'\b(demon slayer|kimetsu no yaiba)\b': 'Tanjiro demon family revenge sword breathing technique',
            r'\b(tokyo ghoul)\b': 'Kaneki ghoul human transformation dark supernatural horror',
            r'\b(my hero academia|boku no hero)\b': 'Midoriya quirk superhero school All Might',
            
            # Mangas seinen
            r'\b(berserk)\b': 'Guts dark fantasy medieval violence mature seinen',
            r'\b(akira)\b': 'cyberpunk post-apocalyptic psychic powers Neo-Tokyo dystopian',
            r'\b(ghost in the shell)\b': 'cyborg cyberpunk philosophy technology future AI',
            
            # Mangas shoujo/romance
            r'\b(sailor moon)\b': 'magical girl transformation friendship love shoujo',
            r'\b(fruits basket)\b': 'zodiac curse romance slice of life shoujo drama',
            
            # Studios et réalisateurs
            r'\b(studio ghibli|ghibli)\b': 'Miyazaki fantasy adventure family magical realism',
            r'\b(spirited away)\b': 'Chihiro spirit world magical adventure family Ghibli',
            r'\b(princess mononoke)\b': 'nature spirits environment conflict fantasy Ghibli',
            r'\b(cowboy bebop)\b': 'space bounty hunter jazz noir adult sophisticated',
            
            # Genres manga
            r'\b(shounen)\b': 'action adventure friendship tournament power young male',
            r'\b(shoujo)\b': 'romance emotion relationship school young female',
            r'\b(seinen)\b': 'mature adult psychological complex dark realistic',
            r'\b(josei)\b': 'mature romance workplace adult woman realistic',
            r'\b(isekai)\b': 'other world transported fantasy adventure magic',
            r'\b(mecha)\b': 'robot pilot giant machine military technology action',
            r'\b(slice of life)\b': 'daily life realistic school friendship family',
            r'\b(sports)\b': 'competition training team effort victory sports manga',
            
            # Thèmes
            r'\b(ninja)\b': 'ninja stealth martial arts village hidden techniques',
            r'\b(samurai)\b': 'samurai sword honor feudal Japan bushido warrior',
            r'\b(magic)\b': 'magic spell wizard fantasy supernatural power mystical',
            r'\b(school)\b': 'school student uniform club friendship youth romance',
        }
        
        # Recherche de correspondances et enrichissement
        found_match = False
        for pattern, expansion in manga_mappings.items():
            if re.search(pattern, query_lower, re.IGNORECASE):
                enhanced_parts.append(expansion)
                found_match = True
                break  # Prendre la première correspondance principale
        
        # Si aucune correspondance spécifique, ajouter des termes génériques
        if not found_match:
            enhanced_parts.append('manga anime Japanese comic otaku')
        
        # Si c'est une requête de similarité (comme, similaire)
        if any(word in query_lower for word in ['comme', 'similar', 'similaire', 'aimé', 'like']):
            enhanced_parts.append('similar recommendation suggest same genre style')
        
        # Garder la requête originale + enrichissements
        return f"{query} {' '.join(enhanced_parts)}"
    
    def get_manga_recommendations(self, user_id: int, query: str, n_recommendations: int = 3) -> List[Dict[str, Any]]:
        """Génère des recommandations de manga personnalisées"""
        try:
            start_time = time.time()
            
            # Rechercher des mangas
            results = self.search_manga(
                query=query,
                n_results=n_recommendations
            )
            
            # Enrichir avec des raisons de recommandation
            recommendations = []
            for result in results:
                recommendation = {
                    'manga': {
                        'id': result['manga_id'],
                        'title': result['title'],
                        'description': result['description'],
                        'rating': result['rating'],
                        'year': result['year'],
                        'tags': result['tags'],
                        'cover': result['cover']
                    },
                    'similarity_score': result['similarity_score'],
                    'reason': self._generate_manga_recommendation_reason(result, query)
                }
                recommendations.append(recommendation)
            
            processing_time = time.time() - start_time
            logger.info(f"Recommandations manga générées en {processing_time:.2f}s: {len(recommendations)} résultats")
            return recommendations
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération des recommandations manga: {e}")
            return []
    
    def _generate_manga_recommendation_reason(self, manga_result: Dict[str, Any], query: str) -> str:
        """Génère une explication pour la recommandation manga"""
        reasons = []
        
        # Score de similarité
        similarity_score = manga_result['similarity_score']
        if similarity_score > 0.9:
            reasons.append("Correspond parfaitement à votre recherche")
        elif similarity_score > 0.7:
            reasons.append("Très pertinent pour votre recherche")
        else:
            reasons.append("Recommandé pour vous")
        
        # Qualité du manga
        rating = manga_result['rating']
        if rating >= 4.5:
            reasons.append(f"Excellente note ({rating}/5)")
        elif rating >= 4.0:
            reasons.append(f"Très bien noté ({rating}/5)")
        elif rating >= 3.5:
            reasons.append(f"Bien noté ({rating}/5)")
        
        # Analyse des tags
        tags = manga_result['tags'].lower()
        if 'shounen' in tags:
            reasons.append("Manga d'action et d'aventure (Shounen)")
        elif 'seinen' in tags:
            reasons.append("Manga mature et complexe (Seinen)")
        elif 'shoujo' in tags:
            reasons.append("Manga romantique et émotionnel (Shoujo)")
        
        # Thèmes populaires
        if any(theme in tags for theme in ['action', 'adventure', 'battle']):
            reasons.append("Plein d'action et d'aventure")
        if any(theme in tags for theme in ['romance', 'love', 'relationship']):
            reasons.append("Histoire d'amour touchante")
        if any(theme in tags for theme in ['comedy', 'humor', 'funny']):
            reasons.append("Moments drôles et divertissants")
        
        # Période
        year = manga_result['year']
        if year and year >= 2015:
            reasons.append("Manga récent")
        elif year and year >= 2000:
            reasons.append("Manga moderne")
        elif year and year >= 1990:
            reasons.append("Classique moderne")
        
        return " | ".join(reasons)
    
    def get_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques de la collection manga"""
        try:
            stats = self.chroma_manager.get_collection_stats(self.collection)
            
            # Charger les données pour compter
            manga_df = self.load_manga_data()
            csv_count = len(manga_df) if not manga_df.empty else 0
            
            return {
                'collection_name': self.collection_name,
                'indexed_manga': stats.get('count', 0),
                'total_manga_in_csv': csv_count,
                'sync_status': 'synchronized' if stats.get('count', 0) == csv_count else 'out_of_sync',
                'data_path': str(self.data_path),
                'chroma_path': str(self.chroma_path)
            }
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des stats manga: {e}")
            return {'error': str(e)}
    
    def health_check(self) -> Dict[str, Any]:
        """Vérifie l'état du système manga RAG"""
        try:
            # Test de recherche basique
            test_results = self.search_manga("naruto", n_results=1)
            
            return {
                "status": "healthy" if test_results else "warning",
                "collection_accessible": True,
                "data_file_exists": self.data_path.exists(),
                "test_search_results": len(test_results),
                "stats": self.get_stats()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "collection_accessible": False,
                "data_file_exists": self.data_path.exists()
            }