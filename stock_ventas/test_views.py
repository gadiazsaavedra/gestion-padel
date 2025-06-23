import pytest
import json
from decimal import Decimal
from django.test import Client
from django.contrib.auth.models import User, Group
from django.urls import reverse
from .models import Producto, CategoriaProducto, Caja


@pytest.mark.django_db
class TestPOSViews:
    
    def setup_method(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        # Agregar usuario al grupo de recepcionistas
        recep_group, _ = Group.objects.get_or_create(name='Recepcionista')
        self.user.groups.add(recep_group)
        
        self.categoria = CategoriaProducto.objects.create(
            nombre="Bebidas",
            tipo="bebidas"
        )
        self.producto = Producto.objects.create(
            sku="TEST001",
            nombre="Coca Cola",
            categoria=self.categoria,
            precio_compra=Decimal('50.00'),
            precio_venta=Decimal('80.00'),
            stock_actual=10
        )
        self.caja = Caja.objects.create(
            saldo_inicial=Decimal('1000.00'),
            usuario_apertura=self.user
        )
    
    def test_pos_dashboard_acceso(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('stock_ventas:pos_dashboard'))
        
        assert response.status_code == 200
        assert 'Punto de Venta' in response.content.decode()
    
    def test_buscar_productos_api(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('stock_ventas:buscar_productos'),
            {'q': 'Coca'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.content)
        assert len(data['productos']) == 1
        assert data['productos'][0]['nombre'] == 'Coca Cola'
    
    def test_procesar_venta_exitosa(self):
        self.client.login(username='testuser', password='testpass123')
        
        venta_data = {
            'productos': [
                {
                    'producto_id': self.producto.id,
                    'cantidad': 2
                }
            ],
            'metodo_pago': 'efectivo',
            'observaciones': 'Test venta'
        }
        
        response = self.client.post(
            reverse('stock_ventas:procesar_venta'),
            data=json.dumps(venta_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True
        
        # Verificar stock actualizado
        self.producto.refresh_from_db()
        assert self.producto.stock_actual == 8
    
    def test_procesar_venta_stock_insuficiente(self):
        self.client.login(username='testuser', password='testpass123')
        
        venta_data = {
            'productos': [
                {
                    'producto_id': self.producto.id,
                    'cantidad': 15  # Más que el stock disponible
                }
            ],
            'metodo_pago': 'efectivo',
            'observaciones': 'Test venta'
        }
        
        response = self.client.post(
            reverse('stock_ventas:procesar_venta'),
            data=json.dumps(venta_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is False
        assert 'Stock insuficiente' in data['error']


@pytest.mark.django_db
class TestReportesViews:
    
    def setup_method(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(
            username='admin',
            password='adminpass123',
            is_staff=True
        )
    
    def test_dashboard_reportes_acceso_admin(self):
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('stock_ventas:dashboard_reportes'))
        
        assert response.status_code == 200
        assert 'Reportes' in response.content.decode()
    
    def test_dashboard_reportes_sin_permisos(self):
        user = User.objects.create_user('normaluser', 'test@test.com', 'pass')
        self.client.login(username='normaluser', password='pass')
        
        response = self.client.get(reverse('stock_ventas:dashboard_reportes'))
        # Debería redirigir o denegar acceso
        assert response.status_code in [302, 403]