from datetime import date
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from blog.models import Videojuego


class VideojuegoApiTests(TestCase):
    def test_api_videojuegos_incluye_portada(self):
        Videojuego.objects.create(
            nombre="Zelda",
            descripcion="Aventura",
            genero="AVT",
            desarrollador="Nintendo",
            fecha_lanzamiento=date(2023, 5, 12),
            imagen_url_externa="https://example.com/zelda.jpg",
        )

        response = self.client.get(reverse("api_videojuegos"))

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["portada_url"], "https://example.com/zelda.jpg")
        self.assertIn("created_at", data[0])
        self.assertIn("updated_at", data[0])
        self.assertIsNotNone(data[0]["created_at"])
        self.assertIsNotNone(data[0]["updated_at"])

    def test_api_buscar_portadas_filtra_por_nombre(self):
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

        response = self.client.get(reverse("api_buscar_portadas"), {"q": "zelda"})

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total"], 1)
        self.assertEqual(data["resultados"][0]["nombre"], "The Legend of Zelda")

    def test_api_buscar_portadas_requiere_query(self):
        response = self.client.get(reverse("api_buscar_portadas"))

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    @patch("blog.views.buscar_portada_videojuego")
    def test_crear_videojuego_asigna_portada_automatica(self, mock_buscar_portada):
        mock_buscar_portada.return_value = {
            "portada_url": "https://images.example.com/zelda-cover.jpg",
            "rawg_id": 1,
            "slug": "the-legend-of-zelda",
            "nombre": "The Legend of Zelda",
        }

        response = self.client.post(
            reverse("crear_videojuego"),
            {
                "nombre": "The Legend of Zelda",
                "descripcion": "Aventura",
                "genero": "AVT",
                "desarrollador": "Nintendo",
                "fecha_lanzamiento": date(2023, 5, 12),
            },
        )

        self.assertEqual(response.status_code, 302)
        juego = Videojuego.objects.get(nombre="The Legend of Zelda")
        self.assertEqual(
            juego.imagen_url_externa,
            "https://images.example.com/zelda-cover.jpg",
        )

    @patch("blog.views.buscar_portada_videojuego")
    def test_crear_videojuego_no_pisa_url_manual(self, mock_buscar_portada):
        response = self.client.post(
            reverse("crear_videojuego"),
            {
                "nombre": "Halo Infinite",
                "descripcion": "Shooter",
                "genero": "ACC",
                "desarrollador": "Xbox Game Studios",
                "fecha_lanzamiento": date(2021, 12, 8),
                "imagen_url_externa": "https://manual.example.com/halo.jpg",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(mock_buscar_portada.called)
        juego = Videojuego.objects.get(nombre="Halo Infinite")
        self.assertEqual(juego.imagen_url_externa, "https://manual.example.com/halo.jpg")

    def test_model_guarda_fechas_automaticas(self):
        juego = Videojuego.objects.create(
            nombre="Chrono Trigger",
            descripcion="RPG clasico",
            genero="RPG",
            desarrollador="Square",
            fecha_lanzamiento=date(1995, 3, 11),
        )

        self.assertIsNotNone(juego.created_at)
        self.assertIsNotNone(juego.updated_at)

    def test_api_posts_recientes_ordena_por_fecha_publicacion(self):
        juego_viejo = Videojuego.objects.create(
            nombre="Metroid Prime",
            descripcion="Accion",
            genero="ACC",
            desarrollador="Nintendo",
            fecha_lanzamiento=date(2002, 11, 17),
        )
        juego_nuevo = Videojuego.objects.create(
            nombre="Elden Ring",
            descripcion="RPG",
            genero="RPG",
            desarrollador="FromSoftware",
            fecha_lanzamiento=date(2022, 2, 25),
        )
        Videojuego.objects.filter(id=juego_viejo.id).update(
            created_at=timezone.now() - timezone.timedelta(days=1)
        )
        Videojuego.objects.filter(id=juego_nuevo.id).update(created_at=timezone.now())

        response = self.client.get(reverse("api_posts_recientes"), {"limit": 1})

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total"], 1)
        self.assertEqual(data["resultados"][0]["nombre"], "Elden Ring")

    def test_listado_muestra_fecha_publicacion(self):
        Videojuego.objects.create(
            nombre="Hades",
            descripcion="Roguelike",
            genero="ACC",
            desarrollador="Supergiant Games",
            fecha_lanzamiento=date(2020, 9, 17),
        )

        response = self.client.get(reverse("listado_videojuegos"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Publicado:")
