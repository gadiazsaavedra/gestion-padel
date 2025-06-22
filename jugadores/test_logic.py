from django.test import TestCase
from club.models import Jugador, DisponibilidadJugador
from jugadores.utils import sugerir_grupos


class EmparejamientoLogicTest(TestCase):
    def setUp(self):
        self.j1 = Jugador.objects.create(
            nombre="A",
            apellido="A",
            email="a@a.com",
            telefono="1",
            nivel="intermedio",
            genero="hombre",
        )
        self.j2 = Jugador.objects.create(
            nombre="B",
            apellido="B",
            email="b@b.com",
            telefono="2",
            nivel="intermedio",
            genero="hombre",
        )
        self.j3 = Jugador.objects.create(
            nombre="C",
            apellido="C",
            email="c@c.com",
            telefono="3",
            nivel="intermedio",
            genero="hombre",
        )
        self.j4 = Jugador.objects.create(
            nombre="D",
            apellido="D",
            email="d@d.com",
            telefono="4",
            nivel="intermedio",
            genero="hombre",
        )
        for jugador in [self.j1, self.j2, self.j3, self.j4]:
            DisponibilidadJugador.objects.create(
                jugador=jugador,
                dia="lunes",
                hora_inicio="18:00",
                hora_fin="19:30",
                nivel="intermedio",
                preferencia_genero="hombre",
            )

    def test_sugerir_grupo(self):
        grupos = sugerir_grupos()
        self.assertTrue(
            any(
                set([self.j1, self.j2, self.j3, self.j4]).issubset(
                    set(g.jugadores().all())
                )
                for g in grupos
            )
        )
