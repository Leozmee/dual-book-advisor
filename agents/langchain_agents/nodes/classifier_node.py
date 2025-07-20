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
            'attaque des titans', "l'attaque des titans", 'shingeki no kyojin',
            'death note', 'fullmetal', 'bleach', 'demon slayer', 'tokyo ghoul',
            'sword art online', 'sao', 'light novel', 'ln', 'slime datta ken',
            'tensei shitara slime', 'akira toriyama', 'oda', 'kishimoto',
            'reki kawahara', 'hajime isayama', 'tite kubo', 'masashi kishimoto',
            'shounen', 'shoujo', 'seinen', 'josei', 'manhua', 'manhwa', 'otaku',
            'comics', 'bd', 'bande dessinée', 'superman', 'batman', 'marvel', 'dc',
            'tintin', 'astérix', 'superhéros', 'mangaka', 'webtoon'
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
        
        # Auteurs littéraires classiques connus
        self.known_authors = [
            'victor hugo', 'gustave flaubert', 'stendhal', 'émile zola', 'marcel proust',
            'albert camus', 'jean-paul sartre', 'simone de beauvoir', 'andré gide',
            'françois mauriac', 'andré malraux', 'charles baudelaire', 'paul verlaine',
            'arthur rimbaud', 'voltaire', 'molière', 'racine', 'corneille',
            'shakespeare', 'dickens', 'tolstoy', 'dostoevsky', 'kafka',
            'hemingway', 'steinbeck', 'orwell', 'joyce', 'wilde'
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
            'stendhal': 'Stendhal Le Rouge et le Noir La Chartreuse de Parme French literature classic',
            'zola': 'Émile Zola Germinal L\'Assommoir naturalisme French literature',
            'flaubert': 'Gustave Flaubert Madame Bovary Salammbô French literature realism',
            
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
            'cobol': 'COBOL programming language legacy business mainframe',
            'fortran': 'Fortran programming language scientific computing numerical',
            'pascal': 'Pascal programming language structured programming education',
            'c++': 'C++ programming language object-oriented system programming',
            'rust': 'Rust programming language systems programming memory safety',
            'swift': 'Swift programming language iOS macOS Apple development',
            'kotlin': 'Kotlin programming language Android JVM development',
            'scala': 'Scala programming language functional programming JVM',
            'machine learning': 'machine learning AI artificial intelligence data science',
            'data science': 'data science analysis statistics Python R visualization',
            
            # Manga/Comics/Light Novels
            'manga': 'manga anime Japanese comic otaku shounen seinen',
            'naruto': 'Naruto ninja village hidden leaf Uzumaki Sasuke Sakura action',
            'one piece': 'One Piece pirate treasure Luffy Straw Hat Grand Line adventure',
            'sword art online': 'Sword Art Online SAO virtual reality MMORPG Kirito Asuna light novel',
            'sao': 'Sword Art Online SAO virtual reality MMORPG Kirito Asuna light novel',
            'slime datta ken': 'Tensei Shitara Slime Datta Ken That Time I Got Reincarnated as a Slime Rimuru isekai',
            'akira toriyama': 'Akira Toriyama Dragon Ball Dr Slump manga creator',
            'reki kawahara': 'Reki Kawahara Sword Art Online Accel World light novel author',
            'comics': 'comics superhero graphic novel DC Marvel',
            'bd': 'bande dessinée comics album français',
        }
    
    def _build_classification_chain(self):
        """Construit la chaîne de classification LangChain"""
        
        classification_prompt = ChatPromptTemplate.from_template("""
# Prompt de Routage Intelligent pour Agents Littéraires

## MISSION PRINCIPALE
Tu es un coordinateur intelligent qui route les demandes vers le bon agent spécialisé. Tu dois ANALYSER le contenu de la requête pour identifier précisément le domaine concerné AVANT de router.

## RÈGLES DE ROUTAGE CRITIQUES

### 1. IDENTIFICATION DES DOMAINES

#### 📚 AGENT LITTÉRAIRE (literature)
**Déclenche quand la requête contient :**
- Noms d'auteurs classiques/littéraires : Hugo, Flaubert, Zola, Proust, Camus, etc.
- Titres de romans/nouvelles classiques : Les Misérables, Madame Bovary, etc.
- Mots-clés : "roman", "livre", "littérature", "auteur", "écrivain", "poète"
- Demandes d'œuvres d'un auteur littéraire
- Questions sur la littérature française/mondiale

**Exemples à router vers LITTÉRAIRE :**
- "qui est l'auteur de Les Misérables"
- "recommande moi des oeuvres de Victor Hugo"
- "donne moi des oeuvres de Stendhal"
- "j'ai aimé L'Étranger de Camus"

#### 🎌 AGENT MANGA/COMICS (manga)
**Déclenche quand la requête contient :**
- Noms de manga/anime : One Piece, Naruto, Slime datta ken, Sword Art Online, etc.
- Termes manga : "manga", "anime", "light novel", "shounen", "seinen", etc.
- Noms d'auteurs manga : Oda, Kishimoto, etc.
- Références à la culture japonaise/comics
- Titres avec des caractéristiques manga (noms japonais, fantasy moderne, etc.)

**RÈGLE CRUCIALE POUR LES MANGAS :**
Si la requête mentionne un titre qui ressemble à un manga/anime/light novel (ex: "slime datta ken", "sword art online", etc.), TOUJOURS router vers manga, même si le titre n'est pas explicitement dans la liste.

**Exemples à router vers MANGA :**
- "qui est l'auteur de Sword Art Online"
- "j'ai aimé slime datta ken, recommande moi deux oeuvres"
- "j'ai aimé one piece recommande moi deux oeuvres"
- "j'ai aimé [tout titre qui semble être un manga/anime]"

#### 🔧 AGENT TECHNIQUE (tech)
**Déclenche quand la requête contient :**
- Langages de programmation : Python, Java, JavaScript, C++, etc.
- Technologies : React, Docker, AWS, etc.
- Mots-clés : "apprendre", "programmation", "développement", "code", "technique"
- Demandes d'apprentissage technologique

**Exemples à router vers TECHNIQUE :**
- "j'aimerais apprendre le python"
- "recommande moi des livres sur React"

### 2. ANALYSE PRÉALABLE OBLIGATOIRE

Avant de router, tu DOIS :
1. **Identifier les entités** : Extraire noms d'auteurs, titres, technologies
2. **Classifier le domaine** : Littérature classique vs Manga vs Technique
3. **Vérifier la cohérence** : S'assurer que le routage correspond au contenu

### 3. GESTION DES CAS AMBIGUS

#### Si AUTEUR INCONNU ou AMBIGU :
Analyser le contexte pour déterminer s'il s'agit de :
- 📚 Littérature classique/contemporaine
- 🎌 Manga/anime/light novel  
- 🔧 Documentation technique

### 4. RÈGLES STRICTES DE COHÉRENCE

#### ❌ ERREURS À ÉVITER ABSOLUMENT :
1. **Router "Slime datta ken" vers l'agent technique** 
2. **Router "Victor Hugo" vers l'agent technique**
3. **Donner des recommandations techniques quand on demande des œuvres littéraires**
4. **Mélanger les formats de réponse entre agents**

#### ✅ VALIDATION AVANT ROUTAGE :
- "Sword Art Online" = MANGA (pas technique)
- "Victor Hugo" = LITERATURE (pas technique)  
- "Python programming" = TECH
- "Stendhal" = LITERATURE
- "One Piece" = MANGA

## EXEMPLES DE ROUTAGE CORRECT

**USER:** "j'ai aimé slime datta ken, recommande moi deux oeuvres"
**ANALYSE:** "Slime datta ken" = manga/light novel japonais
**ROUTE:** manga ✅

**USER:** "qui est l'auteur de Les Misérables"  
**ANALYSE:** "Les Misérables" = roman classique français
**ROUTE:** literature ✅

**USER:** "j'aimerais apprendre le python"
**ANALYSE:** "python" = langage de programmation
**ROUTE:** tech ✅

**USER:** "donne moi des oeuvres de Stendhal"
**ANALYSE:** "Stendhal" = auteur littéraire français classique
**ROUTE:** literature ✅

## CONTRÔLE QUALITÉ FINAL

Avant chaque réponse, vérifie :
- ✅ Le routage correspond-il au domaine de la requête ?
- ✅ L'agent utilisé peut-il réellement répondre à cette demande ?
- ✅ La réponse est-elle cohérente avec la question posée ?

**REQUÊTE UTILISATEUR:** {query}

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
        
        # Détection des auteurs littéraires classiques (priorité haute)
        for author in self.known_authors:
            if author in query_lower:
                return {
                    "agent_type": "literature",
                    "confidence": 0.95,
                    "reasoning": f"Auteur littéraire classique détecté: {author}",
                    "keywords": [author]
                }
        
        # Détection manga/comics/light novels (priorité absolue pour les mots-clés explicites)
        manga_score = sum(1 for keyword in self.manga_keywords if keyword in query_lower)
        if manga_score > 0:
            return {
                "agent_type": "manga",
                "confidence": min(0.9 + manga_score * 0.1, 1.0),
                "reasoning": f"Mots-clés manga/comics/light novel détectés: {manga_score}",
                "keywords": [kw for kw in self.manga_keywords if kw in query_lower]
            }
        
        # Détection spéciale pour les questions d'auteur de manga/anime
        if self._is_manga_author_question(query_lower):
            return {
                "agent_type": "manga",
                "confidence": 0.95,
                "reasoning": "Question d'auteur de manga/anime détectée",
                "keywords": ["qui a écrit", "auteur", "manga", "anime"]
            }
        
        # Détection technique
        tech_score = sum(1 for keyword in self.tech_keywords if keyword in query_lower)
        lit_score = sum(1 for keyword in self.literature_keywords if keyword in query_lower)
        
        # Vérification spéciale pour éviter les faux positifs techniques
        if tech_score > 0 and not self._is_likely_literature_query(query_lower):
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
                "confidence": 0.95,
                "reasoning": "Question d'auteur détectée - littérature classique",
                "keywords": ["qui a écrit", "auteur", "author"]
            }
        
        # Détection des œuvres littéraires par pattern
        if self._is_works_request(query_lower):
            return {
                "agent_type": "literature",
                "confidence": 0.85,
                "reasoning": "Demande d'œuvres détectée - probablement littérature",
                "keywords": ["œuvres", "works", "donne moi"]
            }
        
        # Si aucun mot-clé technique mais des indices littéraires, privilégier la littérature
        if lit_score > 0 or self._has_literary_context(query_lower):
            return {
                "agent_type": "literature",
                "confidence": 0.7,
                "reasoning": f"Contexte littéraire détecté (lit_score: {lit_score})",
                "keywords": [kw for kw in self.literature_keywords if kw in query_lower]
            }
        
        # Par défaut : utiliser le LLM pour analyse plus fine
        return {
            "agent_type": "literature",
            "confidence": 0.2,  # Confiance très faible pour forcer l'utilisation du LLM
            "reasoning": "Classification incertaine - analyse LLM nécessaire",
            "keywords": []
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
    
    def _is_manga_author_question(self, query_lower: str) -> bool:
        """
        Détecte si la requête est une question d'auteur de manga/anime
        """
        # Liste de titres de manga/anime populaires
        popular_manga_titles = [
            'naruto', 'one piece', 'dragon ball', 'attack on titan', 'death note',
            'fullmetal alchemist', 'bleach', 'demon slayer', 'tokyo ghoul',
            'hunter x hunter', 'my hero academia', 'jujutsu kaisen', 'chainsaw man',
            'black clover', 'fairy tail', 'seven deadly sins', 'mob psycho',
            'one punch man', 'overlord', 'konosuba', 'rezero', 'shield hero',
            'that time i got reincarnated as a slime', 'slime datta ken',
            'tensei shitara slime datta ken', 'sword art online', 'sao',
            'log horizon', 'danmachi', 'goblin slayer', 'akame ga kill'
        ]
        
        author_patterns = [
            r'qui\s+(?:a\s+)?(?:écrit|créé)',
            r'auteur\s+de',
            r'créateur\s+de',
            r'mangaka\s+de',
            r'who\s+(?:wrote|created)',
            r'author\s+of',
            r'creator\s+of'
        ]
        
        # Vérifier si c'est une question d'auteur ET qu'un titre de manga est mentionné
        has_author_pattern = any(re.search(pattern, query_lower) for pattern in author_patterns)
        has_manga_title = any(title in query_lower for title in popular_manga_titles)
        
        return has_author_pattern and has_manga_title
    
    def _is_works_request(self, query_lower: str) -> bool:
        """
        Détecte si la requête demande des œuvres d'un auteur
        """
        works_patterns = [
            r'(?:donne|donnez).{0,20}(?:moi|nous).{0,20}(?:des|les).{0,20}(?:œuvres|oeuvres|works|livres)',
            r'(?:œuvres|oeuvres|works|livres).{0,20}(?:de|par|by)',
            r'(?:recommande|suggest).{0,20}(?:des|les).{0,20}(?:œuvres|oeuvres|works)',
            r'(?:liste|list).{0,20}(?:des|les).{0,20}(?:œuvres|oeuvres|works)'
        ]
        
        for pattern in works_patterns:
            if re.search(pattern, query_lower):
                return True
        return False
    
    def _is_likely_literature_query(self, query_lower: str) -> bool:
        """
        Vérifie si la requête a des indices littéraires forts
        MAIS exclut les cas où c'est clairement technique
        """
        # D'abord, vérifier si c'est une demande technique explicite
        tech_learning_patterns = [
            r'apprendre\s+(?:le\s+)?(?:python|javascript|java|c#|php|ruby|go|cobol|fortran|pascal|c\+\+|rust|swift|kotlin|scala)',
            r'(?:python|javascript|java|c#|php|ruby|go|cobol|fortran|pascal|c\+\+|rust|swift|kotlin|scala)\s+(?:livres?|books?)',
            r'programmation\s+(?:livres?|books?)',
            r'développement\s+(?:livres?|books?)',
            r'coding\s+(?:livres?|books?)',
            r'(?:machine\s+learning|data\s+science|ai)\s+(?:livres?|books?)',
            r'(?:react|angular|vue|node|express|django|flask)\s+(?:livres?|books?)',
            r'(?:docker|kubernetes|aws|azure|gcp|cloud)\s+(?:livres?|books?)'
        ]
        
        # Si c'est une demande technique avec "livres", ce n'est pas littéraire
        for pattern in tech_learning_patterns:
            if re.search(pattern, query_lower):
                return False
        
        literary_indicators = [
            'madame bovary', 'les misérables', 'l\'étranger', 'la peste',
            'guerre et paix', 'anna karénine', 'crime et châtiment',
            'roman', 'romans', 'œuvre', 'œuvres',
            'auteur', 'écrivain', 'poète', 'littérature', 'classique'
        ]
        
        return any(indicator in query_lower for indicator in literary_indicators)
    
    def _has_literary_context(self, query_lower: str) -> bool:
        """
        Détecte un contexte littéraire général dans la requête
        """
        literary_context = [
            'j\'ai aimé', 'j\'ai lu', 'j\'ai adoré', 'similaire à',
            'comme', 'dans le style de', 'recommande', 'suggestion',
            'conseil de lecture', 'que lire', 'quoi lire'
        ]
        
        return any(context in query_lower for context in literary_context)
    
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
            "classification": classification.model_dump(),
            "agent_type": classification.agent_type,
            "expanded_query": classification.expanded_query,
            "requested_count": classification.requested_count,
            "confidence": classification.confidence
        })
        
        logger.info(f"Classification: {query} → {classification.agent_type} (confiance: {classification.confidence})")
        
        return state