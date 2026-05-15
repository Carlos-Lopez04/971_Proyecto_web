import pytest
from django.urls import reverse
from datetime import date
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
        fecha_lanzamiento=date(2023, 5, 12)
    )
    url = reverse("api_videojuegos")
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["nombre"] == "Zelda"