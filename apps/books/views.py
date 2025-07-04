from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import TechBook, LiteratureBook, Recommendation, Genre, ProgrammingLanguage
from .serializers import (
    TechBookSerializer, LiteratureBookSerializer, RecommendationSerializer,
    GenreSerializer, ProgrammingLanguageSerializer
)


class TechBookListView(generics.ListAPIView):
    queryset = TechBook.objects.all()
    serializer_class = TechBookSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(author__icontains=search) |
                Q(description__icontains=search)
            )
        return queryset.order_by('-rating', '-publish_date')


class TechBookDetailView(generics.RetrieveAPIView):
    queryset = TechBook.objects.all()
    serializer_class = TechBookSerializer


class LiteratureBookListView(generics.ListAPIView):
    queryset = LiteratureBook.objects.all()
    serializer_class = LiteratureBookSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(authors__icontains=search) |
                Q(description__icontains=search)
            )
        return queryset.order_by('-average_rating', '-published_year')


class LiteratureBookDetailView(generics.RetrieveAPIView):
    queryset = LiteratureBook.objects.all()
    serializer_class = LiteratureBookSerializer


class RecommendationListView(generics.ListAPIView):
    serializer_class = RecommendationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Recommendation.objects.filter(user=self.request.user).order_by('-created_at')


class BookSearchView(APIView):
    def get(self, request):
        query = request.query_params.get('q', '')
        book_type = request.query_params.get('type', 'all')  # 'tech', 'literature', or 'all'
        
        results = {}
        
        if book_type in ['tech', 'all']:
            tech_books = TechBook.objects.filter(
                Q(title__icontains=query) |
                Q(author__icontains=query) |
                Q(description__icontains=query)
            )[:10]
            results['tech_books'] = TechBookSerializer(tech_books, many=True).data
        
        if book_type in ['literature', 'all']:
            literature_books = LiteratureBook.objects.filter(
                Q(title__icontains=query) |
                Q(authors__icontains=query) |
                Q(description__icontains=query)
            )[:10]
            results['literature_books'] = LiteratureBookSerializer(literature_books, many=True).data
        
        return Response(results)


class GenreListView(generics.ListAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class ProgrammingLanguageListView(generics.ListAPIView):
    queryset = ProgrammingLanguage.objects.all()
    serializer_class = ProgrammingLanguageSerializer