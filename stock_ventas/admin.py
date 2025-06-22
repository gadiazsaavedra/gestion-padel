from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Proveedor, CategoriaProducto, Producto, Caja, Venta, DetalleVenta,
    MovimientoStock, MovimientoCaja, CompraProveedor, DetalleCompra
)


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'telefono', 'email', 'calificacion', 'promedio_entrega', 'activo']
    list_filter = ['calificacion', 'activo']
    search_fields = ['nombre', 'email']
    list_editable = ['calificacion', 'activo']
    
    def promedio_entrega(self, obj):
        promedio = obj.promedio_entrega_dias
        if promedio is not None:
            return f"{promedio:.1f} días"
        return "Sin datos"
    promedio_entrega.short_description = "Promedio Entrega"


@admin.register(CategoriaProducto)
class CategoriaProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo', 'activo']
    list_filter = ['tipo', 'activo']
    search_fields = ['nombre']


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = [
        'sku', 'nombre', 'categoria', 'precio_venta', 'precio_compra',
        'stock_actual', 'stock_minimo', 'stock_status', 'margen', 'activo'
    ]
    list_filter = ['categoria', 'activo', 'proveedor_principal']
    search_fields = ['nombre', 'sku', 'marca', 'modelo']
    list_editable = ['precio_venta', 'precio_compra', 'stock_actual', 'activo']
    readonly_fields = ['fecha_alta', 'ultima_modificacion', 'margen_ganancia']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('sku', 'nombre', 'descripcion', 'categoria', 'imagen')
        }),
        ('Precios y Stock', {
            'fields': ('precio_compra', 'precio_venta', 'stock_actual', 'stock_minimo')
        }),
        ('Atributos Específicos', {
            'fields': ('marca', 'modelo', 'peso', 'material', 'color'),
            'classes': ('collapse',)
        }),
        ('Control', {
            'fields': ('proveedor_principal', 'activo', 'fecha_alta', 'ultima_modificacion')
        })
    )
    
    def stock_status(self, obj):
        if obj.stock_bajo:
            return format_html('<span style="color: red;">⚠️ Bajo</span>')
        return format_html('<span style="color: green;">✅ OK</span>')
    stock_status.short_description = "Estado Stock"
    
    def margen(self, obj):
        return f"{obj.margen_ganancia:.1f}%"
    margen.short_description = "Margen"


class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 0
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
    list_display = [
        'id', 'fecha_apertura', 'fecha_cierre', 'saldo_inicial', 
        'total_ventas', 'saldo_teorico', 'saldo_final', 'diferencia', 'abierta'
    ]
    list_filter = ['abierta', 'fecha_apertura']
    readonly_fields = ['total_ventas', 'saldo_teorico', 'diferencia_arqueo']
    
    def diferencia(self, obj):
        diff = obj.diferencia_arqueo
        if diff is not None:
            color = 'red' if diff != 0 else 'green'
            return format_html(f'<span style="color: {color};">${diff}</span>')
        return "-"
    diferencia.short_description = "Diferencia"


class DetalleCompraInline(admin.TabularInline):
    model = DetalleCompra
    extra = 1
    readonly_fields = ['subtotal']


@admin.register(CompraProveedor)
class CompraProveedorAdmin(admin.ModelAdmin):
    list_display = ['id', 'proveedor', 'fecha_pedido', 'fecha_entrega', 'total', 'estado']
    list_filter = ['estado', 'proveedor', 'fecha_pedido']
    inlines = [DetalleCompraInline]
    readonly_fields = ['fecha_pedido', 'total']
    actions = ['marcar_entregado']
    
    def marcar_entregado(self, request, queryset):
        for compra in queryset.filter(estado='pendiente'):
            compra.marcar_entregado()
        self.message_user(request, f"{queryset.count()} compras marcadas como entregadas")
    marcar_entregado.short_description = "Marcar como entregado"


@admin.register(MovimientoStock)
class MovimientoStockAdmin(admin.ModelAdmin):
    list_display = ['producto', 'fecha', 'tipo', 'cantidad', 'stock_nuevo', 'motivo', 'usuario']
    list_filter = ['tipo', 'fecha', 'producto__categoria']
    search_fields = ['producto__nombre', 'motivo']
    readonly_fields = ['fecha']


@admin.register(MovimientoCaja)
class MovimientoCajaAdmin(admin.ModelAdmin):
    list_display = ['caja', 'fecha', 'tipo', 'concepto', 'monto', 'usuario']
    list_filter = ['tipo', 'fecha', 'caja']
    search_fields = ['concepto']
    readonly_fields = ['fecha']