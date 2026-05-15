# blog/views.py
from django.shortcuts import render, redirect
from .models import Videojuego
from datetime import date
from django.http import JsonResponse

# Vista principal: Lista de videojuegos
def listado_videojuegos(request):
    # Filtro opcional por género (mejora de funcionalidad)
    genero_filtro = request.GET.get('genero')
    if genero_filtro:
        juegos = Videojuego.objects.filter(genero=genero_filtro).order_by('-fecha_lanzamiento')
    else:
        juegos = Videojuego.objects.all().order_by('-fecha_lanzamiento')
    return render(request, 'blog/listado.html', {'juegos': juegos, 'generos': Videojuego.GENEROS})

# Vista para crear un nuevo videojuego
def crear_videojuego(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        descripcion = request.POST.get("descripcion", "")
        genero = request.POST.get("genero")
        desarrollador = request.POST.get("desarrollador")
        fecha_lanzamiento = request.POST.get("fecha_lanzamiento")
        imagen_url_externa = request.POST.get("imagen_url_externa", "")
        imagen = request.FILES.get("imagen")  # Archivo subido
        
        # VALIDACIÓN CRÍTICA (corrige el error que marcaba pytest)
        if not nombre:
            return render(request, "blog/crear.html", {
                "error": "El nombre del videojuego no puede estar vacío",
                "generos": Videojuego.GENEROS
            })
        
        # Crear el objeto
        Videojuego.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            genero=genero,
            desarrollador=desarrollador,
            fecha_lanzamiento=fecha_lanzamiento,
            imagen=imagen,
            imagen_url_externa=imagen_url_externa
        )
        return redirect("listado_videojuegos")
    
    return render(request, "blog/crear.html", {"generos": Videojuego.GENEROS})

# --- API (Adaptada de tu documento) ---
def api_videojuegos(request):
    """Retorna todos los videojuegos en formato JSON"""
    juegos = Videojuego.objects.all().values('id', 'nombre', 'descripcion', 'genero', 'desarrollador', 'fecha_lanzamiento')
    return JsonResponse(list(juegos), safe=False)

def api_videojuego_detalle(request, id):
    """Retorna un videojuego específico en JSON"""
    juego = Videojuego.objects.get(id=id)
    data = {
        'nombre': juego.nombre,
        'descripcion': juego.descripcion,
        'genero': juego.get_genero_display(),  # Muestra el texto legible
        'desarrollador': juego.desarrollador,
        'fecha_lanzamiento': juego.fecha_lanzamiento,
    }
    return JsonResponse(data)

def crear_videojuego(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        descripcion = request.POST.get("descripcion", "")
        genero = request.POST.get("genero")
        desarrollador = request.POST.get("desarrollador")
        fecha_lanzamiento = request.POST.get("fecha_lanzamiento")
        imagen_url_externa = request.POST.get("imagen_url_externa", "")
        
        # Validación del nombre (tu documento lo requiere)
        if not nombre:
            return render(request, "blog/crear.html", {
                "error": "El nombre del videojuego no puede estar vacío",
                "generos": Videojuego.GENEROS
            })
        
        # Crear el objeto (con imagen local si se subió)
        nuevo_juego = Videojuego(
            nombre=nombre,
            descripcion=descripcion,
            genero=genero,
            desarrollador=desarrollador,
            fecha_lanzamiento=fecha_lanzamiento,
            imagen_url_externa=imagen_url_externa if imagen_url_externa else None
        )
        
        # Manejar la imagen subida
        if 'imagen' in request.FILES:
            nuevo_juego.imagen = request.FILES['imagen']
        
        nuevo_juego.save()
        return redirect("listado_videojuegos")
    
    return render(request, "blog/crear.html", {"generos": Videojuego.GENEROS})