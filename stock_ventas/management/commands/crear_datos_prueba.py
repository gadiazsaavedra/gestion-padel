from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from stock_ventas.models import (
    Proveedor, CategoriaProducto, Producto, Caja, 
    Venta, DetalleVenta, CompraProveedor, DetalleCompra
)
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Crea datos de prueba para el sistema de stock y ventas'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Creando datos de prueba...')
        
        # Crear proveedores
        self.crear_proveedores()
        
        # Crear categorías
        self.crear_categorias()
        
        # Crear productos
        self.crear_productos()
        
        # Crear compras
        self.crear_compras()
        
        # Crear caja y ventas
        self.crear_ventas()
        
        self.stdout.write(self.style.SUCCESS('✅ Datos de prueba creados exitosamente'))

    def crear_proveedores(self):
        proveedores_data = [
            {
                'nombre': 'Distribuidora Central',
                'telefono': '011-4567-8901',
                'email': 'ventas@distribuidoracentral.com',
                'persona_contacto': 'Juan Pérez',
                'calificacion': 'excelente'
            },
            {
                'nombre': 'Bebidas del Sur',
                'telefono': '011-2345-6789',
                'email': 'pedidos@bebidasdelsur.com',
                'persona_contacto': 'María González',
                'calificacion': 'bueno'
            },
            {
                'nombre': 'Snacks Premium',
                'telefono': '011-9876-5432',
                'email': 'info@snackspremium.com',
                'persona_contacto': 'Carlos López',
                'calificacion': 'regular'
            },
            {
                'nombre': 'Deportes Padel Pro',
                'telefono': '011-1111-2222',
                'email': 'ventas@deportespadelPro.com',
                'persona_contacto': 'Ana Martín',
                'calificacion': 'excelente'
            }
        ]
        
        for data in proveedores_data:
            proveedor, created = Proveedor.objects.get_or_create(
                nombre=data['nombre'],
                defaults=data
            )
            if created:
                self.stdout.write(f'  ✅ Proveedor: {proveedor.nombre}')

    def crear_categorias(self):
        categorias_data = [
            {'nombre': 'Gaseosas', 'tipo': 'bebidas'},
            {'nombre': 'Aguas', 'tipo': 'bebidas'},
            {'nombre': 'Bebidas Isotónicas', 'tipo': 'bebidas'},
            {'nombre': 'Café y Té', 'tipo': 'bebidas'},
            {'nombre': 'Galletitas', 'tipo': 'snacks'},
            {'nombre': 'Alfajores', 'tipo': 'snacks'},
            {'nombre': 'Barras Energéticas', 'tipo': 'snacks'},
            {'nombre': 'Paletas Profesionales', 'tipo': 'paletas'},
            {'nombre': 'Paletas Recreativas', 'tipo': 'paletas'},
            {'nombre': 'Pelotas Presurizadas', 'tipo': 'pelotas'},
            {'nombre': 'Pelotas Sin Presión', 'tipo': 'pelotas'},
        ]
        
        for data in categorias_data:
            categoria, created = CategoriaProducto.objects.get_or_create(
                nombre=data['nombre'],
                defaults=data
            )
            if created:
                self.stdout.write(f'  ✅ Categoría: {categoria.nombre}')

    def crear_productos(self):
        productos_data = [
            # Bebidas
            {'sku': 'COCA-350', 'nombre': 'Coca Cola 350ml', 'categoria': 'Gaseosas', 'precio_compra': 80, 'precio_venta': 150, 'stock': 50},
            {'sku': 'PEPSI-350', 'nombre': 'Pepsi 350ml', 'categoria': 'Gaseosas', 'precio_compra': 75, 'precio_venta': 140, 'stock': 30},
            {'sku': 'SPRITE-350', 'nombre': 'Sprite 350ml', 'categoria': 'Gaseosas', 'precio_compra': 80, 'precio_venta': 150, 'stock': 25},
            {'sku': 'AGUA-500', 'nombre': 'Agua Mineral 500ml', 'categoria': 'Aguas', 'precio_compra': 50, 'precio_venta': 100, 'stock': 100},
            {'sku': 'GATOR-500', 'nombre': 'Gatorade 500ml', 'categoria': 'Bebidas Isotónicas', 'precio_compra': 120, 'precio_venta': 220, 'stock': 40},
            {'sku': 'POWER-500', 'nombre': 'Powerade 500ml', 'categoria': 'Bebidas Isotónicas', 'precio_compra': 110, 'precio_venta': 200, 'stock': 35},
            
            # Snacks
            {'sku': 'OREO-118', 'nombre': 'Oreo Original 118g', 'categoria': 'Galletitas', 'precio_compra': 180, 'precio_venta': 320, 'stock': 20},
            {'sku': 'CHIPA-70', 'nombre': 'Chipá 70g', 'categoria': 'Galletitas', 'precio_compra': 90, 'precio_venta': 180, 'stock': 15},
            {'sku': 'JORG-TRIP', 'nombre': 'Alfajor Jorgito Triple', 'categoria': 'Alfajores', 'precio_compra': 150, 'precio_venta': 280, 'stock': 25},
            {'sku': 'HAVANA-DOBLE', 'nombre': 'Alfajor Havanna Doble', 'categoria': 'Alfajores', 'precio_compra': 200, 'precio_venta': 380, 'stock': 18},
            {'sku': 'CEREAL-BAR', 'nombre': 'Barra de Cereal', 'categoria': 'Barras Energéticas', 'precio_compra': 120, 'precio_venta': 220, 'stock': 30},
            
            # Paletas
            {'sku': 'BABO-DRIVE', 'nombre': 'Babolat Drive', 'categoria': 'Paletas Profesionales', 'precio_compra': 25000, 'precio_venta': 45000, 'stock': 5, 'marca': 'Babolat', 'modelo': 'Drive', 'peso': 365, 'material': 'Carbono'},
            {'sku': 'HEAD-ALPHA', 'nombre': 'Head Alpha Pro', 'categoria': 'Paletas Profesionales', 'precio_compra': 22000, 'precio_venta': 40000, 'stock': 3, 'marca': 'Head', 'modelo': 'Alpha Pro', 'peso': 370, 'material': 'Carbono'},
            {'sku': 'WILSON-BLADE', 'nombre': 'Wilson Blade', 'categoria': 'Paletas Recreativas', 'precio_compra': 15000, 'precio_venta': 28000, 'stock': 8, 'marca': 'Wilson', 'modelo': 'Blade', 'peso': 360, 'material': 'Fibra de Vidrio'},
            
            # Pelotas
            {'sku': 'PENN-PRES', 'nombre': 'Pelotas Penn Presurizadas x3', 'categoria': 'Pelotas Presurizadas', 'precio_compra': 800, 'precio_venta': 1500, 'stock': 50, 'marca': 'Penn'},
            {'sku': 'WILSON-PRES', 'nombre': 'Pelotas Wilson Presurizadas x3', 'categoria': 'Pelotas Presurizadas', 'precio_compra': 750, 'precio_venta': 1400, 'stock': 40, 'marca': 'Wilson'},
            {'sku': 'HEAD-SIN', 'nombre': 'Pelotas Head Sin Presión x3', 'categoria': 'Pelotas Sin Presión', 'precio_compra': 600, 'precio_venta': 1200, 'stock': 30, 'marca': 'Head'},
        ]
        
        for data in productos_data:
            try:
                categoria = CategoriaProducto.objects.get(nombre=data['categoria'])
                
                producto_data = {
                    'nombre': data['nombre'],
                    'categoria': categoria,
                    'precio_compra': Decimal(str(data['precio_compra'])),
                    'precio_venta': Decimal(str(data['precio_venta'])),
                    'stock_actual': data['stock'],
                    'stock_minimo': max(5, data['stock'] // 10),
                    'marca': data.get('marca', ''),
                    'modelo': data.get('modelo', ''),
                    'peso': data.get('peso'),
                    'material': data.get('material', ''),
                }
                
                producto, created = Producto.objects.get_or_create(
                    sku=data['sku'],
                    defaults=producto_data
                )
                if created:
                    self.stdout.write(f'  ✅ Producto: {producto.nombre}')
            except Exception as e:
                self.stdout.write(f'  ❌ Error creando producto {data["nombre"]}: {e}')

    def crear_compras(self):
        # Crear algunas compras de ejemplo
        proveedores = list(Proveedor.objects.all())
        productos = list(Producto.objects.all()[:10])  # Solo algunos productos
        
        admin_user = User.objects.filter(is_staff=True).first()
        
        for i in range(3):
            proveedor = random.choice(proveedores)
            compra = CompraProveedor.objects.create(
                proveedor=proveedor,
                estado='entregado',
                usuario=admin_user,
                observaciones=f'Compra de prueba #{i+1}'
            )
            
            # Agregar algunos productos a la compra
            productos_compra = random.sample(productos, random.randint(2, 5))
            for producto in productos_compra:
                cantidad = random.randint(5, 20)
                precio = producto.precio_compra * Decimal(str(random.uniform(0.9, 1.1)))
                
                DetalleCompra.objects.create(
                    compra=compra,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=precio
                )
            
            self.stdout.write(f'  ✅ Compra: {compra}')

    def crear_ventas(self):
        # Crear caja de prueba
        admin_user = User.objects.filter(is_staff=True).first()
        
        caja = Caja.objects.create(
            saldo_inicial=Decimal('5000.00'),
            usuario_apertura=admin_user,
            observaciones_apertura='Caja de prueba'
        )
        
        # Crear algunas ventas
        productos = list(Producto.objects.filter(stock_actual__gt=0)[:8])
        metodos_pago = ['efectivo', 'tarjeta', 'mercadopago']
        
        for i in range(5):
            venta = Venta.objects.create(
                caja=caja,
                total=Decimal('0.00'),
                metodo_pago=random.choice(metodos_pago),
                usuario=admin_user,
                observaciones=f'Venta de prueba #{i+1}'
            )
            
            # Agregar productos a la venta
            productos_venta = random.sample(productos, random.randint(1, 3))
            total_venta = Decimal('0.00')
            
            for producto in productos_venta:
                if producto.stock_actual > 0:
                    cantidad = min(random.randint(1, 3), producto.stock_actual)
                    
                    detalle = DetalleVenta.objects.create(
                        venta=venta,
                        producto=producto,
                        cantidad=cantidad,
                        precio_unitario=producto.precio_venta
                    )
                    total_venta += detalle.subtotal
            
            venta.total = total_venta
            venta.save()
            
            self.stdout.write(f'  ✅ Venta: ${venta.total}')
        
        self.stdout.write(f'  ✅ Caja creada: {caja}')