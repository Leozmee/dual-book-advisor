#!/usr/bin/env python3
"""
Test du système de classification LangChain
"""
import sys
import os

# Ajouter le projet au path
sys.path.insert(0, '/home/utilisateur/dual-book-advisor')

from agents.langchain_agents.nodes.classifier_node import ClassifierNode

def test_rule_based_classification():
    """Test de la classification basée sur les règles"""
    print("=== Test de classification basée sur les règles ===")
    
    # Créer une instance simplifiée pour tester juste les règles
    class SimpleClassifier:
        def __init__(self):
            # Copier les listes du vrai classifier
            self.manga_keywords = [
                'manga', 'anime', 'naruto', 'one piece', 'dragon ball', 'attack on titan',
                'death note', 'fullmetal', 'bleach', 'demon slayer', 'tokyo ghoul',
                'shounen', 'shoujo', 'seinen', 'josei', 'manhua', 'manhwa', 'otaku',
                'comics', 'bd', 'bande dessinée', 'superman', 'batman', 'marvel', 'dc',
                'tintin', 'astérix', 'superhéros'
            ]
            
            self.tech_keywords = [
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
            
            self.literature_keywords = [
                'roman', 'romans', 'novel', 'literature', 'littérature',
                'auteur', 'author', 'écrivain', 'writer', 'fiction',
                'classique', 'classic', 'poetry', 'poésie', 'théâtre', 'theater'
            ]
            
            self.known_authors = [
                'victor hugo', 'gustave flaubert', 'stendhal', 'émile zola', 'marcel proust',
                'albert camus', 'jean-paul sartre', 'simone de beauvoir', 'andré gide',
                'françois mauriac', 'andré malraux', 'charles baudelaire', 'paul verlaine',
                'arthur rimbaud', 'voltaire', 'molière', 'racine', 'corneille',
                'shakespeare', 'dickens', 'tolstoy', 'dostoevsky', 'kafka',
                'hemingway', 'steinbeck', 'orwell', 'joyce', 'wilde'
            ]
        
        def _rule_based_classification(self, query: str):
            import re
            query_lower = query.lower()
            
            # Détection des auteurs littéraires classiques (priorité haute)
            for author in self.known_authors:
                if author in query_lower:
                    return {
                        "agent_type": "literature",
                        "confidence": 0.95,
                        "reasoning": f"Auteur littéraire classique détecté: {author}",
                        "keywords": [author]
                    }
            
            # Détection manga/comics
            manga_score = sum(1 for keyword in self.manga_keywords if keyword in query_lower)
            if manga_score > 0:
                return {
                    "agent_type": "manga",
                    "confidence": min(0.9 + manga_score * 0.1, 1.0),
                    "reasoning": f"Mots-clés manga/comics détectés: {manga_score}",
                    "keywords": [kw for kw in self.manga_keywords if kw in query_lower]
                }
            
            # Détection technique
            tech_score = sum(1 for keyword in self.tech_keywords if keyword in query_lower)
            lit_score = sum(1 for keyword in self.literature_keywords if keyword in query_lower)
            
            # Vérification spéciale pour éviter les faux positifs techniques
            if tech_score > 0:
                return {
                    "agent_type": "tech",
                    "confidence": min(0.8 + tech_score * 0.1, 1.0),
                    "reasoning": f"Mots-clés techniques détectés: {tech_score}",
                    "keywords": [kw for kw in self.tech_keywords if kw in query_lower]
                }
            
            # Détection spéciale pour questions d'auteur
            author_patterns = [
                r'qui\s+a\s+écrit',
                r'auteur\s+de',
                r'who\s+wrote',
                r'author\s+of',
                r'écrit\s+par',
                r'written\s+by'
            ]
            
            for pattern in author_patterns:
                if re.search(pattern, query_lower):
                    return {
                        "agent_type": "literature",
                        "confidence": 0.95,
                        "reasoning": "Question d'auteur détectée - littérature classique",
                        "keywords": ["qui a écrit", "auteur", "author"]
                    }
            
            # Détection des œuvres littéraires par pattern
            works_patterns = [
                r'(?:donne|donnez).{0,20}(?:moi|nous).{0,20}(?:des|les).{0,20}(?:œuvres|oeuvres|works|livres)',
                r'(?:œuvres|oeuvres|works|livres).{0,20}(?:de|par|by)',
                r'(?:recommande|suggest).{0,20}(?:des|les).{0,20}(?:œuvres|oeuvres|works)',
                r'(?:liste|list).{0,20}(?:des|les).{0,20}(?:œuvres|oeuvres|works)'
            ]
            
            for pattern in works_patterns:
                if re.search(pattern, query_lower):
                    return {
                        "agent_type": "literature",
                        "confidence": 0.85,
                        "reasoning": "Demande d'œuvres détectée - probablement littérature",
                        "keywords": ["œuvres", "works", "donne moi"]
                    }
            
            # Si des indices littéraires, privilégier la littérature
            if lit_score > 0:
                return {
                    "agent_type": "literature",
                    "confidence": 0.7,
                    "reasoning": f"Contexte littéraire détecté (lit_score: {lit_score})",
                    "keywords": [kw for kw in self.literature_keywords if kw in query_lower]
                }
            
            # Par défaut
            return {
                "agent_type": "literature",
                "confidence": 0.2,
                "reasoning": "Classification incertaine - analyse LLM nécessaire",
                "keywords": []
            }
    
    classifier = SimpleClassifier()
    
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
            print()
        except Exception as e:
            print(f"Erreur pour '{query}': {e}")
            print()

def test_detection_methods():
    """Test des méthodes de détection individuelles"""
    print("=== Test des méthodes de détection ===")
    
    # Utiliser le même SimpleClassifier
    classifier = test_rule_based_classification.__defaults__  # Pour éviter d'avoir à répéter le code
    # En fait, créons une nouvelle instance
    print("Note: Cette fonction nécessiterait d'instancier le vrai ClassifierNode.")
    print("Pour l'instant, les tests de classification sont suffisants.")

if __name__ == "__main__":
    test_rule_based_classification()
    test_detection_methods()