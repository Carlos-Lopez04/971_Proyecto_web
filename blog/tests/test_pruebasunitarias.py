import pytest
from django.urls import reverse
from datetime import date
from unittest.mock import patch
from blog.models import Videojuego

@pytest.mark.django_db
def test_crear_videojuego_nombre_vacio(client):
    url = reverse("crear_videojuego")
    response = client.post(url, {
        "nombre": "",
        "descripcion": "Juego de prueba",
        "genero": "ACC",
        "desarrollador": "Test",
        "fecha_lanzamiento": date.today()
    })
    # No debe crear el registro
    assert Videojuego.objects.count() == 0

@pytest.mark.django_db
def test_api_videojuegos_returns_list(client):
    Videojuego.objects.create(
        nombre="Zelda",
        descripcion="Aventura",
        genero="AVT",
        desarrollador="Nintendo",
        fecha_lanzamiento=date(2023, 5, 12),
        imagen_url_externa="https://example.com/zelda.jpg",
    )
    url = reverse("api_videojuegos")
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["nombre"] == "Zelda"
    assert data[0]["portada_url"] == "https://example.com/zelda.jpg"
    assert data[0]["created_at"] is not None
    assert data[0]["updated_at"] is not None


@pytest.mark.django_db
def test_api_buscar_portadas_filtra_por_nombre(client):
    Videojuego.objects.create(
        nombre="The Legend of Zelda",
        descripcion="Aventura",
        genero="AVT",
        desarrollador="Nintendo",
        fecha_lanzamiento=date(2023, 5, 12),
        imagen_url_externa="https://example.com/zelda.jpg",
    )
    Videojuego.objects.create(
        nombre="Halo Infinite",
        descripcion="Shooter",
        genero="ACC",
        desarrollador="Xbox Game Studios",
        fecha_lanzamiento=date(2021, 12, 8),
        imagen_url_externa="https://example.com/halo.jpg",
    )

    url = reverse("api_buscar_portadas")
    response = client.get(url, {"q": "zelda"})

    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "zelda"
    assert data["total"] == 1
    assert data["resultados"][0]["nombre"] == "The Legend of Zelda"
    assert data["resultados"][0]["portada_url"] == "https://example.com/zelda.jpg"


@pytest.mark.django_db
def test_api_buscar_portadas_requires_query(client):
    url = reverse("api_buscar_portadas")
    response = client.get(url)

    assert response.status_code == 400
    assert "error" in response.json()


@pytest.mark.django_db
def test_api_posts_recientes_returns_results(client):
    Videojuego.objects.create(
        nombre="Hades",
        descripcion="Roguelike",
        genero="ACC",
        desarrollador="Supergiant Games",
        fecha_lanzamiento=date(2020, 9, 17),
    )

    response = client.get(reverse("api_posts_recientes"))

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["resultados"][0]["nombre"] == "Hades"


@pytest.mark.django_db
@patch("blog.views.buscar_portada_videojuego")
def test_crear_videojuego_liga_portada_automatica(mock_buscar_portada, client):
    mock_buscar_portada.return_value = {
        "portada_url": "https://images.example.com/zelda-cover.jpg",
        "rawg_id": 1,
        "slug": "the-legend-of-zelda",
        "nombre": "The Legend of Zelda",
    }

    response = client.post(
        reverse("crear_videojuego"),
        {
            "nombre": "The Legend of Zelda",
            "descripcion": "Aventura",
            "genero": "AVT",
            "desarrollador": "Nintendo",
            "fecha_lanzamiento": date(2023, 5, 12),
        },
    )

    assert response.status_code == 302
    juego = Videojuego.objects.get(nombre="The Legend of Zelda")
    assert juego.imagen_url_externa == "https://images.example.com/zelda-cover.jpg"
