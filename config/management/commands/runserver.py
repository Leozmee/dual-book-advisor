"""
Commande runserver personnalisée avec affichage amélioré
"""
import os
import sys
from django.core.management.commands.runserver import Command as BaseRunserverCommand
from django.core.management.base import CommandError
from django.utils import autoreload


class Command(BaseRunserverCommand):
    """Commande runserver avec affichage personnalisé de l'adresse"""
    
    def add_arguments(self, parser):
        super().add_arguments(parser)
    
    def execute(self, *args, **options):
        """Override execute pour afficher des informations personnalisées"""
        # Obtenir l'adresse et le port
        if args:
            addr = args[0]
        else:
            addr = options.get('addrport', '127.0.0.1:8000')
        
        # Parser l'adresse
        if ':' in addr:
            host, port = addr.rsplit(':', 1)
        else:
            host = '127.0.0.1'
            port = addr if addr.isdigit() else '8000'
        
        # Affichage personnalisé avant le démarrage
        self.stdout.write("")
        self.stdout.write("=" * 70)
        self.stdout.write(self.style.SUCCESS("🚀 DUAL BOOK ADVISOR - Serveur Django"))
        self.stdout.write("=" * 70)
        self.stdout.write("")
        
        # URLs principales
        base_url = f"http://{host}:{port}"
        self.stdout.write(f"🌐 Serveur web      : {self.style.HTTP_INFO(base_url)}")
        self.stdout.write(f"🔧 Admin Django     : {self.style.HTTP_INFO(base_url + '/admin/')}")
        self.stdout.write(f"📚 API Books        : {self.style.HTTP_INFO(base_url + '/api/books/')}")
        self.stdout.write(f"💬 API Chat         : {self.style.HTTP_INFO(base_url + '/api/chat/')}")
        self.stdout.write(f"🤖 LangChain Agents : {self.style.HTTP_INFO(base_url + '/api/chat/langchain/')}")
        self.stdout.write("")
        
        # Endpoints LangChain détaillés
        self.stdout.write("🤖 Endpoints LangChain disponibles :")
        endpoints = [
            ("Routage automatique", "/api/chat/langchain/"),
            ("Agent technique", "/api/chat/langchain/tech/"),
            ("Agent littéraire", "/api/chat/langchain/literature/"),
            ("Statut des agents", "/api/chat/langchain/status/")
        ]
        
        for desc, endpoint in endpoints:
            self.stdout.write(f"   • {desc:<20} : {base_url}{endpoint}")
        
        self.stdout.write("")
        self.stdout.write("📖 Documentation LangChain : README_LANGCHAIN.md")
        self.stdout.write("")
        self.stdout.write("🛑 Pour arrêter le serveur : Ctrl+C")
        self.stdout.write("=" * 70)
        self.stdout.write("")
        
        # Exécuter la commande originale
        return super().execute(*args, **options)
    
    def inner_run(self, *args, **options):
        """Override inner_run pour personnaliser les messages de démarrage"""
        # Message de démarrage personnalisé
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("✅ Serveur Django démarré avec succès !"))
        self.stdout.write("")
        
        # Appeler la méthode parent
        return super().inner_run(*args, **options)