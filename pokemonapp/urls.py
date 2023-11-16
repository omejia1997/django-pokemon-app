from django.urls import path
from . import views

urlpatterns = [
    path('', views.pokemons),
    path('view_information_pokemon/', views.pokemon_information, name='view_information_pokemon'),
    path('search/', views.search, name='search')
]
