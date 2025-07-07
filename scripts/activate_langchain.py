#!/usr/bin/env python3
"""
Patch simple pour rendre l'agent littéraire intelligent
"""
import os
import re
from pathlib import Path

def create_intelligent_method():
    """Crée la méthode intelligente pour comprendre les requêtes"""
    
    method_code = '''    def get_literature_recommendations_intelligent(self, query: str, user_id: int = 1) -> str:
        """Version intelligente qui comprend les requêtes complexes"""
        try:
            import re
            from apps.books.models import LiteratureBook
            
            start_time = time.time()
            query_lower = query.lower()
            
            # Analyser la requête
            analysis = self._analyze_literature_query(query_lower)
            
            if analysis['type'] == 'list_request':
                # Demande de liste (ex: "10 livres de fantasy")
                books = self._get_books_by_genre(analysis['genre'], analysis['count'])
                if books:
                    response = f"📚 **{analysis['count']} Livres {analysis['genre'].title()}**\\n\\n"
                    
                    for i, book in enumerate(books, 1):
                        response += f"{i}. **{book.title}** de {book.authors}\\n"
                        if book.average_rating:
                            response += f"   ⭐ Note: {book.average_rating}/5"
                        if book.published_year:
                            response += f" | 📅 {book.published_year}"
                        response += "\\n"
                        if book.description:
                            desc = book.description[:100] + "..." if len(book.description) > 100 else book.description
                            response += f"   📖 {desc}\\n"
                        response += "\\n"
                    
                    processing_time = time.time() - start_time
                    response += f"⚡ Recherche en {processing_time:.1f}s"
                    return response
                else:
                    return f"💔 Désolé, je n'ai pas trouvé de livres {analysis['genre']} dans ma base"
            
            elif analysis['type'] == 'author_works':
                # Demande d'œuvres d'auteur
                books = self._get_books_by_author(analysis['author'])
                if books:
                    response = f"📚 **Œuvres de {analysis['author'].title()}**\\n\\n"
                    
                    for i, book in enumerate(books[:10], 1):
                        response += f"{i}. **{book.title}**\\n"
                        if book.average_rating:
                            response += f"   ⭐ Note: {book.average_rating}/5"
                        if book.published_year:
                            response += f" | 📅 {book.published_year}"
                        response += "\\n\\n"
                    
                    processing_time = time.time() - start_time
                    response += f"⚡ Recherche en {processing_time:.1f}s"
                    return response
                else:
                    return f"💔 Aucune œuvre de {analysis['author'].title()} trouvée dans ma base"
            
            else:
                # Requête générale - utiliser le RAG original
                return self._get_literature_recommendations_original(query, user_id)
        
        except Exception as e:
            logger.error(f"Erreur agent intelligent: {e}")
            return self._get_literature_recommendations_original(query, user_id)
    
    def _analyze_literature_query(self, query_lower: str) -> dict:
        """Analyse intelligente des requêtes littéraires"""
        import re
        
        analysis = {
            'type': 'general',
            'genre': None,
            'author': None,
            'count': 10
        }
        
        # Détecter les demandes de listes
        list_patterns = [
            r'(?:donne.{0,20}moi|liste.{0,10}|trouve.{0,10})?\\s*(\\d+)\\s+livres?\\s+de\\s+(\\w+)',
            r'(\\d+)\\s+(\\w+)\\s+livres?',
            r'livres?\\s+de\\s+(fantasy|science fiction|romance|thriller|horror|mystery)',
        ]
        
        for pattern in list_patterns:
            match = re.search(pattern, query_lower)
            if match:
                analysis['type'] = 'list_request'
                groups = match.groups()
                if len(groups) >= 2 and groups[0].isdigit():
                    analysis['count'] = min(int(groups[0]), 20)  # Max 20 livres
                    analysis['genre'] = groups[1]
                elif len(groups) == 1:
                    analysis['genre'] = groups[0]
                break
        
        # Mapping des genres français vers anglais
        genre_mapping = {
            'fantasy': 'Fantasy',
            'fantastique': 'Fantasy',
            'science fiction': 'Science Fiction',
            'sci-fi': 'Science Fiction',
            'romance': 'Romance',
            'thriller': 'Thriller',
            'horreur': 'Horror',
            'horror': 'Horror',
            'mystery': 'Mystery',
            'policier': 'Mystery',
            'young adult': 'Young Adult',
            'ado': 'Young Adult',
            'classique': 'Classics',
            'historic': 'Historical Fiction',
            'historique': 'Historical Fiction',
        }
        
        if analysis['genre'] and analysis['genre'] in genre_mapping:
            analysis['genre'] = genre_mapping[analysis['genre']]
        
        # Détecter les demandes d'auteur
        author_patterns = [
            r'(?:livres?|oeuvres?|romans?)\\s+de\\s+([a-zA-Z\\s]+?)(?:\\s|$)',
            r'([a-zA-Z\\s]+?)\\s+(?:livres?|oeuvres?|romans?)',
        ]
        
        for pattern in author_patterns:
            match = re.search(pattern, query_lower)
            if match:
                author = match.group(1).strip()
                # Vérifier que ce n'est pas un genre
                if author not in ['fantasy', 'science fiction', 'romance', 'thriller', 'horror']:
                    analysis['type'] = 'author_works'
                    analysis['author'] = author
                    break
        
        return analysis
    
    def _get_books_by_genre(self, genre: str, count: int = 10):
        """Récupère des livres par genre"""
        from apps.books.models import LiteratureBook
        
        if not genre:
            return []
        
        # Recherche par catégories
        books = list(LiteratureBook.objects.filter(
            categories__icontains=genre
        ).order_by('-average_rating')[:count * 2])
        
        if not books:
            # Recherche par description
            books = list(LiteratureBook.objects.filter(
                description__icontains=genre.lower()
            ).order_by('-average_rating')[:count * 2])
        
        # Filtrer les livres bien notés
        good_books = [book for book in books if book.average_rating and book.average_rating >= 3.5]
        
        if len(good_books) >= count:
            return good_books[:count]
        else:
            return books[:count]
    
    def _get_books_by_author(self, author: str):
        """Récupère des livres par auteur"""
        from apps.books.models import LiteratureBook
        
        if not author:
            return []
        
        return list(LiteratureBook.objects.filter(
            authors__icontains=author
        ).order_by('-average_rating')[:15])
    
    def _get_literature_recommendations_original(self, query: str, user_id: int = 1) -> str:
        """Version originale pour les requêtes générales"""
        try:
            if not self.literature_rag:
                return "📚 Service littéraire temporairement indisponible."
            
            expanded_query = self.expand_query(query)
            recommendations = self.literature_rag.get_book_recommendations(
                user_id=user_id,
                query=expanded_query,
                n_recommendations=3
            )
            
            if recommendations:
                response = "📚 **Recommandations Littéraires**\\n\\n"
                
                for i, rec in enumerate(recommendations, 1):
                    book = rec['book']
                    response += f"{i}. **{book['title']}** de {book['authors']}\\n"
                    response += f"   ⭐ Note: {book['average_rating']}/5"
                    if book['published_year']:
                        response += f" | 📅 {book['published_year']}"
                    response += f"\\n   📊 Pertinence: {rec['similarity_score']:.1%}\\n"
                    response += f"   💡 {rec['reason']}\\n"
                    response += f"   📖 {book['description'][:120]}...\\n\\n"
                
                return response
            else:
                return self._generate_literature_fallback(query)
                
        except Exception as e:
            logger.error(f"Erreur dans RAG original: {e}")
            return "📚 Désolé, j'ai rencontré un problème."
'''
    
    return method_code

def patch_simple_agents():
    """Patch le fichier simple_agents.py"""
    
    agents_file = Path('agents/simple_agents.py')
    
    if not agents_file.exists():
        print("❌ agents/simple_agents.py non trouvé")
        return False
    
    print(f"🔧 Patch de {agents_file}")
    
    # Lire le fichier
    content = agents_file.read_text(encoding='utf-8')
    
    # Créer une sauvegarde
    backup_file = agents_file.with_suffix('.py.backup4')
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"💾 Sauvegarde: {backup_file}")
    
    # Ajouter la méthode intelligente après get_literature_recommendations
    intelligent_method = create_intelligent_method()
    
    # Trouver la fin de get_literature_recommendations
    pattern = r'(def get_literature_recommendations\(self.*?return "📚.*?"\n)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        # Insérer la nouvelle méthode après
        end_pos = match.end()
        new_content = content[:end_pos] + "\n" + intelligent_method + "\n" + content[end_pos:]
        
        # Remplacer l'appel dans get_literature_recommendations
        new_content = new_content.replace(
            'def get_literature_recommendations(self, query: str, user_id: int = 1) -> str:',
            'def get_literature_recommendations(self, query: str, user_id: int = 1) -> str:\n        """Point d\'entrée principal - utilise l\'agent intelligent"""\n        return self.get_literature_recommendations_intelligent(query, user_id)\n    \n    def get_literature_recommendations_OLD(self, query: str, user_id: int = 1) -> str:'
        )
        
        # Sauvegarder
        with open(agents_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ Patch appliqué avec succès")
        return True
    else:
        print("❌ Impossible de trouver la méthode à patcher")
        return False

def test_intelligent_agent():
    """Test l'agent intelligent"""
    print("\n🧪 Test de l'agent intelligent...")
    
    test_queries = [
        "donne moi 10 livres de fantasy",
        "5 livres de science fiction", 
        "livres de tolstoy",
        "oeuvres de stephen king",
    ]
    
    try:
        import os, sys, django
        sys.path.append('.')
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
        django.setup()
        
        # Recharger le module
        import importlib
        import agents.simple_agents
        importlib.reload(agents.simple_agents)
        
        from agents.simple_agents import SimpleAgentManager
        
        agent = SimpleAgentManager()
        
        for query in test_queries:
            print(f"\n🔍 Test: '{query}'")
            try:
                result = agent.get_literature_recommendations(query)
                print(f"✅ Résultat: {result[:150]}...")
            except Exception as e:
                print(f"❌ Erreur: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test: {e}")
        return False

def main():
    """Fonction principale"""
    print("🚀 Patch Agent Intelligent")
    print("=" * 40)
    
    if patch_simple_agents():
        if test_intelligent_agent():
            print("\n🎉 Agent intelligent activé !")
            print("💡 Testez avec: python test_agents.py")
            print("💡 Ou directement: 'donne moi 10 livres de fantasy'")
        else:
            print("\n⚠️ Patch appliqué mais test échoué")
    else:
        print("\n❌ Échec du patch")
        # Restaurer la sauvegarde
        backup_file = Path('agents/simple_agents.py.backup4')
        if backup_file.exists():
            print("🔄 Restauration de la sauvegarde...")
            import shutil
            shutil.copy(backup_file, 'agents/simple_agents.py')

if __name__ == "__main__":
    main()