from django.shortcuts import render
from club.models import Reserva, Grupo, Jugador  # <-- Importar Jugador
from club.models_auditoria import Auditoria
from datetime import timedelta, date, time
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from club.utils import notificar_confirmacion_reserva
from django.urls import reverse
from django.http import JsonResponse


# Create your views here.
def grilla_reservas(request):
    # Si el usuario es jugador, primero selecciona duración
    # if request.user.is_authenticated and hasattr(request.user, "jugador"):
    #     if request.method == "POST":
    #         duracion = request.POST.get("duracion")
    #         # Redirige a la grilla con la duración como parámetro GET
    #         return redirect(f"{reverse('reservas:grilla')}?duracion={duracion}")
    #     # Si no hay duración seleccionada, muestra el formulario
    #     if not request.GET.get("duracion"):
    #         return render(request, "reservas/seleccionar_duracion.html")
    #     # Si ya hay duración, continúa con la lógica normal y puedes usar request.GET['duracion']
    # Definir rango de días y horas a mostrar (ejemplo: semana actual, 8-23hs)
    hoy = timezone.localdate()
    dias = [hoy + timedelta(days=i) for i in range(7)]
    horas = [time(h, 0) for h in range(8, 24)]
    # Obtener reservas en ese rango
    reservas = Reserva.objects.filter(fecha__in=dias, hora__in=horas)
    grilla = {}
    for d in dias:
        grilla[d] = {}
        for h in horas:
            res = reservas.filter(fecha=d, hora=h).first()
            grilla[d][h] = res
    canchas = reservas.values_list("grupo__id", flat=True).distinct()
    return render(
        request,
        "reservas/grilla_reservas.html",
        {
            "dias": dias,
            "horas": horas,
            "grilla": grilla,
            "canchas": canchas,
            "duracion": request.GET.get("duracion"),
        },
    )


@login_required
def reservar_turno(request, fecha, hora):
    from datetime import datetime, timedelta

    reserva = Reserva.objects.filter(fecha=fecha, hora=hora).first()
    horas_opciones = [
        ("1:00", "1 hora"),
        ("1:30", "1 hora y media"),
        ("2:00", "2 horas"),
        ("2:30", "2 horas y media"),
        ("3:00", "3 horas"),
    ]
    es_jugador = hasattr(request.user, "jugador")

    # Manejar cantidad de turnos desde el modal
    cantidad_turnos = request.GET.get("cantidad_turnos")
    if cantidad_turnos:
        # Reserva directa desde el modal
        if es_jugador:
            jugador = request.user.jugador
            bloques = int(cantidad_turnos)
            hora_inicio = datetime.strptime(f"{fecha} {hora}", "%Y-%m-%d %H:%M")

            # Verificar disponibilidad de todos los turnos
            for i in range(bloques):
                hora_bloque = (hora_inicio + timedelta(hours=i)).time()
                existe = (
                    Reserva.objects.filter(fecha=fecha, hora=hora_bloque)
                    .exclude(estado="disponible")
                    .exists()
                )
                if existe:
                    messages.error(
                        request,
                        f"El turno de las {hora_bloque.strftime('%H:%M')} ya está reservado u ocupado.",
                    )
                    return redirect("grilla_reservas")

            # Crear las reservas
            PRECIO_POR_HORA = 2000  # Precio fijo por hora
            reservas_creadas = []
            for i in range(bloques):
                hora_bloque = (hora_inicio + timedelta(hours=i)).time()
                reserva = Reserva.objects.create(
                    fecha=fecha,
                    hora=hora_bloque,
                    estado="ocupada",
                    creado_por=request.user,
                    metodo_pago=f"Duración: {bloques} hora(s)",
                    jugador=jugador,
                    pago_total=PRECIO_POR_HORA,  # Precio por hora
                )
                Auditoria.objects.create(
                    usuario=request.user,
                    accion="reserva",
                    descripcion=f"Creación de reserva para {jugador} el {fecha} a las {hora_bloque}",
                    objeto_id=str(reserva.pk),
                    objeto_tipo="Reserva",
                )
                reservas_creadas.append(reserva)

            # Notificación automática solo para la primera reserva
            if reservas_creadas:
                notificar_confirmacion_reserva(jugador, reservas_creadas[0])

            messages.success(
                request, f"Reserva realizada correctamente para {bloques} hora(s)."
            )
            return redirect("grilla_reservas")

    if request.method == "POST":
        if es_jugador:
            jugador = request.user.jugador
        else:
            jugador_id = request.POST.get("jugador")
            jugador = get_object_or_404(Jugador, id=jugador_id)
        duracion = request.POST.get("horas")
        # Calcular cantidad de horas (redondear hacia arriba si es media hora)
        dur_parts = duracion.split(":")
        horas_duracion = int(dur_parts[0])
        minutos_duracion = int(dur_parts[1])
        bloques = horas_duracion + (1 if minutos_duracion >= 30 else 0)
        hora_inicio = datetime.strptime(f"{fecha} {hora}", "%Y-%m-%d %H:%M")
        reservas_creadas = []
        for i in range(bloques):
            hora_bloque = (hora_inicio + timedelta(hours=i)).time()
            # Verificar si ya existe una reserva ocupada/pagada en ese bloque
            existe = (
                Reserva.objects.filter(fecha=fecha, hora=hora_bloque)
                .exclude(estado="disponible")
                .exists()
            )
            if existe:
                messages.error(
                    request,
                    f"El turno de las {hora_bloque.strftime('%H:%M')} ya está reservado u ocupado.",
                )
                return redirect("grilla_reservas")
        PRECIO_POR_HORA = 2000  # Precio fijo por hora
        for i in range(bloques):
            hora_bloque = (hora_inicio + timedelta(hours=i)).time()
            reserva = Reserva.objects.create(
                fecha=fecha,
                hora=hora_bloque,
                estado="ocupada",
                creado_por=request.user,
                metodo_pago=f"Duración: {duracion}",
                jugador=jugador,
                pago_total=PRECIO_POR_HORA,  # Precio por hora
            )
            Auditoria.objects.create(
                usuario=request.user,
                accion="reserva",
                descripcion=f"Creación de reserva para {jugador} el {fecha} a las {hora_bloque}",
                objeto_id=str(reserva.pk),
                objeto_tipo="Reserva",
            )
            reservas_creadas.append(reserva)
        # Notificación automática solo para la primera reserva
        if reservas_creadas:
            notificar_confirmacion_reserva(jugador, reservas_creadas[0])
        messages.success(
            request, f"Reserva realizada correctamente para {bloques} hora(s)."
        )
        return redirect("grilla_reservas")
    context = {
        "fecha": fecha,
        "hora": hora,
        "horas_opciones": horas_opciones,
        "es_jugador": es_jugador,
    }
    # Solo agregar 'jugadores' si NO es jugador
    if not es_jugador:
        context["jugadores"] = Jugador.objects.all().order_by("nombre", "apellido")
    else:
        # Elimina 'jugadores' si por alguna razón está en el contexto
        context.pop("jugadores", None)
    return render(request, "reservas/reservar_turno.html", context)


@login_required
def reservar_turno_modal(request):
    from datetime import datetime, timedelta

    if request.method == "POST":
        fecha = request.POST.get("fecha")
        hora = request.POST.get("hora")
        cantidad = int(request.POST.get("cantidad", 1))
        jugador = getattr(request.user, "jugador", None)
        if not jugador:
            return JsonResponse(
                {"success": False, "error": "Solo jugadores pueden reservar."}
            )
        hora_inicio = datetime.strptime(f"{fecha} {hora}", "%Y-%m-%d %H:%M")
        reservas_creadas = []
        for i in range(cantidad):
            hora_bloque = (hora_inicio + timedelta(hours=i)).time()
            existe = (
                Reserva.objects.filter(fecha=fecha, hora=hora_bloque)
                .exclude(estado="disponible")
                .exists()
            )
            if existe:
                return JsonResponse(
                    {
                        "success": False,
                        "error": f"El turno de las {hora_bloque.strftime('%H:%M')} ya está reservado.",
                    }
                )
            reserva = Reserva.objects.create(
                fecha=fecha,
                hora=hora_bloque,
                estado="ocupada",
                creado_por=request.user,
                metodo_pago=f"Bloques: {cantidad}",
                jugador=jugador,
            )
            Auditoria.objects.create(
                usuario=request.user,
                accion="reserva",
                descripcion=f"Creación de reserva para {jugador} el {fecha} a las {hora_bloque}",
                objeto_id=str(reserva.pk),
                objeto_tipo="Reserva",
            )
            reservas_creadas.append(reserva)
        if reservas_creadas:
            notificar_confirmacion_reserva(jugador, reservas_creadas[0])
        return JsonResponse({"success": True})
    return JsonResponse({"success": False, "error": "Método no permitido"})


@login_required
def detalle_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    return render(request, "reservas/detalle_reserva.html", {"reserva": reserva})


@login_required
def editar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    if request.method == "POST":
        grupo_id = request.POST.get("grupo")
        estado = request.POST.get("estado")
        pago_total = request.POST.get("pago_total")
        pago_parcial = request.POST.get("pago_parcial")
        metodo_pago = request.POST.get("metodo_pago")
        if grupo_id:
            # Validación: ¿el grupo ya tiene reserva en ese horario?
            solapada = (
                Reserva.objects.filter(
                    grupo_id=grupo_id, fecha=reserva.fecha, hora=reserva.hora
                )
                .exclude(id=reserva.id)
                .exclude(estado="disponible")
                .exists()
            )
            if solapada:
                messages.error(
                    request, "Ese grupo ya tiene una reserva en ese horario."
                )
                return redirect("editar_reserva", reserva_id=reserva.id)
            reserva.grupo_id = grupo_id
        if estado:
            reserva.estado = estado
        if pago_total is not None:
            reserva.pago_total = pago_total
        if pago_parcial is not None:
            reserva.pago_parcial = pago_parcial
        if metodo_pago is not None:
            reserva.metodo_pago = metodo_pago
        reserva.save()
        Auditoria.objects.create(
            usuario=request.user,
            accion="reserva",
            descripcion=f"Edición de reserva {reserva.id} para grupo {reserva.grupo_id}",
            objeto_id=str(reserva.pk),
            objeto_tipo="Reserva",
        )
        messages.success(request, "Reserva editada correctamente.")
        return redirect("detalle_reserva", reserva_id=reserva.id)
    grupos = Grupo.objects.all()
    return render(
        request, "reservas/editar_reserva.html", {"reserva": reserva, "grupos": grupos}
    )


@login_required
def cancelar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    if request.method == "POST":
        Auditoria.objects.create(
            usuario=request.user,
            accion="reserva",
            descripcion=f"Cancelación de reserva {reserva.id}",
            objeto_id=str(reserva.pk),
            objeto_tipo="Reserva",
        )
        reserva.delete()
        return redirect("grilla_reservas")
    return render(request, "reservas/cancelar_reserva.html", {"reserva": reserva})
