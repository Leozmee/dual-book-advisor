from django.contrib import admin
from .models import TechBook, LiteratureBook, Recommendation, Genre, ProgrammingLanguage


@admin.register(TechBook)
class TechBookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'rating', 'price', 'publish_date', 'best_seller', 'top_rated')
    list_filter = ('best_seller', 'top_rated', 'publish_date', 'rating')
    search_fields = ('title', 'author', 'description')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-rating', '-publish_date')


@admin.register(LiteratureBook)
class LiteratureBookAdmin(admin.ModelAdmin):
    list_display = ('title', 'authors', 'average_rating', 'published_year', 'num_pages')
    list_filter = ('published_year', 'average_rating', 'categories')
    search_fields = ('title', 'authors', 'description')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-average_rating', '-published_year')


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('user', 'agent_type', 'book_title', 'score', 'created_at')
    list_filter = ('agent_type', 'score', 'created_at')
    search_fields = ('user__email', 'book_title', 'reason')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(ProgrammingLanguage)
class ProgrammingLanguageAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)