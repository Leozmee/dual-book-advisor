#!/usr/bin/env python3
"""
Générateur de documentation PDF pour le système LangChain
Documentation complète du système Dual Book Advisor
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from datetime import datetime
import os

class LangChainDocumentationGenerator:
    def __init__(self):
        self.doc = None
        self.story = []
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configuration des styles personnalisés"""
        # Style pour le titre principal
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.navy
        ))
        
        # Style pour les sous-titres
        self.styles.add(ParagraphStyle(
            name='CustomHeading1',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=20,
            textColor=colors.darkblue,
            borderWidth=1,
            borderColor=colors.darkblue,
            borderPadding=5
        ))
        
        # Style pour les sous-sous-titres
        self.styles.add(ParagraphStyle(
            name='CustomHeading2',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=15,
            textColor=colors.blue
        ))
        
        # Style pour le code
        self.styles.add(ParagraphStyle(
            name='CustomCode',
            parent=self.styles['Normal'],
            fontName='Courier',
            fontSize=9,
            leftIndent=20,
            backgroundColor=colors.lightgrey,
            borderWidth=1,
            borderColor=colors.grey,
            borderPadding=5
        ))
        
        # Style pour les exemples
        self.styles.add(ParagraphStyle(
            name='Example',
            parent=self.styles['Normal'],
            leftIndent=20,
            rightIndent=20,
            backgroundColor=colors.lightyellow,
            borderWidth=1,
            borderColor=colors.orange,
            borderPadding=8
        ))

    def generate_pdf(self, filename="Documentation_LangChain_System.pdf"):
        """Génère la documentation PDF complète"""
        self.doc = SimpleDocTemplate(filename, pagesize=A4)
        self.story = []
        
        # Page de titre
        self._add_title_page()
        
        # Table des matières
        self._add_table_of_contents()
        
        # Chapitres principaux
        self._add_langchain_fundamentals()
        self._add_system_architecture()
        self._add_rag_implementation()
        self._add_workflow_analysis()
        self._add_technical_details()
        self._add_migration_guide()
        self._add_appendices()
        
        # Construction du PDF
        self.doc.build(self.story)
        return filename

    def _add_title_page(self):
        """Page de titre"""
        self.story.append(Spacer(1, 2*inch))
        
        title = Paragraph("Documentation du Système LangChain", self.styles['CustomTitle'])
        self.story.append(title)
        self.story.append(Spacer(1, 0.5*inch))
        
        subtitle = Paragraph("Dual Book Advisor - Agent Intelligent de Recommandation", 
                            self.styles['Heading1'])
        self.story.append(subtitle)
        self.story.append(Spacer(1, 1*inch))
        
        # Informations du document
        info_text = f"""
        <b>Version:</b> 1.0<br/>
        <b>Date:</b> {datetime.now().strftime('%d/%m/%Y')}<br/>
        <b>Architecture:</b> LangChain + LangGraph + RAG<br/>
        <b>Modèle:</b> Llama 3.2 3B (Ollama)<br/>
        <b>Framework:</b> Django + ChromaDB
        """
        info = Paragraph(info_text, self.styles['Normal'])
        self.story.append(info)
        
        self.story.append(PageBreak())

    def _add_table_of_contents(self):
        """Table des matières"""
        self.story.append(Paragraph("Table des Matières", self.styles['CustomHeading1']))
        self.story.append(Spacer(1, 20))
        
        toc_content = """
        1. Fondamentaux de LangChain ......................................................... 3
           1.1 Concepts de base
           1.2 Nodes et Chains
           1.3 LangGraph et orchestration
           
        2. Architecture du Système ........................................................... 8
           2.1 Vue d'ensemble
           2.2 Structure modulaire
           2.3 Composants principaux
           
        3. Implémentation RAG ................................................................ 15
           3.1 Système multi-domaines
           3.2 ChromaDB et embeddings
           3.3 Outils de recherche
           
        4. Analyse des Workflows ............................................................ 22
           4.1 Classification intelligente
           4.2 Routage adaptatif
           4.3 Formatage des réponses
           
        5. Détails Techniques ............................................................... 28
           5.1 Configuration
           5.2 Performance
           5.3 Monitoring
           
        6. Guide de Migration ............................................................... 33
           6.1 Stratégie progressive
           6.2 Compatibilité
           6.3 Tests et validation
           
        7. Annexes .......................................................................... 38
           7.1 Code examples
           7.2 Configuration complète
           7.3 Troubleshooting
        """
        
        toc = Paragraph(toc_content, self.styles['CustomCode'])
        self.story.append(toc)
        self.story.append(PageBreak())

    def _add_langchain_fundamentals(self):
        """Chapitre 1: Fondamentaux de LangChain"""
        self.story.append(Paragraph("1. Fondamentaux de LangChain", self.styles['CustomHeading1']))
        
        # 1.1 Concepts de base
        self.story.append(Paragraph("1.1 Concepts de Base", self.styles['CustomHeading2']))
        
        intro_text = """
        LangChain est un framework révolutionnaire pour le développement d'applications basées sur des 
        modèles de langage (LLM). Il fournit une abstraction puissante pour orchestrer des workflows 
        complexes impliquant des LLM, des bases de données vectorielles, et des outils externes.
        """
        self.story.append(Paragraph(intro_text, self.styles['Normal']))
        self.story.append(Spacer(1, 12))
        
        # Concepts clés
        concepts_data = [
            ['Concept', 'Description', 'Usage dans notre système'],
            ['LLM', 'Large Language Model - Le cœur du système', 'Llama 3.2 3B via Ollama'],
            ['Chain', 'Séquence d\'opérations liées', 'Classification → Routing → Formatting'],
            ['Tool', 'Fonctions externes appelables', 'RAG Search Tools (Tech, Literature, Manga)'],
            ['Prompt', 'Template de requête vers le LLM', 'Prompts spécialisés par domaine'],
            ['Memory', 'Gestion de l\'historique', 'State persistant via TypedDict'],
            ['Agent', 'Entité autonome de décision', 'TechAgent, LiteratureAgent, MangaAgent']
        ]
        
        concepts_table = Table(concepts_data, colWidths=[1.5*inch, 2.5*inch, 2*inch])
        concepts_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.navy),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        self.story.append(concepts_table)
        self.story.append(Spacer(1, 20))
        
        # 1.2 Nodes et Chains
        self.story.append(Paragraph("1.2 Nodes et Chains", self.styles['CustomHeading2']))
        
        nodes_text = """
        <b>Nodes (Nœuds):</b><br/>
        Les nodes sont les unités de traitement atomiques dans LangChain. Chaque node effectue une 
        tâche spécifique et peut être composé avec d'autres nodes pour former des workflows complexes.
        
        <br/><br/><b>Types de Nodes dans notre système:</b><br/>
        • <b>ClassifierNode:</b> Analyse et catégorise les requêtes utilisateur<br/>
        • <b>RouterNode:</b> Dirige vers l'agent spécialisé approprié<br/>
        • <b>AgentNodes:</b> Agents spécialisés (Tech, Literature, Manga)<br/>
        • <b>FormatterNode:</b> Formate la réponse finale pour l'utilisateur<br/>
        
        <br/><b>Chains (Chaînes):</b><br/>
        Les chains connectent plusieurs nodes pour créer un workflow. Notre système utilise 
        LangGraph pour créer des chaînes sophistiquées avec branchement conditionnel.
        """
        
        self.story.append(Paragraph(nodes_text, self.styles['Normal']))
        self.story.append(Spacer(1, 15))
        
        # Exemple de code
        code_example = """
        # Exemple de définition d'un Node
        class ClassifierNode:
            def __init__(self, llm):
                self.llm = llm
                self.parser = PydanticOutputParser(pydantic_object=QueryClassification)
        
            def run(self, state: BookAdvisorState) -> BookAdvisorState:
                # Classification de la requête
                classification = self._classify_query(state["user_query"])
                state["classification"] = classification
                return state
        """
        
        self.story.append(Paragraph("Exemple d'implémentation:", self.styles['Normal']))
        self.story.append(Paragraph(code_example, self.styles['CustomCode']))
        self.story.append(Spacer(1, 15))
        
        # 1.3 LangGraph et orchestration
        self.story.append(Paragraph("1.3 LangGraph et Orchestration", self.styles['CustomHeading2']))
        
        langgraph_text = """
        <b>LangGraph</b> est une extension de LangChain qui permet de créer des workflows sous forme 
        de graphes dirigés. Il offre plusieurs avantages par rapport aux chains linéaires:
        
        <br/><br/><b>Avantages de LangGraph:</b><br/>
        • <b>Branchement conditionnel:</b> Routage dynamique basé sur le contexte<br/>
        • <b>Parallélisation:</b> Exécution simultanée de branches indépendantes<br/>
        • <b>État persistant:</b> Gestion sophistiquée de l'état entre les nodes<br/>
        • <b>Cycle de vie:</b> Contrôle fin du workflow avec points d'arrêt<br/>
        • <b>Debugging:</b> Introspection et monitoring avancés<br/>
        
        <br/><b>Notre Graph Workflow:</b><br/>
        1. <b>START</b> → Initialisation de l'état<br/>
        2. <b>Classifier</b> → Analyse de la requête (règles + LLM)<br/>
        3. <b>Router</b> → Sélection de l'agent approprié<br/>
        4. <b>Agent</b> → Traitement spécialisé (Tech/Literature/Manga)<br/>
        5. <b>Formatter</b> → Mise en forme de la réponse<br/>
        6. <b>END</b> → Retour de la réponse finale
        """
        
        self.story.append(Paragraph(langgraph_text, self.styles['Normal']))
        self.story.append(PageBreak())

    def _add_system_architecture(self):
        """Chapitre 2: Architecture du Système"""
        self.story.append(Paragraph("2. Architecture du Système", self.styles['CustomHeading1']))
        
        # 2.1 Vue d'ensemble
        self.story.append(Paragraph("2.1 Vue d'Ensemble", self.styles['CustomHeading2']))
        
        overview_text = """
        Le système Dual Book Advisor implémente une architecture sophistiquée combinant:
        
        <br/><br/><b>Stack Technologique:</b><br/>
        • <b>Framework:</b> Django (backend web)<br/>
        • <b>Orchestration:</b> LangChain + LangGraph<br/>
        • <b>LLM:</b> Llama 3.2 3B (via Ollama)<br/>
        • <b>Vector DB:</b> ChromaDB (embeddings et similarité)<br/>
        • <b>RAG:</b> Système multi-domaines (Tech, Literature, Manga)<br/>
        
        <br/><b>Principes de Design:</b><br/>
        • <b>Modularité:</b> Séparation claire des responsabilités<br/>
        • <b>Extensibilité:</b> Architecture pluggable pour nouveaux domaines<br/>
        • <b>Robustesse:</b> Gestion d'erreurs et fallbacks<br/>
        • <b>Performance:</b> Optimisations pour modèles locaux<br/>
        • <b>Migration:</b> Compatibilité avec l'ancien système
        """
        
        self.story.append(Paragraph(overview_text, self.styles['Normal']))
        self.story.append(Spacer(1, 15))
        
        # 2.2 Structure modulaire
        self.story.append(Paragraph("2.2 Structure Modulaire", self.styles['CustomHeading2']))
        
        structure_text = """
        <b>Hiérarchie des Modules:</b>
        """
        self.story.append(Paragraph(structure_text, self.styles['Normal']))
        
        structure_code = """
        agents/langchain_agents/
        ├── __init__.py                    # Module principal
        ├── django_integration.py          # Bridge Django ↔ LangChain
        ├── graph_manager.py              # Orchestrateur LangGraph
        ├── nodes/                        # Nœuds de traitement
        │   ├── agent_nodes.py           #   Agents spécialisés
        │   └── classifier_node.py       #   Classification intelligente
        ├── tools/                        # Outils externes
        │   └── rag_tools.py             #   Intégration RAG
        └── chains/                       # Chaînes (réservé)
        
        rags/                             # Systèmes RAG spécialisés
        ├── tech_rag/                    # RAG technique
        ├── literature_rag/              # RAG littérature
        └── manga_rag/                   # RAG manga/BD
        
        apps/chat/                        # Interface Django
        ├── views_langchain.py           # Endpoints API
        └── urls_langchain.py            # Routage URL
        """
        
        self.story.append(Paragraph(structure_code, self.styles['CustomCode']))
        self.story.append(Spacer(1, 15))
        
        # 2.3 Composants principaux
        self.story.append(Paragraph("2.3 Composants Principaux", self.styles['CustomHeading2']))
        
        components_data = [
            ['Composant', 'Fichier', 'Responsabilité', 'Technologies'],
            ['Graph Manager', 'graph_manager.py', 'Orchestration centrale', 'LangGraph, TypedDict'],
            ['Classifier Node', 'classifier_node.py', 'Analyse des requêtes', 'Pydantic, Regex, LLM'],
            ['Agent Nodes', 'agent_nodes.py', 'Traitement spécialisé', 'LangChain Tools, RAG'],
            ['RAG Tools', 'rag_tools.py', 'Recherche vectorielle', 'ChromaDB, Embeddings'],
            ['Django Bridge', 'django_integration.py', 'Intégration framework', 'Singleton, Configuration'],
            ['Views', 'views_langchain.py', 'API endpoints', 'Django REST, JSON']
        ]
        
        components_table = Table(components_data, colWidths=[1.3*inch, 1.3*inch, 1.7*inch, 1.7*inch])
        components_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        self.story.append(components_table)
        self.story.append(PageBreak())

    def _add_rag_implementation(self):
        """Chapitre 3: Implémentation RAG"""
        self.story.append(Paragraph("3. Implémentation RAG", self.styles['CustomHeading1']))
        
        # 3.1 Système multi-domaines
        self.story.append(Paragraph("3.1 Système Multi-Domaines", self.styles['CustomHeading2']))
        
        rag_intro = """
        Notre système RAG (Retrieval-Augmented Generation) implémente une architecture multi-domaines 
        sophistiquée, permettant des recommandations spécialisées pour trois catégories distinctes 
        de contenu littéraire.
        
        <br/><br/><b>Architecture RAG:</b><br/>
        • <b>Séparation des domaines:</b> Collections ChromaDB dédiées<br/>
        • <b>Embeddings spécialisés:</b> Modèles optimisés par type de contenu<br/>
        • <b>Métadonnées riches:</b> Filtrage et ranking avancés<br/>
        • <b>Recherche hybride:</b> Similarité sémantique + filtres<br/>
        • <b>Fallback intelligent:</b> Recherche cross-domaine si nécessaire
        """
        
        self.story.append(Paragraph(rag_intro, self.styles['Normal']))
        self.story.append(Spacer(1, 15))
        
        # Tableau des domaines RAG
        rag_domains_data = [
            ['Domaine', 'Collection ChromaDB', 'Source de Données', 'Métadonnées Clés'],
            ['Tech Books', 'tech_books', 'TechBook (Django)', 'Langages, Difficulté, Notes'],
            ['Literature', 'literature_books', 'LiteratureBook (Django)', 'Genres, Thèmes, Époque'],
            ['Manga/BD', 'manga_comics_collection', 'CSV Files', 'Styles, Origine, Cible']
        ]
        
        rag_table = Table(rag_domains_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 1.5*inch])
        rag_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.green),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        self.story.append(rag_table)
        self.story.append(Spacer(1, 20))
        
        # 3.2 ChromaDB et embeddings
        self.story.append(Paragraph("3.2 ChromaDB et Embeddings", self.styles['CustomHeading2']))
        
        chromadb_text = """
        <b>ChromaDB Configuration:</b><br/>
        ChromaDB sert de base de données vectorielle pour stocker et rechercher les embeddings. 
        Chaque domaine utilise une collection dédiée pour optimiser les performances et la pertinence.
        
        <br/><br/><b>Processus d'Embedding:</b><br/>
        1. <b>Extraction:</b> Texte descriptif depuis les modèles Django<br/>
        2. <b>Vectorisation:</b> Transformation en embeddings via modèle language<br/>
        3. <b>Indexation:</b> Stockage dans ChromaDB avec métadonnées<br/>
        4. <b>Optimisation:</b> Index pour recherche rapide par similarité<br/>
        
        <br/><b>Métadonnées Enrichies:</b><br/>
        • <b>Tech:</b> programming_languages, difficulty_level, rating, price_range<br/>
        • <b>Literature:</b> genres, themes, publication_year, target_audience<br/>
        • <b>Manga:</b> style, origin_country, demographic, completed_status
        """
        
        self.story.append(Paragraph(chromadb_text, self.styles['Normal']))
        self.story.append(Spacer(1, 15))
        
        # Exemple de code ChromaDB
        chromadb_code = """
        # Exemple d'indexation ChromaDB
        class TechRAGManager:
            def __init__(self):
                self.client = chromadb.PersistentClient(path="./chroma_db")
                self.collection = self.client.get_or_create_collection(
                    name="tech_books",
                    embedding_function=embedding_functions.DefaultEmbeddingFunction()
                )
        
            def add_books_batch(self, books):
                documents = []
                metadatas = []
                ids = []
                
                for book in books:
                    # Construction du document texte
                    doc_text = f"{book.title} {book.description} {book.summary}"
                    documents.append(doc_text)
                    
                    # Métadonnées enrichies
                    metadata = {
                        "title": book.title,
                        "programming_languages": book.programming_languages,
                        "difficulty": book.difficulty_level,
                        "rating": float(book.rating) if book.rating else 0.0
                    }
                    metadatas.append(metadata)
                    ids.append(f"tech_book_{book.id}")
                
                # Indexation batch
                self.collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
        """
        
        self.story.append(Paragraph("Exemple d'implémentation ChromaDB:", self.styles['Normal']))
        self.story.append(Paragraph(chromadb_code, self.styles['CustomCode']))
        self.story.append(Spacer(1, 15))
        
        # 3.3 Outils de recherche
        self.story.append(Paragraph("3.3 Outils de Recherche", self.styles['CustomHeading2']))
        
        search_tools_text = """
        Les outils de recherche RAG implémentent l'interface LangChain BaseTool, permettant leur 
        intégration seamless dans les workflows d'agents.
        
        <br/><br/><b>Tools Disponibles:</b><br/>
        • <b>TechBookSearchTool:</b> Recherche de livres techniques<br/>
        • <b>LiteratureBookSearchTool:</b> Recherche littéraire (exclut manga)<br/>
        • <b>MangaContentSearchTool:</b> Recherche manga/BD unifiée<br/>
        • <b>CombinedSearchTool:</b> Recherche multi-domaines<br/>
        
        <br/><b>Caractéristiques Avancées:</b><br/>
        • <b>Validation Pydantic:</b> Schémas stricts pour les entrées<br/>
        • <b>Filtrage intelligent:</b> Exclusions et inclusions dynamiques<br/>
        • <b>Scoring adaptatif:</b> Pondération par pertinence et métadonnées<br/>
        • <b>Fallback gracieux:</b> Gestion des erreurs et alternatives<br/>
        • <b>Limitation intelligente:</b> Contrôle du nombre de résultats
        """
        
        self.story.append(Paragraph(search_tools_text, self.styles['Normal']))
        self.story.append(PageBreak())

    def _add_workflow_analysis(self):
        """Chapitre 4: Analyse des Workflows"""
        self.story.append(Paragraph("4. Analyse des Workflows", self.styles['CustomHeading1']))
        
        # 4.1 Classification intelligente
        self.story.append(Paragraph("4.1 Classification Intelligente", self.styles['CustomHeading2']))
        
        classification_text = """
        Le système de classification hybride combine des règles déterministes avec l'intelligence 
        artificielle pour une catégorisation précise et robuste des requêtes utilisateur.
        
        <br/><br/><b>Architecture de Classification:</b><br/>
        1. <b>Analyse lexicale:</b> Détection de mots-clés avec seuils de confiance<br/>
        2. <b>Expansion sémantique:</b> Enrichissement du vocabulaire détectable<br/>
        3. <b>Classification LLM:</b> Analyse contextuelle pour cas ambigus<br/>
        4. <b>Extraction de quantité:</b> Détection automatique du nombre souhaité<br/>
        5. <b>Validation Pydantic:</b> Structure garantie de la sortie<br/>
        
        <br/><b>Règles de Priorité:</b><br/>
        • <b>Confiance >= 0.8:</b> Classification directe sans LLM<br/>
        • <b>Confiance < 0.8:</b> Analyse LLM + validation<br/>
        • <b>Ambiguïté:</b> Classification 'general' avec recherche multi-domaines<br/>
        • <b>Erreur:</b> Fallback vers classification générale
        """
        
        self.story.append(Paragraph(classification_text, self.styles['Normal']))
        self.story.append(Spacer(1, 15))
        
        # Exemple de classification
        classification_example = """
        # Exemple de classification hybride
        class ClassifierNode:
            TECH_KEYWORDS = {
                'programming': 0.9, 'python': 0.95, 'javascript': 0.95,
                'algorithm': 0.8, 'data science': 0.9, 'machine learning': 0.95
            }
            
            LITERATURE_KEYWORDS = {
                'roman': 0.9, 'poetry': 0.85, 'novel': 0.9,
                'classic': 0.8, 'fiction': 0.7, 'literature': 0.9
            }
            
            MANGA_KEYWORDS = {
                'manga': 0.95, 'anime': 0.9, 'bande dessinée': 0.95,
                'comic': 0.8, 'bd': 0.95, 'shonen': 0.95
            }
            
            def _classify_by_rules(self, query: str) -> Tuple[str, float]:
                query_lower = query.lower()
                max_confidence = 0.0
                best_category = "general"
                
                # Test de chaque catégorie
                for category, keywords in [
                    ("tech", self.TECH_KEYWORDS),
                    ("literature", self.LITERATURE_KEYWORDS),
                    ("manga", self.MANGA_KEYWORDS)
                ]:
                    confidence = max(
                        (score for keyword, score in keywords.items() 
                         if keyword in query_lower), 
                        default=0.0
                    )
                    
                    if confidence > max_confidence:
                        max_confidence = confidence
                        best_category = category
                
                return best_category, max_confidence
        """
        
        self.story.append(Paragraph("Implémentation de la classification:", self.styles['Normal']))
        self.story.append(Paragraph(classification_example, self.styles['CustomCode']))
        self.story.append(Spacer(1, 15))
        
        # 4.2 Routage adaptatif
        self.story.append(Paragraph("4.2 Routage Adaptatif", self.styles['CustomHeading2']))
        
        routing_text = """
        Le RouterNode implémente un système de routage intelligent qui dirige chaque requête 
        vers l'agent spécialisé optimal basé sur la classification et le contexte.
        
        <br/><br/><b>Logique de Routage:</b><br/>
        • <b>Tech:</b> TechAgentNode pour programmation, algorithmique, outils<br/>
        • <b>Literature:</b> LiteratureAgentNode pour romans, poésie, classiques<br/>
        • <b>Manga:</b> MangaAgentNode pour manga, BD, comics, anime<br/>
        • <b>General:</b> Recherche combinée avec fusion des résultats<br/>
        
        <br/><b>Mécanismes Avancés:</b><br/>
        • <b>Routage conditionnel:</b> Décision basée sur confiance et contexte<br/>
        • <b>Fallback intelligent:</b> Redirection en cas d'échec d'agent<br/>
        • <b>Load balancing:</b> Distribution équitable (future feature)<br/>
        • <b>A/B testing:</b> Support pour expérimentations (planifié)
        """
        
        self.story.append(Paragraph(routing_text, self.styles['Normal']))
        self.story.append(Spacer(1, 15))
        
        # 4.3 Formatage des réponses
        self.story.append(Paragraph("4.3 Formatage des Réponses", self.styles['CustomHeading2']))
        
        formatting_text = """
        Le ResponseFormatterNode assure la cohérence et la qualité de toutes les réponses 
        du système, quel que soit l'agent qui les a générées.
        
        <br/><br/><b>Responsabilités du Formatter:</b><br/>
        • <b>Structuration:</b> Format JSON cohérent pour l'API<br/>
        • <b>Validation:</b> Vérification de la complétude des réponses<br/>
        • <b>Enrichissement:</b> Ajout de métadonnées (temps, agent, confiance)<br/>
        • <b>Personnalisation:</b> Adaptation au style utilisateur<br/>
        • <b>Fallback:</b> Messages d'erreur élégants<br/>
        
        <br/><b>Structure de Réponse Standard:</b><br/>
        • <b>recommendations:</b> Liste des livres recommandés<br/>
        • <b>explanation:</b> Justification des choix<br/>
        • <b>metadata:</b> Informations techniques (agent, temps, etc.)<br/>
        • <b>suggestions:</b> Recommandations pour affiner la recherche<br/>
        • <b>total_found:</b> Nombre total de résultats disponibles
        """
        
        self.story.append(Paragraph(formatting_text, self.styles['Normal']))
        self.story.append(PageBreak())

    def _add_technical_details(self):
        """Chapitre 5: Détails Techniques"""
        self.story.append(Paragraph("5. Détails Techniques", self.styles['CustomHeading1']))
        
        # 5.1 Configuration
        self.story.append(Paragraph("5.1 Configuration", self.styles['CustomHeading2']))
        
        config_text = """
        La configuration du système LangChain est centralisée dans les settings Django, 
        permettant une gestion flexible des environnements et des paramètres.
        """
        
        self.story.append(Paragraph(config_text, self.styles['Normal']))
        
        config_code = """
        # Configuration dans settings/development.py
        LANGCHAIN_CONFIG = {
            # Configuration LLM
            'provider': 'ollama',              # openai, anthropic, ollama
            'model': 'llama3.2:3b',           # Modèle spécifique
            'ollama_base_url': 'http://localhost:11434',
            
            # Paramètres de génération
            'temperature': 0.7,               # Créativité vs précision
            'max_tokens': 512,                # Limite de tokens de sortie
            'timeout': 30,                    # Timeout en secondes
            
            # Optimisations spécifiques
            'llama_optimized': True,          # Optimisations Llama
            'collect_stats': True,            # Collecte de métriques
            'debug_mode': False,              # Mode debug détaillé
            
            # Configuration RAG
            'rag_enabled': True,              # Activation des RAG tools
            'max_rag_results': 5,             # Limite résultats par RAG
            'similarity_threshold': 0.7,      # Seuil de similarité
            
            # Gestion d'erreurs
            'fallback_enabled': True,         # Fallback vers ancien système
            'retry_attempts': 3,              # Tentatives en cas d'échec
            'cache_enabled': True,            # Cache des réponses (futur)
        }
        
        # Variables d'environnement pour secrets
        OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
        ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
        """
        
        self.story.append(Paragraph(config_code, self.styles['CustomCode']))
        self.story.append(Spacer(1, 15))
        
        # 5.2 Performance
        self.story.append(Paragraph("5.2 Performance", self.styles['CustomHeading2']))
        
        performance_text = """
        <b>Optimisations Implémentées:</b><br/>
        • <b>Modèle local:</b> Llama 3.2 3B pour latence réduite<br/>
        • <b>Batch processing:</b> Indexation RAG par lots de 100<br/>
        • <b>Lazy loading:</b> Initialisation des composants à la demande<br/>
        • <b>Connection pooling:</b> Réutilisation des connexions ChromaDB<br/>
        • <b>Prompt optimization:</b> Templates optimisés pour tokens réduits<br/>
        
        <br/><b>Métriques de Performance Typiques:</b><br/>
        • <b>Classification:</b> ~200ms (règles) / ~800ms (LLM)<br/>
        • <b>Recherche RAG:</b> ~150ms par domaine<br/>
        • <b>Génération LLM:</b> ~2-5s selon la complexité<br/>
        • <b>Formatage:</b> ~50ms<br/>
        • <b>Total workflow:</b> ~3-8s bout-en-bout<br/>
        
        <br/><b>Optimisations Futures:</b><br/>
        • <b>Async/await:</b> Traitement asynchrone pour parallélisation<br/>
        • <b>Response caching:</b> Cache intelligent des réponses fréquentes<br/>
        • <b>Model quantization:</b> Réduction de taille pour vitesse accrue<br/>
        • <b>Edge deployment:</b> Déploiement distribué pour latence globale
        """
        
        self.story.append(Paragraph(performance_text, self.styles['Normal']))
        self.story.append(Spacer(1, 15))
        
        # 5.3 Monitoring
        self.story.append(Paragraph("5.3 Monitoring", self.styles['CustomHeading2']))
        
        monitoring_text = """
        <b>Système de Monitoring Intégré:</b><br/>
        • <b>Health checks:</b> Endpoints de santé pour chaque composant<br/>
        • <b>Performance tracking:</b> Mesure des temps de réponse<br/>
        • <b>Error logging:</b> Journalisation détaillée des erreurs<br/>
        • <b>Usage analytics:</b> Statistiques d'utilisation par agent<br/>
        • <b>Quality metrics:</b> Évaluation de la pertinence des réponses<br/>
        
        <br/><b>Endpoints de Monitoring:</b><br/>
        • <b>/api/langchain/status/:</b> Statut global du système<br/>
        • <b>/api/langchain/health/:</b> Health check détaillé<br/>
        • <b>/api/langchain/metrics/:</b> Métriques de performance<br/>
        • <b>/api/langchain/debug/:</b> Informations de debug (dev only)
        """
        
        self.story.append(Paragraph(monitoring_text, self.styles['Normal']))
        self.story.append(PageBreak())

    def _add_migration_guide(self):
        """Chapitre 6: Guide de Migration"""
        self.story.append(Paragraph("6. Guide de Migration", self.styles['CustomHeading1']))
        
        # 6.1 Stratégie progressive
        self.story.append(Paragraph("6.1 Stratégie Progressive", self.styles['CustomHeading2']))
        
        migration_text = """
        La migration vers le système LangChain suit une approche progressive pour minimiser 
        les risques et permettre un retour en arrière si nécessaire.
        
        <br/><br/><b>Phases de Migration:</b><br/>
        1. <b>Phase 1:</b> Déploiement parallèle avec tests A/B<br/>
        2. <b>Phase 2:</b> Migration graduelle par endpoint<br/>
        3. <b>Phase 3:</b> Décommissioning de l'ancien système<br/>
        4. <b>Phase 4:</b> Optimisations post-migration<br/>
        
        <br/><b>Stratégie de Fallback:</b><br/>
        • <b>Hybrid Views:</b> Test LangChain puis fallback automatique<br/>
        • <b>Circuit breaker:</b> Désactivation automatique si erreurs<br/>
        • <b>Manual override:</b> Contrôle admin pour forcer ancien système<br/>
        • <b>Monitoring continu:</b> Alertes en cas de dégradation
        """
        
        self.story.append(Paragraph(migration_text, self.styles['Normal']))
        self.story.append(Spacer(1, 15))
        
        # Exemple de vue hybride
        hybrid_view_code = """
        # Exemple de Vue Hybride avec Fallback
        class HybridTechAgentChatView(APIView):
            def post(self, request):
                try:
                    # Tentative avec LangChain
                    langchain_bridge = DjangoLangChainBridge.get_instance()
                    if langchain_bridge.is_available():
                        response = langchain_bridge.process_tech_query(
                            request.data.get('query', '')
                        )
                        
                        # Validation de la réponse
                        if self._is_valid_response(response):
                            return Response({
                                'source': 'langchain',
                                'response': response
                            })
                
                except Exception as e:
                    logger.warning(f"LangChain failed, fallback: {e}")
                
                # Fallback vers ancien système
                old_manager = SimpleAgentManager()
                response = old_manager.get_tech_recommendations(
                    request.data.get('query', '')
                )
                
                return Response({
                    'source': 'fallback',
                    'response': response
                })
        """
        
        self.story.append(Paragraph("Implémentation Vue Hybride:", self.styles['Normal']))
        self.story.append(Paragraph(hybrid_view_code, self.styles['CustomCode']))
        self.story.append(Spacer(1, 15))
        
        # 6.2 Compatibilité
        self.story.append(Paragraph("6.2 Compatibilité", self.styles['CustomHeading2']))
        
        compatibility_text = """
        <b>Interfaces de Compatibilité:</b><br/>
        • <b>LangChainAgentManager:</b> API compatible avec SimpleAgentManager<br/>
        • <b>Response format:</b> Structure JSON identique à l'ancien système<br/>
        • <b>Error handling:</b> Codes d'erreur et messages cohérents<br/>
        • <b>Logging format:</b> Même format pour outils existants<br/>
        
        <br/><b>Gestion des Différences:</b><br/>
        • <b>Temps de réponse:</b> Adaptation des timeouts frontend<br/>
        • <b>Nouvelles features:</b> Gestion gracieuse des champs additionnels<br/>
        • <b>Métriques enrichies:</b> Backward compatibility pour analytics<br/>
        • <b>Configuration:</b> Variables d'environnement non-breaking
        """
        
        self.story.append(Paragraph(compatibility_text, self.styles['Normal']))
        self.story.append(Spacer(1, 15))
        
        # 6.3 Tests et validation
        self.story.append(Paragraph("6.3 Tests et Validation", self.styles['CustomHeading2']))
        
        testing_text = """
        <b>Suite de Tests Complète:</b><br/>
        • <b>Unit tests:</b> Tests unitaires pour chaque composant<br/>
        • <b>Integration tests:</b> Tests d'intégration RAG ↔ LangChain<br/>
        • <b>End-to-end tests:</b> Workflows complets utilisateur<br/>
        • <b>Performance tests:</b> Benchmarks et tests de charge<br/>
        • <b>Regression tests:</b> Non-régression vs ancien système<br/>
        
        <br/><b>Validation de Qualité:</b><br/>
        • <b>Response quality:</b> Évaluation humaine des recommandations<br/>
        • <b>Relevance scoring:</b> Métriques automatiques de pertinence<br/>
        • <b>User feedback:</b> Intégration des retours utilisateurs<br/>
        • <b>A/B testing:</b> Comparaison statistique des performances<br/>
        
        <br/><b>Métriques de Succès:</b><br/>
        • <b>Précision:</b> >90% de recommandations pertinentes<br/>
        • <b>Rapidité:</b> <8s pour 95% des requêtes<br/>
        • <b>Disponibilité:</b> >99.5% uptime<br/>
        • <b>Satisfaction:</b> Feedback utilisateur positif >85%
        """
        
        self.story.append(Paragraph(testing_text, self.styles['Normal']))
        self.story.append(PageBreak())

    def _add_appendices(self):
        """Chapitre 7: Annexes"""
        self.story.append(Paragraph("7. Annexes", self.styles['CustomHeading1']))
        
        # 7.1 Code examples
        self.story.append(Paragraph("7.1 Exemples de Code", self.styles['CustomHeading2']))
        
        # Exemple complet d'utilisation
        complete_example = """
        # Exemple Complet d'Utilisation du Système
        
        from agents.langchain_agents.django_integration import DjangoLangChainBridge
        
        # 1. Initialisation du système
        bridge = DjangoLangChainBridge.get_instance()
        
        # 2. Requête utilisateur
        user_query = "Je cherche 3 livres sur l'apprentissage du Python pour débutants"
        
        # 3. Traitement via LangChain
        response = bridge.process_query_with_routing(user_query)
        
        # 4. Structure de la réponse
        {
            "recommendations": [
                {
                    "title": "Python Crash Course",
                    "author": "Eric Matthes",
                    "description": "Introduction pratique à Python...",
                    "rating": 4.8,
                    "difficulty": "beginner",
                    "programming_languages": ["Python"],
                    "similarity_score": 0.95
                }
            ],
            "explanation": "Ces livres ont été sélectionnés pour leur approche...",
            "metadata": {
                "agent_used": "tech",
                "processing_time": 3.2,
                "rag_results_count": 15,
                "classification_confidence": 0.92
            },
            "suggestions": [
                "Vous pourriez aussi vous intéresser aux frameworks web Python",
                "Considérez des projets pratiques pour consolider"
            ],
            "total_found": 25
        }
        """
        
        self.story.append(Paragraph(complete_example, self.styles['CustomCode']))
        self.story.append(Spacer(1, 15))
        
        # 7.2 Configuration complète
        self.story.append(Paragraph("7.2 Configuration Complète", self.styles['CustomHeading2']))
        
        full_config = """
        Configuration Complete - settings/production.py
        
        LANGCHAIN_CONFIG = {
            Configuration LLM
            'provider': 'ollama',
            'model': 'llama3.2:3b',
            'api_key': os.getenv('LLM_API_KEY'),
            'ollama_base_url': 'http://localhost:11434',
            
            Parametres de Generation
            'temperature': 0.7,
            'max_tokens': 512,
            'timeout': 30,
            'top_p': 0.9,
            'frequency_penalty': 0.1,
            
            Configuration RAG
            'rag_enabled': True,
            'max_rag_results': 5,
            'similarity_threshold': 0.7,
            'rag_rerank': True,
            
            Gestion d'Erreurs
            'fallback_enabled': True,
            'retry_attempts': 3,
            'circuit_breaker_threshold': 5,
            'circuit_breaker_timeout': 300,
            
            Performance
            'llama_optimized': True,
            'collect_stats': True,
            'async_enabled': False,
            'batch_size': 100,
            
            Debugging et Monitoring
            'debug_mode': False,
            'log_level': 'INFO',
            'trace_requests': True,
            'performance_logging': True,
            
            Cache (Futur)
            'cache_enabled': False,
            'cache_ttl': 3600,
            'cache_backend': 'redis',
            
            Securite
            'rate_limit': {
                'enabled': True,
                'requests_per_minute': 60,
                'burst_limit': 10
            },
            'input_validation': {
                'max_query_length': 1000,
                'sanitize_input': True,
                'blocked_patterns': ['script', 'javascript']
            }
        }
        
        Variables d'environnement (secrets)
        OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
        ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
        LANGCHAIN_DEBUG = os.getenv('LANGCHAIN_DEBUG', 'False').lower() == 'true'
        """
        
        self.story.append(Paragraph(full_config, self.styles['CustomCode']))
        self.story.append(Spacer(1, 15))
        
        # 7.3 Troubleshooting
        self.story.append(Paragraph("7.3 Troubleshooting", self.styles['CustomHeading2']))
        
        troubleshooting_text = """
        <b>Problèmes Courants et Solutions:</b>
        
        <br/><br/><b>1. Ollama Connection Failed</b><br/>
        • <b>Symptôme:</b> ConnectionError lors de l'appel LLM<br/>
        • <b>Cause:</b> Ollama non démarré ou URL incorrecte<br/>
        • <b>Solution:</b> Vérifier ollama serve et OLLAMA_BASE_URL<br/>
        
        <br/><b>2. RAG Returns Empty Results</b><br/>
        • <b>Symptôme:</b> Aucune recommandation trouvée<br/>
        • <b>Cause:</b> ChromaDB non indexé ou seuil trop élevé<br/>
        • <b>Solution:</b> Relancer indexation et ajuster similarity_threshold<br/>
        
        <br/><b>3. Slow Response Times</b><br/>
        • <b>Symptôme:</b> Réponses >10s<br/>
        • <b>Cause:</b> Modèle trop gros ou RAG non optimisé<br/>
        • <b>Solution:</b> Utiliser llama3.2:1b ou optimiser ChromaDB<br/>
        
        <br/><b>4. Classification Errors</b><br/>
        • <b>Symptôme:</b> Mauvais routage des requêtes<br/>
        • <b>Cause:</b> Mots-clés manquants ou prompts inadéquats<br/>
        • <b>Solution:</b> Enrichir KEYWORDS ou ajuster prompts<br/>
        
        <br/><b>5. Memory Issues</b><br/>
        • <b>Symptôme:</b> OOM lors de l'indexation<br/>
        • <b>Cause:</b> Batch size trop élevé<br/>
        • <b>Solution:</b> Réduire batch_size à 50 ou moins<br/>
        
        <br/><b>Commandes de Debug Utiles:</b><br/>
        • <b>Test connexion:</b> curl http://localhost:11434/api/version<br/>
        • <b>Status système:</b> GET /api/langchain/status/<br/>
        • <b>Logs détaillés:</b> LANGCHAIN_DEBUG=True dans .env<br/>
        • <b>Reset ChromaDB:</b> rm -rf ./chroma_db && python manage.py index_all<br/>
        • <b>Test classification:</b> python test_langchain_rag.py
        """
        
        self.story.append(Paragraph(troubleshooting_text, self.styles['Normal']))
        
        # Footer final
        self.story.append(Spacer(1, 1*inch))
        footer_text = """
        <b>Document généré automatiquement</b><br/>
        Dual Book Advisor - Système LangChain<br/>
        Pour plus d'informations, consulter la documentation technique interne.
        """
        footer = Paragraph(footer_text, self.styles['Normal'])
        self.story.append(footer)

if __name__ == "__main__":
    # Génération du PDF
    generator = LangChainDocumentationGenerator()
    filename = generator.generate_pdf()
    print(f"Documentation générée: {filename}")