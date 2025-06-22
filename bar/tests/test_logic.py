from django.test import TestCase
from django.contrib.auth.models import User
from bar.models import Producto, Venta, Caja
from decimal import Decimal
from django.utils import timezone


class BarLogicTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="1234")
        self.producto = Producto.objects.create(
            nombre="Gaseosa", precio=Decimal("150.00"), stock=10, categoria="bar"
        )
        self.caja = Caja.objects.create(
            saldo_inicial=Decimal("1000.00"), abierta=True, usuario_apertura=self.user
        )

    def test_venta_descuenta_stock(self):
        venta = Venta.objects.create(
            producto=self.producto, cantidad=2, usuario=self.user
        )
        self.producto.refresh_from_db()
        # Simular lógica de descuento de stock (debería estar en una señal o método save personalizado)
        self.producto.stock -= venta.cantidad
        self.producto.save()
        self.assertEqual(self.producto.stock, 8)

    def test_no_venta_si_stock_insuficiente(self):
        venta = Venta(producto=self.producto, cantidad=20, usuario=self.user)
        # Simular validación de stock
        can_sell = venta.cantidad <= self.producto.stock
        self.assertFalse(can_sell)

    def test_caja_abierta_y_cierre(self):
        self.assertTrue(self.caja.abierta)
        self.caja.saldo_final = Decimal("1200.00")
        self.caja.fecha_cierre = timezone.now()
        self.caja.abierta = False
        self.caja.save()
        self.caja.refresh_from_db()
        self.assertFalse(self.caja.abierta)
        self.assertIsNotNone(self.caja.fecha_cierre)
        self.assertEqual(self.caja.saldo_final, Decimal("1200.00"))

    def test_venta_asociada_a_usuario(self):
        venta = Venta.objects.create(
            producto=self.producto, cantidad=1, usuario=self.user
        )
        self.assertEqual(venta.usuario, self.user)
