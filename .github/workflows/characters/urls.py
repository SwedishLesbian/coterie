# characters/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('character/new/', views.character_create, name='character_create'),
    path('character/<int:pk>/', views.character_detail, name='character_detail'),
    path('character/<int:pk>/edit/', views.character_update, name='character_update'),
]
