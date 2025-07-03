#!/usr/bin/env python
"""
Script to import literature books from CSV files into Django database
Merges data from books.csv and dataframe.csv
"""
import os
import sys
import django
import pandas as pd
from decimal import Decimal

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.books.models import LiteratureBook


def clean_number_string(num_str):
    """Clean number strings by removing quotes and commas"""
    if not num_str:
        return None
    try:
        # Remove quotes and commas
        cleaned = str(num_str).replace('"', '').replace(',', '').strip()
        return int(cleaned) if cleaned else None
    except:
        return None


def parse_rating(rating_str):
    """Parse rating string to decimal"""
    if not rating_str:
        return None
    try:
        return Decimal(str(rating_str))
    except:
        return None


def import_literature_books():
    """Import literature books from CSV files"""
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                           'rags', 'literature_rag', 'data')
    
    books_csv = os.path.join(data_dir, 'books.csv')
    dataframe_csv = os.path.join(data_dir, 'dataframe.csv')
    
    if not os.path.exists(books_csv):
        print(f"Books CSV file not found: {books_csv}")
        return
    
    if not os.path.exists(dataframe_csv):
        print(f"Dataframe CSV file not found: {dataframe_csv}")
        return
    
    print(f"Reading books CSV: {books_csv}")
    print(f"Reading dataframe CSV: {dataframe_csv}")
    
    # Read both CSV files
    try:
        books_df = pd.read_csv(books_csv, encoding='utf-8')
    except UnicodeDecodeError:
        books_df = pd.read_csv(books_csv, encoding='latin-1')
    
    try:
        popularity_df = pd.read_csv(dataframe_csv, encoding='utf-8')
    except UnicodeDecodeError:
        popularity_df = pd.read_csv(dataframe_csv, encoding='latin-1')
    
    print(f"Found {len(books_df)} records in books.csv")
    print(f"Found {len(popularity_df)} records in dataframe.csv")
    print(f"Books columns: {list(books_df.columns)}")
    print(f"Popularity columns: {list(popularity_df.columns)}")
    
    # Clean the data
    books_df = books_df.fillna('')
    popularity_df = popularity_df.fillna('')
    
    # Create a mapping from popularity data for faster lookup
    popularity_map = {}
    for _, row in popularity_df.iterrows():
        key = (str(row.get('booktitle', '')).strip().lower(), 
               str(row.get('author', '')).strip().lower())
        popularity_map[key] = {
            'popularity_rating': parse_rating(row.get('rating')),
            'votes_count': clean_number_string(row.get('voted')),
            'popularity_score': clean_number_string(row.get('score'))
        }
    
    print(f"Created popularity mapping for {len(popularity_map)} books")
    
    # Clear existing data (optional)
    print("Clearing existing literature books...")
    LiteratureBook.objects.all().delete()
    
    imported_count = 0
    matched_count = 0
    errors = []
    
    for index, row in books_df.iterrows():
        try:
            title = str(row.get('title', '')).strip()
            authors = str(row.get('authors', '')).strip()
            
            # Look for popularity data match
            lookup_key = (title.lower(), authors.lower())
            popularity_data = popularity_map.get(lookup_key, {})
            
            if popularity_data:
                matched_count += 1
            
            # Create literature book record
            literature_book = LiteratureBook(
                isbn13=str(row.get('isbn13', '')).strip() or None,
                isbn10=str(row.get('isbn10', '')).strip() or None,
                title=title[:500],
                subtitle=str(row.get('subtitle', '')).strip()[:500],
                authors=authors[:300],
                categories=str(row.get('categories', '')).strip()[:200],
                thumbnail=str(row.get('thumbnail', '')).strip(),
                description=str(row.get('description', '')).strip(),
                published_year=int(row.get('published_year')) if row.get('published_year') else None,
                average_rating=parse_rating(row.get('average_rating')),
                num_pages=int(row.get('num_pages')) if row.get('num_pages') else None,
                ratings_count=int(row.get('ratings_count')) if row.get('ratings_count') else None,
                
                # Popularity data
                booktitle_alt=title,  # Use same title as alternative
                author_alt=authors,   # Use same author as alternative
                popularity_rating=popularity_data.get('popularity_rating'),
                votes_count=popularity_data.get('votes_count'),
                popularity_score=popularity_data.get('popularity_score'),
            )
            
            literature_book.save()
            imported_count += 1
            
            if imported_count % 100 == 0:
                print(f"Imported {imported_count} books...")
                
        except Exception as e:
            error_msg = f"Error importing row {index}: {str(e)}"
            errors.append(error_msg)
            print(error_msg)
    
    print(f"\nImport completed!")
    print(f"Successfully imported: {imported_count} books")
    print(f"Matched with popularity data: {matched_count} books")
    print(f"Errors: {len(errors)}")
    
    if errors:
        print("\nFirst 5 errors:")
        for error in errors[:5]:
            print(f"  - {error}")


if __name__ == '__main__':
    import_literature_books()