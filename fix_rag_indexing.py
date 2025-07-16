#!/usr/bin/env python3
"""
Script to fix RAG indexing by re-indexing all literature books
"""

import os
import sys
import django
import logging

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from rags.literature_rag.literature_rag_manager import LiteratureRAGManager
from apps.books.models import LiteratureBook

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_rag_indexing():
    """Re-index all literature books to fix the RAG search"""
    
    logger.info("🔧 Starting RAG indexing fix...")
    
    # Get current stats
    rag_manager = LiteratureRAGManager()
    stats = rag_manager.get_stats()
    logger.info(f"Current stats: {stats}")
    
    total_books = LiteratureBook.objects.count()
    logger.info(f"Total books in database: {total_books}")
    
    # Check if our specific book exists
    try:
        book = LiteratureBook.objects.get(id=6570)
        logger.info(f"✅ Target book found: {book.title} by {book.authors}")
    except LiteratureBook.DoesNotExist:
        logger.error("❌ Target book (ID: 6570) not found in database")
        return False
    
    # Re-index all books
    logger.info("🚀 Starting full re-indexing...")
    try:
        rag_manager.index_all_books(reset=True)
        logger.info("✅ Re-indexing completed successfully")
        
        # Check stats after re-indexing
        new_stats = rag_manager.get_stats()
        logger.info(f"New stats: {new_stats}")
        
        # Test search for our specific book
        logger.info("🔍 Testing search for 'Tales from Shakespeare'...")
        results = rag_manager.search_books("Tales from Shakespeare Charles Lamb Mary Lamb", n_results=10)
        
        found = False
        for result in results:
            if result.get('book_id') == 6570:
                logger.info(f"✅ SUCCESS! Found book: {result.get('title')} by {result.get('authors')}")
                logger.info(f"   Similarity score: {result.get('similarity_score', 0):.3f}")
                found = True
                break
        
        if not found:
            logger.warning("⚠️ Book still not found after re-indexing")
            if results:
                logger.info("Top results:")
                for i, result in enumerate(results[:5]):
                    logger.info(f"  {i+1}. {result.get('title')} by {result.get('authors')} (score: {result.get('similarity_score', 0):.3f})")
        
        return found
        
    except Exception as e:
        logger.error(f"❌ Error during re-indexing: {e}")
        return False

def test_french_english_correspondence():
    """Test the French/English correspondence after fixing indexing"""
    
    logger.info("🧪 Testing French/English correspondence...")
    
    rag_manager = LiteratureRAGManager()
    
    # Test French query
    logger.info("🔍 Testing French query: 'qui a écrit Les Contes de Shakespeare?'")
    results = rag_manager.search_books("qui a écrit Les Contes de Shakespeare", n_results=10)
    
    found_direct = False
    for result in results:
        if result.get('book_id') == 6570:
            logger.info(f"✅ Direct match found: {result.get('title')} by {result.get('authors')}")
            found_direct = True
            break
    
    if not found_direct:
        logger.info("❌ Direct French search did not find the book")
        
        # Test English query
        logger.info("🔍 Testing English query: 'Tales from Shakespeare'")
        results_en = rag_manager.search_books("Tales from Shakespeare", n_results=10)
        
        found_english = False
        for result in results_en:
            if result.get('book_id') == 6570:
                logger.info(f"✅ English search found: {result.get('title')} by {result.get('authors')}")
                found_english = True
                break
        
        if not found_english:
            logger.info("❌ English search also did not find the book")
        
        return found_english
    
    return found_direct

if __name__ == "__main__":
    print("🔧 RAG Indexing Fix")
    print("=" * 50)
    
    # Fix the indexing
    success = fix_rag_indexing()
    
    if success:
        print("\n✅ RAG indexing fix completed successfully")
        
        # Test the French/English correspondence
        test_success = test_french_english_correspondence()
        
        if test_success:
            print("✅ French/English correspondence test passed")
        else:
            print("❌ French/English correspondence test failed")
    else:
        print("\n❌ RAG indexing fix failed")
        
    print("\n🏁 Fix script completed")