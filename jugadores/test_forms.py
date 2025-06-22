from django.test import TestCase
from club.forms import JugadorForm


class JugadorFormTest(TestCase):
    def test_form_valido(self):
        data = {
            "nombre": "Carlos",
            "apellido": "Sánchez",
            "email": "carlos@test.com",
            "telefono": "123123123",
            "nivel": "intermedio",
            "genero": "hombre",
        }
        form = JugadorForm(data=data)
        self.assertTrue(form.is_valid())

    def test_form_invalido(self):
        data = {
            "nombre": "",
            "apellido": "",
            "email": "noemail",
            "telefono": "",
            "nivel": "",
            "genero": "",
        }
        form = JugadorForm(data=data)
        self.assertFalse(form.is_valid())
