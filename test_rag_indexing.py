#!/usr/bin/env python3
"""
Test script to verify RAG indexing of Tales from Shakespeare book
"""

import os
import sys
import django
import logging

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.books.models import LiteratureBook
from rags.literature_rag.literature_rag_manager import LiteratureRAGManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_specific_book_indexing():
    """Test if the Tales from Shakespeare book is properly indexed"""
    
    # Find the book in the database
    try:
        book = LiteratureBook.objects.get(
            title="Tales from Shakespeare",
            authors__icontains="Charles Lamb"
        )
        logger.info(f"✅ Found book in database: {book.title} by {book.authors}")
        logger.info(f"   ID: {book.id}")
        logger.info(f"   Description: {book.description}")
        logger.info(f"   Rating: {book.average_rating}")
        logger.info(f"   Published: {book.published_year}")
        
    except LiteratureBook.DoesNotExist:
        logger.error("❌ Book not found in database")
        return False
    
    # Test RAG search for this specific book
    rag_manager = LiteratureRAGManager()
    
    # Test various search terms
    search_terms = [
        "Tales from Shakespeare",
        "Charles Lamb",
        "Mary Lamb",
        "Charles Lamb Mary Lamb",
        "Shakespeare tales retold",
        "Tales from Shakespeare Charles Lamb Mary Lamb",
        book.title,
        book.authors
    ]
    
    logger.info(f"\n🔍 Testing RAG search for book ID {book.id}")
    
    for term in search_terms:
        logger.info(f"   Searching for: '{term}'")
        results = rag_manager.search_books(term, n_results=10)
        
        # Check if our book is in the results
        found = False
        for result in results:
            if result.get('book_id') == book.id:
                logger.info(f"   ✅ Found! Score: {result.get('similarity_score', 0):.3f}")
                found = True
                break
        
        if not found:
            logger.info(f"   ❌ Not found in top {len(results)} results")
            # Show what was found instead
            if results:
                top_result = results[0]
                logger.info(f"   Top result: {top_result.get('title')} by {top_result.get('authors')} (score: {top_result.get('similarity_score', 0):.3f})")
    
    return True

def test_rag_collection_content():
    """Test what's actually in the RAG collection"""
    logger.info("\n🗄️ Testing RAG collection content")
    
    rag_manager = LiteratureRAGManager()
    
    # Get collection stats
    stats = rag_manager.get_stats()
    logger.info(f"Collection stats: {stats}")
    
    # Search for all books with "lamb" in them
    logger.info("\n🔍 Searching for all books with 'lamb'")
    results = rag_manager.search_books("lamb", n_results=20)
    
    logger.info(f"Found {len(results)} books with 'lamb':")
    for i, result in enumerate(results):
        logger.info(f"  {i+1}. {result.get('title')} by {result.get('authors')} (ID: {result.get('book_id')}, score: {result.get('similarity_score', 0):.3f})")
    
    # Search for all books with "shakespeare" in them
    logger.info("\n🔍 Searching for all books with 'shakespeare'")
    results = rag_manager.search_books("shakespeare", n_results=20)
    
    logger.info(f"Found {len(results)} books with 'shakespeare':")
    for i, result in enumerate(results):
        logger.info(f"  {i+1}. {result.get('title')} by {result.get('authors')} (ID: {result.get('book_id')}, score: {result.get('similarity_score', 0):.3f})")

def test_direct_embedding_search():
    """Test direct embedding search in ChromaDB"""
    logger.info("\n🧠 Testing direct embedding search")
    
    rag_manager = LiteratureRAGManager()
    
    # Search directly in ChromaDB
    try:
        # Search for the exact book
        results = rag_manager.chroma_manager.search_similar(
            collection=rag_manager.collection,
            query="Tales from Shakespeare Charles Lamb Mary Lamb",
            n_results=10,
            similarity_threshold=0.1
        )
        
        logger.info(f"Direct ChromaDB search found {len(results['documents'])} results")
        
        # Check if our book is in the results
        book_id = 6570  # From our test results
        for i, metadata in enumerate(results['metadatas']):
            if metadata.get('book_id') == book_id:
                logger.info(f"✅ Found book at position {i}")
                logger.info(f"   Document: {results['documents'][i]}")
                logger.info(f"   Distance: {results['distances'][i]}")
                logger.info(f"   Metadata: {metadata}")
                break
        else:
            logger.info(f"❌ Book not found in ChromaDB results")
            
            # Show first few results
            logger.info("First 5 results:")
            for i in range(min(5, len(results['documents']))):
                logger.info(f"  {i+1}. ID: {results['metadatas'][i].get('book_id')}, Title: {results['metadatas'][i].get('title')}")
                logger.info(f"      Distance: {results['distances'][i]:.3f}")
                logger.info(f"      Document: {results['documents'][i][:100]}...")
                
    except Exception as e:
        logger.error(f"❌ Error in direct embedding search: {e}")

def check_book_indexing_status():
    """Check if the specific book is indexed in ChromaDB"""
    logger.info("\n📚 Checking book indexing status")
    
    rag_manager = LiteratureRAGManager()
    book_id = 6570  # Tales from Shakespeare
    
    try:
        # Query ChromaDB directly for this book
        results = rag_manager.collection.get(
            ids=[f"literature_book_{book_id}"]
        )
        
        if results['ids']:
            logger.info(f"✅ Book {book_id} is indexed in ChromaDB")
            logger.info(f"   Document: {results['documents'][0][:200]}...")
            logger.info(f"   Metadata: {results['metadatas'][0]}")
        else:
            logger.info(f"❌ Book {book_id} is NOT indexed in ChromaDB")
            
    except Exception as e:
        logger.error(f"❌ Error checking book indexing: {e}")

if __name__ == "__main__":
    print("🧪 Testing RAG Indexing of Tales from Shakespeare")
    print("=" * 60)
    
    # Run all tests
    test_specific_book_indexing()
    test_rag_collection_content()
    test_direct_embedding_search()
    check_book_indexing_status()
    
    print("\n✅ RAG indexing test completed")