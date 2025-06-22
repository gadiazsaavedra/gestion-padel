from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from gestion_stock.models import Producto, CategoriaProducto


class ProductoStockTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user(
            username="admin_testuser", password="testpass2025", is_staff=True
        )
        cls.categoria = CategoriaProducto.objects.create(
            nombre="Palas", descripcion="Palas de pádel"
        )
        cls.producto = Producto.objects.create(
            nombre="Pala Pro",
            descripcion="Pala profesional",
            categoria=cls.categoria,
            precio_venta=10000,
            precio_costo=7000,
            stock_actual=10,
            stock_minimo=2,
            activo=True,
        )

    def login_as_admin(self):
        self.client.login(username="admin_testuser", password="testpass2025")

    def login_as_user(self):
        user = User.objects.create_user(
            username="user_test", password="testpass2025", is_staff=False
        )
        self.client.login(username="user_test", password="testpass2025")
        return user

    def test_producto_list_view_staff(self):
        self.login_as_admin()
        response = self.client.get(reverse("gestion_stock:producto_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pala Pro")

    def test_producto_create_view(self):
        self.login_as_admin()
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
        self.login_as_user()
        response = self.client.get(reverse("gestion_stock:producto_list"))
        self.assertEqual(response.status_code, 403)

    def test_producto_create_view_no_staff(self):
        self.login_as_user()
        response = self.client.get(reverse("gestion_stock:producto_create"))
        self.assertEqual(response.status_code, 403)
        response = self.client.post(
            reverse("gestion_stock:producto_create"),
            {
                "nombre": "Pala Test2",
                "descripcion": "Test Desc",
                "categoria": self.categoria.id,
                "precio_venta": 5000,
                "precio_costo": 3000,
                "stock_actual": 5,
                "stock_minimo": 1,
                "activo": True,
            },
        )
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Producto.objects.filter(nombre="Pala Test2").exists())

    def test_producto_update_view_no_staff(self):
        self.login_as_user()
        url = reverse("gestion_stock:producto_update", args=[self.producto.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
        response = self.client.post(url, {"nombre": "Hack"})
        self.assertEqual(response.status_code, 403)

    def test_producto_delete_view_no_staff(self):
        self.login_as_user()
        url = reverse("gestion_stock:producto_delete", args=[self.producto.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)
