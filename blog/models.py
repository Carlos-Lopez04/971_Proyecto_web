# blog/models.py
from django.db import models

class Videojuego(models.Model):
    GENEROS = [
        ('ACC', 'Acción'),
        ('AVT', 'Aventura'),
        ('RPG', 'Rol (RPG)'),
        ('EST', 'Estrategia'),
        ('DEP', 'Deportes'),
        ('SIM', 'Simulación'),
    ]
    
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    genero = models.CharField(max_length=3, choices=GENEROS, default='ACC')
    desarrollador = models.CharField(max_length=100)
    fecha_lanzamiento = models.DateField()
    
    # NUEVO: Campo para imagen LOCAL
    imagen = models.ImageField(
        upload_to='videojuegos/',  # Se guardará en media/videojuegos/
        blank=True,
        null=True
    )
    
    # Campo opcional para URL externa (por si no tienes imagen local)
    imagen_url_externa = models.URLField(blank=True, null=True, help_text="URL alternativa si no hay imagen local")
    
    # Campo opcional para URL externa (por si no tienes imagen local)
    imagen_url_externa = models.URLField(blank=True, null=True, help_text="URL alternativa si no hay imagen local")
    
    def __str__(self):
        return self.nombre
    
    @property
    def get_imagen_url(self):
        """Retorna la URL de la imagen local o la externa"""
        if self.imagen:
            return self.imagen.url
        elif self.imagen_url_externa:
            return self.imagen_url_externa
        else:
            return '/static/blog/images/default-game.jpg'  # Imagen por defecto