from django.test import TestCase
from club.models import Jugador


class JugadorModelTest(TestCase):
    def test_creacion_jugador(self):
        jugador = Jugador.objects.create(
            nombre="Juan",
            apellido="Pérez",
            email="juan@test.com",
            telefono="123456789",
            nivel="intermedio",
            genero="hombre",
        )
        self.assertEqual(jugador.nombre, "Juan")
        self.assertEqual(jugador.apellido, "Pérez")
        self.assertEqual(jugador.email, "juan@test.com")
