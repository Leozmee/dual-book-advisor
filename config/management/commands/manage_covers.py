"""
Commande Django pour gérer le service d'images de couvertures
Fichier: config/management/commands/manage_covers.py
"""
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import logging
import time

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Gère le service d\'images de couvertures'

    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            choices=['test', 'health', 'cache-clear', 'cache-stats', 'warmup'],
            help='Action à effectuer'
        )
        
        parser.add_argument(
            '--books',
            type=int,
            default=10,
            help='Nombre de livres pour le warmup (défaut: 10)'
        )
        
        parser.add_argument(
            '--agent',
            choices=['tech', 'literature', 'manga'],
            help='Type d\'agent pour le warmup'
        )
        
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Affichage verbeux'
        )

    def handle(self, *args, **options):
        action = options['action']
        verbose = options['verbose']
        
        if verbose:
            logging.basicConfig(level=logging.DEBUG)
        
        try:
            from agents.cover_image_service import cover_service
        except ImportError:
            raise CommandError("Service d'images non disponible. Vérifiez l'installation.")
        
        if action == 'test':
            self._run_tests(cover_service, verbose)
        elif action == 'health':
            self._check_health(cover_service)
        elif action == 'cache-clear':
            self._clear_cache(cover_service)
        elif action == 'cache-stats':
            self._show_cache_stats(cover_service)
        elif action == 'warmup':
            self._warmup_cache(cover_service, options['books'], options['agent'])

    def _run_tests(self, cover_service, verbose):
        """Lance les tests du service"""
        self.stdout.write("🧪 Lancement des tests du service d'images...")
        
        # Test de santé
        health = cover_service.health_check()
        self.stdout.write("\n📊 État des services :")
        
        for service, status in health.items():
            status_text = self.style.SUCCESS("✅ OK") if status else self.style.ERROR("❌ ERREUR")
            self.stdout.write(f"   {service}: {status_text}")
        
        # Tests rapides
        test_cases = [
            ("Clean Code", "Robert Martin", "book"),
            ("Naruto", "", "manga"),
            ("Harry Potter", "J.K. Rowling", "book"),
        ]
        
        self.stdout.write("\n🔍 Tests de recherche :")
        successful = 0
        
        for title, author, book_type in test_cases:
            if verbose:
                self.stdout.write(f"   Recherche: {title} par {author} (type: {book_type})")
            
            image_url = cover_service.get_cover_image(title, author, book_type)
            
            if image_url:
                successful += 1
                status = self.style.SUCCESS("✅")
                if verbose:
                    self.stdout.write(f"   {status} Image trouvée: {image_url[:60]}...")
            else:
                status = self.style.WARNING("❌")
                if verbose:
                    self.stdout.write(f"   {status} Aucune image trouvée")
            
            if not verbose:
                self.stdout.write(f"   {title}: {status}")
            
            time.sleep(0.3)  # Rate limiting
        
        success_rate = successful / len(test_cases) * 100
        
        if success_rate >= 70:
            self.stdout.write(
                self.style.SUCCESS(f"\n🎉 Tests réussis ! Taux de succès: {success_rate:.1f}%")
            )
        elif success_rate >= 50:
            self.stdout.write(
                self.style.WARNING(f"\n⚠️  Tests partiels. Taux de succès: {success_rate:.1f}%")
            )
        else:
            self.stdout.write(
                self.style.ERROR(f"\n❌ Tests échoués. Taux de succès: {success_rate:.1f}%")
            )

    def _check_health(self, cover_service):
        """Vérifie la santé des services"""
        self.stdout.write("🏥 Vérification de la santé des services...")
        
        health = cover_service.health_check()
        cache_stats = cover_service.get_cache_stats()
        
        self.stdout.write("\n📊 État des APIs :")
        all_healthy = True
        
        for service, status in health.items():
            if status:
                status_text = self.style.SUCCESS("✅ Opérationnel")
            else:
                status_text = self.style.ERROR("❌ Indisponible")
                all_healthy = False
            
            self.stdout.write(f"   {service.replace('_', ' ').title()}: {status_text}")
        
        self.stdout.write(f"\n🗄️ Cache :")
        self.stdout.write(f"   Éléments en cache: {cache_stats['cached_items']}")
        
        if all_healthy:
            self.stdout.write(self.style.SUCCESS("\n✅ Tous les services sont opérationnels"))
        else:
            self.stdout.write(self.style.WARNING("\n⚠️  Certains services sont indisponibles"))

    def _clear_cache(self, cover_service):
        """Vide le cache"""
        self.stdout.write("🗑️ Vidage du cache...")
        
        stats_before = cover_service.get_cache_stats()
        cover_service.clear_cache()
        stats_after = cover_service.get_cache_stats()
        
        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Cache vidé ! {stats_before['cached_items']} → {stats_after['cached_items']} éléments"
            )
        )

    def _show_cache_stats(self, cover_service):
        """Affiche les statistiques du cache"""
        self.stdout.write("📊 Statistiques du cache :")
        
        stats = cover_service.get_cache_stats()
        
        self.stdout.write(f"   Éléments en cache: {stats['cached_items']}")
        
        if stats['cached_items'] > 0:
            self.stdout.write("   Clés récentes :")
            for key in stats['cache_keys'][:5]:
                self.stdout.write(f"     - {key}")
            
            if len(stats['cache_keys']) > 5:
                self.stdout.write(f"     ... et {len(stats['cache_keys']) - 5} autres")
        else:
            self.stdout.write("   Cache vide")

    def _warmup_cache(self, cover_service, num_books, agent_type):
        """Préchauffe le cache avec des livres populaires"""
        self.stdout.write(f"🔥 Préchauffage du cache ({num_books} livres)...")
        
        # Livres populaires par catégorie
        books_by_type = {
            'tech': [
                ("Clean Code", "Robert Martin"),
                ("Design Patterns", "Gang of Four"),
                ("The Pragmatic Programmer", "David Thomas"),
                ("Effective Java", "Joshua Bloch"),
                ("JavaScript: The Good Parts", "Douglas Crockford"),
                ("Python Crash Course", "Eric Matthes"),
                ("You Don't Know JS", "Kyle Simpson"),
                ("Head First Design Patterns", ""),
                ("Clean Architecture", "Robert Martin"),
                ("Refactoring", "Martin Fowler"),
            ],
            'literature': [
                ("Harry Potter", "J.K. Rowling"),
                ("1984", "George Orwell"),
                ("To Kill a Mockingbird", "Harper Lee"),
                ("The Great Gatsby", "F. Scott Fitzgerald"),
                ("Pride and Prejudice", "Jane Austen"),
                ("The Catcher in the Rye", "J.D. Salinger"),
                ("Lord of the Rings", "J.R.R. Tolkien"),
                ("The Hobbit", "J.R.R. Tolkien"),
                ("Brave New World", "Aldous Huxley"),
                ("The Da Vinci Code", "Dan Brown"),
            ],
            'manga': [
                ("Naruto", ""),
                ("One Piece", ""),
                ("Dragon Ball", ""),
                ("Attack on Titan", ""),
                ("Death Note", ""),
                ("Fullmetal Alchemist", ""),
                ("Bleach", ""),
                ("Demon Slayer", ""),
                ("My Hero Academia", ""),
                ("Tokyo Ghoul", ""),
            ]
        }
        
        # Sélectionner les livres selon le type d'agent
        if agent_type:
            if agent_type in books_by_type:
                selected_books = books_by_type[agent_type][:num_books]
                book_type = agent_type if agent_type != 'literature' else 'book'
            else:
                raise CommandError(f"Type d'agent invalide: {agent_type}")
        else:
            # Mélanger tous les types
            all_books = []
            for cat, books in books_by_type.items():
                for title, author in books:
                    book_type = cat if cat != 'literature' else 'book'
                    all_books.append((title, author, book_type))
            
            selected_books = all_books[:num_books]
        
        # Préchauffer le cache
        successful = 0
        start_time = time.time()
        
        for i, book_data in enumerate(selected_books, 1):
            if len(book_data) == 3:
                title, author, book_type = book_data
            else:
                title, author = book_data
                book_type = agent_type if agent_type != 'literature' else 'book'
            
            self.stdout.write(f"   {i:2d}/{len(selected_books)} - {title}", ending="")
            
            image_url = cover_service.get_cover_image(title, author, book_type)
            
            if image_url:
                self.stdout.write(self.style.SUCCESS(" ✅"))
                successful += 1
            else:
                self.stdout.write(self.style.WARNING(" ❌"))
            
            time.sleep(0.3)  # Rate limiting
        
        elapsed = time.time() - start_time
        success_rate = successful / len(selected_books) * 100
        
        self.stdout.write(f"\n📊 Résultats du préchauffage :")
        self.stdout.write(f"   Images trouvées: {successful}/{len(selected_books)} ({success_rate:.1f}%)")
        self.stdout.write(f"   Temps total: {elapsed:.1f}s")
        self.stdout.write(f"   Temps moyen: {elapsed/len(selected_books):.1f}s par livre")
        
        cache_stats = cover_service.get_cache_stats()
        self.stdout.write(f"   Cache final: {cache_stats['cached_items']} éléments")
        
        if success_rate >= 70:
            self.stdout.write(self.style.SUCCESS("🎉 Préchauffage réussi !"))
        else:
            self.stdout.write(self.style.WARNING("⚠️  Préchauffage partiel"))


# Créer le répertoire management/commands s'il n'existe pas
def create_management_structure():
    """Crée la structure management/commands si nécessaire"""
    import os
    from pathlib import Path
    
    base_dir = Path(__file__).parent.parent.parent
    management_dir = base_dir / 'config' / 'management'
    commands_dir = management_dir / 'commands'
    
    management_dir.mkdir(exist_ok=True)
    commands_dir.mkdir(exist_ok=True)
    
    # Créer les fichiers __init__.py
    (management_dir / '__init__.py').touch(exist_ok=True)
    (commands_dir / '__init__.py').touch(exist_ok=True)


if __name__ == "__main__":
    print("📝 Pour utiliser cette commande Django :")
    print("   python manage.py manage_covers test")
    print("   python manage.py manage_covers health")
    print("   python manage.py manage_covers cache-clear")
    print("   python manage.py manage_covers warmup --books 20 --agent tech")