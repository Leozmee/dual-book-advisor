"""
ClassifierNode - Remplace SimpleAgentManager.route_query()
Fichier: agents/langchain_agents/nodes/classifier_node.py
"""
from typing import Dict, Any, List, Optional, Literal
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnablePassthrough
from pydantic import BaseModel, Field
import re
import logging

logger = logging.getLogger(__name__)

# Modèles Pydantic pour les sorties structurées
class QueryClassification(BaseModel):
    """Classification structurée d'une requête utilisateur"""
    agent_type: Literal["tech", "literature", "manga"] = Field(
        description="Type d'agent recommandé: tech, literature, ou manga"
    )
    confidence: float = Field(
        description="Niveau de confiance (0.0 à 1.0)",
        ge=0.0, le=1.0
    )
    reasoning: str = Field(
        description="Explication du choix de classification"
    )
    detected_keywords: List[str] = Field(
        description="Mots-clés détectés qui ont influencé la classification"
    )
    expanded_query: str = Field(
        description="Requête enrichie pour améliorer la recherche"
    )
    requested_count: int = Field(
        description="Nombre de recommandations demandé par l'utilisateur",
        default=3
    )

class ClassifierNode:
    """
    Nœud de classification intelligent pour LangGraph
    Remplace la logique de routage de SimpleAgentManager
    """
    
    def __init__(self, llm):
        self.llm = llm
        self.parser = PydanticOutputParser(pydantic_object=QueryClassification)
        self.classification_chain = self._build_classification_chain()
        
        # Dictionnaires de mots-clés (adaptés de votre logique existante)
        self.manga_keywords = [
            'manga', 'anime', 'naruto', 'one piece', 'dragon ball', 'attack on titan',
            'death note', 'fullmetal', 'bleach', 'demon slayer', 'tokyo ghoul',
            'shounen', 'shoujo', 'seinen', 'josei', 'manhua', 'manhwa', 'otaku',
            'comics', 'bd', 'bande dessinée', 'superman', 'batman', 'marvel', 'dc',
            'tintin', 'astérix', 'superhéros'
        ]
        
        self.tech_keywords = [
            'python', 'javascript', 'java', 'c#', 'csharp', 'php', 'ruby', 'go',
            'programming', 'programmation', 'développement', 'development',
            'web', 'mobile', 'app', 'application', 'software', 'logiciel',
            'machine learning', 'data science', 'ai', 'intelligence artificielle',
            'algorithm', 'algorithme', 'code', 'coding', 'framework',
            'database', 'base de données', 'api', 'backend', 'frontend'
        ]
        
        self.literature_keywords = [
            'roman', 'romans', 'novel', 'literature', 'littérature',
            'auteur', 'author', 'écrivain', 'writer', 'fiction',
            'classique', 'classic', 'poetry', 'poésie', 'théâtre', 'theater'
        ]
        
        # Dictionnaire d'expansion sémantique (adapté de votre logique)
        self.semantic_expansions = {
            # Auteurs littéraires
            'tolstoy': 'Leo Tolstoy War Peace Anna Karenina Russian literature classic',
            'tolstoï': 'Leo Tolstoy War Peace Anna Karenina Russian literature classic',
            'stephen king': 'Stephen King horror thriller It Shining Carrie Salem',
            'murakami': 'Haruki Murakami Norwegian Wood Kafka Shore Japanese literature',
            'victor hugo': 'Victor Hugo Les Misérables Hunchback Notre Dame French classic',
            'shakespeare': 'William Shakespeare Hamlet Romeo Juliet Macbeth English',
            'camus': 'Albert Camus Stranger Plague Myth Sisyphus existentialism',
            
            # Genres littéraires
            'fantasy': 'fantasy magic adventure fiction magical worlds',
            'science fiction': 'science fiction sci-fi futuristic space technology',
            'thriller': 'thriller suspense mystery crime psychological',
            'romance': 'romance love relationship contemporary historical',
            
            # Technique
            'python': 'Python programming language development beginner advanced',
            'javascript': 'JavaScript web development frontend backend Node.js',
            'c#': 'C# CSharp .NET Microsoft programming Windows development',
            'java': 'Java programming language enterprise development Android',
            'machine learning': 'machine learning AI artificial intelligence data science',
            'data science': 'data science analysis statistics Python R visualization',
            
            # Manga/Comics
            'manga': 'manga anime Japanese comic otaku shounen seinen',
            'naruto': 'Naruto ninja village hidden leaf Uzumaki Sasuke Sakura action',
            'one piece': 'One Piece pirate treasure Luffy Straw Hat Grand Line adventure',
            'comics': 'comics superhero graphic novel DC Marvel',
            'bd': 'bande dessinée comics album français',
        }
    
    def _build_classification_chain(self):
        """Construit la chaîne de classification LangChain"""
        
        classification_prompt = ChatPromptTemplate.from_template("""
Tu es un expert en classification de requêtes pour un système de recommandation de livres.

Analyse cette requête utilisateur et détermine quel agent spécialisé devrait la traiter :

**AGENTS DISPONIBLES:**
- **TECH** : Livres techniques, programmation, informatique, data science
- **LITERATURE** : Littérature générale, romans, classiques, fiction (SANS manga/anime)
- **MANGA** : Manga japonais, anime, comics, bandes dessinées

**RÈGLES DE PRIORITÉ:**
1. Si la requête mentionne des mangas, anime, comics ou BD → MANGA (priorité absolue)
2. Si la requête mentionne de la programmation, tech, langages → TECH
3. Sinon → LITERATURE (littérature classique uniquement)

**REQUÊTE UTILISATEUR:** {query}

**MOTS-CLÉS MANGA:** manga, anime, naruto, one piece, dragon ball, attack on titan, death note, shounen, seinen, comics, bd, superman, batman, marvel, dc, tintin, astérix

**MOTS-CLÉS TECH:** python, javascript, java, programming, development, web, mobile, data science, machine learning, ai, code, algorithm

**EXEMPLES:**
- "j'ai aimé naruto" → MANGA (mot-clé manga détecté)
- "livres pour apprendre Python" → TECH (programmation)
- "romans de Tolstoï" → LITERATURE (littérature classique)
- "comics superman" → MANGA (comics détecté)

Analyse la requête et fournis une classification précise avec justification.

{format_instructions}
""")
        
        return (
            {
                "query": RunnablePassthrough(),
                "format_instructions": lambda _: self.parser.get_format_instructions()
            }
            | classification_prompt
            | self.llm
            | self.parser
        )
    
    def classify_query(self, query: str) -> QueryClassification:
        """
        Classifie une requête utilisateur
        
        Args:
            query: Requête utilisateur à classifier
            
        Returns:
            QueryClassification: Classification structurée
        """
        try:
            # Classification hybride : règles + LLM
            rule_based_result = self._rule_based_classification(query)
            
            # Si les règles sont très confiantes, les utiliser directement
            if rule_based_result["confidence"] >= 0.9:
                logger.info(f"Classification par règles (confiance: {rule_based_result['confidence']})")
                return QueryClassification(
                    agent_type=rule_based_result["agent_type"],
                    confidence=rule_based_result["confidence"],
                    reasoning=rule_based_result["reasoning"],
                    detected_keywords=rule_based_result["keywords"],
                    expanded_query=self._expand_query(query),
                    requested_count=self._extract_requested_count(query)
                )
            
            # Sinon, utiliser le LLM pour une analyse plus fine
            logger.info("Classification via LLM pour cas ambigus")
            llm_result = self.classification_chain.invoke(query)
            
            # Enrichir avec l'expansion sémantique
            llm_result.expanded_query = self._expand_query(query)
            llm_result.requested_count = self._extract_requested_count(query)
            
            return llm_result
            
        except Exception as e:
            logger.error(f"Erreur classification: {e}")
            # Fallback par défaut
            return QueryClassification(
                agent_type="literature",
                confidence=0.5,
                reasoning=f"Fallback vers littérature (erreur: {str(e)})",
                detected_keywords=[],
                expanded_query=query,
                requested_count=3
            )
    
    def _rule_based_classification(self, query: str) -> Dict[str, Any]:
        """
        Classification basée sur des règles (logique de votre système actuel)
        """
        query_lower = query.lower()
        
        # Détection manga/comics (priorité absolue)
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
        
        if tech_score > lit_score and tech_score > 0:
            return {
                "agent_type": "tech",
                "confidence": min(0.8 + tech_score * 0.1, 1.0),
                "reasoning": f"Mots-clés techniques détectés: {tech_score}",
                "keywords": [kw for kw in self.tech_keywords if kw in query_lower]
            }
        
        # Détection spéciale pour questions d'auteur classique
        if self._is_author_question(query_lower):
            return {
                "agent_type": "literature",
                "confidence": 0.95,  # Confiance très élevée pour éviter le LLM
                "reasoning": "Question d'auteur détectée - littérature classique",
                "keywords": ["qui a écrit", "auteur", "author"]
            }
        
        # Par défaut : littérature (mais avec confiance modérée pour LLM)
        return {
            "agent_type": "literature",
            "confidence": 0.6 if lit_score > 0 else 0.3,
            "reasoning": f"Classification littérature par défaut (lit_score: {lit_score})",
            "keywords": [kw for kw in self.literature_keywords if kw in query_lower]
        }
    
    def _expand_query(self, query: str) -> str:
        """
        Expansion sémantique de la requête (adaptée de votre logique)
        """
        query_lower = query.lower()
        expanded_parts = [query]
        
        # Recherche de correspondances sémantiques
        for key, expansion in self.semantic_expansions.items():
            if key.lower() in query_lower:
                expanded_parts.append(expansion)
                break  # Prendre la première correspondance principale
        
        # Ajout de synonymes contextuels
        if any(word in query_lower for word in ['livre', 'book', 'ouvrage']):
            expanded_parts.append('book literature reading')
        
        if any(word in query_lower for word in ['recommandation', 'suggestion', 'conseil']):
            expanded_parts.append('recommendation suggest similar')
        
        return ' '.join(expanded_parts)
    
    def _is_author_question(self, query_lower: str) -> bool:
        """
        Détecte si la requête est une question d'auteur classique
        """
        author_patterns = [
            r'qui\s+a\s+écrit',
            r'qui\s+a\s+écrit',
            r'auteur\s+de',
            r'who\s+wrote',
            r'author\s+of',
            r'écrit\s+par',
            r'written\s+by'
        ]
        
        for pattern in author_patterns:
            if re.search(pattern, query_lower):
                return True
        return False
    
    def _extract_requested_count(self, query: str) -> int:
        """
        Extrait le nombre de recommandations demandé (logique de votre système)
        """
        query_lower = query.lower()
        
        # Patterns pour détecter le nombre
        patterns = [
            r'donne.{0,20}moi\s+(\d+)\s+(?:livres?|recommandations?)',
            r'(\d+)\s+(?:livres?|recommandations?)',
            r'(un|une|deux|trois|quatre|cinq|six|sept|huit|neuf|dix)\s+(?:livres?|recommandations?)',
        ]
        
        # Mapping français vers nombres
        french_numbers = {
            'un': 1, 'une': 1, 'deux': 2, 'trois': 3, 'quatre': 4, 'cinq': 5,
            'six': 6, 'sept': 7, 'huit': 8, 'neuf': 9, 'dix': 10
        }
        
        for pattern in patterns:
            match = re.search(pattern, query_lower)
            if match:
                number_str = match.group(1)
                
                # Si c'est un chiffre
                if number_str.isdigit():
                    return min(int(number_str), 10)  # Max 10 recommandations
                
                # Si c'est un nombre en français
                if number_str in french_numbers:
                    return french_numbers[number_str]
        
        # Par défaut, retourner 3 recommandations
        return 3
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Interface LangGraph - traite l'état et retourne la classification
        """
        query = state.get("query", "")
        
        if not query:
            logger.warning("Requête vide reçue")
            classification = QueryClassification(
                agent_type="literature",
                confidence=0.1,
                reasoning="Requête vide - défaut littérature",
                detected_keywords=[],
                expanded_query="",
                requested_count=3
            )
        else:
            classification = self.classify_query(query)
        
        # Mettre à jour l'état
        state.update({
            "classification": classification.dict(),
            "agent_type": classification.agent_type,
            "expanded_query": classification.expanded_query,
            "requested_count": classification.requested_count,
            "confidence": classification.confidence
        })
        
        logger.info(f"Classification: {query} → {classification.agent_type} (confiance: {classification.confidence})")
        
        return state