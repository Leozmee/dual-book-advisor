#!/usr/bin/env python3
"""
Final verification test for French/English correspondence functionality
"""

import os
import sys
import django
import logging

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from agents.langchain_agents.graph_manager import BookAdvisorGraphManager
from rags.literature_rag.literature_rag_manager import LiteratureRAGManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_direct_rag_search():
    """Test direct RAG search for the book"""
    logger.info("🔍 Testing direct RAG search...")
    
    rag_manager = LiteratureRAGManager()
    
    # Test the specific book
    results = rag_manager.search_books("Tales from Shakespeare Charles Lamb Mary Lamb", n_results=5)
    
    found = False
    for result in results:
        if result.get('book_id') == 6570:
            logger.info(f"✅ FOUND: {result.get('title')} by {result.get('authors')}")
            logger.info(f"   Similarity score: {result.get('similarity_score', 0):.3f}")
            found = True
            break
    
    if not found:
        logger.error("❌ Book not found in RAG search")
        if results:
            logger.info("Top results:")
            for i, result in enumerate(results[:3]):
                logger.info(f"  {i+1}. {result.get('title')} by {result.get('authors')} (score: {result.get('similarity_score', 0):.3f})")
    
    return found

def test_agent_system():
    """Test the full agent system with the specific question"""
    logger.info("🤖 Testing full agent system...")
    
    try:
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
            logger.info(f"Response: {response}")
            
            # Check if response mentions the correct information
            response_lower = response.lower()
            if 'lamb' in response_lower:
                if 'charles' in response_lower and 'mary' in response_lower:
                    logger.info("✅ Response mentions both Charles and Mary Lamb correctly")
                    return True
                elif 'charles' in response_lower or 'mary' in response_lower:
                    logger.info("✅ Response mentions at least one Lamb author correctly")
                    return True
                else:
                    logger.info("⚠️ Response mentions Lamb but not the first names")
                    return True
            else:
                logger.warning("❌ Response does not mention Lamb authors")
                return False
        else:
            logger.error(f"❌ Agent failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error testing agent system: {e}")
        return False

def test_wikipedia_integration():
    """Test Wikipedia integration"""
    logger.info("🌐 Testing Wikipedia integration...")
    
    try:
        from agents.langchain_agents.tools.rag_tools import WikipediaSearchTool
        
        wiki_tool = WikipediaSearchTool()
        
        # Test Wikipedia search
        result = wiki_tool._run("Tales from Shakespeare", language="en")
        
        if result.get('success'):
            logger.info(f"✅ Wikipedia found: {result.get('title')}")
            summary = result.get('summary', '')
            if 'lamb' in summary.lower():
                logger.info("✅ Wikipedia summary mentions Lamb correctly")
                return True
            else:
                logger.warning("⚠️ Wikipedia summary doesn't mention Lamb")
                return False
        else:
            logger.error(f"❌ Wikipedia search failed: {result.get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error testing Wikipedia: {e}")
        return False

def test_french_queries():
    """Test French queries specifically"""
    logger.info("🇫🇷 Testing French queries...")
    
    rag_manager = LiteratureRAGManager()
    
    french_queries = [
        "qui a écrit Les Contes de Shakespeare",
        "Les Contes de Shakespeare auteur",
        "Contes de Shakespeare écrivain",
        "auteur des Contes de Shakespeare"
    ]
    
    success_count = 0
    for query in french_queries:
        logger.info(f"🔍 Testing: '{query}'")
        results = rag_manager.search_books(query, n_results=5)
        
        found = False
        for result in results:
            if result.get('book_id') == 6570:
                logger.info(f"  ✅ Found with score: {result.get('similarity_score', 0):.3f}")
                found = True
                success_count += 1
                break
        
        if not found:
            logger.info(f"  ❌ Not found directly")
    
    logger.info(f"French queries success rate: {success_count}/{len(french_queries)}")
    return success_count > 0

if __name__ == "__main__":
    print("🔍 Final Verification Test")
    print("=" * 50)
    
    # Run all tests
    tests = [
        ("Direct RAG Search", test_direct_rag_search),
        ("Wikipedia Integration", test_wikipedia_integration),
        ("French Queries", test_french_queries),
        ("Agent System", test_agent_system),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name}...")
        try:
            result = test_func()
            if result:
                print(f"✅ {test_name} PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    print(f"\n📊 RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ ALL TESTS PASSED! French/English correspondence is working correctly.")
    elif passed > 0:
        print("⚠️ PARTIAL SUCCESS: Some functionality is working.")
    else:
        print("❌ ALL TESTS FAILED: French/English correspondence needs more work.")
    
    print("\n🏁 Final verification completed")