from django.db import models
from django.contrib.auth.models import User


class Empleado(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    dni = models.CharField(max_length=20, unique=True)
    telefono = models.CharField(max_length=20)
    email = models.EmailField()
    cargo = models.CharField(max_length=100)
    salario_base = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_ingreso = models.DateField()
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.cargo}"


class Proveedor(models.Model):
    nombre = models.CharField(max_length=200)
    cuit = models.CharField(max_length=15, unique=True)
    telefono = models.CharField(max_length=20)
    email = models.EmailField()
    direccion = models.TextField()
    contacto = models.CharField(max_length=100, help_text="Persona de contacto")
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class PagoEmpleado(models.Model):
    TIPOS = [
        ('salario', 'Salario'),
        ('bonus', 'Bonus'),
        ('horas_extra', 'Horas Extra'),
        ('aguinaldo', 'Aguinaldo'),
        ('vacaciones', 'Vacaciones'),
    ]
    
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='pagos')
    tipo = models.CharField(max_length=20, choices=TIPOS)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateField()
    periodo = models.CharField(max_length=50, help_text="Ej: Enero 2024")
    observaciones = models.TextField(blank=True)
    pagado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.empleado} - {self.get_tipo_display()} - ${self.monto}"


class PagoProveedor(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('pagado', 'Pagado'),
        ('vencido', 'Vencido'),
    ]
    
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name='pagos')
    concepto = models.CharField(max_length=200)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_factura = models.DateField()
    fecha_vencimiento = models.DateField()
    fecha_pago = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=10, choices=ESTADOS, default='pendiente')
    numero_factura = models.CharField(max_length=50)
    observaciones = models.TextField(blank=True)
    pagado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.proveedor} - {self.concepto} - ${self.monto}"


class ServicioPublico(models.Model):
    TIPOS = [
        ('luz', 'Electricidad'),
        ('agua', 'Agua'),
        ('gas', 'Gas'),
        ('internet', 'Internet'),
        ('telefono', 'Teléfono'),
        ('seguridad', 'Seguridad'),
        ('limpieza', 'Limpieza'),
    ]
    
    tipo = models.CharField(max_length=20, choices=TIPOS)
    proveedor = models.CharField(max_length=200)
    numero_cuenta = models.CharField(max_length=50)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.proveedor}"


class PagoServicio(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('pagado', 'Pagado'),
        ('vencido', 'Vencido'),
    ]
    
    servicio = models.ForeignKey(ServicioPublico, on_delete=models.CASCADE, related_name='pagos')
    periodo = models.CharField(max_length=50, help_text="Ej: Enero 2024")
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_vencimiento = models.DateField()
    fecha_pago = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=10, choices=ESTADOS, default='pendiente')
    numero_factura = models.CharField(max_length=50)
    observaciones = models.TextField(blank=True)
    pagado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.servicio} - {self.periodo} - ${self.monto}"


class Impuesto(models.Model):
    TIPOS = [
        ('iva', 'IVA'),
        ('ganancias', 'Ganancias'),
        ('ingresos_brutos', 'Ingresos Brutos'),
        ('monotributo', 'Monotributo'),
        ('municipal', 'Municipal'),
    ]
    
    tipo = models.CharField(max_length=20, choices=TIPOS)
    periodo = models.CharField(max_length=50, help_text="Ej: Enero 2024")
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_vencimiento = models.DateField()
    fecha_pago = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=10, choices=[
        ('pendiente', 'Pendiente'),
        ('pagado', 'Pagado'),
        ('vencido', 'Vencido'),
    ], default='pendiente')
    observaciones = models.TextField(blank=True)
    pagado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.periodo} - ${self.monto}"