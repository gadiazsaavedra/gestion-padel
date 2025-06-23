import pytest
from django.test import Client
from django.contrib.auth.models import User, Group
from django.urls import reverse


@pytest.mark.django_db
class TestAutenticacionPermisos:
    
    def setup_method(self):
        self.client = Client()
        
        # Crear grupos
        self.admin_group = Group.objects.create(name='Administrador')
        self.recep_group = Group.objects.create(name='Recepcionista')
        self.jugador_group = Group.objects.create(name='Jugador')
        
        # Crear usuarios
        self.admin_user = User.objects.create_user(
            username='admin',
            password='admin123',
            is_staff=True
        )
        self.admin_user.groups.add(self.admin_group)
        
        self.recep_user = User.objects.create_user(
            username='recepcionista',
            password='recep123'
        )
        self.recep_user.groups.add(self.recep_group)
        
        self.jugador_user = User.objects.create_user(
            username='jugador',
            password='jugador123'
        )
        self.jugador_user.groups.add(self.jugador_group)
    
    def test_login_exitoso(self):
        """Test login exitoso"""
        response = self.client.post(reverse('login'), {
            'username': 'admin',
            'password': 'admin123'
        })
        
        assert response.status_code == 302  # Redirección después de login
    
    def test_login_fallido(self):
        """Test login con credenciales incorrectas"""
        response = self.client.post(reverse('login'), {
            'username': 'admin',
            'password': 'wrongpass'
        })
        
        assert response.status_code == 200  # Se queda en la página de login
        assert 'error' in response.context or 'form' in response.context
    
    def test_acceso_pos_recepcionista(self):
        """Test que recepcionista puede acceder al POS"""
        self.client.login(username='recepcionista', password='recep123')
        response = self.client.get(reverse('stock_ventas:pos_dashboard'))
        
        assert response.status_code == 200
    
    def test_acceso_admin_panel_solo_admin(self):
        """Test que solo admin puede acceder al panel de administración"""
        # Admin puede acceder
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('stock_ventas:dashboard_admin'))
        assert response.status_code == 200
        
        # Recepcionista no puede acceder
        self.client.login(username='recepcionista', password='recep123')
        response = self.client.get(reverse('stock_ventas:dashboard_admin'))
        assert response.status_code in [302, 403]  # Redirección o acceso denegado
    
    def test_menu_dinamico_por_rol(self):
        """Test que el menú se adapta según el rol"""
        from club.menu_config import get_user_menu
        
        # Menú de admin
        admin_menu = get_user_menu(self.admin_user)
        admin_items = [item['name'] for item in admin_menu]
        assert 'Dashboard' in admin_items
        assert 'Stock & Ventas' in admin_items
        
        # Menú de recepcionista
        recep_menu = get_user_menu(self.recep_user)
        recep_items = [item['name'] for item in recep_menu]
        assert 'Dashboard' in recep_items
        assert 'Punto de Venta' in recep_items
        
        # Menú de jugador
        jugador_menu = get_user_menu(self.jugador_user)
        jugador_items = [item['name'] for item in jugador_menu]
        assert 'Mi Panel' in jugador_items
        assert 'Mi Perfil' in jugador_items