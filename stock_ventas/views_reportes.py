from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum, Count, Avg, F
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Producto, Caja, Venta, DetalleVenta, Proveedor, CompraProveedor


@login_required
def dashboard_reportes(request):
    """Dashboard principal de reportes"""
    # Datos generales
    total_productos = Producto.objects.filter(activo=True).count()
    productos_bajo_stock = Producto.objects.filter(stock_actual__lte=F('stock_minimo')).count()
    total_ventas_mes = Venta.objects.filter(
        fecha__month=timezone.now().month,
        fecha__year=timezone.now().year
    ).aggregate(total=Sum('total'))['total'] or 0
    
    # Productos más vendidos (últimos 30 días)
    fecha_inicio = timezone.now() - timedelta(days=30)
    productos_vendidos = DetalleVenta.objects.filter(
        venta__fecha__gte=fecha_inicio
    ).values(
        'producto__nombre'
    ).annotate(
        total_vendido=Sum('cantidad'),
        ingresos=Sum(F('cantidad') * F('precio_unitario'))
    ).order_by('-total_vendido')[:10]
    
    # Ventas por método de pago
    ventas_por_metodo = Venta.objects.filter(
        fecha__gte=fecha_inicio
    ).values('metodo_pago').annotate(
        total=Sum('total'),
        cantidad=Count('id')
    ).order_by('-total')
    
    context = {
        'total_productos': total_productos,
        'productos_bajo_stock': productos_bajo_stock,
        'total_ventas_mes': total_ventas_mes,
        'productos_vendidos': productos_vendidos,
        'ventas_por_metodo': ventas_por_metodo,
    }
    
    return render(request, 'stock_ventas/dashboard_reportes.html', context)


@login_required
def reporte_ventas_periodo(request):
    """Reporte de ventas por período"""
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    if not fecha_inicio:
        fecha_inicio = (timezone.now() - timedelta(days=30)).date()
    else:
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
    
    if not fecha_fin:
        fecha_fin = timezone.now().date()
    else:
        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
    
    # Ventas del período
    ventas = Venta.objects.filter(
        fecha__date__gte=fecha_inicio,
        fecha__date__lte=fecha_fin
    ).order_by('-fecha')
    
    # Resumen
    resumen = ventas.aggregate(
        total_ventas=Sum('total'),
        cantidad_ventas=Count('id'),
        promedio_venta=Avg('total')
    )
    
    # Ventas por día
    ventas_por_dia = ventas.extra(
        select={'dia': 'DATE(fecha)'}
    ).values('dia').annotate(
        total=Sum('total'),
        cantidad=Count('id')
    ).order_by('dia')
    
    context = {
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'ventas': ventas,
        'resumen': resumen,
        'ventas_por_dia': ventas_por_dia,
    }
    
    return render(request, 'stock_ventas/reporte_ventas_periodo.html', context)


@login_required
def reporte_productos_vendidos(request):
    """Análisis de productos más vendidos"""
    dias = int(request.GET.get('dias', 30))
    fecha_inicio = timezone.now() - timedelta(days=dias)
    
    productos_vendidos = DetalleVenta.objects.filter(
        venta__fecha__gte=fecha_inicio
    ).values(
        'producto__nombre',
        'producto__sku',
        'producto__categoria__nombre',
        'producto__precio_venta',
        'producto__precio_compra'
    ).annotate(
        total_vendido=Sum('cantidad'),
        ingresos=Sum(F('cantidad') * F('precio_unitario')),
        ganancia=Sum(F('cantidad') * (F('precio_unitario') - F('producto__precio_compra')))
    ).order_by('-total_vendido')
    
    context = {
        'productos_vendidos': productos_vendidos,
        'dias': dias,
        'fecha_inicio': fecha_inicio,
    }
    
    return render(request, 'stock_ventas/reporte_productos_vendidos.html', context)


@login_required
def reporte_margenes(request):
    """Control de márgenes de ganancia"""
    productos = Producto.objects.filter(activo=True).annotate(
        margen_calculado=((F('precio_venta') - F('precio_compra')) / F('precio_compra')) * 100
    ).order_by('-margen_calculado')
    
    # Productos con margen bajo (menos del 20%)
    productos_margen_bajo = productos.filter(margen_calculado__lt=20)
    
    # Productos con mejor margen
    productos_mejor_margen = productos.filter(margen_calculado__gte=50)[:10]
    
    context = {
        'productos': productos,
        'productos_margen_bajo': productos_margen_bajo,
        'productos_mejor_margen': productos_mejor_margen,
    }
    
    return render(request, 'stock_ventas/reporte_margenes.html', context)


@login_required
def reporte_proveedores(request):
    """Reportes de proveedores"""
    proveedores = Proveedor.objects.filter(activo=True).annotate(
        total_compras=Count('compras'),
        monto_total=Sum('compras__total'),
        productos_suministrados=Count('producto', distinct=True)
    ).order_by('-monto_total')
    
    # Compras recientes
    compras_recientes = CompraProveedor.objects.filter(
        fecha_pedido__gte=timezone.now() - timedelta(days=90)
    ).order_by('-fecha_pedido')[:20]
    
    context = {
        'proveedores': proveedores,
        'compras_recientes': compras_recientes,
    }
    
    return render(request, 'stock_ventas/reporte_proveedores.html', context)