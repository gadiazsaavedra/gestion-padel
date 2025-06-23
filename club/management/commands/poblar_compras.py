from django.core.management.base import BaseCommand
from stock_ventas.models import Proveedor, CompraProveedor, DetalleCompra, Producto
from datetime import datetime, timedelta
from django.utils import timezone
import random


class Command(BaseCommand):
    help = 'Poblar compras recientes de los últimos 90 días'

    def handle(self, *args, **options):
        # Obtener proveedores y productos existentes
        proveedores = list(Proveedor.objects.all())
        productos = list(Producto.objects.all())
        
        if not proveedores:
            self.stdout.write(self.style.ERROR('No hay proveedores. Ejecuta primero: python manage.py poblar_stock_simple'))
            return
            
        if not productos:
            self.stdout.write(self.style.ERROR('No hay productos. Ejecuta primero: python manage.py poblar_stock_simple'))
            return

        # Crear compras de los últimos 90 días
        for i in range(90):
            fecha = timezone.now() - timedelta(days=i)
            
            # Crear 0-2 compras por día (no todos los días)
            if random.random() < 0.3:  # 30% de probabilidad por día
                num_compras = random.randint(1, 2)
                
                for _ in range(num_compras):
                    proveedor = random.choice(proveedores)
                    
                    # Determinar estado de la compra
                    if i < 30:  # Últimos 30 días - más probabilidad de estar pendiente
                        estado = random.choice(['pendiente', 'entregado', 'entregado'])
                    else:  # Más de 30 días - probablemente entregado
                        estado = random.choice(['entregado', 'entregado', 'entregado', 'cancelado'])
                    
                    # Crear la compra
                    compra = CompraProveedor.objects.create(
                        proveedor=proveedor,
                        fecha_pedido=fecha,
                        estado=estado,
                        observaciones=f'Compra automática - {estado}',
                        total=0  # Se calculará después
                    )
                    
                    # Si está entregado, asignar fecha de entrega
                    if estado == 'entregado':
                        dias_entrega = random.randint(1, 15)
                        compra.fecha_entrega = fecha + timedelta(days=dias_entrega)
                        compra.save()
                    
                    # Agregar productos a la compra
                    num_productos = random.randint(1, 4)
                    productos_compra = random.sample(productos, min(num_productos, len(productos)))
                    
                    total_compra = 0
                    for producto in productos_compra:
                        cantidad = random.randint(5, 50)
                        precio_unitario = producto.precio_compra
                        subtotal = cantidad * precio_unitario
                        total_compra += subtotal
                        
                        DetalleCompra.objects.create(
                            compra=compra,
                            producto=producto,
                            cantidad=cantidad,
                            precio_unitario=precio_unitario,
                            subtotal=subtotal
                        )
                    
                    # Actualizar total de la compra
                    compra.total = total_compra
                    compra.save()
                    
                    self.stdout.write(f'✓ Compra creada: {proveedor.nombre} - ${total_compra:,.2f} ({estado})')

        # Mostrar resumen
        self.stdout.write('\n' + '='*60)
        self.stdout.write('RESUMEN DE COMPRAS CREADAS:')
        
        total_compras = CompraProveedor.objects.count()
        compras_pendientes = CompraProveedor.objects.filter(estado='pendiente').count()
        compras_entregadas = CompraProveedor.objects.filter(estado='entregado').count()
        compras_canceladas = CompraProveedor.objects.filter(estado='cancelado').count()
        
        self.stdout.write(f'Total Compras: {total_compras}')
        self.stdout.write(f'Pendientes: {compras_pendientes}')
        self.stdout.write(f'Entregadas: {compras_entregadas}')
        self.stdout.write(f'Canceladas: {compras_canceladas}')
        
        # Total en dinero
        total_monto = sum(c.total for c in CompraProveedor.objects.all())
        monto_pendiente = sum(c.total for c in CompraProveedor.objects.filter(estado='pendiente'))
        
        self.stdout.write(f'Monto Total: ${total_monto:,.2f}')
        self.stdout.write(f'Monto Pendiente: ${monto_pendiente:,.2f}')
        self.stdout.write('='*60)

        self.stdout.write(
            self.style.SUCCESS('¡Compras recientes pobladas exitosamente!')
        )