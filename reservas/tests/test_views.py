from django.test import TestCase, Client
from django.urls import reverse
from club.models import Reserva, Grupo, Jugador
from django.utils import timezone


class ReservaViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.jugador = Jugador.objects.create(
            nombre="Laura",
            apellido="Martínez",
            email="laura@test.com",
            telefono="444555666",
            nivel="intermedio",
            genero="mujer",
        )
        self.grupo = Grupo.objects.create(
            nivel="intermedio",
            genero="mujer",
            disponibilidad={"martes": ["19:00"]},
        )
        self.grupo.jugadores.add(self.jugador)
        self.reserva = Reserva.objects.create(
            grupo=self.grupo,
            fecha=timezone.now().date(),
            hora=timezone.now().time(),
        )

    def test_lista_reservas(self):
        response = self.client.get(reverse("reservas:grilla"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Laura")

    def test_reserva_create_view_get(self):
        response = self.client.get(
            reverse("reservas:crear")
        )  # Ajusta el nombre de la url
        self.assertEqual(response.status_code, 200)

    def test_reserva_create_view_post(self):
        data = {
            "grupo": self.grupo.id,
            "fecha": "2025-06-21",
            "hora": "19:00",
        }
        response = self.client.post(reverse("reservas:crear"), data)
        self.assertIn(response.status_code, [200, 302])  # Ajusta según tu lógica

    def test_reserva_create_view_post_invalido(self):
        data = {
            "grupo": "",  # Falta grupo
            "fecha": "",
            "hora": "",
        }
        response = self.client.post(reverse("reservas:crear"), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "error")  # Ajusta según tu template

    def test_reserva_update_view(self):
        response = self.client.post(
            reverse("reservas:editar", args=[self.reserva.id]),
            {"hora": "20:00"},
        )
        self.assertIn(response.status_code, [200, 302])

    def test_reserva_delete_view(self):
        response = self.client.post(reverse("reservas:borrar", args=[self.reserva.id]))
        self.assertIn(response.status_code, [200, 302])

    def test_reserva_detail_view(self):
        response = self.client.get(reverse("reservas:detalle", args=[self.reserva.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Laura")

    def test_reserva_create_view_no_login(self):
        self.client.logout()
        response = self.client.get(reverse("reservas:crear"))
        self.assertNotEqual(response.status_code, 200)

    def test_reserva_update_view_no_perm(self):
        self.client.logout()
        response = self.client.post(
            reverse("reservas:editar", args=[self.reserva.id]), {"hora": "21:00"}
        )
        self.assertNotEqual(response.status_code, 200)

    def test_reserva_delete_view_no_perm(self):
        self.client.logout()
        response = self.client.post(reverse("reservas:borrar", args=[self.reserva.id]))
        self.assertNotEqual(response.status_code, 200)
