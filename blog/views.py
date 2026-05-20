from django.conf import settings
from django.contrib import messages
from django.db import models
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import Videojuego
from .services import buscar_portada_videojuego


def listado_videojuegos(request):
    """Muestra todos los videojuegos con filtros y ordenamiento."""
    orden = request.GET.get("orden", "recientes")
    juegos = Videojuego.objects.all()

    if orden == "recientes":
        juegos = juegos.order_by("-created_at")
        titulo_orden = "Mas recientes"
    elif orden == "antiguos":
        juegos = juegos.order_by("created_at")
        titulo_orden = "Mas antiguos"
    elif orden == "lanzamiento":
        juegos = juegos.order_by("-fecha_lanzamiento")
        titulo_orden = "Por fecha de lanzamiento"
    elif orden == "alfabetico":
        juegos = juegos.order_by("nombre")
        titulo_orden = "Alfabetico A-Z"
    elif orden == "alfabetico_inv":
        juegos = juegos.order_by("-nombre")
        titulo_orden = "Alfabetico Z-A"
    else:
        juegos = juegos.order_by("-created_at")
        titulo_orden = "Mas recientes"

    genero_filtro = request.GET.get("genero")
    if genero_filtro:
        juegos = juegos.filter(genero=genero_filtro)

    busqueda = request.GET.get("busqueda", "")
    if busqueda:
        juegos = juegos.filter(
            models.Q(nombre__icontains=busqueda)
            | models.Q(desarrollador__icontains=busqueda)
        )

    return render(
        request,
        "blog/listado.html",
        {
            "juegos": juegos,
            "generos": Videojuego.GENEROS,
            "total_juegos": juegos.count(),
            "busqueda": busqueda,
            "orden_actual": orden,
            "titulo_orden": titulo_orden,
            "genero_actual": genero_filtro,
        },
    )


def detalle_videojuego(request, id):
    juego = get_object_or_404(Videojuego, id=id)
    return render(request, "blog/detalle.html", {"juego": juego})


def crear_videojuego(request):
    """Crea un nuevo videojuego e intenta asociar portada desde RAWG."""
    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        descripcion = request.POST.get("descripcion", "").strip()
        genero = request.POST.get("genero", "ACC")
        desarrollador = request.POST.get("desarrollador", "").strip()
        fecha_lanzamiento = request.POST.get("fecha_lanzamiento")

        if not nombre:
            return render(
                request,
                "blog/crear.html",
                {
                    "error": "El nombre del videojuego no puede estar vacio",
                    "generos": Videojuego.GENEROS,
                },
            )

        if not fecha_lanzamiento:
            return render(
                request,
                "blog/crear.html",
                {
                    "error": "La fecha de lanzamiento es obligatoria",
                    "generos": Videojuego.GENEROS,
                },
            )

        portada = buscar_portada_videojuego(nombre)
        imagen_url_externa = portada["portada_url"] if portada else None

        juego = Videojuego.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            genero=genero,
            desarrollador=desarrollador,
            fecha_lanzamiento=fecha_lanzamiento,
            imagen_url_externa=imagen_url_externa,
        )

        messages.success(request, f"{juego.nombre} ha sido agregado exitosamente.")
        return redirect("detalle_videojuego", id=juego.id)

    return render(request, "blog/crear.html", {"generos": Videojuego.GENEROS})


def editar_videojuego(request, id):
    """Edita un videojuego existente."""
    juego = get_object_or_404(Videojuego, id=id)

    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        descripcion = request.POST.get("descripcion", "").strip()
        genero = request.POST.get("genero")
        desarrollador = request.POST.get("desarrollador", "").strip()
        fecha_lanzamiento = request.POST.get("fecha_lanzamiento")
        imagen_url_externa = request.POST.get("imagen_url_externa", "").strip()

        if not nombre:
            return render(
                request,
                "blog/editar.html",
                {
                    "error": "El nombre del videojuego no puede estar vacio",
                    "juego": juego,
                    "generos": Videojuego.GENEROS,
                },
            )

        juego.nombre = nombre
        juego.descripcion = descripcion
        juego.genero = genero
        juego.desarrollador = desarrollador
        juego.fecha_lanzamiento = fecha_lanzamiento

        if request.POST.get("eliminar_imagen") and juego.imagen:
            juego.imagen.delete(save=False)
            juego.imagen = None

        if "imagen" in request.FILES:
            juego.imagen = request.FILES["imagen"]

        if imagen_url_externa:
            juego.imagen_url_externa = imagen_url_externa
        elif request.POST.get("eliminar_url"):
            juego.imagen_url_externa = None

        juego.save()
        messages.success(request, f"{juego.nombre} ha sido actualizado correctamente.")
        return redirect("detalle_videojuego", id=juego.id)

    return render(
        request,
        "blog/editar.html",
        {
            "juego": juego,
            "generos": Videojuego.GENEROS,
        },
    )


def eliminar_videojuego(request, id):
    if not request.user.is_authenticated or not request.user.is_staff:
        return HttpResponseForbidden("No tienes permisos para eliminar publicaciones.")

    juego = get_object_or_404(Videojuego, id=id)

    if request.method == "POST":
        if juego.imagen:
            juego.imagen.delete(save=False)
        juego.delete()
        messages.warning(request, f"{juego.nombre} ha sido eliminado del catalogo.")
        return redirect("listado_videojuegos")

    return render(request, "blog/eliminar.html", {"juego": juego})


def diagnostico_rawg(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return HttpResponseForbidden("No tienes permisos para ver este diagnostico.")

    consulta = request.GET.get("q", "Elden Ring").strip()
    api_key = getattr(settings, "RAWG_API_KEY", "") or ""
    resultado = buscar_portada_videojuego(consulta) if api_key else None

    if api_key:
        api_key_masked = f"{api_key[:4]}...{api_key[-4:]}" if len(api_key) >= 8 else "***"
    else:
        api_key_masked = ""

    return JsonResponse(
        {
            "query": consulta,
            "has_rawg_api_key": bool(api_key),
            "rawg_api_key_masked": api_key_masked,
            "resultado": resultado,
        }
    )


def api_videojuegos(request):
    """API para obtener todos los videojuegos en JSON."""
    juegos = Videojuego.objects.all().order_by("-created_at")
    data = [
        {
            "id": juego.id,
            "nombre": juego.nombre,
            "descripcion": juego.descripcion,
            "genero": juego.get_genero_display(),
            "desarrollador": juego.desarrollador,
            "fecha_lanzamiento": juego.fecha_lanzamiento.isoformat(),
            "portada_url": juego.get_imagen_url,
            "created_at": juego.created_at.isoformat(),
            "updated_at": juego.updated_at.isoformat(),
        }
        for juego in juegos
    ]
    return JsonResponse(data, safe=False)


def api_buscar_portadas(request):
    consulta = request.GET.get("q", "").strip()
    if not consulta:
        return JsonResponse({"error": "Debes enviar el parametro q."}, status=400)

    juegos = Videojuego.objects.filter(nombre__icontains=consulta).order_by("nombre")
    data = [
        {
            "id": juego.id,
            "nombre": juego.nombre,
            "portada_url": juego.get_imagen_url,
        }
        for juego in juegos
    ]

    return JsonResponse(
        {
            "query": consulta,
            "total": len(data),
            "resultados": data,
        }
    )


def api_posts_recientes(request):
    """API para obtener los juegos mas recientes."""
    limite_raw = request.GET.get("limit", "5")
    try:
        limite = max(1, min(int(limite_raw), 20))
    except ValueError:
        return JsonResponse({"error": "Limit debe ser un numero entre 1 y 20"}, status=400)

    juegos = Videojuego.objects.all().order_by("-created_at")[:limite]
    data = [{"id": j.id, "nombre": j.nombre, "created_at": j.created_at.isoformat()} for j in juegos]
    return JsonResponse({"total": len(data), "resultados": data})
