from django.test import TestCase
from club.models import Reserva
from jugadores.models import Jugador


class ReservaLogicTest(TestCase):
    def setUp(self):
        self.jugador = Jugador.objects.create(
            nombre="E",
            apellido="E",
            email="e@e.com",
            telefono="5",
            nivel="intermedio",
            genero="hombre",
            disponibilidad={"lunes": ["18:00"]},
        )
        Reserva.objects.create(jugador=self.jugador, dia="2025-06-23", hora="19:00")

    # def test_no_solapamiento(self):
    #     result = validar_solapamiento(self.jugador, "2025-06-23", "20:00")
    #     self.assertTrue(result)

    # def test_solapamiento(self):
    #     result = validar_solapamiento(self.jugador, "2025-06-23", "19:00")
    #     self.assertFalse(result)
