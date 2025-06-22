from datetime import timedelta, datetime
from django.db.models import Q
from .models import Jugador, DisponibilidadJugador
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.conf import settings
from jugadores.models import Notificacion
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse


def buscar_matches():
    """
    Busca y retorna grupos de 4 jugadores compatibles para partido de pádel
    según nivel, género, disponibilidad y participación en Tinder.
    """
    # 1. Filtrar jugadores activos en Tinder con al menos una disponibilidad
    jugadores = Jugador.objects.filter(en_tinder=True, user__isnull=False)
    # 2. Agrupar por nivel, preferencia de género y día
    matches = []
    for nivel, _ in Jugador.NIVELES:
        for genero, _ in Jugador.GENEROS:
            for dia, _ in DisponibilidadJugador.DIAS:
                # Buscar disponibilidades compatibles
                disponibilidades = DisponibilidadJugador.objects.filter(
                    nivel=nivel,
                    preferencia_genero=genero,
                    dia=dia,
                    jugador__in=jugadores,
                ).select_related("jugador")
                # 3. Buscar superposición de horarios entre grupos de 4
                grupos = agrupar_por_horario(disponibilidades)
                for grupo, hora_inicio, hora_fin in grupos:
                    if len(grupo) == 4:
                        matches.append(
                            {
                                "jugadores": [d.jugador for d in grupo],
                                "dia": dia,
                                "hora_inicio": hora_inicio,
                                "hora_fin": hora_fin,
                                "nivel": nivel,
                                "genero": genero,
                            }
                        )
    return matches


def agrupar_por_horario(disponibilidades):
    """
    Busca grupos de 4 disponibilidades con superposición de al menos 1h30m.
    Devuelve lista de tuplas: ([disponibilidades], hora_inicio, hora_fin)
    """
    from itertools import combinations

    resultado = []
    for grupo in combinations(disponibilidades, 4):
        # Buscar intersección de horarios
        hora_inicio = max(d.hora_inicio for d in grupo)
        hora_fin = min(d.hora_fin for d in grupo)
        if hora_fin > hora_inicio:
            # Duración de la intersección
            delta = datetime.combine(datetime.today(), hora_fin) - datetime.combine(
                datetime.today(), hora_inicio
            )
            if delta >= timedelta(minutes=90):
                resultado.append((grupo, hora_inicio, hora_fin))
    return resultado


def notificar_recepcionista(match):
    """
    Envía un email a los recepcionistas con la info del match formado.
    """
    recepcionistas = User.objects.filter(groups__name="recepcionistas")
    emails = [r.email for r in recepcionistas if r.email]
    jugadores_info = [
        f"{j.nombre} {j.apellido} - WhatsApp: {j.telefono}" for j in match["jugadores"]
    ]
    mensaje = (
        f"Se ha formado un match de pádel:\n"
        f"Jugadores:\n" + "\n".join(jugadores_info) + "\n"
        f"Día: {match['dia']}, Horario sugerido: {match['hora_inicio']} - {match['hora_fin']}\n"
        f"Nivel: {match['nivel']}, Género: {match['genero']}"
    )
    send_mail(
        subject="Nuevo Match de Pádel formado",
        message=mensaje,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None) or "noreply@club.com",
        recipient_list=emails,
        fail_silently=True,
    )


def notificar_recepcionista_panel(match):
    """
    Crea una notificación interna para cada recepcionista con la info del match.
    """
    from django.contrib.auth.models import User

    recepcionistas = User.objects.filter(groups__name="recepcionistas")
    jugadores_info = [
        f"{j.nombre} {j.apellido} - WhatsApp: {j.telefono}" for j in match["jugadores"]
    ]
    mensaje = (
        f"Se ha formado un match de pádel:\n"
        f"Jugadores:\n" + "\n".join(jugadores_info) + "\n"
        f"Día: {match['dia']}, Horario sugerido: {match['hora_inicio']} - {match['hora_fin']}\n"
        f"Nivel: {match['nivel']}, Género: {match['genero']}"
    )
    for user in recepcionistas:
        Notificacion.objects.create(destinatario=user, mensaje=mensaje)


def notificar_recepcionista_whatsapp(match):
    """
    (Estructura) Envía mensaje WhatsApp a los recepcionistas usando una API externa.
    """
    # Aquí deberías integrar con Twilio, WATI, o la API que uses
    # Ejemplo de estructura:
    # for recep in recepcionistas:
    #     send_whatsapp_message(recep.telefono, mensaje)
    pass


def buscar_matches_y_notificar(metodo="email"):
    """
    Busca matches y notifica a los recepcionistas por el método elegido: 'email', 'panel' o 'whatsapp'.
    """
    matches = buscar_matches()
    for match in matches:
        if metodo == "email":
            notificar_recepcionista(match)
        elif metodo == "panel":
            notificar_recepcionista_panel(match)
        elif metodo == "whatsapp":
            notificar_recepcionista_whatsapp(match)
    return matches


def enviar_email_activacion(user, request):
    """
    Envía un email de activación de cuenta con un token seguro.
    """
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    url = request.build_absolute_uri(
        reverse("activar_cuenta", kwargs={"uidb64": uid, "token": token})
    )
    subject = "Activa tu cuenta en Club de Pádel"
    message = f"Hola {user.username},\n\nPor favor activa tu cuenta haciendo clic en el siguiente enlace:\n{url}\n\nSi no creaste esta cuenta, ignora este mensaje."
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])


def get_sugerencias_usuario(jugador):
    """
    Devuelve sugerencias de horarios para el jugador según su disponibilidad y nivel,
    y matches grupales si hay 4 compatibles.
    """
    sugerencias = []
    # Sugerencias individuales: horarios libres según disponibilidad
    if jugador:
        disponibilidades = jugador.disponibilidades.all()
        for disp in disponibilidades:
            sugerencias.append(
                f"Podrías reservar el {disp.get_dia_display()} de {disp.hora_inicio.strftime('%H:%M')} a {disp.hora_fin.strftime('%H:%M')} (Nivel: {disp.nivel}, Género: {disp.preferencia_genero})"
            )
    # Matches grupales: si hay 4 compatibles, mostrar info
    from .utils import buscar_matches

    matches = buscar_matches()
    for match in matches:
        if jugador in match["jugadores"]:
            sugerencias.append(
                f"¡Match grupal! {match['dia'].capitalize()} de {match['hora_inicio'].strftime('%H:%M')} a {match['hora_fin'].strftime('%H:%M')} con jugadores de nivel {match['nivel']} y género {match['genero']}"
            )
    return sugerencias


def notificar_inscripcion_torneo(jugador, torneo):
    """
    Notifica a los recepcionistas y admins cuando un jugador se inscribe a un torneo.
    """
    from jugadores.models import Notificacion
    from django.contrib.auth.models import User

    # Notificación interna
    recepcionistas = User.objects.filter(
        groups__name__in=["recepcionistas", "administradores"]
    )
    mensaje = f"{jugador} se ha inscripto en el torneo '{torneo.nombre}'."
    for user in recepcionistas:
        Notificacion.objects.create(destinatario=user, mensaje=mensaje)
    # Notificación por email (opcional)
    emails = [u.email for u in recepcionistas if u.email]
    if emails:
        send_mail(
            subject="Nueva inscripción a torneo",
            message=mensaje,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None)
            or "noreply@club.com",
            recipient_list=emails,
            fail_silently=True,
        )
    # Notificación en tiempo real por WebSocket
    try:
        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer

        channel_layer = get_channel_layer()
        for user in recepcionistas:
            group_name = f"notificaciones_{user.id}"
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    "type": "enviar_notificacion",
                    "mensaje": mensaje,
                    "tipo": "info",
                },
            )
    except Exception as e:
        pass  # No romper si no está channels o hay error


def enviar_whatsapp(numero, mensaje):
    """
    Envía un WhatsApp usando una API externa (ejemplo: Twilio, WATI, etc).
    Implementa aquí la integración real según el proveedor elegido.
    """
    # Ejemplo de integración (pseudo-código):
    # import requests
    # requests.post('https://api.twilio.com/whatsapp', data={...})
    print(f"[WhatsApp] A {numero}: {mensaje}")
    # return True si fue exitoso
    return True


def notificar_confirmacion_reserva(jugador, reserva):
    """
    Envía confirmación de reserva por email y WhatsApp.
    """
    # Email
    if jugador.email:
        send_mail(
            subject="Confirmación de reserva",
            message=f"Hola {jugador.nombre}, tu reserva para el {reserva.fecha} a las {reserva.hora} ha sido confirmada.",
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None)
            or "noreply@club.com",
            recipient_list=[jugador.email],
            fail_silently=True,
        )
    # WhatsApp
    if jugador.telefono:
        enviar_whatsapp(
            jugador.telefono,
            f"Tu reserva para el {reserva.fecha} a las {reserva.hora} está confirmada. ¡Te esperamos!",
        )


def notificar_recordatorio_reserva(jugador, reserva):
    """
    Envía recordatorio de reserva por email y WhatsApp (ejemplo: 1 día antes).
    """
    # Email
    if jugador.email:
        send_mail(
            subject="Recordatorio de reserva",
            message=f"Hola {jugador.nombre}, te recordamos tu reserva para el {reserva.fecha} a las {reserva.hora}.",
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None)
            or "noreply@club.com",
            recipient_list=[jugador.email],
            fail_silently=True,
        )
    # WhatsApp
    if jugador.telefono:
        enviar_whatsapp(
            jugador.telefono,
            f"Recordatorio: tienes una reserva el {reserva.fecha} a las {reserva.hora} en el club.",
        )
