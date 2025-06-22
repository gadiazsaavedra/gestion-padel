from django.test import TestCase
from club.models import FAQ


class FAQModelTest(TestCase):
    def test_creacion_faq(self):
        faq = FAQ.objects.create(
            pregunta="¿Cómo reservar?", respuesta="Desde la web o app."
        )
        self.assertEqual(faq.pregunta, "¿Cómo reservar?")
        self.assertEqual(faq.respuesta, "Desde la web o app.")
