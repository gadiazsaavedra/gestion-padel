from django.contrib.auth.models import User
from django.test import TestCase
from bar.models import Caja, MovimientoCaja, Producto, Venta


class ProductoModelTest(TestCase):
    def test_creacion_producto(self):
        producto = Producto.objects.create(nombre="Agua", precio=500, stock=20)
        self.assertEqual(producto.nombre, "Agua")
        self.assertEqual(producto.precio, 500)
        self.assertEqual(producto.stock, 20)

    def test_producto_str(self):
        producto = Producto.objects.create(nombre="Sprite", precio=800, stock=15)
        self.assertEqual(str(producto), "Sprite")


class ModelStrMethodsTest(TestCase):
    def test_caja_str(self):
        user = User.objects.create_user(username="cajero", password="testpass")
        caja = Caja.objects.create(saldo_inicial=1000, usuario_apertura=user)
        texto = str(caja)
        self.assertIn("Caja", texto)
        self.assertTrue("Abierta" in texto or "Cerrada" in texto)

    def test_movimientocaja_str(self):
        user = User.objects.create_user(username="cajero2", password="testpass")
        caja = Caja.objects.create(saldo_inicial=500, usuario_apertura=user)
        mov = MovimientoCaja.objects.create(
            caja=caja, concepto="Ingreso", monto=200, usuario=user
        )
        texto = str(mov)
        self.assertIn("Ingreso", texto)
        self.assertIn("$200", texto)
        self.assertIn("/", texto)  # Fecha
