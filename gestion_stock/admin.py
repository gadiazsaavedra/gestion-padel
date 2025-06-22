from django.contrib import admin
from .models import (
    Producto, CategoriaProducto, MovimientoStock, 
    Proveedor, CompraProveedor, DetalleCompra
)


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'telefono', 'email', 'calificacion', 'activo']
    list_filter = ['calificacion', 'activo']
    search_fields = ['nombre', 'email']
    list_editable = ['calificacion', 'activo']


@admin.register(CategoriaProducto)
class CategoriaProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo', 'activo']
    list_filter = ['tipo', 'activo']
    search_fields = ['nombre']


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = [
        'sku', 'nombre', 'categoria', 'precio_venta', 'precio_compra',
        'stock_actual', 'stock_minimo', 'stock_bajo', 'activo'
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


class DetalleCompraInline(admin.TabularInline):
    model = DetalleCompra
    extra = 1


@admin.register(CompraProveedor)
class CompraProveedorAdmin(admin.ModelAdmin):
    list_display = ['id', 'proveedor', 'fecha_pedido', 'fecha_entrega', 'total', 'estado']
    list_filter = ['estado', 'proveedor']
    inlines = [DetalleCompraInline]
    readonly_fields = ['fecha_pedido']


@admin.register(MovimientoStock)
class MovimientoStockAdmin(admin.ModelAdmin):
    list_display = ['producto', 'fecha', 'tipo', 'cantidad', 'stock_nuevo', 'motivo', 'usuario']
    list_filter = ['tipo', 'fecha']
    search_fields = ['producto__nombre', 'motivo']
    readonly_fields = ['fecha']
