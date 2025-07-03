from django.db import models
from django.contrib.auth import get_user_model
from apps.accounts.models import Genre, ProgrammingLanguage

User = get_user_model()


class TechBook(models.Model):
    # Based on Amazon Books Data.csv structure
    title = models.CharField(max_length=500)
    description = models.TextField()
    author = models.CharField(max_length=200)
    isbn10 = models.CharField(max_length=10, blank=True, null=True)
    isbn13 = models.CharField(max_length=13, blank=True, null=True)
    publish_date = models.DateField(null=True, blank=True)
    edition = models.CharField(max_length=50, blank=True)
    best_seller = models.BooleanField(default=False)
    top_rated = models.BooleanField(default=False)
    rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    review_count = models.IntegerField(null=True, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    # Additional fields for RAG and recommendations
    programming_languages = models.ManyToManyField(ProgrammingLanguage, blank=True)
    tech_categories = models.TextField(blank=True, help_text="Comma-separated tech categories")
    difficulty_level = models.CharField(max_length=20, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ], default='intermediate')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-rating', '-publish_date']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['author']),
            models.Index(fields=['rating']),
            models.Index(fields=['best_seller']),
        ]
    
    def __str__(self):
        return f"{self.title} by {self.author}"


class LiteratureBook(models.Model):
    # Based on books.csv structure
    isbn13 = models.CharField(max_length=13, unique=True)
    isbn10 = models.CharField(max_length=10, blank=True, null=True)
    title = models.CharField(max_length=500)
    subtitle = models.CharField(max_length=500, blank=True)
    authors = models.CharField(max_length=300)
    categories = models.CharField(max_length=200, blank=True)
    thumbnail = models.URLField(blank=True)
    description = models.TextField()
    published_year = models.IntegerField(null=True, blank=True)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    num_pages = models.IntegerField(null=True, blank=True)
    ratings_count = models.IntegerField(null=True, blank=True)
    
    # Additional fields from dataframe.csv (popularity scores)
    booktitle_alt = models.CharField(max_length=500, blank=True, help_text="Alternative title from popularity dataset")
    author_alt = models.CharField(max_length=300, blank=True, help_text="Alternative author from popularity dataset")
    popularity_rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    votes_count = models.IntegerField(null=True, blank=True)
    popularity_score = models.BigIntegerField(null=True, blank=True)
    
    # Additional fields for RAG and recommendations
    genres = models.ManyToManyField(Genre, blank=True)
    themes = models.TextField(blank=True, help_text="Comma-separated themes")
    reading_difficulty = models.CharField(max_length=20, choices=[
        ('easy', 'Easy'),
        ('moderate', 'Moderate'),
        ('challenging', 'Challenging'),
        ('difficult', 'Difficult'),
    ], default='moderate')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-average_rating', '-published_year']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['authors']),
            models.Index(fields=['average_rating']),
            models.Index(fields=['published_year']),
        ]
    
    def __str__(self):
        return f"{self.title} by {self.authors}"


class Recommendation(models.Model):
    AGENT_CHOICES = [
        ('tech', 'Tech Agent'),
        ('literature', 'Literature Agent'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    agent_type = models.CharField(max_length=20, choices=AGENT_CHOICES)
    
    # Book information (flexible to handle both tech and literature books)
    book_title = models.CharField(max_length=500)
    book_author = models.CharField(max_length=300)
    book_isbn = models.CharField(max_length=13, blank=True)
    
    # Recommendation details
    score = models.DecimalField(max_digits=3, decimal_places=2, help_text="Confidence score 0-1")
    reason = models.TextField(help_text="Why this book was recommended")
    context_query = models.TextField(help_text="Original user query that led to this recommendation")
    
    # Links to actual book records (optional)
    tech_book = models.ForeignKey(TechBook, on_delete=models.SET_NULL, null=True, blank=True)
    literature_book = models.ForeignKey(LiteratureBook, on_delete=models.SET_NULL, null=True, blank=True)
    
    # User feedback
    user_rating = models.IntegerField(null=True, blank=True, choices=[
        (1, 'Poor'),
        (2, 'Fair'),
        (3, 'Good'),
        (4, 'Very Good'),
        (5, 'Excellent'),
    ])
    user_feedback = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'agent_type']),
            models.Index(fields=['score']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.agent_type.title()} recommendation: {self.book_title} for {self.user.email}"