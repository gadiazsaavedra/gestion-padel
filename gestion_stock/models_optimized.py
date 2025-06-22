from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal


class Proveedor(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    direccion = models.TextField(blank=True)
    persona_contacto = models.CharField(max_length=100, blank=True)
    calificacion = models.CharField(
        max_length=20,
        choices=[
            ('excelente', 'Excelente'),
            ('bueno', 'Bueno'),
            ('regular', 'Regular'),
            ('malo', 'Malo'),
        ],
        default='bueno'
    )
    activo = models.BooleanField(default=True)
    fecha_alta = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nombre


class CategoriaProducto(models.Model):
    TIPOS_CATEGORIA = [
        ('bebidas', 'Bebidas'),
        ('snacks', 'Snacks'),
        ('paletas', 'Paletas'),
        ('pelotas', 'Pelotas'),
        ('otros', 'Otros'),
    ]
    
    nombre = models.CharField(max_length=100, unique=True)
    tipo = models.CharField(max_length=20, choices=TIPOS_CATEGORIA)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        return self.nombre


class Producto(models.Model):
    # Información básica
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    sku = models.CharField(max_length=50, unique=True, help_text="Código único del producto")
    categoria = models.ForeignKey(CategoriaProducto, on_delete=models.CASCADE)
    
    # Precios y stock
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    stock_actual = models.PositiveIntegerField(default=0)
    stock_minimo = models.PositiveIntegerField(default=5)
    
    # Atributos específicos para paletas
    marca = models.CharField(max_length=50, blank=True)
    modelo = models.CharField(max_length=50, blank=True)
    peso = models.PositiveIntegerField(blank=True, null=True, help_text="Peso en gramos")
    material = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=30, blank=True)
    
    # Imagen
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    
    # Control
    activo = models.BooleanField(default=True)
    fecha_alta = models.DateTimeField(auto_now_add=True)
    ultima_modificacion = models.DateTimeField(auto_now=True)
    
    # Proveedor principal
    proveedor_principal = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['categoria']),
            models.Index(fields=['activo']),
        ]
    
    def __str__(self):
        return f"{self.nombre} ({self.sku})"
    
    @property
    def margen_ganancia(self):
        if self.precio_compra > 0:
            return ((self.precio_venta - self.precio_compra) / self.precio_compra) * 100
        return 0
    
    @property
    def stock_bajo(self):
        return self.stock_actual <= self.stock_minimo
    
    def puede_vender(self, cantidad):
        return self.activo and self.stock_actual >= cantidad


class CompraProveedor(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name='compras')
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    fecha_entrega = models.DateTimeField(null=True, blank=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    estado = models.CharField(
        max_length=20,
        choices=[
            ('pendiente', 'Pendiente'),
            ('entregado', 'Entregado'),
            ('cancelado', 'Cancelado'),
        ],
        default='pendiente'
    )
    observaciones = models.TextField(blank=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return f"Compra #{self.id} - {self.proveedor.nombre}"


class DetalleCompra(models.Model):
    compra = models.ForeignKey(CompraProveedor, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)


class Caja(models.Model):
    fecha_apertura = models.DateTimeField(auto_now_add=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True)
    saldo_inicial = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    saldo_final = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    abierta = models.BooleanField(default=True)
    usuario_apertura = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='cajas_abiertas')
    usuario_cierre = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='cajas_cerradas')
    observaciones_apertura = models.TextField(blank=True)
    observaciones_cierre = models.TextField(blank=True)
    
    def __str__(self):
        return f"Caja {self.id} - {self.fecha_apertura.strftime('%d/%m/%Y')}"
    
    @property
    def total_ventas(self):
        return self.ventas.aggregate(total=models.Sum('total'))['total'] or 0
    
    @property
    def diferencia_arqueo(self):
        if self.saldo_final is not None:
            esperado = self.saldo_inicial + self.total_ventas
            return self.saldo_final - esperado
        return None


class Venta(models.Model):
    METODOS_PAGO = [
        ('efectivo', 'Efectivo'),
        ('tarjeta', 'Tarjeta'),
        ('mercadopago', 'Mercado Pago'),
        ('transferencia', 'Transferencia'),
    ]
    
    caja = models.ForeignKey(Caja, on_delete=models.CASCADE, related_name='ventas')
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.CharField(max_length=20, choices=METODOS_PAGO)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    observaciones = models.TextField(blank=True)
    
    def __str__(self):
        return f"Venta #{self.id} - ${self.total}"


class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)


class MovimientoStock(models.Model):
    TIPOS_MOVIMIENTO = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
        ('ajuste', 'Ajuste'),
        ('venta', 'Venta'),
    ]
    
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='movimientos')
    tipo = models.CharField(max_length=20, choices=TIPOS_MOVIMIENTO)
    cantidad = models.IntegerField()  # Puede ser negativo para salidas
    stock_anterior = models.PositiveIntegerField()
    stock_nuevo = models.PositiveIntegerField()
    motivo = models.CharField(max_length=200)
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    venta = models.ForeignKey(Venta, on_delete=models.SET_NULL, null=True, blank=True)
    compra = models.ForeignKey(CompraProveedor, on_delete=models.SET_NULL, null=True, blank=True)
    observaciones = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.producto.nombre} - {self.tipo} ({self.cantidad})"