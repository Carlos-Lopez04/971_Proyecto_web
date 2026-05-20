from urllib.parse import urlencode

import requests
from django.conf import settings


RAWG_GAMES_URL = "https://api.rawg.io/api/games"


def _normalizar(texto):
    return " ".join((texto or "").strip().lower().split())


def _extraer_portada(resultado):
    portada = resultado.get("background_image")
    if portada:
        return portada

    screenshots = resultado.get("short_screenshots") or []
    if screenshots:
        return screenshots[0].get("image")

    return None


def _buscar_en_rawg(nombre, search_precise):
    api_key = getattr(settings, "RAWG_API_KEY", "")
    if not api_key or not nombre:
        return []

    params = {
        "key": api_key,
        "search": nombre,
        "search_precise": str(search_precise).lower(),
        "page_size": 5,
    }

    try:
        response = requests.get(
            f"{RAWG_GAMES_URL}?{urlencode(params)}",
            timeout=8,
        )
        response.raise_for_status()
    except requests.RequestException:
        return []

    payload = response.json()
    return payload.get("results") or []


def buscar_portada_videojuego(nombre):
    """
    Busca una portada en RAWG usando el nombre del videojuego.
    Retorna un diccionario con la URL de la portada o None si no encuentra nada.
    """
    nombre_normalizado = _normalizar(nombre)
    if not nombre_normalizado:
        return None

    resultados = _buscar_en_rawg(nombre, search_precise=True)
    if not resultados:
        resultados = _buscar_en_rawg(nombre, search_precise=False)

    if not resultados:
        return None

    exacto = None
    con_portada = None

    for resultado in resultados:
        portada_url = _extraer_portada(resultado)
        if not portada_url:
            continue

        candidato = {
            "portada_url": portada_url,
            "rawg_id": resultado.get("id"),
            "slug": resultado.get("slug"),
            "nombre": resultado.get("name"),
        }

        nombre_resultado = _normalizar(resultado.get("name"))
        if nombre_resultado == nombre_normalizado:
            exacto = candidato
            break

        if con_portada is None:
            con_portada = candidato

    return exacto or con_portada
