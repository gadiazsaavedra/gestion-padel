from django.db import models
from django.contrib.auth.models import User


class Auditoria(models.Model):
    ACCION_CHOICES = [
        ("stock", "Stock"),
        ("reserva", "Reserva"),
        ("pago", "Pago"),
        ("otro", "Otro"),
    ]
    usuario = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    accion = models.CharField(max_length=20, choices=ACCION_CHOICES)
    descripcion = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    objeto_id = models.CharField(max_length=64, blank=True, null=True)
    objeto_tipo = models.CharField(max_length=64, blank=True, null=True)

    def __str__(self):
        return f"{self.get_accion_display()} - {self.descripcion[:40]}... ({self.fecha:%d/%m/%Y %H:%M})"
