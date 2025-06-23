import pytest
from decimal import Decimal
from django.contrib.auth.models import User
from stock_ventas.models import Producto, CategoriaProducto, Caja, Venta, DetalleVenta


@pytest.mark.django_db
class TestProductoStock:
    
    def test_stock_negativo_error(self):
        """Test que el stock no puede ser negativo"""
        categoria = CategoriaProducto.objects.create(nombre="Bebidas", tipo="bebidas")
        producto = Producto.objects.create(
            sku="TEST001",
            nombre="Coca Cola",
            categoria=categoria,
            precio_compra=Decimal('50.00'),
            precio_venta=Decimal('80.00'),
            stock_actual=5
        )
        
        with pytest.raises(ValueError, match="Stock insuficiente"):
            producto.actualizar_stock(-10, 'venta', 'Test venta')
    
    def test_margen_ganancia(self):
        """Test cálculo de margen de ganancia"""
        categoria = CategoriaProducto.objects.create(nombre="Bebidas", tipo="bebidas")
        producto = Producto.objects.create(
            sku="TEST002",
            nombre="Sprite",
            categoria=categoria,
            precio_compra=Decimal('50.00'),
            precio_venta=Decimal('80.00'),
            stock_actual=10
        )
        
        assert producto.margen_ganancia == 60.0
    
    def test_stock_bajo(self):
        """Test detección de stock bajo"""
        categoria = CategoriaProducto.objects.create(nombre="Bebidas", tipo="bebidas")
        producto = Producto.objects.create(
            sku="TEST003",
            nombre="Agua",
            categoria=categoria,
            precio_compra=Decimal('20.00'),
            precio_venta=Decimal('30.00'),
            stock_actual=3,
            stock_minimo=5
        )
        
        assert producto.stock_bajo is True


@pytest.mark.django_db
class TestVentaCompleta:
    
    def test_venta_descuenta_stock(self):
        """Test que la venta descuenta stock correctamente"""
        # Setup
        user = User.objects.create_user('testuser', 'test@test.com', 'pass')
        caja = Caja.objects.create(saldo_inicial=Decimal('1000.00'), usuario_apertura=user)
        categoria = CategoriaProducto.objects.create(nombre="Bebidas", tipo="bebidas")
        producto = Producto.objects.create(
            sku="TEST004",
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
        
        # Crear detalle (esto debería descontar stock)
        DetalleVenta.objects.create(
            venta=venta,
            producto=producto,
            cantidad=2,
            precio_unitario=Decimal('65.00')
        )
        
        # Verificar stock actualizado
        producto.refresh_from_db()
        assert producto.stock_actual == 18
    
    def test_calculo_subtotal(self):
        """Test cálculo automático de subtotal"""
        user = User.objects.create_user('testuser', 'test@test.com', 'pass')
        caja = Caja.objects.create(saldo_inicial=Decimal('1000.00'), usuario_apertura=user)
        categoria = CategoriaProducto.objects.create(nombre="Bebidas", tipo="bebidas")
        producto = Producto.objects.create(
            sku="TEST005",
            nombre="Fanta",
            categoria=categoria,
            precio_compra=Decimal('45.00'),
            precio_venta=Decimal('70.00'),
            stock_actual=15
        )
        
        venta = Venta.objects.create(
            caja=caja,
            total=Decimal('210.00'),
            metodo_pago='tarjeta',
            usuario=user
        )
        
        detalle = DetalleVenta.objects.create(
            venta=venta,
            producto=producto,
            cantidad=3,
            precio_unitario=Decimal('70.00')
        )
        
        assert detalle.subtotal == Decimal('210.00')


@pytest.mark.django_db
class TestCajaOperaciones:
    
    def test_saldo_teorico(self):
        """Test cálculo de saldo teórico de caja"""
        user = User.objects.create_user('testuser', 'test@test.com', 'pass')
        caja = Caja.objects.create(
            saldo_inicial=Decimal('1000.00'),
            usuario_apertura=user
        )
        
        # Crear venta
        Venta.objects.create(
            caja=caja,
            total=Decimal('150.00'),
            metodo_pago='efectivo',
            usuario=user
        )
        
        assert caja.saldo_teorico == Decimal('1150.00')
    
    def test_diferencia_arqueo(self):
        """Test cálculo de diferencia en arqueo"""
        user = User.objects.create_user('testuser', 'test@test.com', 'pass')
        caja = Caja.objects.create(
            saldo_inicial=Decimal('1000.00'),
            usuario_apertura=user
        )
        
        # Simular venta
        Venta.objects.create(
            caja=caja,
            total=Decimal('100.00'),
            metodo_pago='efectivo',
            usuario=user
        )
        
        # Cerrar caja con diferencia
        caja.saldo_final = Decimal('1090.00')  # $10 menos de lo esperado
        caja.save()
        
        assert caja.diferencia_arqueo == Decimal('-10.00')