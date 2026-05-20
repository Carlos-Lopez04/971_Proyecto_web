from django.urls import path
from . import views

urlpatterns = [
    # Vistas principales
    path('', views.listado_videojuegos, name='listado_videojuegos'),
    path('detalle/<int:id>/', views.detalle_videojuego, name='detalle_videojuego'),
    path('crear/', views.crear_videojuego, name='crear_videojuego'),
    path('editar/<int:id>/', views.editar_videojuego, name='editar_videojuego'),
    path('eliminar/<int:id>/', views.eliminar_videojuego, name='eliminar_videojuego'),
    
    # APIs
    path('api/juegos/', views.api_videojuegos, name='api_videojuegos'),
    path('api/recientes/', views.api_posts_recientes, name='api_posts_recientes'),
]
