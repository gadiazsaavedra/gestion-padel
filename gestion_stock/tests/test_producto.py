from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from gestion_stock.models import Producto, CategoriaProducto


class ProductoStockTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin_testuser", password="testpass2025", is_staff=True
        )
        self.categoria = CategoriaProducto.objects.create(
            nombre="Palas", descripcion="Palas de pádel"
        )
        self.producto = Producto.objects.create(
            nombre="Pala Pro",
            descripcion="Pala profesional",
            categoria=self.categoria,
            precio_venta=10000,
            precio_costo=7000,
            stock_actual=10,
            stock_minimo=2,
            activo=True,
        )

    def test_producto_list_view_staff(self):
        self.client.login(username="admin_testuser", password="testpass2025")
        response = self.client.get(reverse("gestion_stock:producto_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pala Pro")

    def test_producto_create_view(self):
        self.client.login(username="admin_testuser", password="testpass2025")
        response = self.client.post(
            reverse("gestion_stock:producto_create"),
            {
                "nombre": "Pala Test",
                "descripcion": "Test Desc",
                "categoria": self.categoria.id,
                "precio_venta": 5000,
                "precio_costo": 3000,
                "stock_actual": 5,
                "stock_minimo": 1,
                "activo": True,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Producto.objects.filter(nombre="Pala Test").exists())

    def test_producto_list_view_no_staff(self):
        user = User.objects.create_user(
            username="user_test", password="testpass2025", is_staff=False
        )
        self.client.login(username="user_test", password="testpass2025")
        response = self.client.get(reverse("gestion_stock:producto_list"))
        self.assertEqual(response.status_code, 403)
