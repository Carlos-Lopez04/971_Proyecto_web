from django.urls import path
from . import views

urlpatterns = [
    path('', views.listado_videojuegos, name='listado_videojuegos'),
    path('crear/', views.crear_videojuego, name='crear_videojuego'),
    # APIs
    path('api/juegos/', views.api_videojuegos, name='api_videojuegos'),
    path('api/juegos/<int:id>/', views.api_videojuego_detalle, name='api_videojuego_detalle'),
]