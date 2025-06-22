from django.test import TestCase, Client
from django.urls import reverse
from club.models import Jugador


class JugadorViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.jugador = Jugador.objects.create(
            nombre="Ana",
            apellido="García",
            email="ana@test.com",
            telefono="987654321",
            nivel="intermedio",
            genero="mujer",
        )

    def test_lista_jugadores(self):
        response = self.client.get(reverse("jugadores:list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ana")
