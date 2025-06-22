from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Grupo
from django.contrib.auth.models import Group, User


@receiver(m2m_changed, sender=Grupo.jugadores.through)
def notificar_recepcionista_grupo(sender, instance, action, **kwargs):
    if action == "post_add":
        if instance.jugadores.count() == 4:
            # Buscar recepcionistas
            recepcionistas = User.objects.filter(groups__name__iexact="Recepcionistas")
            if not recepcionistas.exists():
                return
            subject = "[Club de Pádel] Nuevo grupo formado"
            jugadores = ", ".join([str(j) for j in instance.jugadores.all()])
            message = f"Se ha formado un nuevo grupo de pádel:\n\nJugadores: {jugadores}\nNivel: {instance.get_nivel_display()}\nGénero: {instance.get_genero_display()}\nDisponibilidad: {instance.disponibilidad}"
            for recep in recepcionistas:
                if recep.email:
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [recep.email],
                        fail_silently=True,
                    )
