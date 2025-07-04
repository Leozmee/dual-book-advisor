#!/usr/bin/env python3
"""
Script de migration pour appliquer la nouvelle configuration RAG
"""
import os
import sys
import django
from pathlib import Path

# Configuration Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

def apply_new_rag_config():
    """Applique la nouvelle configuration RAG"""
    print("🔧 Migration vers la nouvelle configuration RAG...")
    
    try:
        django.setup()
        from django.conf import settings
        
        # Vérifier les nouveaux paramètres
        print(f"✅ Seuil de similarité: {settings.RAG_CONFIG['similarity_threshold']}")
        print(f"✅ Nombre de résultats: {settings.RAG_CONFIG['top_k_results']}")
        print(f"✅ Support multilingue: {settings.RAG_CONFIG['multilingual_queries']}")
        print(f"✅ Expansion de requêtes: {settings.RAG_CONFIG['query_expansion']}")
        
        # Créer les répertoires nécessaires
        os.makedirs(settings.RAG_CONFIG['tech_chroma_path'], exist_ok=True)
        os.makedirs(settings.RAG_CONFIG['literature_chroma_path'], exist_ok=True)
        os.makedirs(BASE_DIR / 'logs', exist_ok=True)
        
        print("✅ Répertoires créés")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la migration: {e}")
        return False

def test_new_config():
    """Test la nouvelle configuration"""
    print("\n🧪 Test de la nouvelle configuration...")
    
    try:
        from rags.tech_rag.tech_rag_manager import TechRAGManager
        from rags.literature_rag.literature_rag_manager import LiteratureRAGManager
        
        # Test avec les requêtes problématiques
        print("📚 Test agent littéraire:")
        lit_rag = LiteratureRAGManager()
        
        test_queries = [
            "oeuvres principales de tolstoy",
            "livres de stephen king",
            "romans comme harry potter"
        ]
        
        for query in test_queries:
            results = lit_rag.search_books(query, n_results=3)
            print(f"   '{query}' → {len(results)} résultats")
            if results:
                for i, result in enumerate(results[:2], 1):
                    print(f"      {i}. {result['title']} (score: {result['similarity_score']:.2f})")
        
        print("\n🔧 Test agent technique:")
        tech_rag = TechRAGManager()
        
        tech_queries = [
            "apprendre python",
            "livres javascript",
            "développement web"
        ]
        
        for query in tech_queries:
            results = tech_rag.search_books(query, n_results=3)
            print(f"   '{query}' → {len(results)} résultats")
            if results:
                for i, result in enumerate(results[:2], 1):
                    print(f"      {i}. {result['title']} (score: {result['similarity_score']:.2f})")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

def create_query_expansion_module():
    """Crée le module d'expansion de requêtes"""
    print("\n🔧 Création du module d'expansion de requêtes...")
    
    expansion_code = '''"""
Module d'expansion de requêtes pour améliorer la recherche RAG
"""
import re
from typing import Dict, List
from django.conf import settings

def expand_query(query: str) -> str:
    """Enrichit une requête pour améliorer la recherche sémantique"""
    query_lower = query.lower()
    expanded_parts = [query]
    
    # Utiliser le dictionnaire de traduction des settings
    translations = getattr(settings, 'QUERY_TRANSLATIONS', {})
    
    for key, expansion in translations.items():
        if key.lower() in query_lower:
            expanded_parts.append(expansion)
            break  # Prendre la première correspondance principale
    
    # Ajout de synonymes contextuels
    if any(word in query_lower for word in ['livre', 'book', 'ouvrage']):
        expanded_parts.append('book literature reading')
    
    if any(word in query_lower for word in ['recommandation', 'suggestion', 'conseil']):
        expanded_parts.append('recommendation suggest similar')
    
    if any(word in query_lower for word in ['apprendre', 'learn', 'étudier']):
        expanded_parts.append('learn study tutorial beginner guide')
    
    return ' '.join(expanded_parts)

def detect_language(query: str) -> str:
    """Détecte la langue d'une requête"""
    french_indicators = ['de', 'le', 'la', 'les', 'du', 'des', 'un', 'une', 'oeuvres', 'livres', 'apprendre']
    english_indicators = ['the', 'and', 'or', 'to', 'for', 'with', 'books', 'learn', 'programming']
    
    query_lower = query.lower()
    french_count = sum(1 for word in french_indicators if word in query_lower)
    english_count = sum(1 for word in english_indicators if word in query_lower)
    
    return 'french' if french_count > english_count else 'english'

def normalize_author_query(query: str) -> str:
    """Normalise les requêtes d'auteurs pour améliorer la correspondance"""
    # Variations courantes d'auteurs
    author_variations = {
        'tolstoy': ['tolstoi', 'tolstoï', 'leo tolstoy', 'leon tolstoi'],
        'stephen king': ['king', 's. king', 'stephen edwin king'],
        'murakami': ['haruki murakami', 'h. murakami'],
        'victor hugo': ['hugo', 'v. hugo'],
        'shakespeare': ['william shakespeare', 'w. shakespeare'],
    }
    
    query_lower = query.lower()
    for standard, variations in author_variations.items():
        for variation in variations:
            if variation in query_lower:
                return query_lower.replace(variation, standard)
    
    return query
'''
    
    # Créer le fichier
    module_path = BASE_DIR / 'rags' / 'shared' / 'query_expansion.py'
    os.makedirs(module_path.parent, exist_ok=True)
    
    with open(module_path, 'w', encoding='utf-8') as f:
        f.write(expansion_code)
    
    print(f"✅ Module créé: {module_path}")
    return True

def main():
    """Fonction principale de migration"""
    print("🚀 Migration de la configuration RAG")
    print("=" * 50)
    
    # Étapes de migration
    steps = [
        ("Application de la nouvelle config", apply_new_rag_config),
        ("Création du module d'expansion", create_query_expansion_module),
        ("Test de la nouvelle config", test_new_config),
    ]
    
    for step_name, step_func in steps:
        print(f"\n📋 {step_name}...")
        if not step_func():
            print(f"❌ Échec de l'étape: {step_name}")
            return False
    
    print("\n🎉 Migration terminée avec succès!")
    print("\n💡 Prochaines étapes:")
    print("1. Redémarrer le serveur Django")
    print("2. Tester les requêtes problématiques:")
    print("   - 'oeuvres principales de tolstoy'")
    print("   - 'livres de stephen king'")
    print("   - 'apprendre python'")
    print("3. Vérifier que les résultats sont maintenant pertinents")
    
    return True

if __name__ == "__main__":
    main()