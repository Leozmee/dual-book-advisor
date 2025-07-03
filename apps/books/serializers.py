from rest_framework import serializers
from .models import TechBook, LiteratureBook, Recommendation, Genre, ProgrammingLanguage


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name', 'description']


class ProgrammingLanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgrammingLanguage
        fields = ['id', 'name', 'description']


class TechBookSerializer(serializers.ModelSerializer):
    programming_languages = ProgrammingLanguageSerializer(many=True, read_only=True)
    
    class Meta:
        model = TechBook
        fields = [
            'id', 'title', 'description', 'author', 'isbn10', 'isbn13', 
            'publish_date', 'edition', 'best_seller', 'top_rated', 'rating', 
            'review_count', 'price', 'programming_languages', 'tech_categories', 
            'difficulty_level', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class LiteratureBookSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)
    
    class Meta:
        model = LiteratureBook
        fields = [
            'id', 'isbn13', 'isbn10', 'title', 'subtitle', 'authors', 
            'categories', 'thumbnail', 'description', 'published_year', 
            'average_rating', 'num_pages', 'ratings_count', 'booktitle_alt', 
            'author_alt', 'popularity_rating', 'votes_count', 'popularity_score', 
            'genres', 'themes', 'reading_difficulty', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class RecommendationSerializer(serializers.ModelSerializer):
    tech_book = TechBookSerializer(read_only=True)
    literature_book = LiteratureBookSerializer(read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = Recommendation
        fields = [
            'id', 'user_email', 'agent_type', 'book_title', 'book_author', 
            'book_isbn', 'score', 'reason', 'context_query', 'tech_book', 
            'literature_book', 'user_rating', 'user_feedback', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'user_email']