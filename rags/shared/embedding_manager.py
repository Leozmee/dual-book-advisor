"""
Gestionnaire d'embeddings partagé pour les systèmes RAG
"""
import os
import logging
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import numpy as np

logger = logging.getLogger(__name__)


class EmbeddingManager:
    """Gestionnaire des embeddings pour ChromaDB"""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Charge le modèle d'embedding"""
        try:
            logger.info(f"Chargement du modèle d'embedding: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info("Modèle d'embedding chargé avec succès")
        except Exception as e:
            logger.error(f"Erreur lors du chargement du modèle: {e}")
            raise
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Génère les embeddings pour une liste de textes"""
        if not self.model:
            raise ValueError("Modèle d'embedding non chargé")
        
        try:
            embeddings = self.model.encode(texts, convert_to_tensor=False)
            # Convertir en liste de listes pour ChromaDB
            return [embedding.tolist() for embedding in embeddings]
        except Exception as e:
            logger.error(f"Erreur lors de la génération des embeddings: {e}")
            raise
    
    def generate_single_embedding(self, text: str) -> List[float]:
        """Génère l'embedding pour un seul texte"""
        embeddings = self.generate_embeddings([text])
        return embeddings[0]


class ChromaDBManager:
    """Gestionnaire ChromaDB pour les collections de livres"""
    
    def __init__(self, persist_directory: str):
        self.persist_directory = persist_directory
        self.client = None
        self.embedding_manager = EmbeddingManager()
        self._init_client()
    
    def _init_client(self):
        """Initialise le client ChromaDB"""
        try:
            # Créer le répertoire s'il n'existe pas
            os.makedirs(self.persist_directory, exist_ok=True)
            
            # Initialiser le client ChromaDB
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            logger.info(f"Client ChromaDB initialisé: {self.persist_directory}")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation de ChromaDB: {e}")
            raise
    
    def create_collection(self, collection_name: str, reset: bool = False) -> chromadb.Collection:
        """Crée ou récupère une collection ChromaDB"""
        try:
            if reset:
                try:
                    self.client.delete_collection(collection_name)
                    logger.info(f"Collection {collection_name} supprimée")
                except Exception:
                    pass  # Collection n'existe pas
            
            collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Collection {collection_name} créée/récupérée")
            return collection
        except Exception as e:
            logger.error(f"Erreur lors de la création de la collection {collection_name}: {e}")
            raise
    
    def add_documents(self, collection: chromadb.Collection, documents: List[Dict[str, Any]]):
        """Ajoute des documents à une collection"""
        try:
            texts = [doc['text'] for doc in documents]
            ids = [doc['id'] for doc in documents]
            metadatas = [doc.get('metadata', {}) for doc in documents]
            
            # Générer les embeddings
            logger.info(f"Génération des embeddings pour {len(texts)} documents...")
            embeddings = self.embedding_manager.generate_embeddings(texts)
            
            # Ajouter à ChromaDB
            collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"{len(documents)} documents ajoutés à la collection")
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout des documents: {e}")
            raise
    
    def search_similar(self, collection: chromadb.Collection, query: str, 
                      n_results: int = 5, similarity_threshold: float = 0.7) -> Dict[str, Any]:
        """Recherche des documents similaires"""
        try:
            # Générer l'embedding de la requête
            query_embedding = self.embedding_manager.generate_single_embedding(query)
            
            # Rechercher dans ChromaDB
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Filtrer par seuil de similarité (distance < 1 - similarité)
            filtered_results = {
                'documents': [],
                'metadatas': [],
                'distances': [],
                'ids': []
            }
            
            if results['distances'] and results['distances'][0]:
                for i, distance in enumerate(results['distances'][0]):
                    similarity = 1 - distance
                    if similarity >= similarity_threshold:
                        filtered_results['documents'].append(results['documents'][0][i])
                        filtered_results['metadatas'].append(results['metadatas'][0][i])
                        filtered_results['distances'].append(distance)
                        filtered_results['ids'].append(results['ids'][0][i])
            
            logger.info(f"Recherche terminée: {len(filtered_results['documents'])} résultats trouvés")
            return filtered_results
        except Exception as e:
            logger.error(f"Erreur lors de la recherche: {e}")
            raise
    
    def get_collection_stats(self, collection: chromadb.Collection) -> Dict[str, Any]:
        """Récupère les statistiques d'une collection"""
        try:
            count = collection.count()
            return {
                'name': collection.name,
                'count': count,
                'metadata': collection.metadata
            }
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des stats: {e}")
            return {'error': str(e)}