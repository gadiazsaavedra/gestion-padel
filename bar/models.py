from django.db import models
from django.contrib.auth.models import User
from gestion_stock.models import Producto
from django.db import transaction


class Venta(models.Model):
    METODOS_PAGO = [
        ('efectivo', 'Efectivo'),
        ('tarjeta', 'Tarjeta'),
        ('mercadopago', 'Mercado Pago'),
        ('transferencia', 'Transferencia'),
    ]
    
    caja = models.ForeignKey('Caja', on_delete=models.CASCADE, related_name='ventas')
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.CharField(max_length=20, choices=METODOS_PAGO)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    observaciones = models.TextField(blank=True)
    
    def __str__(self):
        return f"Venta #{self.id} - ${self.total}"
    
    def save(self, *args, **kwargs):
        # Calcular total automáticamente
        if self.pk:
            self.total = sum(detalle.subtotal for detalle in self.detalles.all())
        super().save(*args, **kwargs)


class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)
        
        # Actualizar stock automáticamente
        with transaction.atomic():
            producto = self.producto
            stock_anterior = producto.stock_actual
            producto.stock_actual -= self.cantidad
            producto.save()
            
            # Registrar movimiento de stock
            from gestion_stock.models import MovimientoStock
            MovimientoStock.objects.create(
                producto=producto,
                tipo='venta',
                cantidad=-self.cantidad,
                stock_anterior=stock_anterior,
                stock_nuevo=producto.stock_actual,
                motivo=f'Venta #{self.venta.id}',
                usuario=self.venta.usuario
            )


class Caja(models.Model):
    fecha_apertura = models.DateTimeField(auto_now_add=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True)
    saldo_inicial = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    saldo_final = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    abierta = models.BooleanField(default=True)
    usuario_apertura = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cajas_abiertas",
    )
    usuario_cierre = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cajas_cerradas",
    )

    def __str__(self):
        return f"Caja {self.id} - {'Abierta' if self.abierta else 'Cerrada'}"


class MovimientoCaja(models.Model):
    TIPOS_MOVIMIENTO = [
        ('ingreso', 'Ingreso'),
        ('egreso', 'Egreso'),
        ('venta', 'Venta'),
        ('ajuste', 'Ajuste'),
    ]
    
    caja = models.ForeignKey(Caja, on_delete=models.CASCADE, related_name="movimientos")
    venta = models.ForeignKey(Venta, on_delete=models.SET_NULL, null=True, blank=True)
    tipo = models.CharField(max_length=20, choices=TIPOS_MOVIMIENTO, default='venta')
    concepto = models.CharField(max_length=100)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f"{self.concepto} - ${self.monto} ({self.fecha:%d/%m/%Y %H:%M})"
