#!/usr/bin/env python3
"""
Configuration rapide pour faire fonctionner le serveur sans ChromaDB
"""
import os
import sys
import django
from pathlib import Path

# Configuration Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')

def setup_minimal_data():
    """Configure des données minimales pour tester"""
    try:
        django.setup()
        
        from apps.books.models import TechBook, LiteratureBook
        from apps.accounts.models import User, Genre, ProgrammingLanguage
        
        print("🔧 Configuration des données minimales...")
        
        # Créer quelques langages de programmation
        js, _ = ProgrammingLanguage.objects.get_or_create(name="JavaScript")
        python, _ = ProgrammingLanguage.objects.get_or_create(name="Python")
        csharp, _ = ProgrammingLanguage.objects.get_or_create(name="C#")
        
        # Créer quelques genres littéraires
        fantasy, _ = Genre.objects.get_or_create(name="Fantasy")
        scifi, _ = Genre.objects.get_or_create(name="Science Fiction")
        romance, _ = Genre.objects.get_or_create(name="Romance")
        
        # Créer quelques livres techniques
        if not TechBook.objects.filter(title__contains="JavaScript").exists():
            js_book = TechBook.objects.create(
                title="JavaScript: The Good Parts",
                author="Douglas Crockford",
                description="Un guide des meilleures pratiques JavaScript",
                rating=4.2,
                price=25.99,
                difficulty_level="intermediate",
                tech_categories="Web Development,Programming",
                best_seller=True
            )
            js_book.programming_languages.add(js)
        
        if not TechBook.objects.filter(title__contains="Python").exists():
            python_book = TechBook.objects.create(
                title="Python Crash Course",
                author="Eric Matthes",
                description="Introduction pratique à la programmation Python",
                rating=4.5,
                price=29.99,
                difficulty_level="beginner",
                tech_categories="Programming,Data Science",
                top_rated=True
            )
            python_book.programming_languages.add(python)
        
        if not TechBook.objects.filter(title__contains="C#").exists():
            csharp_book = TechBook.objects.create(
                title="C# 10 in a Nutshell",
                author="Joseph Albahari",
                description="Guide complet de C# et .NET",
                rating=4.3,
                price=45.99,
                difficulty_level="intermediate",
                tech_categories="Programming,.NET"
            )
            csharp_book.programming_languages.add(csharp)
        
        # Créer quelques livres littéraires
        if not LiteratureBook.objects.filter(title__contains="Harry Potter").exists():
            hp_book = LiteratureBook.objects.create(
                title="Harry Potter and the Philosopher's Stone",
                authors="J.K. Rowling",
                description="Un jeune sorcier découvre le monde magique",
                average_rating=4.47,
                published_year=1997,
                categories="Fiction,Fantasy,Young Adult",
                reading_difficulty="easy",
                themes="Magic,Friendship,Coming of Age",
                popularity_rating=4.8,
                ratings_count=2500000
            )
            hp_book.genres.add(fantasy)
        
        if not LiteratureBook.objects.filter(title__contains="Dune").exists():
            dune_book = LiteratureBook.objects.create(
                title="Dune",
                authors="Frank Herbert",
                description="Épopée de science-fiction sur la planète Arrakis",
                average_rating=4.25,
                published_year=1965,
                categories="Fiction,Science Fiction,Space Opera",
                reading_difficulty="difficult",
                themes="Politics,Ecology,Power",
                popularity_rating=4.3,
                ratings_count=800000
            )
            dune_book.genres.add(scifi)
        
        if not LiteratureBook.objects.filter(title__contains="Pride").exists():
            pride_book = LiteratureBook.objects.create(
                title="Pride and Prejudice",
                authors="Jane Austen",
                description="Romance classique dans l'Angleterre du 19e siècle",
                average_rating=4.27,
                published_year=1813,
                categories="Fiction,Romance,Classics",
                reading_difficulty="moderate",
                themes="Love,Class,Society",
                popularity_rating=4.4,
                ratings_count=1200000
            )
            pride_book.genres.add(romance)
        
        # Créer un utilisateur test
        if not User.objects.filter(email="test@example.com").exists():
            User.objects.create_user(
                email="test@example.com",
                password="testpass123",
                first_name="Test",
                last_name="User"
            )
        
        print("✅ Données minimales créées !")
        print(f"📚 Livres techniques: {TechBook.objects.count()}")
        print(f"📖 Livres littéraires: {LiteratureBook.objects.count()}")
        print(f"👥 Utilisateurs: {User.objects.count()}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    
    return True

if __name__ == "__main__":
    setup_minimal_data()