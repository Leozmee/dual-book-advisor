#!/usr/bin/env python
"""
Script to import tech books from CSV file into Django database
"""
import os
import sys
import django
import pandas as pd
from datetime import datetime
from decimal import Decimal

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.books.models import TechBook


def parse_price(price_str):
    """Parse price string to decimal"""
    if not price_str or price_str == '':
        return None
    try:
        # Remove currency symbols and convert to decimal
        price_cleaned = str(price_str).replace('$', '').replace(',', '').strip()
        return Decimal(price_cleaned)
    except:
        return None


def parse_date(date_str):
    """Parse date string to date object"""
    if not date_str or date_str == '':
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except:
        try:
            return datetime.strptime(date_str, '%m/%d/%Y').date()
        except:
            return None


def parse_boolean(bool_str):
    """Parse boolean string"""
    if not bool_str:
        return False
    return str(bool_str).lower() in ['yes', 'true', '1', 'y']


def import_tech_books():
    """Import tech books from CSV file"""
    csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                           'rags', 'tech_rag', 'data', 'Amazon Books Data.csv')
    
    if not os.path.exists(csv_path):
        print(f"CSV file not found: {csv_path}")
        return
    
    print(f"Reading CSV file: {csv_path}")
    
    # Read CSV with proper encoding
    try:
        df = pd.read_csv(csv_path, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(csv_path, encoding='latin-1')
    
    print(f"Found {len(df)} records in CSV")
    print(f"Columns: {list(df.columns)}")
    
    # Clean the data
    df = df.fillna('')
    
    # Clear existing data (optional - comment out if you want to keep existing data)
    print("Clearing existing tech books...")
    TechBook.objects.all().delete()
    
    imported_count = 0
    errors = []
    
    for index, row in df.iterrows():
        try:
            # Create tech book record
            tech_book = TechBook(
                title=str(row.get('title', '')).strip()[:500],
                description=str(row.get('description', '')).strip(),
                author=str(row.get('author', '')).strip()[:200],
                isbn10=str(row.get('isbn10', '')).strip() or None,
                isbn13=str(row.get('isbn13', '')).strip() or None,
                publish_date=parse_date(row.get('publish_date')),
                edition=str(row.get('edition', '')).strip()[:50],
                best_seller=parse_boolean(row.get('best_seller')),
                top_rated=parse_boolean(row.get('top_rated')),
                rating=Decimal(str(row.get('rating', 0))) if row.get('rating') else None,
                review_count=int(row.get('review_count', 0)) if row.get('review_count') else None,
                price=parse_price(row.get('price')),
            )
            
            tech_book.save()
            imported_count += 1
            
            if imported_count % 10 == 0:
                print(f"Imported {imported_count} books...")
                
        except Exception as e:
            error_msg = f"Error importing row {index}: {str(e)}"
            errors.append(error_msg)
            print(error_msg)
    
    print(f"\nImport completed!")
    print(f"Successfully imported: {imported_count} books")
    print(f"Errors: {len(errors)}")
    
    if errors:
        print("\nFirst 5 errors:")
        for error in errors[:5]:
            print(f"  - {error}")


if __name__ == '__main__':
    import_tech_books()