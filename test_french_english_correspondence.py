#!/usr/bin/env python3
"""
Test script for French/English title correspondence functionality
Tests the specific case: "qui a écrit Les Contes de Shakespeare?" 
Expected: Should find "Tales from Shakespeare" by Charles Lamb and Mary Lamb
"""

import os
import sys
import django
import logging
from typing import Dict, Any, List
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class FrenchEnglishCorrespondenceTest:
    """Test class for French/English title correspondence"""
    
    def __init__(self):
        self.test_results = []
        self.setup_components()
    
    def setup_components(self):
        """Setup all required components for testing"""
        try:
            # Import components
            from agents.langchain_agents.graph_manager import BookAdvisorGraphManager
            from agents.langchain_agents.tools.rag_tools import LiteratureBookSearchTool, WikipediaSearchTool
            from rags.literature_rag.literature_rag_manager import LiteratureRAGManager
            from langchain_ollama import ChatOllama
            
            # Initialize components
            self.graph_manager = BookAdvisorGraphManager(
                llm_provider="ollama",
                model_name="llama3.2"
            )
            
            self.literature_tool = LiteratureBookSearchTool()
            self.wikipedia_tool = WikipediaSearchTool()
            self.rag_manager = LiteratureRAGManager()
            
            logger.info("✅ All components initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Error setting up components: {e}")
            raise
    
    def test_specific_case(self) -> Dict[str, Any]:
        """Test the specific case: 'qui a écrit Les Contes de Shakespeare?'"""
        logger.info("🧪 Testing specific case: 'qui a écrit Les Contes de Shakespeare?'")
        
        query = "qui a écrit Les Contes de Shakespeare?"
        test_result = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "steps": [],
            "final_result": None,
            "success": False,
            "found_authors": [],
            "found_title": None
        }
        
        try:
            # Step 1: Test direct RAG search in French
            logger.info("📚 Step 1: Testing direct RAG search with French title")
            rag_results = self.literature_tool._run(query, n_results=5, user_id=1)
            
            step1_result = {
                "step": "direct_rag_search",
                "query": query,
                "results_count": len(rag_results),
                "results": rag_results[:3] if rag_results else [],
                "success": len(rag_results) > 0
            }
            test_result["steps"].append(step1_result)
            
            # Check if we found the correct book directly
            found_shakespeare_tales = False
            for result in rag_results:
                title = result.get('title', '').lower()
                if 'shakespeare' in title and ('tales' in title or 'contes' in title):
                    found_shakespeare_tales = True
                    test_result["found_title"] = result.get('title')
                    test_result["found_authors"] = result.get('authors', '')
                    logger.info(f"✅ Found directly: {result.get('title')} by {result.get('authors')}")
                    break
            
            # Step 2: Test Wikipedia search for title correspondence
            logger.info("🌐 Step 2: Testing Wikipedia search for title correspondence")
            wiki_queries = [
                "Les Contes de Shakespeare",
                "Contes de Shakespeare",
                "Tales from Shakespeare",
                "Charles Lamb Mary Lamb Shakespeare"
            ]
            
            wiki_results = []
            for wiki_query in wiki_queries:
                logger.info(f"   🔍 Searching Wikipedia for: {wiki_query}")
                wiki_result = self.wikipedia_tool._run(wiki_query, language="fr")
                wiki_results.append({
                    "query": wiki_query,
                    "success": wiki_result.get('success', False),
                    "result": wiki_result
                })
                
                # Check if we found useful information
                if wiki_result.get('success') and wiki_result.get('summary'):
                    summary = wiki_result.get('summary', '').lower()
                    if ('lamb' in summary or 'shakespeare' in summary) and 'tales' in summary:
                        logger.info(f"   ✅ Found Wikipedia info: {wiki_result.get('title')}")
                        break
            
            step2_result = {
                "step": "wikipedia_search",
                "searches": wiki_results,
                "success": any(r["success"] for r in wiki_results)
            }
            test_result["steps"].append(step2_result)
            
            # Step 3: Test RAG search with English title
            logger.info("📚 Step 3: Testing RAG search with English title")
            english_queries = [
                "Tales from Shakespeare Charles Lamb",
                "Tales from Shakespeare Mary Lamb",
                "Tales from Shakespeare",
                "Charles Lamb Mary Lamb",
                "Shakespeare tales retold"
            ]
            
            english_results = []
            for eng_query in english_queries:
                logger.info(f"   🔍 Searching RAG for: {eng_query}")
                eng_result = self.literature_tool._run(eng_query, n_results=5, user_id=1)
                english_results.append({
                    "query": eng_query,
                    "results_count": len(eng_result),
                    "results": eng_result[:3] if eng_result else []
                })
                
                # Check if we found the correct book
                for result in eng_result:
                    title = result.get('title', '').lower()
                    authors = result.get('authors', '').lower()
                    if ('shakespeare' in title and 'tales' in title) or ('lamb' in authors and 'shakespeare' in title):
                        test_result["found_title"] = result.get('title')
                        test_result["found_authors"] = result.get('authors')
                        logger.info(f"   ✅ Found with English: {result.get('title')} by {result.get('authors')}")
                        found_shakespeare_tales = True
                        break
                
                if found_shakespeare_tales:
                    break
            
            step3_result = {
                "step": "english_rag_search",
                "searches": english_results,
                "success": found_shakespeare_tales
            }
            test_result["steps"].append(step3_result)
            
            # Step 4: Test full agent system
            logger.info("🤖 Step 4: Testing full agent system")
            try:
                agent_response = self.graph_manager.get_literature_recommendations(query, user_id=1)
                step4_result = {
                    "step": "full_agent_system",
                    "success": agent_response.get('success', False),
                    "response": agent_response.get('response', ''),
                    "agent_used": agent_response.get('agent_used', ''),
                    "processing_time": agent_response.get('processing_time', 0),
                    "metadata": agent_response.get('metadata', {})
                }
                test_result["steps"].append(step4_result)
                
                # Check if agent response mentions the correct information
                response_text = agent_response.get('response', '').lower()
                if ('lamb' in response_text and 'shakespeare' in response_text) or 'tales from shakespeare' in response_text:
                    logger.info("✅ Agent response contains correct information")
                    test_result["success"] = True
                    test_result["final_result"] = agent_response
                else:
                    logger.warning("⚠️ Agent response may not contain correct information")
                    
            except Exception as e:
                logger.error(f"❌ Error in agent system: {e}")
                step4_result = {
                    "step": "full_agent_system",
                    "success": False,
                    "error": str(e)
                }
                test_result["steps"].append(step4_result)
            
            # Final assessment
            if not test_result["success"]:
                test_result["success"] = found_shakespeare_tales
            
            logger.info(f"📊 Test completed. Success: {test_result['success']}")
            
        except Exception as e:
            logger.error(f"❌ Error in test: {e}")
            test_result["error"] = str(e)
        
        return test_result
    
    def test_database_content(self) -> Dict[str, Any]:
        """Test what's actually in the database for Shakespeare-related content"""
        logger.info("🗄️ Testing database content for Shakespeare-related works")
        
        try:
            from apps.books.models import LiteratureBook
            
            # Search for Shakespeare-related books
            shakespeare_books = LiteratureBook.objects.filter(
                title__icontains="shakespeare"
            )
            
            lamb_books = LiteratureBook.objects.filter(
                authors__icontains="lamb"
            )
            
            tales_books = LiteratureBook.objects.filter(
                title__icontains="tales"
            )
            
            result = {
                "shakespeare_books": [
                    {
                        "id": book.id,
                        "title": book.title,
                        "authors": book.authors,
                        "description": book.description[:200] if book.description else "",
                        "average_rating": float(book.average_rating) if book.average_rating else 0.0
                    } for book in shakespeare_books[:10]
                ],
                "lamb_books": [
                    {
                        "id": book.id,
                        "title": book.title,
                        "authors": book.authors,
                        "description": book.description[:200] if book.description else "",
                        "average_rating": float(book.average_rating) if book.average_rating else 0.0
                    } for book in lamb_books[:10]
                ],
                "tales_books": [
                    {
                        "id": book.id,
                        "title": book.title,
                        "authors": book.authors,
                        "description": book.description[:200] if book.description else "",
                        "average_rating": float(book.average_rating) if book.average_rating else 0.0
                    } for book in tales_books[:10]
                ],
                "counts": {
                    "shakespeare_books": shakespeare_books.count(),
                    "lamb_books": lamb_books.count(),
                    "tales_books": tales_books.count()
                }
            }
            
            logger.info(f"📚 Found {result['counts']['shakespeare_books']} Shakespeare books")
            logger.info(f"📚 Found {result['counts']['lamb_books']} Lamb books")
            logger.info(f"📚 Found {result['counts']['tales_books']} Tales books")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error checking database: {e}")
            return {"error": str(e)}
    
    def test_wikipedia_tool_directly(self) -> Dict[str, Any]:
        """Test Wikipedia tool directly with various queries"""
        logger.info("🌐 Testing Wikipedia tool directly")
        
        queries = [
            ("Les Contes de Shakespeare", "fr"),
            ("Tales from Shakespeare", "en"),
            ("Charles Lamb", "en"),
            ("Mary Lamb", "en"),
            ("Charles Lamb Mary Lamb", "en"),
            ("Contes de Shakespeare", "fr")
        ]
        
        results = []
        for query, language in queries:
            logger.info(f"   🔍 Testing: {query} ({language})")
            try:
                result = self.wikipedia_tool._run(query, language=language)
                results.append({
                    "query": query,
                    "language": language,
                    "success": result.get('success', False),
                    "title": result.get('title', ''),
                    "summary": result.get('summary', '')[:300] if result.get('summary') else '',
                    "type": result.get('type', ''),
                    "url": result.get('url', '')
                })
                
                if result.get('success'):
                    logger.info(f"   ✅ Found: {result.get('title')}")
                else:
                    logger.info(f"   ❌ Not found: {result.get('message', 'Unknown error')}")
                    
            except Exception as e:
                logger.error(f"   ❌ Error: {e}")
                results.append({
                    "query": query,
                    "language": language,
                    "success": False,
                    "error": str(e)
                })
        
        return {
            "wikipedia_tests": results,
            "successful_queries": len([r for r in results if r.get('success', False)])
        }
    
    def test_rag_embeddings(self) -> Dict[str, Any]:
        """Test RAG embeddings and similarity search"""
        logger.info("🧠 Testing RAG embeddings and similarity search")
        
        try:
            # Test different query variations
            test_queries = [
                "Les Contes de Shakespeare",
                "Contes de Shakespeare",
                "Tales from Shakespeare",
                "Charles Lamb Shakespeare",
                "Mary Lamb Shakespeare",
                "qui a écrit Les Contes de Shakespeare",
                "author of Tales from Shakespeare",
                "Shakespeare stories retold"
            ]
            
            results = []
            for query in test_queries:
                logger.info(f"   🔍 Testing RAG: {query}")
                try:
                    search_results = self.rag_manager.search_books(query, n_results=5)
                    results.append({
                        "query": query,
                        "results_count": len(search_results),
                        "top_results": [
                            {
                                "title": r.get('title'),
                                "authors": r.get('authors'),
                                "similarity_score": r.get('similarity_score', 0),
                                "matched_text": r.get('matched_text', '')[:100]
                            } for r in search_results[:3]
                        ]
                    })
                    
                    # Check for relevant results
                    found_relevant = False
                    for result in search_results:
                        title = result.get('title', '').lower()
                        authors = result.get('authors', '').lower()
                        if ('shakespeare' in title and 'tales' in title) or ('lamb' in authors and 'shakespeare' in title):
                            found_relevant = True
                            logger.info(f"   ✅ Found relevant: {result.get('title')} by {result.get('authors')}")
                            break
                    
                    if not found_relevant:
                        logger.info(f"   ❌ No relevant results for: {query}")
                        
                except Exception as e:
                    logger.error(f"   ❌ Error with query '{query}': {e}")
                    results.append({
                        "query": query,
                        "error": str(e)
                    })
            
            return {
                "rag_tests": results,
                "total_queries": len(test_queries)
            }
            
        except Exception as e:
            logger.error(f"❌ Error in RAG testing: {e}")
            return {"error": str(e)}
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and compile results"""
        logger.info("🚀 Starting comprehensive French/English correspondence test")
        
        all_results = {
            "test_timestamp": datetime.now().isoformat(),
            "test_description": "French/English title correspondence test for 'qui a écrit Les Contes de Shakespeare?'",
            "expected_result": "Should find 'Tales from Shakespeare' by Charles Lamb and Mary Lamb",
            "tests": {}
        }
        
        # Run all tests
        test_functions = [
            ("database_content", self.test_database_content),
            ("wikipedia_tool", self.test_wikipedia_tool_directly),
            ("rag_embeddings", self.test_rag_embeddings),
            ("specific_case", self.test_specific_case)
        ]
        
        for test_name, test_func in test_functions:
            try:
                logger.info(f"🧪 Running test: {test_name}")
                result = test_func()
                all_results["tests"][test_name] = result
                logger.info(f"✅ Test {test_name} completed")
            except Exception as e:
                logger.error(f"❌ Test {test_name} failed: {e}")
                all_results["tests"][test_name] = {"error": str(e)}
        
        # Generate summary
        all_results["summary"] = self.generate_summary(all_results["tests"])
        
        return all_results
    
    def generate_summary(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of all test results"""
        summary = {
            "overall_success": False,
            "issues_found": [],
            "recommendations": [],
            "data_availability": {},
            "functionality_status": {}
        }
        
        # Check database content
        db_test = test_results.get("database_content", {})
        if db_test.get("counts"):
            summary["data_availability"] = {
                "shakespeare_books": db_test["counts"]["shakespeare_books"],
                "lamb_books": db_test["counts"]["lamb_books"],
                "tales_books": db_test["counts"]["tales_books"]
            }
            
            if db_test["counts"]["shakespeare_books"] == 0:
                summary["issues_found"].append("No Shakespeare books found in database")
            if db_test["counts"]["lamb_books"] == 0:
                summary["issues_found"].append("No Lamb books found in database")
        
        # Check Wikipedia functionality
        wiki_test = test_results.get("wikipedia_tool", {})
        if wiki_test.get("successful_queries", 0) > 0:
            summary["functionality_status"]["wikipedia"] = "working"
        else:
            summary["functionality_status"]["wikipedia"] = "not_working"
            summary["issues_found"].append("Wikipedia search not working properly")
        
        # Check RAG functionality
        rag_test = test_results.get("rag_embeddings", {})
        if rag_test.get("rag_tests"):
            summary["functionality_status"]["rag"] = "working"
        else:
            summary["functionality_status"]["rag"] = "not_working"
            summary["issues_found"].append("RAG search not working properly")
        
        # Check specific case
        specific_test = test_results.get("specific_case", {})
        if specific_test.get("success"):
            summary["overall_success"] = True
        else:
            summary["issues_found"].append("Specific French/English correspondence test failed")
        
        # Generate recommendations
        if summary["data_availability"].get("shakespeare_books", 0) == 0:
            summary["recommendations"].append("Add Shakespeare-related books to the database")
        if summary["data_availability"].get("lamb_books", 0) == 0:
            summary["recommendations"].append("Add Charles Lamb and Mary Lamb books to the database")
        if summary["functionality_status"].get("wikipedia") == "not_working":
            summary["recommendations"].append("Fix Wikipedia search functionality")
        if not summary["overall_success"]:
            summary["recommendations"].append("Improve French/English title correspondence logic")
        
        return summary

def main():
    """Main function to run the tests"""
    print("🧪 French/English Title Correspondence Test")
    print("=" * 60)
    
    try:
        # Create test instance
        test = FrenchEnglishCorrespondenceTest()
        
        # Run all tests
        results = test.run_all_tests()
        
        # Save results to file
        output_file = f"/home/utilisateur/dual-book-advisor/test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Full results saved to: {output_file}")
        
        # Print summary
        print("\n📊 TEST SUMMARY")
        print("=" * 40)
        
        summary = results.get("summary", {})
        print(f"Overall Success: {'✅' if summary.get('overall_success') else '❌'}")
        
        print("\nData Availability:")
        data_avail = summary.get("data_availability", {})
        print(f"  - Shakespeare books: {data_avail.get('shakespeare_books', 0)}")
        print(f"  - Lamb books: {data_avail.get('lamb_books', 0)}")
        print(f"  - Tales books: {data_avail.get('tales_books', 0)}")
        
        print("\nFunctionality Status:")
        func_status = summary.get("functionality_status", {})
        for func, status in func_status.items():
            print(f"  - {func}: {'✅' if status == 'working' else '❌'}")
        
        if summary.get("issues_found"):
            print("\nIssues Found:")
            for issue in summary["issues_found"]:
                print(f"  - ❌ {issue}")
        
        if summary.get("recommendations"):
            print("\nRecommendations:")
            for rec in summary["recommendations"]:
                print(f"  - 💡 {rec}")
        
        # Show specific case result
        specific_test = results.get("tests", {}).get("specific_case", {})
        if specific_test:
            print(f"\nSpecific Case Result:")
            print(f"  Query: {specific_test.get('query', 'N/A')}")
            print(f"  Success: {'✅' if specific_test.get('success') else '❌'}")
            if specific_test.get("found_title"):
                print(f"  Found Title: {specific_test['found_title']}")
            if specific_test.get("found_authors"):
                print(f"  Found Authors: {specific_test['found_authors']}")
        
        return results
        
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main()