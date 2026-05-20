from datetime import date
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model

from blog.models import Videojuego


class VideojuegoApiTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()

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
    def test_crear_videojuego_guarda_sin_portada_si_api_no_encuentra(self, mock_buscar_portada):
        mock_buscar_portada.return_value = None

        response = self.client.post(
            reverse("crear_videojuego"),
            {
                "nombre": "Halo Infinite",
                "descripcion": "Shooter",
                "genero": "ACC",
                "desarrollador": "Xbox Game Studios",
                "fecha_lanzamiento": date(2021, 12, 8),
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(mock_buscar_portada.called)
        juego = Videojuego.objects.get(nombre="Halo Infinite")
        self.assertIsNone(juego.imagen_url_externa)

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

    def test_formulario_crear_no_muestra_campos_manuales_de_imagen(self):
        response = self.client.get(reverse("crear_videojuego"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'type="file"')
        self.assertNotContains(response, "imagen_url_externa")
        self.assertContains(response, "La portada se buscara automaticamente")

    def test_admin_puede_eliminar_videojuego(self):
        admin = self.user_model.objects.create_user(
            username="admin",
            password="secret123",
            is_staff=True,
        )
        juego = Videojuego.objects.create(
            nombre="Juego de prueba",
            descripcion="Descripcion",
            genero="ACC",
            desarrollador="Dev",
            fecha_lanzamiento=date(2024, 1, 1),
        )

        self.client.force_login(admin)
        response = self.client.post(reverse("eliminar_videojuego", args=[juego.id]))

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Videojuego.objects.filter(id=juego.id).exists())

    def test_no_admin_no_puede_eliminar_videojuego(self):
        user = self.user_model.objects.create_user(
            username="user",
            password="secret123",
        )
        juego = Videojuego.objects.create(
            nombre="Juego protegido",
            descripcion="Descripcion",
            genero="ACC",
            desarrollador="Dev",
            fecha_lanzamiento=date(2024, 1, 1),
        )

        self.client.force_login(user)
        response = self.client.post(reverse("eliminar_videojuego", args=[juego.id]))

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Videojuego.objects.filter(id=juego.id).exists())

    def test_listado_muestra_boton_eliminar_solo_a_admin(self):
        admin = self.user_model.objects.create_user(
            username="admin2",
            password="secret123",
            is_staff=True,
        )
        user = self.user_model.objects.create_user(
            username="user2",
            password="secret123",
        )
        Videojuego.objects.create(
            nombre="Control",
            descripcion="Accion",
            genero="ACC",
            desarrollador="Remedy",
            fecha_lanzamiento=date(2019, 8, 27),
        )

        self.client.force_login(admin)
        response_admin = self.client.get(reverse("listado_videojuegos"))
        self.assertContains(response_admin, "Eliminar")

        self.client.force_login(user)
        response_user = self.client.get(reverse("listado_videojuegos"))
        self.assertNotContains(response_user, "Eliminar")

    @patch("blog.views.buscar_portada_videojuego")
    @patch("blog.views.settings")
    def test_admin_puede_ver_diagnostico_rawg(self, mock_settings, mock_buscar_portada):
        admin = self.user_model.objects.create_user(
            username="admin3",
            password="secret123",
            is_staff=True,
        )
        mock_settings.RAWG_API_KEY = "abcd1234efgh5678"
        mock_buscar_portada.return_value = {
            "portada_url": "https://images.example.com/elden-ring.jpg",
            "rawg_id": 42,
            "slug": "elden-ring",
            "nombre": "Elden Ring",
        }

        self.client.force_login(admin)
        response = self.client.get(reverse("diagnostico_rawg"), {"q": "Elden Ring"})

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["has_rawg_api_key"])
        self.assertEqual(data["rawg_api_key_masked"], "abcd...5678")
        self.assertEqual(data["resultado"]["nombre"], "Elden Ring")

    def test_no_admin_no_puede_ver_diagnostico_rawg(self):
        user = self.user_model.objects.create_user(
            username="user3",
            password="secret123",
        )

        self.client.force_login(user)
        response = self.client.get(reverse("diagnostico_rawg"))

        self.assertEqual(response.status_code, 403)
