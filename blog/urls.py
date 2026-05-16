from django.urls import path
from . import views

urlpatterns = [
    path('', views.listado_videojuegos, name='listado_videojuegos'),
    path('crear/', views.crear_videojuego, name='crear_videojuego'),
    path('api/juegos/', views.api_videojuegos, name='api_videojuegos'),
    path('api/juegos/<int:id>/', views.api_videojuego_detalle, name='api_videojuego_detalle'),
    path('api/posts/recientes/', views.api_posts_recientes, name='api_posts_recientes'),
    path('api/portadas/buscar/', views.api_buscar_portadas, name='api_buscar_portadas'),
]
