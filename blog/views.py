from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import Videojuego
from .services import buscar_portada_videojuego


def _build_portada_url(request, juego):
    portada = juego.portada_url
    if portada.startswith("http://") or portada.startswith("https://"):
        return portada
    return request.build_absolute_uri(portada)


def _serialize_videojuego(request, juego):
    return {
        "id": juego.id,
        "nombre": juego.nombre,
        "descripcion": juego.descripcion,
        "genero": juego.genero,
        "genero_nombre": juego.get_genero_display(),
        "desarrollador": juego.desarrollador,
        "fecha_lanzamiento": juego.fecha_lanzamiento.isoformat(),
        "created_at": juego.created_at.isoformat(),
        "updated_at": juego.updated_at.isoformat(),
        "portada_url": _build_portada_url(request, juego),
        "tiene_imagen_local": bool(juego.imagen),
        "imagen_url_externa": juego.imagen_url_externa,
    }


def listado_videojuegos(request):
    genero_filtro = request.GET.get("genero")
    juegos = Videojuego.objects.all().order_by("-fecha_lanzamiento")

    if genero_filtro:
        juegos = juegos.filter(genero=genero_filtro)

    return render(
        request,
        "blog/listado.html",
        {"juegos": juegos, "generos": Videojuego.GENEROS},
    )


def crear_videojuego(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        descripcion = request.POST.get("descripcion", "").strip()
        genero = request.POST.get("genero", "ACC")
        desarrollador = request.POST.get("desarrollador", "").strip()
        fecha_lanzamiento = request.POST.get("fecha_lanzamiento")
        imagen_url_externa = (
            request.POST.get("imagen_url_externa")
            or request.POST.get("imagen_url")
            or ""
        ).strip()
        imagen = request.FILES.get("imagen") or request.FILES.get("imagen_local")

        if not nombre:
            return render(
                request,
                "blog/crear.html",
                {
                    "error": "El nombre del videojuego no puede estar vacio",
                    "generos": Videojuego.GENEROS,
                },
            )

        if not imagen and not imagen_url_externa:
            portada = buscar_portada_videojuego(nombre)
            if portada:
                imagen_url_externa = portada["portada_url"]

        Videojuego.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            genero=genero,
            desarrollador=desarrollador,
            fecha_lanzamiento=fecha_lanzamiento,
            imagen=imagen,
            imagen_url_externa=imagen_url_externa or None,
        )
        return redirect("listado_videojuegos")

    return render(request, "blog/crear.html", {"generos": Videojuego.GENEROS})


def api_videojuegos(request):
    juegos = Videojuego.objects.all().order_by("-fecha_lanzamiento")
    data = [_serialize_videojuego(request, juego) for juego in juegos]
    return JsonResponse(data, safe=False)


def api_videojuego_detalle(request, id):
    juego = get_object_or_404(Videojuego, id=id)
    return JsonResponse(_serialize_videojuego(request, juego))


def api_posts_recientes(request):
    limite_raw = request.GET.get("limit", "5").strip()

    try:
        limite = max(1, min(int(limite_raw), 20))
    except ValueError:
        return JsonResponse(
            {"error": "El parametro limit debe ser un numero entre 1 y 20."},
            status=400,
        )

    juegos = Videojuego.objects.all().order_by("-created_at")[:limite]
    resultados = [_serialize_videojuego(request, juego) for juego in juegos]
    return JsonResponse({"total": len(resultados), "resultados": resultados})


def api_buscar_portadas(request):
    consulta = request.GET.get("q", "").strip()
    genero = request.GET.get("genero", "").strip()
    limite_raw = request.GET.get("limit", "10").strip()

    if not consulta:
        return JsonResponse(
            {"error": "Debes enviar el parametro q con el nombre del videojuego."},
            status=400,
        )

    try:
        limite = max(1, min(int(limite_raw), 20))
    except ValueError:
        return JsonResponse(
            {"error": "El parametro limit debe ser un numero entre 1 y 20."},
            status=400,
        )

    juegos = Videojuego.objects.filter(nombre__icontains=consulta).order_by(
        "-fecha_lanzamiento"
    )
    if genero:
        juegos = juegos.filter(genero=genero)

    resultados = [_serialize_videojuego(request, juego) for juego in juegos[:limite]]
    return JsonResponse(
        {
            "query": consulta,
            "genero": genero or None,
            "total": len(resultados),
            "resultados": resultados,
        }
    )
