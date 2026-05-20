from django.db import models
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from .models import Videojuego

# ============================================
# VISTAS PRINCIPALES
# ============================================

def listado_videojuegos(request):
    """Muestra todos los videojuegos con filtros y ordenamiento"""
    
    # Obtener el parámetro de ordenamiento
    orden = request.GET.get("orden", "recientes")
    
    # Base de la consulta
    juegos = Videojuego.objects.all()
    
    # Aplicar ordenamiento
    if orden == "recientes":
        juegos = juegos.order_by("-created_at")
        titulo_orden = "📅 Más Recientes"
    elif orden == "antiguos":
        juegos = juegos.order_by("created_at")
        titulo_orden = "📅 Más Antiguos"
    elif orden == "lanzamiento":
        juegos = juegos.order_by("-fecha_lanzamiento")
        titulo_orden = "🎮 Por fecha de lanzamiento"
    elif orden == "alfabetico":
        juegos = juegos.order_by("nombre")
        titulo_orden = "🔤 Alfabético A-Z"
    elif orden == "alfabetico_inv":
        juegos = juegos.order_by("-nombre")
        titulo_orden = "🔤 Alfabético Z-A"
    else:
        juegos = juegos.order_by("-created_at")
        titulo_orden = "📅 Más Recientes"
    
    # Filtro por género
    genero_filtro = request.GET.get("genero")
    if genero_filtro:
        juegos = juegos.filter(genero=genero_filtro)
    
    # Búsqueda
    busqueda = request.GET.get("busqueda", "")
    if busqueda:
        juegos = juegos.filter(
            models.Q(nombre__icontains=busqueda) |
            models.Q(desarrollador__icontains=busqueda)
        )
    
    return render(request, "blog/listado.html", {
        "juegos": juegos,
        "generos": Videojuego.GENEROS,
        "total_juegos": juegos.count(),
        "busqueda": busqueda,
        "orden_actual": orden,
        "titulo_orden": titulo_orden,
        "genero_actual": genero_filtro,
    })


def detalle_videojuego(request, id):
    """Muestra el detalle completo de un videojuego"""
    juego = get_object_or_404(Videojuego, id=id)
    return render(request, "blog/detalle.html", {"juego": juego})


def crear_videojuego(request):
    """Crea un nuevo videojuego"""
    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        descripcion = request.POST.get("descripcion", "").strip()
        genero = request.POST.get("genero", "ACC")
        desarrollador = request.POST.get("desarrollador", "").strip()
        fecha_lanzamiento = request.POST.get("fecha_lanzamiento")
        imagen_url_externa = request.POST.get("imagen_url_externa", "").strip()
        imagen = request.FILES.get("imagen")
        
        # Validaciones
        if not nombre:
            return render(request, "blog/crear.html", {
                "error": "El nombre del videojuego no puede estar vacío",
                "generos": Videojuego.GENEROS,
            })
        
        if not fecha_lanzamiento:
            return render(request, "blog/crear.html", {
                "error": "La fecha de lanzamiento es obligatoria",
                "generos": Videojuego.GENEROS,
            })
        
        # Crear el juego
        juego = Videojuego.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            genero=genero,
            desarrollador=desarrollador,
            fecha_lanzamiento=fecha_lanzamiento,
            imagen=imagen,
            imagen_url_externa=imagen_url_externa if imagen_url_externa else None,
        )
        
        messages.success(request, f'✅ ¡{juego.nombre} ha sido agregado exitosamente!')
        return redirect("detalle_videojuego", id=juego.id)
    
    return render(request, "blog/crear.html", {"generos": Videojuego.GENEROS})


def editar_videojuego(request, id):
    """Edita un videojuego existente"""
    juego = get_object_or_404(Videojuego, id=id)
    
    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        descripcion = request.POST.get("descripcion", "").strip()
        genero = request.POST.get("genero")
        desarrollador = request.POST.get("desarrollador", "").strip()
        fecha_lanzamiento = request.POST.get("fecha_lanzamiento")
        imagen_url_externa = request.POST.get("imagen_url_externa", "").strip()
        
        # Validaciones
        if not nombre:
            return render(request, "blog/editar.html", {
                "error": "El nombre del videojuego no puede estar vacío",
                "juego": juego,
                "generos": Videojuego.GENEROS,
            })
        
        # Actualizar campos
        juego.nombre = nombre
        juego.descripcion = descripcion
        juego.genero = genero
        juego.desarrollador = desarrollador
        juego.fecha_lanzamiento = fecha_lanzamiento
        
        # Manejar eliminación de imagen
        if request.POST.get("eliminar_imagen"):
            juego.imagen.delete()
            juego.imagen = None
        
        # Manejar nueva imagen local
        if "imagen" in request.FILES:
            juego.imagen = request.FILES["imagen"]
        
        # Manejar URL externa
        if imagen_url_externa:
            juego.imagen_url_externa = imagen_url_externa
        elif request.POST.get("eliminar_url"):
            juego.imagen_url_externa = None
        
        juego.save()
        messages.success(request, f'✅ ¡{juego.nombre} ha sido actualizado correctamente!')
        return redirect("detalle_videojuego", id=juego.id)
    
    return render(request, "blog/editar.html", {
        "juego": juego,
        "generos": Videojuego.GENEROS,
    })


def eliminar_videojuego(request, id):
    """Elimina un videojuego"""
    juego = get_object_or_404(Videojuego, id=id)
    
    if request.method == "POST":
        nombre = juego.nombre
        # Eliminar la imagen local si existe
        if juego.imagen:
            juego.imagen.delete()
        juego.delete()
        messages.warning(request, f'🗑️ ¡{nombre} ha sido eliminado del catálogo!')
        return redirect("listado_videojuegos")
    
    return render(request, "blog/eliminar.html", {"juego": juego})


# ============================================
# APIS (Opcionales)
# ============================================

def api_videojuegos(request):
    """API para obtener todos los videojuegos en JSON"""
    juegos = Videojuego.objects.all().order_by("-created_at")
    data = [
        {
            "id": juego.id,
            "nombre": juego.nombre,
            "descripcion": juego.descripcion,
            "genero": juego.get_genero_display(),
            "desarrollador": juego.desarrollador,
            "fecha_lanzamiento": juego.fecha_lanzamiento.isoformat(),
            "created_at": juego.created_at.isoformat(),
        }
        for juego in juegos
    ]
    return JsonResponse(data, safe=False)


def api_posts_recientes(request):
    """API para obtener los juegos más recientes"""
    limite_raw = request.GET.get("limit", "5")
    try:
        limite = max(1, min(int(limite_raw), 20))
    except ValueError:
        return JsonResponse({"error": "Limit debe ser un número entre 1 y 20"}, status=400)
    
    juegos = Videojuego.objects.all().order_by("-created_at")[:limite]
    data = [{"id": j.id, "nombre": j.nombre, "created_at": j.created_at.isoformat()} for j in juegos]
    return JsonResponse({"total": len(data), "resultados": data})
