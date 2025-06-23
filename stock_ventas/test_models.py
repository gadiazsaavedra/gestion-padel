import pytest
from decimal import Decimal
from django.contrib.auth.models import User
from django.db import transaction
from .models import Producto, CategoriaProducto, Proveedor, Caja, Venta, DetalleVenta


@pytest.mark.django_db
class TestProducto:
    
    def test_crear_producto(self):
        categoria = CategoriaProducto.objects.create(
            nombre="Bebidas", 
            tipo="bebidas"
        )
        producto = Producto.objects.create(
            sku="TEST001",
            nombre="Coca Cola",
            categoria=categoria,
            precio_compra=Decimal('50.00'),
            precio_venta=Decimal('80.00'),
            stock_actual=10
        )
        
        assert producto.sku == "TEST001"
        assert producto.margen_ganancia == 60.0
        assert not producto.stock_bajo
    
    def test_stock_bajo(self):
        categoria = CategoriaProducto.objects.create(
            nombre="Bebidas", 
            tipo="bebidas"
        )
        producto = Producto.objects.create(
            sku="TEST002",
            nombre="Agua",
            categoria=categoria,
            precio_compra=Decimal('20.00'),
            precio_venta=Decimal('30.00'),
            stock_actual=3,
            stock_minimo=5
        )
        
        assert producto.stock_bajo
    
    def test_actualizar_stock_valido(self):
        categoria = CategoriaProducto.objects.create(
            nombre="Bebidas", 
            tipo="bebidas"
        )
        producto = Producto.objects.create(
            sku="TEST003",
            nombre="Sprite",
            categoria=categoria,
            precio_compra=Decimal('45.00'),
            precio_venta=Decimal('70.00'),
            stock_actual=10
        )
        
        producto.actualizar_stock(5, 'entrada', 'Compra')
        assert producto.stock_actual == 15
    
    def test_actualizar_stock_negativo_error(self):
        categoria = CategoriaProducto.objects.create(
            nombre="Bebidas", 
            tipo="bebidas"
        )
        producto = Producto.objects.create(
            sku="TEST004",
            nombre="Fanta",
            categoria=categoria,
            precio_compra=Decimal('45.00'),
            precio_venta=Decimal('70.00'),
            stock_actual=5
        )
        
        with pytest.raises(ValueError, match="Stock insuficiente"):
            producto.actualizar_stock(-10, 'venta', 'Venta')


@pytest.mark.django_db
class TestCaja:
    
    def test_crear_caja(self):
        user = User.objects.create_user('testuser', 'test@test.com', 'pass')
        caja = Caja.objects.create(
            saldo_inicial=Decimal('1000.00'),
            usuario_apertura=user
        )
        
        assert caja.abierta
        assert caja.saldo_inicial == Decimal('1000.00')
        assert caja.total_ventas == 0
    
    def test_saldo_teorico(self):
        user = User.objects.create_user('testuser', 'test@test.com', 'pass')
        caja = Caja.objects.create(
            saldo_inicial=Decimal('1000.00'),
            usuario_apertura=user
        )
        
        # Crear venta
        venta = Venta.objects.create(
            caja=caja,
            total=Decimal('150.00'),
            metodo_pago='efectivo',
            usuario=user
        )
        
        assert caja.saldo_teorico == Decimal('1150.00')


@pytest.mark.django_db
class TestVenta:
    
    def test_crear_venta_completa(self):
        # Setup
        user = User.objects.create_user('testuser', 'test@test.com', 'pass')
        caja = Caja.objects.create(
            saldo_inicial=Decimal('1000.00'),
            usuario_apertura=user
        )
        categoria = CategoriaProducto.objects.create(
            nombre="Bebidas", 
            tipo="bebidas"
        )
        producto = Producto.objects.create(
            sku="TEST005",
            nombre="Pepsi",
            categoria=categoria,
            precio_compra=Decimal('40.00'),
            precio_venta=Decimal('65.00'),
            stock_actual=20
        )
        
        # Crear venta
        venta = Venta.objects.create(
            caja=caja,
            total=Decimal('130.00'),
            metodo_pago='efectivo',
            usuario=user
        )
        
        # Crear detalle
        detalle = DetalleVenta.objects.create(
            venta=venta,
            producto=producto,
            cantidad=2,
            precio_unitario=Decimal('65.00')
        )
        
        assert detalle.subtotal == Decimal('130.00')
        # Verificar que se descontó stock
        producto.refresh_from_db()
        assert producto.stock_actual == 18