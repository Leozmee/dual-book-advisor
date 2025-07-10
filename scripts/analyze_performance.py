#!/usr/bin/env python3
"""
Analyse des performances du système de recommandations
"""
import os
import sys
import time
import django

# Configuration Django
sys.path.insert(0, '/home/utilisateur/dual-book-advisor')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from agents.ollama_gemma_manager import GemmaAgentManager
from agents.cover_image_service import cover_service

def analyze_performance():
    print("=== ANALYSE DES PERFORMANCES ===\n")
    
    manager = GemmaAgentManager()
    
    # Test Literature Agent
    print("1. Test Agent Littérature")
    query = "Je cherche des livres comme Harry Potter"
    
    total_start = time.time()
    
    # Mesure RAG
    rag_start = time.time()
    if manager.literature_rag:
        recommendations = manager.literature_rag.search_content(query, n_results=5)
        rag_time = time.time() - rag_start
        print(f"   ⏱️  RAG search: {rag_time:.2f}s ({len(recommendations)} résultats)")
    else:
        print("   ❌ RAG Literature non disponible")
        return
    
    # Mesure préparation contexte
    context_start = time.time()
    books_context = manager._format_books_context(recommendations)
    context_time = time.time() - context_start
    print(f"   ⏱️  Contexte: {context_time:.2f}s")
    
    # Mesure Gemma
    gemma_start = time.time()
    gemma_response = manager.gemma.generate_book_recommendation(
        query=query,
        books_context=books_context,
        agent_type="literature"
    )
    gemma_time = time.time() - gemma_start
    print(f"   ⏱️  Gemma: {gemma_time:.2f}s")
    
    # Mesure enrichissement images
    if manager.use_cover_images:
        images_start = time.time()
        enriched_response = manager._enrich_response_with_images(gemma_response, recommendations, 'literature')
        images_time = time.time() - images_start
        print(f"   ⏱️  Images: {images_time:.2f}s")
    
    total_time = time.time() - total_start
    print(f"   ⏱️  TOTAL: {total_time:.2f}s")
    
    print("\n" + "="*50)
    
    # Analyse des composants
    print("\n2. Analyse des goulots d'étranglement:")
    if 'rag_time' in locals():
        print(f"   📊 RAG: {rag_time:.2f}s ({rag_time/total_time*100:.1f}%)")
    if 'context_time' in locals():
        print(f"   📊 Contexte: {context_time:.2f}s ({context_time/total_time*100:.1f}%)")
    if 'gemma_time' in locals():
        print(f"   📊 Gemma: {gemma_time:.2f}s ({gemma_time/total_time*100:.1f}%)")
    if 'images_time' in locals():
        print(f"   📊 Images: {images_time:.2f}s ({images_time/total_time*100:.1f}%)")
    
    # Test service d'images seul
    print("\n3. Test service d'images:")
    img_start = time.time()
    test_url = cover_service.get_cover_image("Harry Potter", "J.K. Rowling", "book")
    img_time = time.time() - img_start
    print(f"   ⏱️  Image seule: {img_time:.2f}s")
    
    # Test Ollama seul
    print("\n4. Test Ollama seul:")
    ollama_start = time.time()
    test_response = manager.gemma.generate_response("Bonjour, comment allez-vous?", max_tokens=50)
    ollama_time = time.time() - ollama_start
    print(f"   ⏱️  Ollama simple: {ollama_time:.2f}s")
    
    return {
        'total_time': total_time,
        'rag_time': locals().get('rag_time', 0),
        'gemma_time': locals().get('gemma_time', 0),
        'images_time': locals().get('images_time', 0),
        'context_time': locals().get('context_time', 0)
    }

def suggest_optimizations(perf_data):
    print("\n" + "="*50)
    print("📈 SUGGESTIONS D'OPTIMISATION")
    print("="*50)
    
    total = perf_data['total_time']
    
    if perf_data['gemma_time'] > total * 0.5:
        print("\n🔴 PRIORITÉ HAUTE - Gemma/Ollama (>50% du temps)")
        print("   • Réduire max_tokens dans les prompts")
        print("   • Utiliser des prompts plus courts et précis")
        print("   • Envisager un modèle plus rapide (gemma2:2b-instruct-q4_0)")
        print("   • Optimiser le cache d'Ollama")
    
    if perf_data['rag_time'] > total * 0.3:
        print("\n🟡 PRIORITÉ MOYENNE - RAG (>30% du temps)")
        print("   • Réduire n_results de 5 à 3")
        print("   • Optimiser les embeddings")
        print("   • Ajouter un cache pour les requêtes fréquentes")
    
    if perf_data['images_time'] > total * 0.2:
        print("\n🟡 PRIORITÉ MOYENNE - Images (>20% du temps)")
        print("   • Limiter à 1 image au lieu de 2")
        print("   • Paralléliser les requêtes d'images")
        print("   • Augmenter le cache d'images")
    
    print("\n🟢 OPTIMISATIONS GÉNÉRALES:")
    print("   • Implémenter un cache Redis")
    print("   • Paralléliser RAG + démarrage Ollama")
    print("   • Pré-charger le modèle Ollama")
    print("   • Optimiser les prompts système")

if __name__ == "__main__":
    try:
        perf_data = analyze_performance()
        suggest_optimizations(perf_data)
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()