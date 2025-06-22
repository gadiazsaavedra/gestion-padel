from django.db.models.signals import post_save
from django.dispatch import receiver
from club.models import Reserva, Pago
from .models import Notificacion
from django.contrib.auth.models import User, Group


@receiver(post_save, sender=Reserva)
def crear_notificacion_reserva(sender, instance, created, **kwargs):
    if created and instance.jugador and instance.jugador.user:
        usuario = instance.jugador.user
        mensaje = f"¡Tienes una nueva reserva para el día {instance.fecha} a las {instance.hora}!"
        Notificacion.objects.create(
            destinatario=usuario, mensaje=mensaje, tipo="recordatorio"
        )


@receiver(post_save, sender=Pago)
def crear_notificacion_pago(sender, instance, created, **kwargs):
    if created and instance.jugador and instance.jugador.user:
        usuario = instance.jugador.user
        mensaje = f"Se registró un nuevo pago de ${instance.monto:.2f}. Estado: {instance.get_estado_display()}"
        Notificacion.objects.create(destinatario=usuario, mensaje=mensaje, tipo="pago")
        # Notificar a administradores
        admins = User.objects.filter(is_superuser=True)
        for admin in admins:
            Notificacion.objects.create(
                destinatario=admin,
                mensaje=f"{usuario.username} registró un pago de ${instance.monto:.2f} (pendiente de validación)",
                tipo="pago-admin",
            )
        # Notificar a recepcionistas
        try:
            recepcionistas = Group.objects.get(name="recepcionistas").user_set.all()
            for recep in recepcionistas:
                Notificacion.objects.create(
                    destinatario=recep,
                    mensaje=f"{usuario.username} registró un pago de ${instance.monto:.2f} (pendiente de validación)",
                    tipo="pago-recep",
                )
        except Group.DoesNotExist:
            pass
