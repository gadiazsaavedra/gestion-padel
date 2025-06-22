from django.test import TestCase, Client
from django.urls import reverse
from bar.models import Producto
from django.contrib.auth.models import User


class ProductoViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="admin", password="test", is_staff=True
        )
        self.producto = Producto.objects.create(nombre="Café", precio=700, stock=10)

    def test_lista_productos(self):
        self.client.login(username="admin", password="test")
        response = self.client.get(reverse("bar:productos_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Café")

    def test_producto_detail_view(self):
        self.client.login(username="admin", password="test")
        response = self.client.get(
            reverse("bar:producto_detail", args=[self.producto.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Café")

    def test_producto_update_view(self):
        self.client.login(username="admin", password="test")
        response = self.client.post(
            reverse("bar:producto_update", args=[self.producto.id]),
            {
                "nombre": "Café Editado",
                "precio": 800,
                "stock": 5,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.nombre, "Café Editado")

    def test_producto_delete_view(self):
        self.client.login(username="admin", password="test")
        response = self.client.post(
            reverse("bar:producto_delete", args=[self.producto.id])
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Producto.objects.filter(id=self.producto.id).exists())

    def test_producto_create_view_no_login(self):
        response = self.client.get(reverse("bar:producto_create"))
        self.assertNotEqual(response.status_code, 200)

    def test_producto_update_view_no_perm(self):
        user = User.objects.create_user(
            username="user_test2", password="testpass2025", is_staff=False
        )
        self.client.login(username="user_test2", password="testpass2025")
        response = self.client.get(
            reverse("bar:producto_update", args=[self.producto.id])
        )
        self.assertNotEqual(response.status_code, 200)

    def test_producto_delete_view_no_perm(self):
        user = User.objects.create_user(
            username="user_test3", password="testpass2025", is_staff=False
        )
        self.client.login(username="user_test3", password="testpass2025")
        response = self.client.post(
            reverse("bar:producto_delete", args=[self.producto.id])
        )
        self.assertNotEqual(response.status_code, 302)
