from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from club.models import Pago, Reserva
import json


def es_recepcionista(user):
    return user.is_authenticated and user.groups.filter(name="recepcionistas").exists()


@user_passes_test(es_recepcionista)
def dashboard(request):
    return render(request, "recepcionista/dashboard.html")


@user_passes_test(es_recepcionista)
def emparejador(request):
    return render(request, "recepcionista/emparejador.html")


@user_passes_test(es_recepcionista)
def notificaciones(request):
    return render(request, "recepcionista/notificaciones.html")


@user_passes_test(es_recepcionista)
def gestion_reservas(request):
    return render(request, "recepcionista/gestion_reservas.html")


@user_passes_test(es_recepcionista)
def gestion_stock(request):
    return render(request, "recepcionista/gestion_stock.html")


@user_passes_test(es_recepcionista)
def ventas(request):
    return render(request, "recepcionista/ventas.html")


@user_passes_test(es_recepcionista)
def reportes(request):
    return render(request, "recepcionista/reportes.html")


@user_passes_test(es_recepcionista)
def soporte(request):
    return render(request, "recepcionista/soporte.html")


@user_passes_test(es_recepcionista)
def pagos(request):
    # Obtener pagos pendientes
    pagos_pendientes = Pago.objects.filter(estado='pendiente').order_by('-fecha')
    pagos_recientes = Pago.objects.filter(estado__in=['pagado', 'rechazado']).order_by('-fecha')[:10]
    
    return render(request, "recepcionista/pagos.html", {
        'pagos_pendientes': pagos_pendientes,
        'pagos_recientes': pagos_recientes
    })


@user_passes_test(es_recepcionista)
@csrf_exempt
def confirmar_pago(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'})
    
    try:
        data = json.loads(request.body)
        pago_id = data.get('pago_id')
        accion = data.get('accion')  # 'confirmar' o 'rechazar'
        
        pago = get_object_or_404(Pago, id=pago_id, estado='pendiente')
        
        if accion == 'confirmar':
            # Marcar pago como pagado
            pago.estado = 'pagado'
            pago.save()
            
            # Buscar y actualizar la reserva asociada
            reserva = Reserva.objects.filter(
                jugador=pago.jugador,
                pago_total=pago.monto,
                estado='ocupada'
            ).first()
            
            if reserva:
                reserva.estado = 'pagada'
                reserva.save()
                
                # Crear notificación para el jugador
                from jugadores.models import Notificacion as NotificacionJugador
                NotificacionJugador.objects.create(
                    destinatario=pago.jugador.user,
                    mensaje=f'✅ Pago confirmado: ${pago.monto} - Reserva {reserva.fecha} {reserva.hora}',
                    leida=False
                )
            
            return JsonResponse({
                'success': True, 
                'message': 'Pago confirmado y reserva actualizada'
            })
            
        elif accion == 'rechazar':
            pago.estado = 'rechazado'
            pago.save()
            
            return JsonResponse({
                'success': True, 
                'message': 'Pago rechazado'
            })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
