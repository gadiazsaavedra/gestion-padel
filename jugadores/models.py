from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from club.models import Jugador

# Create your models here.


class GrupoSugerido(models.Model):
    ESTADOS = [
        ("nuevo", "Nuevo"),
        ("aceptado", "Aceptado"),
        ("rechazado", "Rechazado"),
        ("reservado", "Reservado"),
    ]
    jugadores = models.ManyToManyField(Jugador)
    nivel = models.CharField(max_length=15, choices=Jugador.NIVELES)
    genero = models.CharField(max_length=10, choices=Jugador.GENEROS)
    # Ahora solo se guarda el día como referencia, la lógica de horarios está en DisponibilidadJugador
    disponibilidad = models.JSONField(help_text="Día sugerido para el grupo")
    fecha_sugerencia = models.DateTimeField(auto_now_add=True)
    criterios = models.JSONField(
        blank=True, null=True, help_text="Criterios de emparejamiento usados"
    )
    estado = models.CharField(max_length=10, choices=ESTADOS, default="nuevo")
    sugerido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="grupos_sugeridos",
    )

    def __str__(self):
        jugadores_str = ", ".join(str(j) for j in self.jugadores.all())
        return f"Grupo sugerido: {jugadores_str} ({self.nivel}, {self.genero})"


class Notificacion(models.Model):
    destinatario = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notificaciones"
    )
    mensaje = models.TextField()
    leida = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    tipo = models.CharField(
        max_length=50, default="info"
    )  # info, recordatorio, deuda, etc.

    def __str__(self):
        return f"Notificación para {self.destinatario.username}: {self.mensaje[:40]}..."
