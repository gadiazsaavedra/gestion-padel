from django.contrib import admin
from .models import (
    Jugador,
    Grupo,
    Reserva,
    Blog,
    BlogComentario,
    Review,
    FAQ,
    Torneo,
    PartidoTorneo,
    Ranking,
    BrandingConfig,
)
from .models_multimedia import Multimedia, Testimonio


@admin.register(Jugador)
class JugadorAdmin(admin.ModelAdmin):
    list_display = ("nombre", "apellido", "email", "telefono", "nivel", "genero")
    search_fields = ("nombre", "apellido", "email")
    list_filter = ("nivel", "genero")


@admin.register(Grupo)
class GrupoAdmin(admin.ModelAdmin):
    list_display = ("id", "nivel", "genero", "creado")
    list_filter = ("nivel", "genero")
    filter_horizontal = ("jugadores",)


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ("fecha", "hora", "estado", "grupo", "pago_total", "pago_parcial")
    list_filter = ("estado", "fecha")
    search_fields = ("grupo__id",)


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ("titulo", "fecha", "autor", "destacado")
    list_filter = ("destacado", "fecha")
    search_fields = ("titulo", "contenido")


@admin.register(BlogComentario)
class BlogComentarioAdmin(admin.ModelAdmin):
    list_display = ("blog", "usuario", "fecha", "publicado")
    list_filter = ("publicado", "fecha")
    search_fields = ("blog__titulo", "usuario__username", "texto")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("jugador", "puntaje", "fecha")
    search_fields = ("jugador__nombre", "comentario")


@admin.register(Multimedia)
class MultimediaAdmin(admin.ModelAdmin):
    list_display = ("titulo", "tipo", "fecha")
    search_fields = ("titulo", "descripcion")
    list_filter = ("tipo", "fecha")


@admin.register(Testimonio)
class TestimonioAdmin(admin.ModelAdmin):
    list_display = ("nombre", "fecha", "publicado")
    search_fields = ("nombre", "texto")
    list_filter = ("publicado",)


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("pregunta", "publicado", "orden")
    list_filter = ("publicado",)
    search_fields = ("pregunta", "respuesta")


@admin.register(Torneo)
class TorneoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "fecha_inicio", "fecha_fin", "activo")
    list_filter = ("activo",)
    search_fields = ("nombre",)
    filter_horizontal = ("jugadores",)


@admin.register(PartidoTorneo)
class PartidoTorneoAdmin(admin.ModelAdmin):
    list_display = (
        "torneo",
        "jugador1",
        "jugador2",
        "fecha",
        "puntaje_jugador1",
        "puntaje_jugador2",
        "finalizado",
    )
    list_filter = ("torneo", "finalizado")
    search_fields = ("torneo__nombre", "jugador1__nombre", "jugador2__nombre")


@admin.register(Ranking)
class RankingAdmin(admin.ModelAdmin):
    list_display = ("torneo", "jugador", "puntos")
    list_filter = ("torneo",)
    search_fields = ("torneo__nombre", "jugador__nombre", "jugador__apellido")


@admin.register(BrandingConfig)
class BrandingConfigAdmin(admin.ModelAdmin):
    list_display = ("nombre_sitio", "color_primario", "color_secundario")


from .admin_auditoria import *
