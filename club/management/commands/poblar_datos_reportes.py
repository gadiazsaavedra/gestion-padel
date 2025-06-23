from django.core.management.base import BaseCommand
from club.models import Jugador, Reserva, Pago
from gestion_stock.models import Producto, CategoriaProducto
from bar.models import Venta, DetalleVenta, Caja
from django.contrib.auth.models import User
from datetime import date, timedelta, datetime, time
import random


class Command(BaseCommand):
    help = 'Poblar datos para generar reportes financieros interesantes'

    def handle(self, *args, **options):
        # Crear jugadores si no existen
        jugadores_data = [
            {'nombre': 'Carlos', 'apellido': 'Mendez', 'email': 'carlos.mendez@email.com', 'telefono': '1111111111', 'nivel': 'avanzado', 'genero': 'hombre'},
            {'nombre': 'Ana', 'apellido': 'Rodriguez', 'email': 'ana.rodriguez@email.com', 'telefono': '2222222222', 'nivel': 'intermedio', 'genero': 'mujer'},
            {'nombre': 'Luis', 'apellido': 'Garcia', 'email': 'luis.garcia@email.com', 'telefono': '3333333333', 'nivel': 'novato', 'genero': 'hombre'},
            {'nombre': 'Sofia', 'apellido': 'Martinez', 'email': 'sofia.martinez@email.com', 'telefono': '4444444444', 'nivel': 'avanzado', 'genero': 'mujer'},
            {'nombre': 'Diego', 'apellido': 'Lopez', 'email': 'diego.lopez@email.com', 'telefono': '5555555555', 'nivel': 'intermedio', 'genero': 'hombre'},
        ]

        for jug_data in jugadores_data:
            jugador, created = Jugador.objects.get_or_create(
                email=jug_data['email'],
                defaults=jug_data
            )
            if created:
                self.stdout.write(f'✓ Jugador creado: {jugador}')

        # Crear categorías y productos
        categoria, _ = CategoriaProducto.objects.get_or_create(
            nombre='Bebidas',
            defaults={'descripcion': 'Bebidas del bar', 'tipo': 'consumible'}
        )
        
        productos_data = [
            {'nombre': 'Agua Mineral', 'precio_venta': 500, 'stock_actual': 100},
            {'nombre': 'Gatorade', 'precio_venta': 800, 'stock_actual': 50},
            {'nombre': 'Coca Cola', 'precio_venta': 600, 'stock_actual': 80},
            {'nombre': 'Cerveza', 'precio_venta': 1200, 'stock_actual': 60},
            {'nombre': 'Sandwich', 'precio_venta': 1500, 'stock_actual': 30},
        ]

        for prod_data in productos_data:
            producto, created = Producto.objects.get_or_create(
                nombre=prod_data['nombre'],
                defaults={
                    'categoria': categoria,
                    'descripcion': f'Producto {prod_data["nombre"]}',
                    'precio_venta': prod_data['precio_venta'],
                    'precio_compra': prod_data['precio_venta'] * 0.6,
                    'stock_actual': prod_data['stock_actual'],
                    'stock_minimo': 10,
                    'sku': f'SKU{random.randint(1000, 9999)}',
                }
            )
            if created:
                self.stdout.write(f'✓ Producto creado: {producto}')

        # Crear caja
        caja, _ = Caja.objects.get_or_create(
            id=1,
            defaults={'saldo_inicial': 10000, 'abierta': True}
        )

        # Crear reservas y pagos de los últimos 7 días
        jugadores = list(Jugador.objects.all())
        productos = list(Producto.objects.all())
        
        for i in range(7):
            fecha = date.today() - timedelta(days=i)
            
            # Crear 3-8 reservas por día
            num_reservas = random.randint(3, 8)
            for _ in range(num_reservas):
                jugador = random.choice(jugadores)
                hora = time(random.randint(8, 21), random.choice([0, 30]))
                monto = random.randint(3000, 8000)
                
                reserva, created = Reserva.objects.get_or_create(
                    jugador=jugador,
                    fecha=fecha,
                    hora=hora,
                    defaults={
                        'estado': 'pagada',
                        'pago_total': monto,
                        'metodo_pago': random.choice(['efectivo', 'tarjeta', 'transferencia'])
                    }
                )
                
                if created:
                    # Crear pago correspondiente
                    Pago.objects.create(
                        jugador=jugador,
                        monto=monto,
                        fecha=fecha,
                        estado='pagado',
                        metodo=reserva.metodo_pago
                    )

            # Crear ventas del bar
            num_ventas = random.randint(5, 15)
            for _ in range(num_ventas):
                total_venta = 0
                venta = Venta.objects.create(
                    caja=caja,
                    total=0,  # Se calculará después
                    metodo_pago=random.choice(['efectivo', 'tarjeta', 'mercadopago']),
                    fecha=datetime.combine(fecha, time(random.randint(9, 22), random.randint(0, 59)))
                )
                
                # Agregar 1-4 productos por venta
                num_productos = random.randint(1, 4)
                for _ in range(num_productos):
                    producto = random.choice(productos)
                    cantidad = random.randint(1, 3)
                    precio = producto.precio_venta
                    subtotal = cantidad * precio
                    total_venta += subtotal
                    
                    # Solo crear la venta sin afectar el stock
                    DetalleVenta.objects.create(
                        venta=venta,
                        producto=producto,
                        cantidad=cantidad,
                        precio_unitario=precio,
                        subtotal=subtotal
                    )
                    
                    # Asegurar que el stock no baje de 0
                    if producto.stock_actual >= cantidad:
                        producto.stock_actual -= cantidad
                        producto.save()
                
                # Actualizar total de la venta
                venta.total = total_venta
                venta.save()

        self.stdout.write('\n' + '='*50)
        self.stdout.write('RESUMEN DE DATOS CREADOS:')
        self.stdout.write(f'Jugadores: {Jugador.objects.count()}')
        self.stdout.write(f'Reservas: {Reserva.objects.count()}')
        self.stdout.write(f'Pagos: {Pago.objects.count()}')
        self.stdout.write(f'Productos: {Producto.objects.count()}')
        self.stdout.write(f'Ventas Bar: {Venta.objects.count()}')
        self.stdout.write('='*50)

        self.stdout.write(
            self.style.SUCCESS('¡Datos para reportes poblados exitosamente!')
        )