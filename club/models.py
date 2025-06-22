from django.db import models
from django.contrib.auth.models import User


class Jugador(models.Model):
    NIVELES = [
        ("novato", "Novato"),
        ("intermedio", "Intermedio"),
        ("avanzado", "Avanzado"),
    ]
    GENEROS = [("hombre", "Hombre"), ("mujer", "Mujer"), ("mixto", "Mixto")]
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20)
    nivel = models.CharField(max_length=15, choices=NIVELES)
    genero = models.CharField(max_length=10, choices=GENEROS)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    en_tinder = models.BooleanField(
        default=True, help_text="¿Acepta aparecer en el emparejador tipo Tinder?"
    )
    avatar = models.ImageField(
        upload_to="avatars/",
        null=True,
        blank=True,
        help_text="Foto de perfil del jugador",
    )

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    def calcular_deuda(self):
        total_reservas = sum(r.pago_total or 0 for r in self.reservas.all())
        total_pagos = sum(p.monto for p in self.pagos.all())
        return total_reservas - total_pagos


class Grupo(models.Model):
    jugadores = models.ManyToManyField(Jugador)
    nivel = models.CharField(max_length=15, choices=Jugador.NIVELES)
    genero = models.CharField(max_length=10, choices=Jugador.GENEROS)
    disponibilidad = models.JSONField()
    creado = models.DateTimeField(auto_now_add=True)


class Reserva(models.Model):
    ESTADOS = [
        ("disponible", "Disponible"),
        ("ocupada", "Ocupada"),
        ("pagada", "Pagada"),
        ("cancelada", "Cancelada"),
    ]
    grupo = models.ForeignKey(Grupo, on_delete=models.SET_NULL, null=True, blank=True)
    jugador = models.ForeignKey(
        Jugador,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reservas",
    )
    fecha = models.DateField()
    hora = models.TimeField()
    estado = models.CharField(max_length=10, choices=ESTADOS, default="disponible")
    pago_total = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    pago_parcial = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    metodo_pago = models.CharField(max_length=30, blank=True)
    creado_por = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )


class Blog(models.Model):
    titulo = models.CharField(max_length=100)
    contenido = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    autor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    imagen_destacada = models.ImageField(upload_to="blog/", blank=True, null=True)
    destacado = models.BooleanField(
        default=False, help_text="¿Mostrar como noticia destacada?"
    )


class BlogComentario(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="comentarios")
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    texto = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    publicado = models.BooleanField(default=True)

    def __str__(self):
        return f"Comentario de {self.usuario} en {self.blog}"


class Review(models.Model):
    jugador = models.ForeignKey(Jugador, on_delete=models.CASCADE)
    comentario = models.TextField()
    puntaje = models.PositiveSmallIntegerField(default=5)
    fecha = models.DateTimeField(auto_now_add=True)


class FAQ(models.Model):
    pregunta = models.CharField(max_length=200)
    respuesta = models.TextField()
    orden = models.PositiveIntegerField(default=0)
    publicado = models.BooleanField(default=True)

    def __str__(self):
        return self.pregunta


class DisponibilidadJugador(models.Model):
    DIAS = [
        ("lunes", "Lunes"),
        ("martes", "Martes"),
        ("miércoles", "Miércoles"),
        ("jueves", "Jueves"),
        ("viernes", "Viernes"),
        ("sábado", "Sábado"),
        ("domingo", "Domingo"),
    ]
    jugador = models.ForeignKey(
        Jugador, on_delete=models.CASCADE, related_name="disponibilidades"
    )
    dia = models.CharField(max_length=10, choices=DIAS)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    nivel = models.CharField(max_length=15, choices=Jugador.NIVELES)
    preferencia_genero = models.CharField(max_length=10, choices=Jugador.GENEROS)

    class Meta:
        unique_together = ("jugador", "dia", "hora_inicio", "hora_fin")

    def __str__(self):
        return f"{self.jugador} - {self.dia} {self.hora_inicio}-{self.hora_fin} ({self.nivel}, {self.preferencia_genero})"


class PreferenciasEmparejamiento(models.Model):
    DIAS_SEMANA = [
        ('lunes', 'Lunes'),
        ('martes', 'Martes'),
        ('miercoles', 'Miércoles'),
        ('jueves', 'Jueves'),
        ('viernes', 'Viernes'),
        ('sabado', 'Sábado'),
        ('domingo', 'Domingo'),
    ]
    
    PREFERENCIAS_GENERO = [
        ('hombres', 'Solo Hombres'),
        ('mujeres', 'Solo Mujeres'),
        ('mixto', 'Mixto'),
    ]
    
    jugador = models.OneToOneField(
        Jugador, on_delete=models.CASCADE, related_name='preferencias_emparejamiento'
    )
    activo = models.BooleanField(default=True, help_text='¿Buscar emparejamientos activamente?')
    nivel_juego = models.CharField(max_length=15, choices=Jugador.NIVELES)
    preferencia_genero = models.CharField(max_length=10, choices=PREFERENCIAS_GENERO)
    
    def __str__(self):
        return f'Preferencias de {self.jugador.nombre} - {self.nivel_juego} ({self.preferencia_genero})'


class DisponibilidadEmparejamiento(models.Model):
    DIAS_SEMANA = [
        ('lunes', 'Lunes'),
        ('martes', 'Martes'),
        ('miercoles', 'Miércoles'),
        ('jueves', 'Jueves'),
        ('viernes', 'Viernes'),
        ('sabado', 'Sábado'),
        ('domingo', 'Domingo'),
    ]
    
    preferencias = models.ForeignKey(
        PreferenciasEmparejamiento, on_delete=models.CASCADE, related_name='disponibilidades'
    )
    dia = models.CharField(max_length=10, choices=DIAS_SEMANA)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    
    class Meta:
        unique_together = ('preferencias', 'dia', 'hora_inicio')
    
    def __str__(self):
        return f'{self.preferencias.jugador.nombre} - {self.dia} {self.hora_inicio}-{self.hora_fin}'


class EmparejamientoEncontrado(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('notificado', 'Notificado'),
        ('confirmado', 'Confirmado'),
        ('cancelado', 'Cancelado'),
        ('expirado', 'Expirado'),
        ('reservado', 'Reservado'),
    ]
    
    jugadores = models.ManyToManyField(Jugador, related_name='emparejamientos')
    dia = models.CharField(max_length=10)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    nivel = models.CharField(max_length=15)
    estado = models.CharField(max_length=15, choices=ESTADOS, default='pendiente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_expiracion = models.DateTimeField(null=True, blank=True)
    reserva = models.ForeignKey('Reserva', on_delete=models.SET_NULL, null=True, blank=True, related_name='emparejamiento')
    
    def __str__(self):
        return f'Emparejamiento {self.id} - {self.dia} {self.hora_inicio}-{self.hora_fin} ({self.nivel})'
    
    def confirmaciones_count(self):
        return self.confirmaciones.filter(confirmado=True).count()
    
    def rechazos_count(self):
        return self.confirmaciones.filter(confirmado=False).count()
    
    def pendientes_count(self):
        return self.confirmaciones.filter(confirmado__isnull=True).count()


class ConfirmacionEmparejamiento(models.Model):
    emparejamiento = models.ForeignKey(
        EmparejamientoEncontrado, on_delete=models.CASCADE, related_name='confirmaciones'
    )
    jugador = models.ForeignKey(Jugador, on_delete=models.CASCADE)
    confirmado = models.BooleanField(null=True, blank=True)  # True=confirma, False=rechaza, None=pendiente
    fecha_respuesta = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('emparejamiento', 'jugador')
    
    def __str__(self):
        estado = 'Pendiente'
        if self.confirmado is True:
            estado = 'Confirmado'
        elif self.confirmado is False:
            estado = 'Rechazado'
        return f'{self.jugador.nombre} - {estado}'


class Torneo(models.Model):
    nombre = models.CharField(max_length=100)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    descripcion = models.TextField(blank=True)
    jugadores = models.ManyToManyField(Jugador, related_name="torneos")
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class PartidoTorneo(models.Model):
    torneo = models.ForeignKey(
        Torneo, on_delete=models.CASCADE, related_name="partidos"
    )
    jugador1 = models.ForeignKey(
        Jugador, on_delete=models.CASCADE, related_name="partidos_jugador1"
    )
    jugador2 = models.ForeignKey(
        Jugador, on_delete=models.CASCADE, related_name="partidos_jugador2"
    )
    fecha = models.DateTimeField()
    puntaje_jugador1 = models.PositiveIntegerField(default=0)
    puntaje_jugador2 = models.PositiveIntegerField(default=0)
    finalizado = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.torneo}: {self.jugador1} vs {self.jugador2}"


class Ranking(models.Model):
    torneo = models.ForeignKey(Torneo, on_delete=models.CASCADE, related_name="ranking")
    jugador = models.ForeignKey(Jugador, on_delete=models.CASCADE)
    puntos = models.IntegerField(default=0)

    class Meta:
        unique_together = ("torneo", "jugador")
        ordering = ["-puntos"]

    def __str__(self):
        return f"{self.jugador} - {self.puntos} pts ({self.torneo})"


class BrandingConfig(models.Model):
    nombre_sitio = models.CharField(max_length=100, default="Club de Pádel")
    logo = models.ImageField(upload_to="branding/", blank=True, null=True)
    color_primario = models.CharField(
        max_length=7, default="#2563eb", help_text="Color principal (hex)"
    )
    color_secundario = models.CharField(
        max_length=7, default="#facc15", help_text="Color secundario (hex)"
    )
    mensaje_bienvenida = models.CharField(max_length=200, blank=True, null=True)
    mensaje_footer = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return "Configuración de Branding"

    class Meta:
        verbose_name = "Branding (colores, logo, mensajes)"
        verbose_name_plural = "Branding (colores, logo, mensajes)"


class Pago(models.Model):
    ESTADOS = [
        ("pendiente", "Pendiente"),
        ("pagado", "Pagado"),
        ("rechazado", "Rechazado"),
    ]
    jugador = models.ForeignKey(Jugador, on_delete=models.CASCADE, related_name="pagos")
    monto = models.DecimalField(max_digits=8, decimal_places=2)
    fecha = models.DateField(auto_now_add=True)
    estado = models.CharField(max_length=10, choices=ESTADOS, default="pendiente")
    metodo = models.CharField(max_length=30, blank=True)
    referencia = models.CharField(max_length=100, blank=True)
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f"Pago de {self.jugador} - ${self.monto} ({self.get_estado_display()})"
