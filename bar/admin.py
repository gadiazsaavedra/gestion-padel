from django.contrib import admin
from .models import Venta, DetalleVenta, Caja, MovimientoCaja


class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 1
    readonly_fields = ['subtotal']


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ['id', 'fecha', 'total', 'metodo_pago', 'usuario', 'caja']
    list_filter = ['fecha', 'metodo_pago', 'caja']
    search_fields = ['id', 'observaciones']
    inlines = [DetalleVentaInline]
    readonly_fields = ['total']


@admin.register(Caja)
class CajaAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "fecha_apertura",
        "fecha_cierre",
        "saldo_inicial",
        "saldo_final",
        "abierta",
    )
    search_fields = ("id",)
    list_filter = ("abierta",)


@admin.register(MovimientoCaja)
class MovimientoCajaAdmin(admin.ModelAdmin):
    list_display = ("caja", "monto", "concepto", "fecha", "usuario")
    search_fields = ("caja__id", "concepto")
    list_filter = ("caja", "fecha")
