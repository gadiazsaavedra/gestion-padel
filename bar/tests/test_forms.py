from django.test import TestCase
from bar.forms import ProductoForm


class ProductoFormTest(TestCase):
    def test_form_valido(self):
        data = {
            "nombre": "Galletitas",
            "categoria": "bar",
            "stock": 15,
            "precio": 300,
        }
        form = ProductoForm(data=data)
        self.assertTrue(form.is_valid())

    def test_form_invalido(self):
        data = {"nombre": "", "precio": "", "stock": "", "categoria": ""}
        form = ProductoForm(data=data)
        self.assertFalse(form.is_valid())
