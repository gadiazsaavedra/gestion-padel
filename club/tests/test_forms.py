from django.test import TestCase
from club.forms import FAQForm


class FAQFormTest(TestCase):
    def test_form_valido(self):
        data = {"pregunta": "¿Cómo me registro?", "respuesta": "Desde la web."}
        form = FAQForm(data=data)
        self.assertTrue(form.is_valid())

    def test_form_invalido(self):
        data = {"pregunta": "", "respuesta": ""}
        form = FAQForm(data=data)
        self.assertFalse(form.is_valid())
