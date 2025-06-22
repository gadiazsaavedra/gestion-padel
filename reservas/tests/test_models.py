from django.test import TestCase
from club.models import Reserva, Grupo
from jugadores.models import Jugador
from django.utils import timezone


class ReservaModelTest(TestCase):
    def test_creacion_reserva(self):
        jugador = Jugador.objects.create(
            nombre="Pedro",
            apellido="López",
            email="pedro@test.com",
            telefono="111222333",
            nivel="intermedio",
            genero="hombre",
            disponibilidad={"lunes": ["18:00"]},
        )
        grupo = Grupo.objects.create(
            nivel="intermedio",
            genero="hombre",
            disponibilidad={"lunes": ["18:00"]},
        )
        grupo.jugadores.add(jugador)
        reserva = Reserva.objects.create(
            grupo=grupo, fecha=timezone.now().date(), hora=timezone.now().time()
        )
        self.assertEqual(reserva.grupo, grupo)
        self.assertEqual(reserva.grupo.jugadores.first().nombre, "Pedro")
