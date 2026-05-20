from django.urls import path

from . import views


urlpatterns = [
    path("", views.listado_videojuegos, name="listado_videojuegos"),
    path("detalle/<int:id>/", views.detalle_videojuego, name="detalle_videojuego"),
    path("crear/", views.crear_videojuego, name="crear_videojuego"),
    path("editar/<int:id>/", views.editar_videojuego, name="editar_videojuego"),
    path("eliminar/<int:id>/", views.eliminar_videojuego, name="eliminar_videojuego"),
    path("diagnostico/rawg/", views.diagnostico_rawg, name="diagnostico_rawg"),
    path("api/juegos/", views.api_videojuegos, name="api_videojuegos"),
    path("api/buscar-portadas/", views.api_buscar_portadas, name="api_buscar_portadas"),
    path("api/recientes/", views.api_posts_recientes, name="api_posts_recientes"),
]
