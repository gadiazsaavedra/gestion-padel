from django.test import TestCase, Client
from django.urls import reverse
from club.models import FAQ, Jugador, Torneo, PartidoTorneo, Ranking, Reserva
from django.contrib.auth.models import User
from bar.models import Producto, Venta
from datetime import date, timedelta


class FAQViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.faq = FAQ.objects.create(
            pregunta="¿Cómo pagar?", respuesta="En línea o en el club."
        )

    def test_lista_faq(self):
        response = self.client.get(reverse("club:faq_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "¿Cómo pagar?")


class DashboardViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="admin", password="test", is_staff=True
        )
        self.jugador = Jugador.objects.create(
            nombre="Juan",
            apellido="Pérez",
            email="jp@test.com",
            telefono="123",
            nivel="novato",
            genero="hombre",
            user=self.user,
        )
        self.torneo = Torneo.objects.create(
            nombre="Torneo Test",
            fecha_inicio=date.today(),
            fecha_fin=date.today() + timedelta(days=1),
        )
        self.torneo.jugadores.add(self.jugador)
        self.ranking = Ranking.objects.create(
            torneo=self.torneo, jugador=self.jugador, puntos=10
        )
        self.reserva = Reserva.objects.create(
            jugador=self.jugador, fecha=date.today(), hora="10:00", estado="pagada"
        )
        self.venta = Venta.objects.create(
            fecha=date.today(),
            producto=Producto.objects.create(
                nombre="Bebida",
                precio_venta=100,
                precio_costo=50,
                stock=10,
                stock_minimo=1,
                categoria_id=1,
            ),
            cantidad=1,
            total=100,
        )
        self.partido = PartidoTorneo.objects.create(
            torneo=self.torneo,
            jugador1=self.jugador,
            jugador2=self.jugador,
            fecha=date.today(),
        )

    def test_dashboard_status(self):
        self.client.login(username="admin", password="test")
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Panel de Métricas")

    def test_dashboard_filtros(self):
        self.client.login(username="admin", password="test")
        response = self.client.get(
            reverse("dashboard"),
            {
                "fecha_inicio": date.today().isoformat(),
                "fecha_fin": date.today().isoformat(),
                "torneo": self.torneo.id,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.torneo.nombre)


class TorneosViewsTest(TestCase):
    def setUp(self):
        self.torneo = Torneo.objects.create(
            nombre="Torneo Test",
            fecha_inicio=date.today(),
            fecha_fin=date.today() + timedelta(days=1),
        )

    def test_torneos_list(self):
        response = self.client.get(reverse("club:torneos_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Torneo Test")

    def test_torneo_detalle(self):
        response = self.client.get(
            reverse("club:torneo_detalle", args=[self.torneo.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.torneo.nombre)


class RankingGeneralViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user1", password="test")
        self.jugador = Jugador.objects.create(
            nombre="Ana",
            apellido="López",
            email="al@test.com",
            telefono="321",
            nivel="novato",
            genero="mujer",
            user=self.user,
        )
        self.torneo = Torneo.objects.create(
            nombre="Torneo Ranking",
            fecha_inicio=date.today(),
            fecha_fin=date.today() + timedelta(days=1),
        )
        Ranking.objects.create(torneo=self.torneo, jugador=self.jugador, puntos=20)

    def test_ranking_general(self):
        response = self.client.get(reverse("club:ranking_general"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ana")
