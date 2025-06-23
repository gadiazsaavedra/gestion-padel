from django.core.management.base import BaseCommand
from stock_ventas.models import Producto, CategoriaProducto, Proveedor, Caja, Venta, DetalleVenta
from datetime import datetime, timedelta
from django.utils import timezone
import random


class Command(BaseCommand):
    help = 'Poblar datos para stock y ventas'

    def handle(self, *args, **options):
        # Crear categorías
        categorias_data = [
            {'nombre': 'Bebidas', 'descripcion': 'Bebidas y refrescos', 'tipo': 'bebidas'},
            {'nombre': 'Snacks', 'descripcion': 'Comida rápida y snacks', 'tipo': 'snacks'},
            {'nombre': 'Deportivo', 'descripcion': 'Artículos deportivos', 'tipo': 'otros'},
        ]

        for cat_data in categorias_data:
            categoria, created = CategoriaProducto.objects.get_or_create(
                nombre=cat_data['nombre'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f'✓ Categoría creada: {categoria}')

        # Crear proveedor
        proveedor, _ = Proveedor.objects.get_or_create(
            nombre='Distribuidora Central',
            defaults={
                'persona_contacto': 'Juan Pérez',
                'telefono': '1123456789',
                'email': 'ventas@distribuidora.com'
            }
        )

        # Crear productos
        bebidas = CategoriaProducto.objects.get(nombre='Bebidas')
        snacks = CategoriaProducto.objects.get(nombre='Snacks')
        deportivo = CategoriaProducto.objects.get(nombre='Deportivo')

        productos_data = [
            {'nombre': 'Agua Mineral', 'categoria': bebidas, 'precio_compra': 300, 'precio_venta': 500, 'stock': 100},
            {'nombre': 'Gatorade', 'categoria': bebidas, 'precio_compra': 500, 'precio_venta': 800, 'stock': 50},
            {'nombre': 'Coca Cola', 'categoria': bebidas, 'precio_compra': 400, 'precio_venta': 600, 'stock': 80},
            {'nombre': 'Cerveza', 'categoria': bebidas, 'precio_compra': 800, 'precio_venta': 1200, 'stock': 60},
            {'nombre': 'Sandwich', 'categoria': snacks, 'precio_compra': 1000, 'precio_venta': 1500, 'stock': 30},
            {'nombre': 'Papas Fritas', 'categoria': snacks, 'precio_compra': 200, 'precio_venta': 400, 'stock': 40},
            {'nombre': 'Barrita Cereal', 'categoria': snacks, 'precio_compra': 150, 'precio_venta': 300, 'stock': 25},
            {'nombre': 'Pelota Pádel', 'categoria': deportivo, 'precio_compra': 1200, 'precio_venta': 2000, 'stock': 20},
        ]

        for prod_data in productos_data:
            producto, created = Producto.objects.get_or_create(
                nombre=prod_data['nombre'],
                defaults={
                    'categoria': prod_data['categoria'],
                    'descripcion': f'Producto {prod_data["nombre"]}',
                    'precio_compra': prod_data['precio_compra'],
                    'precio_venta': prod_data['precio_venta'],
                    'stock_actual': prod_data['stock'],
                    'stock_minimo': 10,
                    'sku': f'SKU{random.randint(1000, 9999)}',
                    'proveedor_principal': proveedor,
                }
            )
            if created:
                self.stdout.write(f'✓ Producto creado: {producto}')

        # Crear caja
        caja, _ = Caja.objects.get_or_create(
            id=1,
            defaults={'saldo_inicial': 50000, 'abierta': True}
        )

        # Crear ventas de los últimos 15 días
        productos = list(Producto.objects.all())
        
        for i in range(15):
            fecha = timezone.now() - timedelta(days=i)
            
            # Crear 2-8 ventas por día
            num_ventas = random.randint(2, 8)
            for _ in range(num_ventas):
                total_venta = 0
                venta = Venta.objects.create(
                    caja=caja,
                    total=0,  # Se calculará después
                    metodo_pago=random.choice(['efectivo', 'tarjeta', 'mercadopago']),
                    fecha=fecha
                )
                
                # Agregar 1-4 productos por venta
                num_productos = random.randint(1, 4)
                productos_venta = random.sample(productos, min(num_productos, len(productos)))
                
                for producto in productos_venta:
                    cantidad = random.randint(1, 3)
                    precio = producto.precio_venta
                    subtotal = cantidad * precio
                    total_venta += subtotal
                    
                    DetalleVenta.objects.create(
                        venta=venta,
                        producto=producto,
                        cantidad=cantidad,
                        precio_unitario=precio,
                        subtotal=subtotal
                    )
                
                # Actualizar total de la venta
                venta.total = total_venta
                venta.save()

        self.stdout.write('\n' + '='*50)
        self.stdout.write('RESUMEN DE DATOS CREADOS:')
        self.stdout.write(f'Categorías: {CategoriaProducto.objects.count()}')
        self.stdout.write(f'Productos: {Producto.objects.count()}')
        self.stdout.write(f'Ventas: {Venta.objects.count()}')
        self.stdout.write(f'Detalles de Venta: {DetalleVenta.objects.count()}')
        
        total_ventas = sum(v.total for v in Venta.objects.all())
        self.stdout.write(f'Total Ventas: ${total_ventas:,.2f}')
        self.stdout.write('='*50)

        self.stdout.write(
            self.style.SUCCESS('¡Datos de stock y ventas poblados exitosamente!')
        )