from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    path('tech/', views.TechBookListView.as_view(), name='tech_books'),
    path('tech/<int:pk>/', views.TechBookDetailView.as_view(), name='tech_book_detail'),
    path('literature/', views.LiteratureBookListView.as_view(), name='literature_books'),
    path('literature/<int:pk>/', views.LiteratureBookDetailView.as_view(), name='literature_book_detail'),
    path('recommendations/', views.RecommendationListView.as_view(), name='recommendations'),
    path('search/', views.BookSearchView.as_view(), name='search'),
    path('genres/', views.GenreListView.as_view(), name='genres'),
    path('programming-languages/', views.ProgrammingLanguageListView.as_view(), name='programming_languages'),
]