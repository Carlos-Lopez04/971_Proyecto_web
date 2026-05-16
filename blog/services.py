from urllib.parse import urlencode

import requests
from django.conf import settings


RAWG_GAMES_URL = "https://api.rawg.io/api/games"


def buscar_portada_videojuego(nombre):
    """
    Busca una portada en RAWG usando el nombre del videojuego.
    Retorna un diccionario con la URL de la portada o None si no encuentra nada.
    """
    api_key = getattr(settings, "RAWG_API_KEY", "")
    if not api_key or not nombre:
        return None

    params = {
        "key": api_key,
        "search": nombre,
        "search_precise": "true",
        "page_size": 1,
    }

    try:
        response = requests.get(
            f"{RAWG_GAMES_URL}?{urlencode(params)}",
            timeout=5,
        )
        response.raise_for_status()
    except requests.RequestException:
        return None

    payload = response.json()
    resultados = payload.get("results") or []
    if not resultados:
        return None

    juego = resultados[0]
    portada_url = juego.get("background_image")
    if not portada_url:
        return None

    return {
        "portada_url": portada_url,
        "rawg_id": juego.get("id"),
        "slug": juego.get("slug"),
        "nombre": juego.get("name"),
    }
