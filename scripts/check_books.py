#!/usr/bin/env python3
"""
Script pour inspecter les livres dans la base de données
"""
import os
import sys
import django
from pathlib import Path

# Configuration Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.books.models import LiteratureBook

def inspect_database():
    """Inspecte le contenu de la base de données littéraire"""
    print("🔍 Inspection de la base de données littéraire")
    print("=" * 60)
    
    total_books = LiteratureBook.objects.count()
    print(f"📊 Total de livres littéraires: {total_books}")
    
    # Recherche de livres spécifiques
    test_searches = [
        ("Tolstoy", "Tolstoy"),
        ("Stephen King", "King"),
        ("Harry Potter", "Harry Potter"),
        ("Fantasy", "fantasy"),
        ("Fiction", "fiction"),
    ]
    
    print("\n🔍 Recherche d'auteurs et genres spécifiques:")
    for search_term, filter_term in test_searches:
        # Recherche dans authors
        books_by_author = LiteratureBook.objects.filter(authors__icontains=filter_term)
        print(f"\n📚 Livres avec '{search_term}' dans authors: {books_by_author.count()}")
        
        for book in books_by_author[:3]:  # Afficher les 3 premiers
            print(f"   • {book.title} - {book.authors} ({book.published_year})")
        
        # Recherche dans title
        books_by_title = LiteratureBook.objects.filter(title__icontains=filter_term)
        print(f"📖 Livres avec '{search_term}' dans title: {books_by_title.count()}")
        
        for book in books_by_title[:3]:  # Afficher les 3 premiers
            print(f"   • {book.title} - {book.authors}")
        
        # Recherche dans categories
        books_by_category = LiteratureBook.objects.filter(categories__icontains=filter_term)
        print(f"🏷️ Livres avec '{search_term}' dans categories: {books_by_category.count()}")
    
    # Afficher quelques exemples de livres populaires
    print("\n⭐ Top 10 des livres les mieux notés:")
    top_books = LiteratureBook.objects.filter(
        average_rating__gte=4.0
    ).order_by('-average_rating', '-ratings_count')[:10]
    
    for i, book in enumerate(top_books, 1):
        print(f"{i:2d}. {book.title[:40]:<40} - {book.authors[:20]:<20} ({book.average_rating}⭐)")
    
    # Vérifier les catégories populaires
    print("\n🏷️ Analyse des catégories:")
    all_categories = []
    for book in LiteratureBook.objects.exclude(categories='')[:1000]:  # Échantillon
        if book.categories:
            all_categories.extend([cat.strip() for cat in book.categories.split(',')])
    
    from collections import Counter
    common_categories = Counter(all_categories).most_common(10)
    for category, count in common_categories:
        print(f"   • {category}: {count} livres")

def test_rag_search():
    """Test direct du système RAG"""
    print("\n🧪 Test direct du système RAG")
    print("=" * 60)
    
    try:
        from rags.literature_rag.literature_rag_manager import LiteratureRAGManager
        
        lit_rag = LiteratureRAGManager()
        
        test_queries = [
            "Harry Potter",
            "fantasy magic",
            "Tolstoy",
            "Leo Tolstoy", 
            "Stephen King",
            "horror",
            "young adult",
            "magic wizards",
        ]
        
        for query in test_queries:
            print(f"\n🔍 Test RAG: '{query}'")
            try:
                results = lit_rag.search_books(query, n_results=3)
                print(f"   Résultats trouvés: {len(results)}")
                
                for i, result in enumerate(results, 1):
                    title = result.get('title', 'Titre inconnu')
                    authors = result.get('authors', result.get('author', 'Auteur inconnu'))
                    score = result.get('similarity_score', 0)
                    print(f"   {i}. {title} - {authors} (score: {score:.3f})")
                    
            except Exception as e:
                print(f"   ❌ Erreur: {e}")
    
    except Exception as e:
        print(f"❌ Erreur initialisation RAG: {e}")

def analyze_harry_potter_problem():
    """Analyse spécifique du problème Harry Potter"""
    print("\n🔍 Analyse spécifique: Problème Harry Potter")
    print("=" * 60)
    
    # Recherche directe dans la base
    hp_books = LiteratureBook.objects.filter(
        title__icontains="Harry Potter"
    )
    print(f"📚 Livres 'Harry Potter' trouvés directement: {hp_books.count()}")
    
    for book in hp_books:
        print(f"   • {book.title} - {book.authors}")
        print(f"     Catégories: {book.categories}")
        print(f"     Note: {book.average_rating}, Année: {book.published_year}")
    
    # Recherche de livres similaires (fantasy, young adult, magic)
    similar_books = LiteratureBook.objects.filter(
        categories__icontains="Fantasy"
    ).order_by('-average_rating')[:5]
    
    print(f"\n📖 Livres Fantasy bien notés: {similar_books.count()}")
    for book in similar_books:
        print(f"   • {book.title} - {book.authors} ({book.average_rating}⭐)")
    
    # Recherche par mots-clés
    magic_books = LiteratureBook.objects.filter(
        description__icontains="magic"
    )[:5]
    
    print(f"\n✨ Livres avec 'magic' dans description: {magic_books.count()}")
    for book in magic_books:
        print(f"   • {book.title} - {book.authors}")

if __name__ == "__main__":
    inspect_database()
    test_rag_search()
    analyze_harry_potter_problem()
    
    print("\n💡 Recommandations:")
    print("1. Si Harry Potter n'est pas dans la base → Normal que ça ne trouve rien")
    print("2. Si Harry Potter est dans la base → Problème de seuil ou d'indexation")
    print("3. Vérifier si les livres fantasy/young adult existent")
    print("4. Possibilité d'ajuster la requête en fonction des résultats")