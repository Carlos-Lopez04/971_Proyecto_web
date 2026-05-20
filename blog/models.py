from django.db import models
from django.utils import timezone

class Videojuego(models.Model):
    GENEROS = [
        ('ACC', 'Acción'),
        ('AVT', 'Aventura'),
        ('RPG', 'Rol (RPG)'),
        ('EST', 'Estrategia'),
        ('DEP', 'Deportes'),
        ('SIM', 'Simulación'),
        ('TER', 'Terror'),
        ('PZL', 'Puzzle'),
    ]
    
    nombre = models.CharField(max_length=200, verbose_name="Nombre del juego")
    descripcion = models.TextField(verbose_name="Descripción")
    genero = models.CharField(max_length=3, choices=GENEROS, default='ACC', verbose_name="Género")
    desarrollador = models.CharField(max_length=100, verbose_name="Desarrolladora")
    fecha_lanzamiento = models.DateField(verbose_name="Fecha de lanzamiento")
    
    # Imágenes
    imagen = models.ImageField(
        upload_to='videojuegos/',
        blank=True,
        null=True,
        verbose_name="Imagen local"
    )
    imagen_url_externa = models.URLField(
        blank=True, 
        null=True,
        verbose_name="URL de imagen externa"
    )
    
    # Fechas automáticas
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última modificación")
    
    class Meta:
        verbose_name = "Videojuego"
        verbose_name_plural = "Videojuegos"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.nombre
    
    @property
    def get_imagen_url(self):
        """Retorna la URL de la imagen disponible"""
        if self.imagen:
            return self.imagen.url
        elif self.imagen_url_externa:
            return self.imagen_url_externa
        return None
