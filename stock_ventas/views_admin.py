from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, F, Sum
from django.http import JsonResponse
from .models import Producto, Proveedor, CompraProveedor, DetalleCompra, MovimientoStock
import json


def is_admin(user):
    return user.is_staff or user.is_superuser


@login_required
@user_passes_test(is_admin)
def dashboard_admin(request):
    """Dashboard principal para administradores"""
    # Métricas clave
    productos_bajo_stock = Producto.objects.filter(
        stock_actual__lte=F('stock_minimo'), 
        activo=True
    ).count()
    
    compras_pendientes = CompraProveedor.objects.filter(estado='pendiente').count()
    
    total_productos = Producto.objects.filter(activo=True).count()
    
    # Productos críticos (stock = 0)
    productos_sin_stock = Producto.objects.filter(
        stock_actual=0, 
        activo=True
    ).count()
    
    # Últimos movimientos
    movimientos_recientes = MovimientoStock.objects.select_related(
        'producto', 'usuario'
    ).order_by('-fecha')[:10]
    
    # Alertas de stock bajo
    alertas_stock = Producto.objects.filter(
        stock_actual__lte=F('stock_minimo'),
        activo=True
    ).order_by('stock_actual')[:10]
    
    context = {
        'productos_bajo_stock': productos_bajo_stock,
        'compras_pendientes': compras_pendientes,
        'total_productos': total_productos,
        'productos_sin_stock': productos_sin_stock,
        'movimientos_recientes': movimientos_recientes,
        'alertas_stock': alertas_stock,
    }
    
    return render(request, 'stock_ventas/admin_dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def gestionar_productos(request):
    """Gestión de productos"""
    query = request.GET.get('q', '')
    categoria = request.GET.get('categoria', '')
    estado = request.GET.get('estado', 'activo')
    
    productos = Producto.objects.select_related('categoria', 'proveedor_principal')
    
    if query:
        productos = productos.filter(
            Q(nombre__icontains=query) | Q(sku__icontains=query)
        )
    
    if categoria:
        productos = productos.filter(categoria__id=categoria)
    
    if estado == 'activo':
        productos = productos.filter(activo=True)
    elif estado == 'inactivo':
        productos = productos.filter(activo=False)
    elif estado == 'bajo_stock':
        productos = productos.filter(stock_actual__lte=F('stock_minimo'))
    
    productos = productos.order_by('nombre')
    
    from .models import CategoriaProducto
    categorias = CategoriaProducto.objects.filter(activo=True)
    
    context = {
        'productos': productos,
        'categorias': categorias,
        'query': query,
        'categoria_sel': categoria,
        'estado_sel': estado,
    }
    
    return render(request, 'stock_ventas/admin_productos.html', context)


@login_required
@user_passes_test(is_admin)
def ajustar_stock(request, producto_id):
    """Ajustar stock de un producto"""
    producto = get_object_or_404(Producto, id=producto_id)
    
    if request.method == 'POST':
        try:
            nuevo_stock = int(request.POST.get('nuevo_stock'))
            motivo = request.POST.get('motivo', 'Ajuste manual')
            
            if nuevo_stock < 0:
                messages.error(request, 'El stock no puede ser negativo')
                return redirect('stock_ventas:gestionar_productos')
            
            stock_anterior = producto.stock_actual
            diferencia = nuevo_stock - stock_anterior
            
            with transaction.atomic():
                producto.stock_actual = nuevo_stock
                producto.save()
                
                # Registrar movimiento
                MovimientoStock.objects.create(
                    producto=producto,
                    tipo='ajuste',
                    cantidad=diferencia,
                    stock_anterior=stock_anterior,
                    stock_nuevo=nuevo_stock,
                    motivo=motivo,
                    usuario=request.user
                )
            
            messages.success(request, f'Stock de {producto.nombre} ajustado correctamente')
            
        except ValueError:
            messages.error(request, 'Stock debe ser un número válido')
        except Exception as e:
            messages.error(request, f'Error al ajustar stock: {e}')
    
    return redirect('stock_ventas:gestionar_productos')


@login_required
@user_passes_test(is_admin)
def crear_compra(request):
    """Crear nueva compra a proveedor"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            proveedor_id = data.get('proveedor_id')
            productos_compra = data.get('productos', [])
            observaciones = data.get('observaciones', '')
            
            if not productos_compra:
                return JsonResponse({'error': 'Debe agregar productos a la compra'}, status=400)
            
            proveedor = get_object_or_404(Proveedor, id=proveedor_id)
            
            with transaction.atomic():
                # Crear compra
                compra = CompraProveedor.objects.create(
                    proveedor=proveedor,
                    observaciones=observaciones,
                    usuario=request.user
                )
                
                total_compra = 0
                
                # Agregar productos
                for item in productos_compra:
                    producto = get_object_or_404(Producto, id=item['producto_id'])
                    cantidad = int(item['cantidad'])
                    precio_unitario = float(item['precio_unitario'])
                    
                    DetalleCompra.objects.create(
                        compra=compra,
                        producto=producto,
                        cantidad=cantidad,
                        precio_unitario=precio_unitario
                    )
                    
                    total_compra += cantidad * precio_unitario
                
                compra.total = total_compra
                compra.save()
                
                return JsonResponse({
                    'success': True,
                    'compra_id': compra.id,
                    'mensaje': f'Compra #{compra.id} creada exitosamente'
                })
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    # GET - Mostrar formulario
    proveedores = Proveedor.objects.filter(activo=True)
    productos = Producto.objects.filter(activo=True).order_by('nombre')
    
    context = {
        'proveedores': proveedores,
        'productos': productos,
    }
    
    return render(request, 'stock_ventas/admin_crear_compra.html', context)


@login_required
@user_passes_test(is_admin)
def gestionar_compras(request):
    """Gestionar compras a proveedores"""
    estado = request.GET.get('estado', '')
    proveedor = request.GET.get('proveedor', '')
    
    compras = CompraProveedor.objects.select_related('proveedor', 'usuario')
    
    if estado:
        compras = compras.filter(estado=estado)
    
    if proveedor:
        compras = compras.filter(proveedor__id=proveedor)
    
    compras = compras.order_by('-fecha_pedido')
    
    proveedores = Proveedor.objects.filter(activo=True)
    
    context = {
        'compras': compras,
        'proveedores': proveedores,
        'estado_sel': estado,
        'proveedor_sel': proveedor,
    }
    
    return render(request, 'stock_ventas/admin_compras.html', context)


@login_required
@user_passes_test(is_admin)
def recibir_compra(request, compra_id):
    """Marcar compra como recibida y actualizar stock"""
    compra = get_object_or_404(CompraProveedor, id=compra_id)
    
    if compra.estado != 'pendiente':
        messages.warning(request, 'Esta compra ya fue procesada')
        return redirect('stock_ventas:gestionar_compras')
    
    try:
        with transaction.atomic():
            compra.marcar_entregado()
            
        messages.success(request, f'Compra #{compra.id} recibida y stock actualizado')
        
    except Exception as e:
        messages.error(request, f'Error al recibir compra: {e}')
    
    return redirect('stock_ventas:gestionar_compras')


@login_required
@user_passes_test(is_admin)
def historial_movimientos(request):
    """Ver historial completo de movimientos de stock"""
    producto = request.GET.get('producto', '')
    tipo = request.GET.get('tipo', '')
    usuario = request.GET.get('usuario', '')
    
    movimientos = MovimientoStock.objects.select_related('producto', 'usuario')
    
    if producto:
        movimientos = movimientos.filter(producto__nombre__icontains=producto)
    
    if tipo:
        movimientos = movimientos.filter(tipo=tipo)
    
    if usuario:
        movimientos = movimientos.filter(usuario__username__icontains=usuario)
    
    movimientos = movimientos.order_by('-fecha')[:100]  # Limitar a 100 registros
    
    context = {
        'movimientos': movimientos,
        'producto_filtro': producto,
        'tipo_filtro': tipo,
        'usuario_filtro': usuario,
        'tipos_movimiento': MovimientoStock.TIPOS_MOVIMIENTO,
    }
    
    return render(request, 'stock_ventas/admin_historial.html', context)


@login_required
@user_passes_test(is_admin)
def alertas_stock(request):
    """Ver alertas de stock bajo"""
    # Productos con stock bajo
    productos_bajo_stock = Producto.objects.filter(
        stock_actual__lte=F('stock_minimo'),
        activo=True
    ).select_related('categoria', 'proveedor_principal').order_by('stock_actual')
    
    # Productos sin stock
    productos_sin_stock = Producto.objects.filter(
        stock_actual=0,
        activo=True
    ).select_related('categoria', 'proveedor_principal')
    
    context = {
        'productos_bajo_stock': productos_bajo_stock,
        'productos_sin_stock': productos_sin_stock,
    }
    
    return render(request, 'stock_ventas/admin_alertas.html', context)