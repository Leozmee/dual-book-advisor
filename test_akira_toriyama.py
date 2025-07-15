#!/usr/bin/env python3
"""
Test spécifique pour vérifier le problème avec Akira Toriyama
"""
import os
import sys
import django
import pandas as pd

# Configurer Django
sys.path.insert(0, '/home/utilisateur/dual-book-advisor')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from rags.manga_rag.manga_rag_manager import MangaRAGManager
from agents.ollama_gemma_manager import GemmaAgentManager

def test_csv_data():
    """Test les données CSV pour Akira Toriyama"""
    print("=== TEST DONNÉES CSV ===")
    
    csv_path = '/home/utilisateur/dual-book-advisor/rags/manga_rag/data/albums_from_seen_clean.csv'
    
    try:
        df = pd.read_csv(csv_path, encoding='utf-8')
        print(f"Colonnes CSV: {df.columns.tolist()}")
        print(f"Nombre total de lignes: {len(df)}")
        
        # Rechercher Akira Toriyama
        toriyama_mask = df['auteur'].str.contains('Toriyama', case=False, na=False)
        toriyama_works = df[toriyama_mask]
        
        print(f"\nŒuvres d'Akira Toriyama trouvées: {len(toriyama_works)}")
        
        for idx, row in toriyama_works.head(10).iterrows():
            print(f"- {row['titre']} (Auteur: {row['auteur']})")
            
    except Exception as e:
        print(f"❌ Erreur lecture CSV: {e}")

def test_manga_rag_search():
    """Test la recherche dans le RAG manga"""
    print("\n=== TEST RECHERCHE RAG MANGA ===")
    
    try:
        rag_manager = MangaRAGManager()
        
        # Test différentes requêtes
        queries = [
            "Akira Toriyama",
            "Dragon Ball",
            "Toriyama",
            "œuvres de Akira Toriyama",
            "recommande moi des mangas d'Akira Toriyama"
        ]
        
        for query in queries:
            print(f"\n--- Requête: '{query}' ---")
            try:
                results = rag_manager.search_content(query, n_results=5, content_type='comics')
                print(f"Résultats trouvés: {len(results)}")
                
                for i, result in enumerate(results):
                    title = result.get('title', 'N/A')
                    author = result.get('author', 'N/A')
                    score = result.get('score', 'N/A')
                    print(f"  {i+1}. {title} - Auteur: {author} - Score: {score}")
                    
            except Exception as e:
                print(f"❌ Erreur recherche '{query}': {e}")
                
    except Exception as e:
        print(f"❌ Erreur initialisation RAG: {e}")

def test_full_system():
    """Test le système complet avec l'agent Gemma"""
    print("\n=== TEST SYSTÈME COMPLET ===")
    
    try:
        gemma_manager = GemmaAgentManager()
        
        query = "recommande moi deux oeuvres de Akira Toriyama"
        print(f"Requête: {query}")
        
        response = gemma_manager.get_manga_recommendations(query)
        print(f"Réponse (longueur): {len(response)}")
        print(f"Réponse: {response}")
        
        # Vérifier si des œuvres de Toriyama sont mentionnées
        toriyama_keywords = ['Dragon Ball', 'Dr Slump', 'Toriyama']
        found_keywords = [kw for kw in toriyama_keywords if kw in response]
        
        print(f"\nMots-clés Toriyama trouvés: {found_keywords}")
        
    except Exception as e:
        print(f"❌ Erreur système complet: {e}")

if __name__ == "__main__":
    test_csv_data()
    test_manga_rag_search()
    test_full_system()