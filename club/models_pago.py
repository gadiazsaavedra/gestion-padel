from django.db import models
from django.contrib.auth.models import User
from jugadores.models import Jugador
from club.models import Reserva


class Pago(models.Model):
    jugador = models.ForeignKey(Jugador, on_delete=models.CASCADE, related_name="pagos")
    reserva = models.ForeignKey(
        Reserva, on_delete=models.SET_NULL, null=True, blank=True, related_name="pagos"
    )
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)
    metodo = models.CharField(max_length=50, default="efectivo")
    referencia = models.CharField(max_length=100, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Pago de {self.jugador} - ${self.monto} ({self.fecha:%d/%m/%Y})"


# Lógica básica de control de deudas
# Puedes agregar este método en el modelo Jugador o como función utilitaria


def calcular_deuda_jugador(jugador):
    total_reservas = sum(r.pago_total or 0 for r in jugador.reservas.all())
    total_pagos = sum(p.monto for p in jugador.pagos.all())
    return total_reservas - total_pagos
