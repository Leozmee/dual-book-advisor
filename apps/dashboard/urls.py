from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='home'),
    path('chat/', views.ChatView.as_view(), name='chat'),
    path('api/dashboard/', views.DashboardAPIView.as_view(), name='dashboard'),
    path('api/stats/', views.UserStatsView.as_view(), name='user_stats'),
]