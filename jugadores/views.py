from django.shortcuts import render, get_object_or_404, redirect
from .utils import buscar_grupos
from django.contrib import messages
from .models import GrupoSugerido, Notificacion
from django.contrib.auth.models import Group
from django.db.models import Count
from django.contrib.auth.decorators import login_required, user_passes_test
from club.models import DisponibilidadJugador, Jugador, Reserva
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.utils import timezone
from jugadores.models import Notificacion as NotificacionJugador
from club.models import Pago, Ranking, Torneo
from club.forms import PagoJugadorForm, JugadorForm, CambioPasswordForm
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import update_session_auth_hash
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json


def sugerir_grupo(request):
    if request.method == "POST":
        nivel = request.POST.get("nivel")
        genero = request.POST.get("genero")
        dia = request.POST.get("dia")
        # Buscar grupos compatibles usando DisponibilidadJugador
        grupos = buscar_grupos(nivel, genero, dia=dia)
        if grupos:
            creados = 0
            for grupo in grupos:
                jugadores_ids = sorted([j.id for j in grupo])
                existe = (
                    GrupoSugerido.objects.annotate(num_jugadores=Count("jugadores"))
                    .filter(
                        nivel=nivel,
                        genero=genero,
                        num_jugadores=len(jugadores_ids),
                        jugadores__id__in=jugadores_ids,
                    )
                    .distinct()
                )
                existe = [
                    g
                    for g in existe
                    if set(g.jugadores.values_list("id", flat=True))
                    == set(jugadores_ids)
                ]
                if not existe:
                    grupo_sugerido = GrupoSugerido.objects.create(
                        nivel=nivel,
                        genero=genero,
                        disponibilidad={"dia": dia},
                        criterios={
                            "nivel": nivel,
                            "genero": genero,
                            "dia": dia,
                        },
                        sugerido_por=(
                            request.user if request.user.is_authenticated else None
                        ),
                        estado="nuevo",
                    )
                    grupo_sugerido.jugadores.set(grupo)
                    creados += 1
            # Notificación interna a recepcionistas
            try:
                recepcionistas = Group.objects.get(name="recepcionistas").user_set.all()
                mensaje = f"Se han sugerido {creados} grupo(s) nuevos para nivel {nivel}, género {genero}."
                for user in recepcionistas:
                    Notificacion.objects.create(destinatario=user, mensaje=mensaje)
            except Group.DoesNotExist:
                pass
            if creados:
                messages.success(
                    request,
                    f"¡Se encontraron {len(grupos)} grupo(s) sugeridos! ({creados} nuevos registrados)",
                )
            else:
                messages.info(
                    request,
                    "No se registraron grupos nuevos (ya existen en la base de datos).",
                )
            return render(
                request, "jugadores/grupos_sugeridos.html", {"grupos": grupos}
            )
        else:
            messages.error(request, "No se encontró ningún grupo compatible.")
    return render(request, "jugadores/sugerir_grupo.html")


@login_required
def notificaciones_panel(request):
    notificaciones = request.user.notificacion_set.order_by("-id")[:30]
    return render(
        request, "club/notificaciones_panel.html", {"notificaciones": notificaciones}
    )


@login_required
@user_passes_test(
    lambda u: u.is_superuser or u.groups.filter(name="recepcionistas").exists()
)
def gestionar_grupo_sugerido(request, grupo_id, accion):
    grupo = get_object_or_404(GrupoSugerido, id=grupo_id)
    if accion == "aceptar":
        grupo.estado = "aceptado"
        grupo.save()
        messages.success(request, "Grupo sugerido aceptado.")
    elif accion == "rechazar":
        grupo.estado = "rechazado"
        grupo.save()
        messages.info(request, "Grupo sugerido rechazado.")
    return redirect("notificaciones_panel")


class PanelJugadorView(LoginRequiredMixin, TemplateView):
    template_name = "jugadores/panel_jugador.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        jugador = self.request.user
        context["mensajes_bienvenida"] = [
            f"¡Hola {jugador.first_name or jugador.username}! Este es tu panel personalizado.",
            "Recuerda revisar tus próximas reservas y mantener tus datos actualizados.",
        ]
        # Ejemplo de notificaciones (reemplaza por lógica real)
        context["notificaciones"] = NotificacionJugador.objects.filter(
            destinatario=jugador, leida=False
        ).order_by("-fecha_creacion")
        return context


@login_required
def mis_reservas(request):
    user = request.user
    try:
        jugador = user.jugador
    except Jugador.DoesNotExist:
        jugador = None
    proximas = []
    pasadas = []
    if jugador:
        hoy = timezone.localdate()
        proximas = Reserva.objects.filter(jugador=jugador, fecha__gte=hoy).order_by(
            "fecha", "hora"
        )
        pasadas = Reserva.objects.filter(jugador=jugador, fecha__lt=hoy).order_by(
            "-fecha", "-hora"
        )
    return render(
        request,
        "jugadores/mis_reservas.html",
        {"proximas_reservas": proximas, "reservas_pasadas": pasadas},
    )


def pagos_jugador(request):
    from django.db.models import Sum, Count, Q
    from datetime import datetime, timedelta
    import json
    
    jugador = (
        request.user.jugador
        if request.user.is_authenticated and hasattr(request.user, "jugador")
        else None
    )
    pagos = []
    deuda = 0
    form = None
    estadisticas = {}
    grafico_gastos = {}
    
    if jugador:
        # Filtros
        filtro_estado = request.GET.get('estado', 'todos')  # todos, pendiente, pagado
        filtro_mes = request.GET.get('mes', '')  # YYYY-MM
        
        # Base queryset
        pagos_qs = Pago.objects.filter(jugador=jugador)
        
        # Aplicar filtros
        if filtro_estado != 'todos':
            pagos_qs = pagos_qs.filter(estado=filtro_estado)
        
        if filtro_mes:
            try:
                year, month = filtro_mes.split('-')
                pagos_qs = pagos_qs.filter(fecha__year=year, fecha__month=month)
            except:
                pass
        
        pagos = pagos_qs.order_by("-fecha")
        deuda = jugador.calcular_deuda()
        
        # === ESTADÍSTICAS ===
        total_pagos = Pago.objects.filter(jugador=jugador).count()
        pagos_confirmados = Pago.objects.filter(jugador=jugador, estado='pagado').count()
        pagos_pendientes = Pago.objects.filter(jugador=jugador, estado='pendiente').count()
        
        # Total gastado
        total_gastado = Pago.objects.filter(
            jugador=jugador, estado='pagado'
        ).aggregate(total=Sum('monto'))['total'] or 0
        
        # Gasto promedio mensual (últimos 6 meses)
        hace_6_meses = datetime.now().date() - timedelta(days=180)
        gasto_6_meses = Pago.objects.filter(
            jugador=jugador, estado='pagado', fecha__gte=hace_6_meses
        ).aggregate(total=Sum('monto'))['total'] or 0
        promedio_mensual = gasto_6_meses / 6 if gasto_6_meses > 0 else 0
        
        # Gasto este mes
        hoy = datetime.now().date()
        inicio_mes = hoy.replace(day=1)
        gasto_mes_actual = Pago.objects.filter(
            jugador=jugador, estado='pagado',
            fecha__gte=inicio_mes, fecha__lte=hoy
        ).aggregate(total=Sum('monto'))['total'] or 0
        
        # Método de pago más usado
        metodo_favorito = Pago.objects.filter(
            jugador=jugador, estado='pagado'
        ).values('metodo').annotate(
            count=Count('metodo')
        ).order_by('-count').first()
        
        estadisticas = {
            'total_pagos': total_pagos,
            'pagos_confirmados': pagos_confirmados,
            'pagos_pendientes': pagos_pendientes,
            'total_gastado': total_gastado,
            'promedio_mensual': promedio_mensual,
            'gasto_mes_actual': gasto_mes_actual,
            'metodo_favorito': metodo_favorito['metodo'] if metodo_favorito else 'N/A',
        }
        
        # === GRÁFICO DE GASTOS MENSUALES ===
        meses = []
        gastos_por_mes = []
        
        for i in range(6):
            mes = datetime.now().date().replace(day=1) - timedelta(days=30*i)
            mes_siguiente = (mes.replace(day=28) + timedelta(days=4)).replace(day=1)
            
            gasto_mes = Pago.objects.filter(
                jugador=jugador, estado='pagado',
                fecha__gte=mes, fecha__lt=mes_siguiente
            ).aggregate(total=Sum('monto'))['total'] or 0
            
            meses.insert(0, mes.strftime('%b %Y'))
            gastos_por_mes.insert(0, float(gasto_mes))
        
        grafico_gastos = {
            "type": "line",
            "data": {
                "labels": meses,
                "datasets": [
                    {
                        "label": "Gastos ($)",
                        "backgroundColor": "#10b981",
                        "borderColor": "#10b981",
                        "data": gastos_por_mes,
                        "fill": True,
                    }
                ],
            },
            "options": {
                "responsive": True,
                "plugins": {"legend": {"position": "top"}},
                "scales": {
                    "y": {
                        "beginAtZero": True,
                        "ticks": {
                            "callback": "function(value) { return '$' + value; }"
                        }
                    }
                }
            },
        }
        
        # Formulario
        if request.method == "POST":
            form = PagoJugadorForm(request.POST)
            if form.is_valid():
                nuevo_pago = form.save(commit=False)
                nuevo_pago.jugador = jugador
                nuevo_pago.estado = "pendiente"  # Siempre pendiente hasta validación
                nuevo_pago.save()
                
                # Crear notificación
                from jugadores.models import Notificacion as NotificacionJugador
                NotificacionJugador.objects.create(
                    destinatario=request.user,
                    mensaje=f'💳 Nuevo pago registrado: ${nuevo_pago.monto} - Pendiente de validación',
                    leida=False
                )
                
                messages.success(
                    request,
                    "Pago registrado correctamente. Será validado por la administración.",
                )
                return redirect("jugadores:pagos_jugador")
        else:
            form = PagoJugadorForm()
    
    return render(
        request,
        "jugadores/pagos_jugador.html",
        {
            "pagos": pagos, 
            "deuda": deuda, 
            "form": form,
            "estadisticas": estadisticas,
            "grafico_gastos": json.dumps(grafico_gastos),
            "filtro_estado": filtro_estado,
            "filtro_mes": filtro_mes,
        },
    )


def ranking(request):
    from django.db.models import Sum, Count, Avg
    from datetime import datetime, timedelta
    import json
    
    user = request.user
    jugador = getattr(user, "jugador", None)
    ranking_data = []
    estadisticas_personales = {}
    progreso_chart = {}
    comparacion_chart = {}
    
    if jugador:
        # Ranking por torneos (existente)
        torneos = Torneo.objects.filter(activo=True)
        for torneo in torneos:
            ranking_qs = Ranking.objects.filter(torneo=torneo).order_by("-puntos")
            ranking_list = list(ranking_qs)
            try:
                mi_ranking = ranking_qs.get(jugador=jugador)
                posicion = ranking_list.index(mi_ranking) + 1
                ranking_data.append({
                    "torneo": torneo,
                    "puntos": mi_ranking.puntos,
                    "posicion": posicion,
                    "total": len(ranking_list),
                })
            except Ranking.DoesNotExist:
                ranking_data.append({
                    "torneo": torneo,
                    "puntos": None,
                    "posicion": None,
                    "total": len(ranking_list),
                })
        
        # === ESTADÍSTICAS PERSONALES ===
        # Reservas del jugador
        total_reservas = Reserva.objects.filter(jugador=jugador).count()
        reservas_pagadas = Reserva.objects.filter(jugador=jugador, estado='pagada').count()
        reservas_canceladas = Reserva.objects.filter(jugador=jugador, estado='cancelada').count()
        
        # Gastos del jugador
        total_gastado = Pago.objects.filter(
            jugador=jugador, estado='pagado'
        ).aggregate(total=Sum('monto'))['total'] or 0
        
        # Promedio mensual
        hace_6_meses = datetime.now().date() - timedelta(days=180)
        gasto_6_meses = Pago.objects.filter(
            jugador=jugador, estado='pagado', fecha__gte=hace_6_meses
        ).aggregate(total=Sum('monto'))['total'] or 0
        promedio_mensual = gasto_6_meses / 6 if gasto_6_meses > 0 else 0
        
        # Horario favorito
        horario_favorito = Reserva.objects.filter(
            jugador=jugador, estado__in=['ocupada', 'pagada']
        ).values('hora').annotate(
            count=Count('hora')
        ).order_by('-count').first()
        
        # Puntos totales en todos los torneos
        puntos_totales = Ranking.objects.filter(
            jugador=jugador
        ).aggregate(total=Sum('puntos'))['total'] or 0
        
        estadisticas_personales = {
            'total_reservas': total_reservas,
            'reservas_pagadas': reservas_pagadas,
            'reservas_canceladas': reservas_canceladas,
            'total_gastado': total_gastado,
            'promedio_mensual': promedio_mensual,
            'horario_favorito': horario_favorito['hora'].strftime('%H:%M') if horario_favorito else 'N/A',
            'puntos_totales': puntos_totales,
        }
        
        # === GRÁFICO DE PROGRESO (últimos 6 meses) ===
        meses = []
        gastos_por_mes = []
        reservas_por_mes = []
        
        for i in range(6):
            mes = datetime.now().date().replace(day=1) - timedelta(days=30*i)
            mes_siguiente = (mes.replace(day=28) + timedelta(days=4)).replace(day=1)
            
            gasto_mes = Pago.objects.filter(
                jugador=jugador, estado='pagado',
                fecha__gte=mes, fecha__lt=mes_siguiente
            ).aggregate(total=Sum('monto'))['total'] or 0
            
            reservas_mes = Reserva.objects.filter(
                jugador=jugador, estado__in=['ocupada', 'pagada'],
                fecha__gte=mes, fecha__lt=mes_siguiente
            ).count()
            
            meses.insert(0, mes.strftime('%b %Y'))
            gastos_por_mes.insert(0, float(gasto_mes))
            reservas_por_mes.insert(0, reservas_mes)
        
        progreso_chart = {
            "type": "line",
            "data": {
                "labels": meses,
                "datasets": [
                    {
                        "label": "Gastos ($)",
                        "backgroundColor": "#10b981",
                        "borderColor": "#10b981",
                        "data": gastos_por_mes,
                        "yAxisID": "y",
                    },
                    {
                        "label": "Reservas",
                        "backgroundColor": "#3b82f6",
                        "borderColor": "#3b82f6",
                        "data": reservas_por_mes,
                        "yAxisID": "y1",
                    }
                ],
            },
            "options": {
                "responsive": True,
                "plugins": {"legend": {"position": "top"}},
                "scales": {
                    "y": {"type": "linear", "display": True, "position": "left"},
                    "y1": {"type": "linear", "display": True, "position": "right", "grid": {"drawOnChartArea": False}}
                }
            },
        }
        
        # === COMPARACIÓN CON OTROS JUGADORES ===
        # Top 5 jugadores por puntos totales
        top_jugadores = Ranking.objects.values(
            'jugador__nombre', 'jugador__apellido'
        ).annotate(
            total_puntos=Sum('puntos')
        ).order_by('-total_puntos')[:5]
        
        # Encontrar posición del jugador actual
        mi_posicion = 0
        for i, j in enumerate(top_jugadores):
            if (j['jugador__nombre'] == jugador.nombre and 
                j['jugador__apellido'] == jugador.apellido):
                mi_posicion = i
                break
        
        comparacion_chart = {
            "type": "bar",
            "data": {
                "labels": [f"{j['jugador__nombre']} {j['jugador__apellido']}" for j in top_jugadores],
                "datasets": [
                    {
                        "label": "Puntos Totales",
                        "backgroundColor": [
                            "#ef4444" if i == mi_posicion else "#6b7280" 
                            for i in range(len(top_jugadores))
                        ],
                        "data": [j['total_puntos'] for j in top_jugadores],
                    }
                ],
            },
            "options": {
                "responsive": True,
                "plugins": {"legend": {"display": False}},
            },
        }
    
    return render(request, "jugadores/ranking.html", {
        "ranking_data": ranking_data,
        "estadisticas_personales": estadisticas_personales,
        "progreso_chart": json.dumps(progreso_chart),
        "comparacion_chart": json.dumps(comparacion_chart),
    })


def notificaciones_jugador(request):
    user = request.user
    notificaciones = []
    estadisticas = {}
    
    if user.is_authenticated:
        # Filtros
        filtro = request.GET.get('filtro', 'todas')  # todas, no_leidas, leidas
        categoria = request.GET.get('categoria', 'todas')  # todas, pago, reserva, sistema
        
        # Base queryset
        notificaciones_qs = user.notificaciones.all()
        
        # Aplicar filtros
        if filtro == 'no_leidas':
            notificaciones_qs = notificaciones_qs.filter(leida=False)
        elif filtro == 'leidas':
            notificaciones_qs = notificaciones_qs.filter(leida=True)
        
        # Filtro por categoría (basado en palabras clave en el mensaje)
        if categoria == 'pago':
            notificaciones_qs = notificaciones_qs.filter(
                mensaje__icontains='pago'
            ) | notificaciones_qs.filter(
                mensaje__icontains='confirmado'
            ) | notificaciones_qs.filter(
                mensaje__icontains='reembolso'
            )
        elif categoria == 'reserva':
            notificaciones_qs = notificaciones_qs.filter(
                mensaje__icontains='reserva'
            ) | notificaciones_qs.filter(
                mensaje__icontains='cancelada'
            ) | notificaciones_qs.filter(
                mensaje__icontains='turno'
            )
        elif categoria == 'sistema':
            notificaciones_qs = notificaciones_qs.filter(
                mensaje__icontains='sistema'
            ) | notificaciones_qs.filter(
                mensaje__icontains='actualización'
            )
        
        notificaciones = notificaciones_qs.order_by("-fecha_creacion")
        
        # Estadísticas
        total = user.notificaciones.count()
        no_leidas = user.notificaciones.filter(leida=False).count()
        leidas = user.notificaciones.filter(leida=True).count()
        
        # Notificaciones por categoría
        pagos = user.notificaciones.filter(
            mensaje__icontains='pago'
        ).count() + user.notificaciones.filter(
            mensaje__icontains='confirmado'
        ).count()
        
        reservas = user.notificaciones.filter(
            mensaje__icontains='reserva'
        ).count() + user.notificaciones.filter(
            mensaje__icontains='cancelada'
        ).count()
        
        estadisticas = {
            'total': total,
            'no_leidas': no_leidas,
            'leidas': leidas,
            'pagos': pagos,
            'reservas': reservas,
        }
    
    return render(
        request,
        "jugadores/notificaciones_jugador.html",
        {
            "notificaciones": notificaciones,
            "estadisticas": estadisticas,
            "filtro_actual": request.GET.get('filtro', 'todas'),
            "categoria_actual": request.GET.get('categoria', 'todas'),
        },
    )


def perfil_jugador(request):
    from django.db.models import Sum, Count
    from datetime import datetime, timedelta
    
    user = request.user
    jugador = getattr(user, "jugador", None)
    if not jugador:
        return redirect("jugadores:panel_jugador")
    
    # === ESTADÍSTICAS DEL PERFIL ===
    # Actividad general
    total_reservas = Reserva.objects.filter(jugador=jugador).count()
    reservas_activas = Reserva.objects.filter(
        jugador=jugador, estado__in=['ocupada', 'pagada']
    ).count()
    
    # Gastos
    total_gastado = Pago.objects.filter(
        jugador=jugador, estado='pagado'
    ).aggregate(total=Sum('monto'))['total'] or 0
    
    # Actividad reciente (último mes)
    hace_un_mes = datetime.now().date() - timedelta(days=30)
    actividad_reciente = Reserva.objects.filter(
        jugador=jugador, fecha__gte=hace_un_mes
    ).count()
    
    # Puntos de ranking
    puntos_totales = Ranking.objects.filter(
        jugador=jugador
    ).aggregate(total=Sum('puntos'))['total'] or 0
    
    # Fecha de registro
    fecha_registro = jugador.user.date_joined
    dias_miembro = (datetime.now().date() - fecha_registro.date()).days
    
    estadisticas_perfil = {
        'total_reservas': total_reservas,
        'reservas_activas': reservas_activas,
        'total_gastado': total_gastado,
        'actividad_reciente': actividad_reciente,
        'puntos_totales': puntos_totales,
        'dias_miembro': dias_miembro,
        'fecha_registro': fecha_registro,
    }
    
    password_form = CambioPasswordForm(user)
    if request.method == "POST":
        if "cambiar_password" in request.POST:
            password_form = CambioPasswordForm(user, request.POST)
            form = JugadorForm(
                instance=jugador
            )  # No procesar datos de perfil en este POST
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, user)
                
                # Crear notificación
                from jugadores.models import Notificacion as NotificacionJugador
                NotificacionJugador.objects.create(
                    destinatario=user,
                    mensaje='🔒 Contraseña actualizada correctamente por seguridad',
                    leida=False
                )
                
                messages.success(request, "Contraseña actualizada correctamente.")
                return redirect("jugadores:perfil_jugador")
        else:
            form = JugadorForm(request.POST, request.FILES, instance=jugador)
            if form.is_valid():
                form.save()
                
                # Crear notificación
                from jugadores.models import Notificacion as NotificacionJugador
                NotificacionJugador.objects.create(
                    destinatario=user,
                    mensaje='👤 Perfil actualizado correctamente',
                    leida=False
                )
                
                messages.success(request, "Perfil actualizado correctamente.")
                return redirect("jugadores:perfil_jugador")
    else:
        form = JugadorForm(instance=jugador)
    
    return render(
        request,
        "jugadores/perfil_jugador.html",
        {
            "form": form, 
            "password_form": password_form,
            "estadisticas_perfil": estadisticas_perfil,
        },
    )


@login_required
def ejecutar_emparejamiento(request):
    """Vista para ejecutar manualmente el algoritmo de emparejamiento"""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para ejecutar emparejamientos')
        return redirect('jugadores:emparejamiento')
    
    resultado = buscar_emparejamientos()
    messages.success(request, resultado)
    return redirect('jugadores:emparejamiento')


@login_required
def emparejamiento(request):
    from club.models import PreferenciasEmparejamiento, DisponibilidadEmparejamiento, EmparejamientoEncontrado
    
    jugador = getattr(request.user, 'jugador', None)
    if not jugador:
        return redirect('jugadores:panel_jugador')
    
    # Obtener o crear preferencias
    preferencias, created = PreferenciasEmparejamiento.objects.get_or_create(
        jugador=jugador,
        defaults={
            'nivel_juego': jugador.nivel,
            'preferencia_genero': 'mixto',
            'activo': True
        }
    )
    
    # Obtener disponibilidades
    disponibilidades = DisponibilidadEmparejamiento.objects.filter(
        preferencias=preferencias
    ).order_by('dia', 'hora_inicio')
    
    # Obtener emparejamientos encontrados con confirmaciones
    emparejamientos = EmparejamientoEncontrado.objects.filter(
        jugadores=jugador
    ).prefetch_related('confirmaciones', 'jugadores').order_by('-fecha_creacion')[:5]
    
    if request.method == 'POST':
        accion = request.POST.get('accion')
        
        if accion == 'actualizar_preferencias':
            preferencias.activo = request.POST.get('activo') == 'on'
            preferencias.nivel_juego = request.POST.get('nivel_juego')
            preferencias.preferencia_genero = request.POST.get('preferencia_genero')
            preferencias.save()
            
            messages.success(request, 'Preferencias actualizadas correctamente')
            
        elif accion == 'agregar_disponibilidad':
            dia = request.POST.get('dia')
            hora_inicio = request.POST.get('hora_inicio')
            hora_fin = request.POST.get('hora_fin')
            
            if dia and hora_inicio and hora_fin:
                DisponibilidadEmparejamiento.objects.get_or_create(
                    preferencias=preferencias,
                    dia=dia,
                    hora_inicio=hora_inicio,
                    defaults={'hora_fin': hora_fin}
                )
                messages.success(request, 'Disponibilidad agregada correctamente')
            
        elif accion == 'eliminar_disponibilidad':
            disp_id = request.POST.get('disponibilidad_id')
            try:
                disp = DisponibilidadEmparejamiento.objects.get(
                    id=disp_id, preferencias=preferencias
                )
                disp.delete()
                messages.success(request, 'Disponibilidad eliminada')
            except DisponibilidadEmparejamiento.DoesNotExist:
                messages.error(request, 'Disponibilidad no encontrada')
        
        return redirect('jugadores:emparejamiento')
    
    return render(request, 'jugadores/emparejamiento.html', {
        'preferencias': preferencias,
        'disponibilidades': disponibilidades,
        'emparejamientos': emparejamientos,
        'dias_semana': PreferenciasEmparejamiento.DIAS_SEMANA,
        'niveles': Jugador.NIVELES,
        'preferencias_genero': PreferenciasEmparejamiento.PREFERENCIAS_GENERO,
    })


@login_required
def confirmar_emparejamiento(request, emparejamiento_id):
    from club.models import EmparejamientoEncontrado, ConfirmacionEmparejamiento
    from jugadores.models import Notificacion as NotificacionJugador
    
    jugador = getattr(request.user, 'jugador', None)
    if not jugador:
        return redirect('jugadores:panel_jugador')
    
    try:
        emparejamiento = EmparejamientoEncontrado.objects.get(id=emparejamiento_id)
        confirmacion = ConfirmacionEmparejamiento.objects.get(
            emparejamiento=emparejamiento, jugador=jugador
        )
        
        accion = request.POST.get('accion')
        
        if accion == 'confirmar':
            confirmacion.confirmado = True
            confirmacion.save()
            
            # Crear notificación
            NotificacionJugador.objects.create(
                destinatario=request.user,
                mensaje=f'✅ Has confirmado tu participación en el emparejamiento del {emparejamiento.dia.title()}',
                leida=False
            )
            
            messages.success(request, 'Emparejamiento confirmado correctamente')
            
        elif accion == 'rechazar':
            confirmacion.confirmado = False
            confirmacion.save()
            
            # Crear notificación
            NotificacionJugador.objects.create(
                destinatario=request.user,
                mensaje=f'❌ Has rechazado el emparejamiento del {emparejamiento.dia.title()}',
                leida=False
            )
            
            messages.info(request, 'Emparejamiento rechazado')
        
        # Verificar si todos confirmaron
        verificar_estado_emparejamiento(emparejamiento)
        
    except (EmparejamientoEncontrado.DoesNotExist, ConfirmacionEmparejamiento.DoesNotExist):
        messages.error(request, 'Emparejamiento no encontrado')
    
    return redirect('jugadores:emparejamiento')


def verificar_estado_emparejamiento(emparejamiento):
    """Verifica y actualiza el estado del emparejamiento según las confirmaciones"""
    from club.models import ConfirmacionEmparejamiento
    from jugadores.models import Notificacion as NotificacionJugador
    
    total_jugadores = emparejamiento.jugadores.count()
    confirmaciones = emparejamiento.confirmaciones.filter(confirmado=True).count()
    rechazos = emparejamiento.confirmaciones.filter(confirmado=False).count()
    
    if confirmaciones == total_jugadores:
        # Todos confirmaron
        emparejamiento.estado = 'confirmado'
        emparejamiento.save()
        
        # Notificar a todos que el emparejamiento está confirmado
        mensaje = f'🎉 ¡Emparejamiento confirmado! Todos los jugadores han confirmado para el {emparejamiento.dia.title()} {emparejamiento.hora_inicio}-{emparejamiento.hora_fin}'
        
        for jugador in emparejamiento.jugadores.all():
            NotificacionJugador.objects.create(
                destinatario=jugador.user,
                mensaje=mensaje,
                leida=False
            )
        
        # Crear reserva automática
        try:
            reserva_creada = crear_reserva_automatica(emparejamiento)
            if reserva_creada:
                emparejamiento.estado = 'reservado'
                emparejamiento.save()
                print(f'🎾 Reserva automática creada: {reserva_creada}')
        except Exception as e:
            print(f'⚠️ Error creando reserva automática: {e}')
        
        # Enviar WhatsApp de confirmación completa
        try:
            from club.whatsapp_service import WhatsAppService
            whatsapp = WhatsAppService()
            jugadores_lista = list(emparejamiento.jugadores.all())
            enviados = whatsapp.send_confirmacion_completa(jugadores_lista, emparejamiento)
            print(f'🎉 WhatsApp de confirmación enviado a {enviados}/{len(jugadores_lista)} jugadores')
        except Exception as e:
            print(f'⚠️ Error enviando WhatsApp de confirmación: {e}')
    
    elif rechazos > 0:
        # Al menos uno rechazó, cancelar emparejamiento
        emparejamiento.estado = 'cancelado'
        emparejamiento.save()
        
        # Reactivar jugadores que confirmaron para nuevos emparejamientos
        from club.models import PreferenciasEmparejamiento
        for confirmacion in emparejamiento.confirmaciones.filter(confirmado=True):
            try:
                pref = PreferenciasEmparejamiento.objects.get(jugador=confirmacion.jugador)
                pref.activo = True
                pref.save()
            except PreferenciasEmparejamiento.DoesNotExist:
                pass
        
        # Notificar cancelación
        mensaje = f'❌ Emparejamiento cancelado: Uno o más jugadores rechazaron la propuesta del {emparejamiento.dia.title()}'
        
        for jugador in emparejamiento.jugadores.all():
            NotificacionJugador.objects.create(
                destinatario=jugador.user,
                mensaje=mensaje,
                leida=False
            )


def buscar_emparejamientos():
    """Algoritmo para encontrar grupos de 4 jugadores compatibles"""
    from club.models import PreferenciasEmparejamiento, DisponibilidadEmparejamiento, EmparejamientoEncontrado
    from datetime import time
    from collections import defaultdict
    
    # Obtener jugadores activos
    jugadores_activos = PreferenciasEmparejamiento.objects.filter(activo=True)
    
    emparejamientos_creados = 0
    
    # Agrupar por nivel y preferencia de género
    for nivel in ['novato', 'intermedio', 'avanzado']:
        for pref_genero in ['hombres', 'mujeres', 'mixto']:
            
            # Filtrar jugadores por nivel y preferencia
            candidatos = []
            for pref in jugadores_activos:
                if pref.nivel_juego == nivel:
                    # Lógica de compatibilidad de género
                    jugador_genero = pref.jugador.genero
                    
                    if pref_genero == 'hombres' and jugador_genero == 'hombre' and pref.preferencia_genero in ['hombres', 'mixto']:
                        candidatos.append(pref)
                    elif pref_genero == 'mujeres' and jugador_genero == 'mujer' and pref.preferencia_genero in ['mujeres', 'mixto']:
                        candidatos.append(pref)
                    elif pref_genero == 'mixto' and pref.preferencia_genero == 'mixto':
                        candidatos.append(pref)
            
            if len(candidatos) < 4:
                continue
            
            # Buscar coincidencias de horarios
            horarios_compatibles = defaultdict(list)
            
            for candidato in candidatos:
                disponibilidades = DisponibilidadEmparejamiento.objects.filter(
                    preferencias=candidato
                )
                
                for disp in disponibilidades:
                    clave = f"{disp.dia}_{disp.hora_inicio}_{disp.hora_fin}"
                    horarios_compatibles[clave].append(candidato)
            
            # Encontrar grupos de exactamente 4 jugadores
            for clave, grupo in horarios_compatibles.items():
                if len(grupo) >= 4:
                    # Tomar los primeros 4 jugadores
                    grupo_final = grupo[:4]
                    
                    # Verificar que no exista ya este emparejamiento
                    jugadores_ids = [p.jugador.id for p in grupo_final]
                    
                    existe = EmparejamientoEncontrado.objects.filter(
                        jugadores__in=jugadores_ids
                    ).distinct().count() > 0
                    
                    if not existe:
                        # Crear emparejamiento
                        dia, hora_inicio, hora_fin = clave.split('_')
                        
                        emparejamiento = EmparejamientoEncontrado.objects.create(
                            dia=dia,
                            hora_inicio=time.fromisoformat(hora_inicio),
                            hora_fin=time.fromisoformat(hora_fin),
                            nivel=nivel,
                            estado='pendiente'
                        )
                        
                        # Agregar jugadores al emparejamiento
                        for pref in grupo_final:
                            emparejamiento.jugadores.add(pref.jugador)
                        
                        # Crear confirmaciones individuales
                        from club.models import ConfirmacionEmparejamiento
                        from datetime import datetime, timedelta
                        from django.utils import timezone
                        
                        # Establecer fecha de expiración (24 horas)
                        emparejamiento.fecha_expiracion = timezone.now() + timedelta(hours=24)
                        
                        for pref in grupo_final:
                            ConfirmacionEmparejamiento.objects.create(
                                emparejamiento=emparejamiento,
                                jugador=pref.jugador,
                                confirmado=None  # Pendiente
                            )
                        
                        # Crear notificaciones
                        from jugadores.models import Notificacion as NotificacionJugador
                        mensaje = f'🎾 ¡Emparejamiento encontrado! {dia.title()} {hora_inicio}-{hora_fin} (Nivel: {nivel.title()}) - ¡Confirma tu participación!'
                        
                        for pref in grupo_final:
                            NotificacionJugador.objects.create(
                                destinatario=pref.jugador.user,
                                mensaje=mensaje,
                                leida=False
                            )
                        
                        # Enviar WhatsApp
                        try:
                            from club.whatsapp_service import WhatsAppService
                            whatsapp = WhatsAppService()
                            jugadores_lista = [pref.jugador for pref in grupo_final]
                            enviados = whatsapp.send_emparejamiento_notification(jugadores_lista, emparejamiento)
                            print(f'📱 WhatsApp enviado a {enviados}/{len(jugadores_lista)} jugadores')
                        except Exception as e:
                            print(f'⚠️ Error enviando WhatsApp: {e}')
                        
                        emparejamiento.estado = 'notificado'
                        emparejamiento.save()
                        
                        emparejamientos_creados += 1
                        
                        # Desactivar jugadores para evitar múltiples emparejamientos
                        for pref in grupo_final:
                            pref.activo = False
                            pref.save()
    
    return f'Se crearon {emparejamientos_creados} emparejamientos'


def crear_reserva_automatica(emparejamiento):
    """Crea una reserva automática para un emparejamiento confirmado"""
    from club.models import Reserva, Cancha
    from datetime import datetime, timedelta
    
    try:
        # Obtener próxima fecha del día especificado
        dias_semana = {
            'lunes': 0, 'martes': 1, 'miercoles': 2, 'jueves': 3,
            'viernes': 4, 'sabado': 5, 'domingo': 6
        }
        
        dia_objetivo = dias_semana.get(emparejamiento.dia)
        if dia_objetivo is None:
            return None
        
        # Calcular próxima fecha
        hoy = datetime.now().date()
        dias_hasta = (dia_objetivo - hoy.weekday()) % 7
        if dias_hasta == 0:  # Si es hoy, programar para la próxima semana
            dias_hasta = 7
        
        fecha_reserva = hoy + timedelta(days=dias_hasta)
        
        # Buscar cancha disponible
        canchas = Cancha.objects.all()
        for cancha in canchas:
            # Verificar si la cancha está libre en ese horario
            reservas_existentes = Reserva.objects.filter(
                cancha=cancha,
                fecha=fecha_reserva,
                hora=emparejamiento.hora_inicio,
                estado__in=['ocupada', 'pagada']
            )
            
            if not reservas_existentes.exists():
                # Crear reserva con el primer jugador como titular
                jugador_principal = emparejamiento.jugadores.first()
                
                reserva = Reserva.objects.create(
                    jugador=jugador_principal,
                    cancha=cancha,
                    fecha=fecha_reserva,
                    hora=emparejamiento.hora_inicio,
                    estado='ocupada',
                    precio=cancha.precio_hora,
                    observaciones=f'Reserva automática - Emparejamiento #{emparejamiento.id}'
                )
                
                # Asociar reserva al emparejamiento
                emparejamiento.reserva = reserva
                emparejamiento.save()
                
                return reserva
        
        return None  # No hay canchas disponibles
        
    except Exception as e:
        print(f'Error en crear_reserva_automatica: {e}')
        return None


def marcar_notificacion_leida(request, notificacion_id):
    user = request.user
    if not user.is_authenticated:
        return redirect("login")
    notificacion = get_object_or_404(user.notificaciones, id=notificacion_id)
    notificacion.leida = True
    notificacion.save()
    return HttpResponseRedirect(reverse("jugadores:notificaciones_jugador"))


def marcar_todas_notificaciones_leidas(request):
    user = request.user
    if not user.is_authenticated:
        return redirect("login")
    user.notificaciones.filter(leida=False).update(leida=True)
    return HttpResponseRedirect(reverse("jugadores:notificaciones_jugador"))


def crear_recordatorios_reservas():
    """Función para crear recordatorios de reservas próximas"""
    from datetime import datetime, timedelta
    from django.utils import timezone
    from jugadores.models import Notificacion as NotificacionJugador
    
    # Recordatorios para mañana
    manana = timezone.now().date() + timedelta(days=1)
    reservas_manana = Reserva.objects.filter(
        fecha=manana,
        estado__in=['ocupada', 'pagada'],
        jugador__isnull=False
    )
    
    for reserva in reservas_manana:
        # Verificar si ya existe recordatorio
        existe_recordatorio = NotificacionJugador.objects.filter(
            destinatario=reserva.jugador.user,
            mensaje__icontains=f'Recordatorio: {reserva.fecha}'
        ).exists()
        
        if not existe_recordatorio:
            NotificacionJugador.objects.create(
                destinatario=reserva.jugador.user,
                mensaje=f'⏰ Recordatorio: Tienes una reserva mañana {reserva.fecha} a las {reserva.hora}',
                leida=False
            )
    
    # Recordatorios de pagos pendientes
    pagos_pendientes = Pago.objects.filter(
        estado='pendiente',
        fecha__lte=timezone.now().date() - timedelta(days=2)  # Más de 2 días pendientes
    )
    
    for pago in pagos_pendientes:
        existe_recordatorio = NotificacionJugador.objects.filter(
            destinatario=pago.jugador.user,
            mensaje__icontains=f'Pago pendiente: ${pago.monto}'
        ).exists()
        
        if not existe_recordatorio:
            NotificacionJugador.objects.create(
                destinatario=pago.jugador.user,
                mensaje=f'💳 Recordatorio: Tienes un pago pendiente de ${pago.monto} desde {pago.fecha}',
                leida=False
            )
    
    return f'Recordatorios creados: {reservas_manana.count()} reservas, {pagos_pendientes.count()} pagos'


@login_required
@csrf_exempt
def procesar_pago(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'})
    
    try:
        data = json.loads(request.body)
        reserva_id = data.get('reserva_id')
        metodo_pago = data.get('metodo_pago')
        
        # Verificar que la reserva pertenece al usuario
        reserva = Reserva.objects.get(
            id=reserva_id, 
            jugador=request.user.jugador,
            estado='ocupada'
        )
        
        # Crear registro de pago pendiente
        from club.models import Pago
        pago = Pago.objects.create(
            jugador=request.user.jugador,
            monto=reserva.pago_total,
            metodo=metodo_pago,
            estado='pendiente',
            observaciones=f'Reserva {reserva.fecha} {reserva.hora}'
        )
        
        # Actualizar metodo_pago de la reserva para tracking
        reserva.metodo_pago = f'{metodo_pago} - Pago ID: {pago.id}'
        reserva.save()
        
        # Crear notificación de solicitud de pago
        from jugadores.models import Notificacion as NotificacionJugador
        NotificacionJugador.objects.create(
            destinatario=request.user,
            mensaje=f'💳 Solicitud de pago enviada: ${reserva.pago_total} - Método: {metodo_pago}',
            leida=False
        )
        
        return JsonResponse({
            'success': True, 
            'message': 'Solicitud de pago registrada correctamente'
        })
        
    except Reserva.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Reserva no encontrada'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@csrf_exempt
def cancelar_reserva(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'})
    
    try:
        data = json.loads(request.body)
        reserva_id = data.get('reserva_id')
        
        # Verificar que la reserva pertenece al usuario
        reserva = Reserva.objects.get(
            id=reserva_id, 
            jugador=request.user.jugador,
            estado__in=['ocupada', 'pagada']
        )
        
        # Verificar política de cancelación (mínimo 2 horas antes)
        from datetime import datetime, timedelta
        from django.utils import timezone
        
        ahora = timezone.now()
        fecha_hora_reserva = datetime.combine(reserva.fecha, reserva.hora)
        fecha_hora_reserva = timezone.make_aware(fecha_hora_reserva)
        
        # Calcular diferencia en horas
        diferencia = fecha_hora_reserva - ahora
        horas_restantes = diferencia.total_seconds() / 3600
        
        if horas_restantes < 2:
            return JsonResponse({
                'success': False, 
                'error': 'No se puede cancelar con menos de 2 horas de anticipación'
            })
        
        # Determinar reembolso según política
        reembolso_porcentaje = 100  # 100% si cancela con más de 2 horas
        if horas_restantes < 24:
            reembolso_porcentaje = 50  # 50% si cancela el mismo día
        
        # Cancelar reserva
        reserva.estado = 'cancelada'
        reserva.metodo_pago += f' - CANCELADA (Reembolso: {reembolso_porcentaje}%)'
        reserva.save()
        
        # Si estaba pagada, crear reembolso
        if reserva.estado == 'pagada' or reserva.pago_total > 0:
            from club.models import Pago
            monto_reembolso = (reserva.pago_total * reembolso_porcentaje) / 100
            
            Pago.objects.create(
                jugador=request.user.jugador,
                monto=-monto_reembolso,  # Monto negativo = reembolso
                metodo='reembolso',
                estado='pendiente',
                observaciones=f'Reembolso por cancelación - Reserva {reserva.fecha} {reserva.hora}'
            )
        
        # Crear notificación de cancelación
        from jugadores.models import Notificacion as NotificacionJugador
        NotificacionJugador.objects.create(
            destinatario=request.user,
            mensaje=f'❌ Reserva cancelada: {reserva.fecha} {reserva.hora} - Reembolso: {reembolso_porcentaje}%',
            leida=False
        )
        
        return JsonResponse({
            'success': True, 
            'message': f'Reserva cancelada. Reembolso: {reembolso_porcentaje}%',
            'reembolso': reembolso_porcentaje
        })
        
    except Reserva.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Reserva no encontrada'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
