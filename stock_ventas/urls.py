from django.urls import path
from . import views
from . import views_reportes
from . import views_admin

app_name = 'stock_ventas'

urlpatterns = [
    # POS Principal
    path('', views.pos_dashboard, name='pos_dashboard'),
    path('pos/', views.pos_dashboard, name='pos'),
    
    # Gestión de Caja
    path('caja/abrir/', views.abrir_caja, name='abrir_caja'),
    path('caja/cerrar/', views.cerrar_caja, name='cerrar_caja'),
    
    # Ventas
    path('venta/procesar/', views.procesar_venta, name='procesar_venta'),
    path('ventas/historial/', views.historial_ventas, name='historial_ventas'),
    path('venta/<int:venta_id>/ticket/', views.imprimir_ticket, name='imprimir_ticket'),
    
    # API
    path('api/buscar-productos/', views.buscar_productos, name='buscar_productos'),
    
    # Reportes
    path('reportes/', views_reportes.dashboard_reportes, name='dashboard_reportes'),
    path('reportes/ventas/', views_reportes.reporte_ventas_periodo, name='reporte_ventas_periodo'),
    path('reportes/productos/', views_reportes.reporte_productos_vendidos, name='reporte_productos_vendidos'),
    path('reportes/margenes/', views_reportes.reporte_margenes, name='reporte_margenes'),
    path('reportes/proveedores/', views_reportes.reporte_proveedores, name='reporte_proveedores'),
    
    # Gestión Avanzada (Admin)
    path('admin/', views_admin.dashboard_admin, name='dashboard_admin'),
    path('admin/productos/', views_admin.gestionar_productos, name='gestionar_productos'),
    path('admin/productos/<int:producto_id>/ajustar/', views_admin.ajustar_stock, name='ajustar_stock'),
    path('admin/compras/', views_admin.gestionar_compras, name='gestionar_compras'),
    path('admin/compras/nueva/', views_admin.crear_compra, name='crear_compra'),
    path('admin/compras/<int:compra_id>/recibir/', views_admin.recibir_compra, name='recibir_compra'),
    path('admin/movimientos/', views_admin.historial_movimientos, name='historial_movimientos'),
    path('admin/alertas/', views_admin.alertas_stock, name='alertas_stock'),
]