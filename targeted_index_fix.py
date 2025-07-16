#!/usr/bin/env python3
"""
Targeted fix to index specific missing books including Tales from Shakespeare
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

def index_specific_books():
    """Index specific books that are missing from the RAG"""
    
    logger.info("🎯 Starting targeted book indexing...")
    
    rag_manager = LiteratureRAGManager()
    
    # Books to specifically index
    target_books = [
        6570,  # Tales from Shakespeare by Charles Lamb;Mary Lamb
        3824,  # She's Come Undone by Wally Lamb (other Lamb book)
    ]
    
    # Also index all books by Charles Lamb and Mary Lamb
    lamb_books = LiteratureBook.objects.filter(authors__icontains="lamb")
    logger.info(f"Found {lamb_books.count()} books with 'lamb' in authors")
    
    # Get all Shakespeare-related books
    shakespeare_books = LiteratureBook.objects.filter(title__icontains="shakespeare")
    logger.info(f"Found {shakespeare_books.count()} books with 'shakespeare' in title")
    
    # Combine all books to index
    all_books_to_index = set(target_books)
    all_books_to_index.update(lamb_books.values_list('id', flat=True))
    all_books_to_index.update(shakespeare_books.values_list('id', flat=True))
    
    logger.info(f"Total unique books to index: {len(all_books_to_index)}")
    
    # Index each book
    indexed_count = 0
    for book_id in all_books_to_index:
        try:
            book = LiteratureBook.objects.get(id=book_id)
            
            # Check if already indexed
            try:
                existing = rag_manager.collection.get(ids=[f"literature_book_{book_id}"])
                if existing['ids']:
                    logger.info(f"  ✅ Book {book_id} already indexed: {book.title}")
                    continue
            except:
                pass
            
            # Build the document
            text_content = rag_manager._build_book_text(book)
            
            # Prepare metadata
            metadata = {
                'book_id': book.id,
                'title': book.title,
                'authors': book.authors,
                'isbn13': book.isbn13,
                'average_rating': float(book.average_rating) if book.average_rating else 0.0,
                'published_year': book.published_year or 0,
                'categories': book.categories or '',
                'reading_difficulty': book.reading_difficulty,
                'themes': book.themes or '',
                'genres': ','.join(book.genres.values_list('name', flat=True)),
                'popularity_rating': float(book.popularity_rating) if book.popularity_rating else 0.0,
                'popularity_score': book.popularity_score or 0,
                'ratings_count': book.ratings_count or 0,
                'votes_count': book.votes_count or 0,
                'type': 'literature_book'
            }
            
            # Index the book
            document = {
                'id': f"literature_book_{book.id}",
                'text': text_content,
                'metadata': metadata
            }
            
            rag_manager.chroma_manager.add_documents(rag_manager.collection, [document])
            indexed_count += 1
            
            logger.info(f"  ✅ Indexed book {book_id}: {book.title}")
            
            # Special log for our target book
            if book_id == 6570:
                logger.info(f"  🎯 TARGET BOOK INDEXED: {book.title} by {book.authors}")
                
        except LiteratureBook.DoesNotExist:
            logger.warning(f"  ❌ Book {book_id} not found in database")
        except Exception as e:
            logger.error(f"  ❌ Error indexing book {book_id}: {e}")
    
    logger.info(f"✅ Indexed {indexed_count} books")
    return indexed_count > 0

def test_target_book():
    """Test if our target book is now findable"""
    
    logger.info("🧪 Testing target book search...")
    
    rag_manager = LiteratureRAGManager()
    
    # Test various search terms
    search_terms = [
        "Tales from Shakespeare",
        "Charles Lamb",
        "Mary Lamb",
        "Charles Lamb Mary Lamb",
        "Tales from Shakespeare Charles Lamb Mary Lamb",
        "qui a écrit Les Contes de Shakespeare"
    ]
    
    found_any = False
    for term in search_terms:
        logger.info(f"🔍 Testing: '{term}'")
        results = rag_manager.search_books(term, n_results=10)
        
        found = False
        for result in results:
            if result.get('book_id') == 6570:
                logger.info(f"  ✅ FOUND! Score: {result.get('similarity_score', 0):.3f}")
                found = True
                found_any = True
                break
        
        if not found:
            logger.info(f"  ❌ Not found")
            if results:
                top = results[0]
                logger.info(f"  Top result: {top.get('title')} by {top.get('authors')} (score: {top.get('similarity_score', 0):.3f})")
    
    return found_any

def test_full_agent_system():
    """Test the full agent system with our target question"""
    
    logger.info("🤖 Testing full agent system...")
    
    try:
        from agents.langchain_agents.graph_manager import BookAdvisorGraphManager
        
        # Initialize the graph manager
        graph_manager = BookAdvisorGraphManager(
            llm_provider="ollama",
            model_name="llama3.2"
        )
        
        # Test the specific question
        query = "qui a écrit Les Contes de Shakespeare?"
        logger.info(f"🔍 Testing query: {query}")
        
        result = graph_manager.get_literature_recommendations(query, user_id=1)
        
        if result.get('success'):
            response = result.get('response', '')
            logger.info(f"✅ Agent response successful")
            
            # Check if response mentions the correct information
            response_lower = response.lower()
            if 'lamb' in response_lower and ('charles' in response_lower or 'mary' in response_lower):
                logger.info("✅ Response mentions Lamb authors correctly")
                return True
            else:
                logger.warning("⚠️ Response does not mention Lamb authors")
                logger.info(f"Response preview: {response[:200]}...")
                return False
        else:
            logger.error(f"❌ Agent failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error testing agent system: {e}")
        return False

if __name__ == "__main__":
    print("🎯 Targeted RAG Indexing Fix")
    print("=" * 50)
    
    # Index specific books
    index_success = index_specific_books()
    
    if index_success:
        print("\n✅ Targeted indexing completed")
        
        # Test target book search
        search_success = test_target_book()
        
        if search_success:
            print("✅ Target book search successful")
            
            # Test full agent system
            agent_success = test_full_agent_system()
            
            if agent_success:
                print("✅ Full agent system test successful")
            else:
                print("❌ Full agent system test failed")
        else:
            print("❌ Target book search failed")
    else:
        print("\n❌ Targeted indexing failed")
        
    print("\n🏁 Targeted fix completed")