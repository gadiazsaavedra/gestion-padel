from django.test import TestCase
from club.forms import ReservaForm
from club.models import Grupo, Jugador
from django.utils import timezone


class ReservaFormTest(TestCase):
    def setUp(self):
        self.jugador = Jugador.objects.create(
            nombre="Test",
            apellido="User",
            email="test@user.com",
            telefono="111111111",
            nivel="intermedio",
            genero="hombre",
            disponibilidad={"lunes": ["18:00"]},
        )
        self.grupo = Grupo.objects.create(
            nivel="intermedio",
            genero="hombre",
            disponibilidad={"lunes": ["18:00"]},
        )
        self.grupo.jugadores.add(self.jugador)

    def test_form_valido(self):
        data = {
            "grupo": self.grupo.id,
            "fecha": timezone.now().date(),
            "hora": timezone.now().time(),
            "estado": "disponible",
            "pago_total": 0,
            "pago_parcial": 0,
            "metodo_pago": "",
        }
        form = ReservaForm(data=data)
        self.assertTrue(form.is_valid())

    def test_form_invalido(self):
        data = {"grupo": "", "fecha": "", "hora": ""}
        form = ReservaForm(data=data)
        self.assertFalse(form.is_valid())
