from django.db import models


class Videojuego(models.Model):
    GENEROS = [
        ("ACC", "Accion"),
        ("AVT", "Aventura"),
        ("RPG", "Rol (RPG)"),
        ("EST", "Estrategia"),
        ("DEP", "Deportes"),
        ("SIM", "Simulacion"),
    ]

    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    genero = models.CharField(max_length=3, choices=GENEROS, default="ACC")
    desarrollador = models.CharField(max_length=100)
    fecha_lanzamiento = models.DateField()
    imagen = models.ImageField(upload_to="videojuegos/", blank=True, null=True)
    imagen_url_externa = models.URLField(
        blank=True,
        null=True,
        help_text="URL alternativa si no hay imagen local",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre

    @property
    def portada_url(self):
        if self.imagen:
            return self.imagen.url
        if self.imagen_url_externa:
            return self.imagen_url_externa
        return "/static/blog/images/default-game.jpg"
