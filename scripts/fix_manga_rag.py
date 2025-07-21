#!/usr/bin/env python3
"""
Script pour corriger et initialiser le RAG manga
"""
import os
import sys
import django
from pathlib import Path
import pandas as pd
import numpy as np
import logging

# Configuration Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

django.setup()

from rags.manga_rag.manga_rag_manager import MangaRAGManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_manga_data(csv_path):
    """Nettoie les données manga du CSV"""
    print("🧹 Nettoyage des données manga...")
    
    try:
        # Charger le CSV
        df = pd.read_csv(csv_path, encoding='utf-8')
        print(f"📊 {len(df)} lignes chargées")
        
        # Nettoyer les données
        df = df.fillna('')
        
        # Nettoyer les colonnes numériques
        if 'rating' in df.columns:
            # Convertir rating en numérique, remplacer les erreurs par 0.0
            df['rating'] = pd.to_numeric(df['rating'], errors='coerce').fillna(0.0)
            
        if 'year' in df.columns:
            # Convertir year en entier, remplacer les erreurs par 0
            df['year'] = pd.to_numeric(df['year'], errors='coerce').fillna(0).astype(int)
        
        # Nettoyer les tags (convertir les listes Python en chaînes)
        if 'tags' in df.columns:
            df['tags'] = df['tags'].apply(lambda x: str(x) if x else '')
            
        # Nettoyer les descriptions
        if 'description' in df.columns:
            df['description'] = df['description'].apply(lambda x: str(x) if x and str(x) != 'nan' else '')
            
        print(f"✅ Données nettoyées: {len(df)} lignes valides")
        
        # Sauvegarder le fichier nettoyé
        clean_path = csv_path.replace('.csv', '_clean.csv')
        df.to_csv(clean_path, index=False, encoding='utf-8')
        print(f"💾 Données nettoyées sauvées dans {clean_path}")
        
        return df, clean_path
        
    except Exception as e:
        print(f"❌ Erreur lors du nettoyage: {e}")
        return None, None

def index_manga_safe(manga_rag_manager, df):
    """Indexe les mangas avec gestion d'erreurs"""
    print("🔄 Indexation sécurisée des mangas...")
    
    successful_indexes = 0
    errors = 0
    
    # Reset la collection
    try:
        manga_rag_manager.collection.delete(where={})
        print("🗑️ Collection vidée")
    except:
        print("⚠️ Erreur lors du vidage (normal si vide)")
    
    # Indexer ligne par ligne avec gestion d'erreurs
    batch_size = 50
    total = len(df)
    
    for i in range(0, total, batch_size):
        batch = df.iloc[i:i+batch_size]
        batch_documents = []
        batch_metadatas = []
        batch_ids = []
        
        for idx, row in batch.iterrows():
            try:
                # Construire le document texte
                title = str(row.get('title', ''))
                description = str(row.get('description', ''))
                tags = str(row.get('tags', ''))
                
                if not title:  # Skip si pas de titre
                    continue
                    
                document = f"Titre: {title}\nDescription: {description}\nTags: {tags}"
                
                # Métadonnées sécurisées
                metadata = {
                    'title': title,
                    'description': description[:500],  # Limiter la taille
                    'rating': float(row.get('rating', 0.0)) if row.get('rating') else 0.0,
                    'year': int(row.get('year', 0)) if row.get('year') else 0,
                    'tags': tags[:200],  # Limiter la taille
                    'source': 'manga'
                }
                
                batch_documents.append(document)
                batch_metadatas.append(metadata)
                batch_ids.append(f"manga_{idx}")
                
                successful_indexes += 1
                
            except Exception as e:
                errors += 1
                if errors < 10:  # Afficher seulement les 10 premières erreurs
                    print(f"⚠️ Erreur ligne {idx}: {e}")
        
        # Ajouter le batch à ChromaDB
        if batch_documents:
            try:
                manga_rag_manager.collection.add(
                    documents=batch_documents,
                    metadatas=batch_metadatas,
                    ids=batch_ids
                )
                print(f"✅ Batch {i//batch_size + 1}: {len(batch_documents)} mangas indexés")
            except Exception as e:
                print(f"❌ Erreur batch {i//batch_size + 1}: {e}")
    
    print(f"🎯 Indexation terminée: {successful_indexes} succès, {errors} erreurs")
    return successful_indexes > 0

def test_search(manga_rag_manager):
    """Test les recherches"""
    print("🔍 Test des recherches...")
    
    test_queries = ["naruto", "dragon ball", "one piece", "attack on titan"]
    
    for query in test_queries:
        try:
            results = manga_rag_manager.search_manga(query, n_results=3)
            print(f"📖 '{query}': {len(results)} résultats")
            for result in results[:2]:
                print(f"   - {result.get('title', 'N/A')} (score: {result.get('similarity_score', 0):.2f})")
        except Exception as e:
            print(f"❌ Erreur recherche '{query}': {e}")

def main():
    """Fonction principale"""
    print("🎌 Fix et initialisation du RAG Manga")
    print("=" * 50)
    
    manga_csv = Path(BASE_DIR) / 'rags' / 'manga_rag' / 'data' / 'manga_data.csv'
    
    if not manga_csv.exists():
        print(f"❌ Fichier manga non trouvé: {manga_csv}")
        return False
    
    # 1. Nettoyer les données
    df, clean_path = clean_manga_data(str(manga_csv))
    if df is None:
        print("❌ Échec du nettoyage")
        return False
    
    # 2. Initialiser le manager RAG
    print("🔧 Initialisation du gestionnaire RAG...")
    try:
        manga_rag = MangaRAGManager()
        print("✅ Gestionnaire RAG initialisé")
    except Exception as e:
        print(f"❌ Erreur initialisation RAG: {e}")
        return False
    
    # 3. Indexer de manière sécurisée
    success = index_manga_safe(manga_rag, df)
    if not success:
        print("❌ Échec de l'indexation")
        return False
    
    # 4. Tester les recherches
    test_search(manga_rag)
    
    print("🎉 RAG Manga corrigé et opérationnel!")
    return True

if __name__ == "__main__":
    main()