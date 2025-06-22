from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Sum, Count, Avg, F
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Producto, Caja, Venta, DetalleVenta, MovimientoCaja, Proveedor, CompraProveedor
import json


@login_required
def pos_dashboard(request):
    """Dashboard principal del POS"""
    # Verificar si hay caja abierta
    caja_abierta = Caja.objects.filter(abierta=True).first()
    
    if not caja_abierta:
        return redirect('stock_ventas:abrir_caja')
    
    # Productos más vendidos para acceso rápido
    productos_populares = Producto.objects.filter(
        activo=True, 
        stock_actual__gt=0
    ).order_by('-stock_actual')[:12]
    
    context = {
        'caja': caja_abierta,
        'productos_populares': productos_populares,
        'total_ventas_hoy': caja_abierta.total_ventas,
    }
    
    return render(request, 'stock_ventas/pos_dashboard.html', context)


@login_required
def buscar_productos(request):
    """API para buscar productos en tiempo real"""
    query = request.GET.get('q', '')
    
    if len(query) < 2:
        return JsonResponse({'productos': []})
    
    productos = Producto.objects.filter(
        Q(nombre__icontains=query) | Q(sku__icontains=query),
        activo=True,
        stock_actual__gt=0
    )[:10]
    
    productos_data = []
    for producto in productos:
        productos_data.append({
            'id': producto.id,
            'sku': producto.sku,
            'nombre': producto.nombre,
            'precio': float(producto.precio_venta),
            'stock': producto.stock_actual,
            'imagen': producto.imagen.url if producto.imagen else None
        })
    
    return JsonResponse({'productos': productos_data})


@login_required
def procesar_venta(request):
    """Procesar venta desde POS"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        productos_venta = data.get('productos', [])
        metodo_pago = data.get('metodo_pago', 'efectivo')
        observaciones = data.get('observaciones', '')
        
        if not productos_venta:
            return JsonResponse({'error': 'No hay productos en la venta'}, status=400)
        
        # Verificar caja abierta
        caja = Caja.objects.filter(abierta=True).first()
        if not caja:
            return JsonResponse({'error': 'No hay caja abierta'}, status=400)
        
        with transaction.atomic():
            # Crear venta
            venta = Venta.objects.create(
                caja=caja,
                total=0,
                metodo_pago=metodo_pago,
                usuario=request.user,
                observaciones=observaciones
            )
            
            total_venta = 0
            
            # Procesar cada producto
            for item in productos_venta:
                producto = get_object_or_404(Producto, id=item['producto_id'])
                cantidad = int(item['cantidad'])
                
                # Verificar stock
                if producto.stock_actual < cantidad:
                    raise Exception(f'Stock insuficiente para {producto.nombre}')
                
                # Crear detalle de venta (esto actualiza stock automáticamente)
                detalle = DetalleVenta.objects.create(
                    venta=venta,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=producto.precio_venta
                )
                
                total_venta += detalle.subtotal
            
            # Actualizar total de venta
            venta.total = total_venta
            venta.save()
            
            return JsonResponse({
                'success': True,
                'venta_id': venta.id,
                'total': float(venta.total),
                'mensaje': f'Venta procesada exitosamente. Total: ${venta.total}'
            })
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def abrir_caja(request):
    """Abrir caja para el turno"""
    # Verificar si ya hay caja abierta
    if Caja.objects.filter(abierta=True).exists():
        messages.warning(request, 'Ya hay una caja abierta')
        return redirect('stock_ventas:pos_dashboard')
    
    if request.method == 'POST':
        saldo_inicial = request.POST.get('saldo_inicial', 0)
        observaciones = request.POST.get('observaciones', '')
        
        caja = Caja.objects.create(
            saldo_inicial=saldo_inicial,
            usuario_apertura=request.user,
            observaciones_apertura=observaciones
        )
        
        messages.success(request, f'Caja abierta exitosamente con saldo inicial ${saldo_inicial}')
        return redirect('stock_ventas:pos_dashboard')
    
    return render(request, 'stock_ventas/abrir_caja.html')


@login_required
def cerrar_caja(request):
    """Cerrar caja del turno"""
    caja = get_object_or_404(Caja, abierta=True)
    
    if request.method == 'POST':
        saldo_final = request.POST.get('saldo_final')
        observaciones = request.POST.get('observaciones', '')
        
        from decimal import Decimal
        caja.saldo_final = Decimal(saldo_final)
        caja.observaciones_cierre = observaciones
        caja.abierta = False
        caja.usuario_cierre = request.user
        caja.save()
        
        diferencia = caja.diferencia_arqueo
        if diferencia == 0:
            messages.success(request, 'Caja cerrada correctamente. Arqueo perfecto!')
        else:
            tipo_msg = messages.warning if abs(diferencia) < 100 else messages.error
            tipo_msg(request, f'Caja cerrada. Diferencia en arqueo: ${diferencia}')
        
        return redirect('stock_ventas:pos_dashboard')
    
    context = {
        'caja': caja,
        'saldo_teorico': caja.saldo_teorico,
    }
    
    return render(request, 'stock_ventas/cerrar_caja.html', context)


@login_required
def historial_ventas(request):
    """Ver historial de ventas del día"""
    caja = Caja.objects.filter(abierta=True).first()
    
    if caja:
        ventas = caja.ventas.all().order_by('-fecha')
    else:
        ventas = Venta.objects.filter(fecha__date=timezone.now().date()).order_by('-fecha')
    
    context = {
        'ventas': ventas,
        'caja': caja,
    }
    
    return render(request, 'stock_ventas/historial_ventas.html', context)


@login_required
def imprimir_ticket(request, venta_id):
    """Generar ticket de venta para impresión"""
    venta = get_object_or_404(Venta, id=venta_id)
    
    context = {
        'venta': venta,
        'detalles': venta.detalles.all(),
        'fecha_impresion': timezone.now(),
    }
    
    return render(request, 'stock_ventas/ticket_venta.html', context)