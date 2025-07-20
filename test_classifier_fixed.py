#!/usr/bin/env python3
"""
Test du système de classification LangChain avec les corrections
"""
import sys
import os

# Ajouter le projet au path
sys.path.insert(0, '/home/utilisateur/dual-book-advisor')

def test_fixed_classification():
    """Test de la classification avec les corrections appliquées"""
    print("=== Test de classification avec corrections ===")
    
    # Importer le vrai ClassifierNode modifié (mais sans LLM pour les règles seules)
    from agents.langchain_agents.nodes.classifier_node import ClassifierNode
    
    # Créer une instance partielle pour tester les méthodes de règles
    classifier = ClassifierNode.__new__(ClassifierNode)
    classifier.manga_keywords = [
        'manga', 'anime', 'naruto', 'one piece', 'dragon ball', 'attack on titan',
        'death note', 'fullmetal', 'bleach', 'demon slayer', 'tokyo ghoul',
        'shounen', 'shoujo', 'seinen', 'josei', 'manhua', 'manhwa', 'otaku',
        'comics', 'bd', 'bande dessinée', 'superman', 'batman', 'marvel', 'dc',
        'tintin', 'astérix', 'superhéros'
    ]
    
    classifier.tech_keywords = [
        'python', 'javascript', 'java', 'c#', 'csharp', 'php', 'ruby', 'go',
        'cobol', 'fortran', 'pascal', 'ada', 'perl', 'scala', 'kotlin',
        'swift', 'rust', 'c++', 'cpp', 'c', 'assembly', 'assembler',
        'sql', 'nosql', 'mongodb', 'postgresql', 'mysql', 'sqlite',
        'programming', 'programmation', 'développement', 'development',
        'web', 'mobile', 'app', 'application', 'software', 'logiciel',
        'machine learning', 'data science', 'ai', 'intelligence artificielle',
        'algorithm', 'algorithme', 'code', 'coding', 'framework',
        'database', 'base de données', 'api', 'backend', 'frontend',
        'react', 'angular', 'vue', 'node', 'express', 'django', 'flask',
        'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'cloud',
        'git', 'github', 'gitlab', 'devops', 'ci/cd', 'agile', 'scrum'
    ]
    
    classifier.literature_keywords = [
        'roman', 'romans', 'novel', 'literature', 'littérature',
        'auteur', 'author', 'écrivain', 'writer', 'fiction',
        'classique', 'classic', 'poetry', 'poésie', 'théâtre', 'theater'
    ]
    
    # Liste mise à jour avec les auteurs contemporains
    classifier.known_authors = [
        # Auteurs français classiques
        'victor hugo', 'gustave flaubert', 'stendhal', 'émile zola', 'marcel proust',
        'albert camus', 'jean-paul sartre', 'simone de beauvoir', 'andré gide',
        'françois mauriac', 'andré malraux', 'charles baudelaire', 'paul verlaine',
        'arthur rimbaud', 'voltaire', 'molière', 'racine', 'corneille',
        'honoré de balzac', 'anatole france', 'georges sand', 'marguerite duras',
        'marguerite yourcenar', 'françoise sagan', 'andré breton', 'louis aragon',
        
        # Auteurs français contemporains
        'joël dicker', 'joëlle dicker', 'michel houellebecq', 'amélie nothomb',
        'frédéric beigbeder', 'anna gavalda', 'guillaume musso', 'marc lévy',
        'katherine pancol', 'agnès martin-lugand', 'david foenkinos', 'éric-emmanuel schmitt',
        'bernard werber', 'maxime chattam', 'fred vargas', 'pierre lemaitre',
        'delphine de vigan', 'leïla slimani', 'yasmina reza', 'philippe claudel',
        
        # Auteurs internationaux classiques
        'shakespeare', 'dickens', 'tolstoy', 'tolstoï', 'dostoevsky', 'kafka',
        'hemingway', 'steinbeck', 'orwell', 'joyce', 'wilde', 'austen',
        'charlotte brontë', 'emily brontë', 'virginia woolf', 'james joyce',
        'thomas mann', 'hermann hesse', 'gabriel garcia marquez', 'mario vargas llosa',
        'jorge luis borges', 'julio cortázar', 'isabel allende', 'octavio paz',
        
        # Auteurs internationaux contemporains
        'stephen king', 'dan brown', 'john grisham', 'haruki murakami',
        'paulo coelho', 'elena ferrante', 'sally rooney', 'margaret atwood',
        'toni morrison', 'zadie smith', 'ian mcewan', 'salman rushdie',
        'chimamanda ngozi adichie', 'donna tartt', 'jonathan franzen', 'david mitchell',
        'gillian flynn', 'gone girl', 'stieg larsson', 'henning mankell'
    ]
    
    # Tester avec les requêtes problématiques
    test_queries = [
        "recommande moi des oeuvres de joël dicker",
        "livres de victor hugo", 
        "oeuvres de gabriel garcia marquez",
        "romans de stephen king",
        "joël dicker",
        "donne moi des livres de elena ferrante",
        "œuvres de marguerite duras",
        "qui a écrit l'étranger",
        "livres de tolstoï",  # Dans known_authors
        "recommande moi des livres de shakespeare"  # Dans known_authors
    ]
    
    for query in test_queries:
        try:
            result = classifier._rule_based_classification(query)
            print(f"Query: '{query}'")
            print(f"  -> Agent: {result['agent_type']}")
            print(f"  -> Confidence: {result['confidence']}")
            print(f"  -> Reasoning: {result['reasoning']}")
            
            # Test des méthodes individuelles
            query_lower = query.lower()
            print(f"  -> is_likely_literature_query: {classifier._is_likely_literature_query(query_lower)}")
            potential_author = classifier._detect_author_name_pattern(query_lower)
            print(f"  -> detected_author_pattern: {potential_author}")
            print()
        except Exception as e:
            print(f"Erreur pour '{query}': {e}")
            print()

if __name__ == "__main__":
    test_fixed_classification()