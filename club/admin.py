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
    Pago,
)
from .models_multimedia import Multimedia, Testimonio
from .models_finanzas import (
    Empleado, Proveedor, PagoEmpleado, PagoProveedor,
    ServicioPublico, PagoServicio, Impuesto
)


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


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ("jugador", "monto", "fecha", "estado", "metodo")
    list_filter = ("estado", "metodo", "fecha")
    search_fields = ("jugador__nombre", "jugador__apellido", "referencia")
    date_hierarchy = "fecha"


@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "apellido", "cargo", "salario_base", "activo")
    list_filter = ("activo", "cargo")
    search_fields = ("nombre", "apellido", "dni")


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ("nombre", "cuit", "contacto", "activo")
    list_filter = ("activo",)
    search_fields = ("nombre", "cuit", "contacto")


@admin.register(PagoEmpleado)
class PagoEmpleadoAdmin(admin.ModelAdmin):
    list_display = ("empleado", "tipo", "monto", "fecha_pago", "periodo")
    list_filter = ("tipo", "fecha_pago")
    search_fields = ("empleado__nombre", "empleado__apellido")
    date_hierarchy = "fecha_pago"


@admin.register(PagoProveedor)
class PagoProveedorAdmin(admin.ModelAdmin):
    list_display = ("proveedor", "concepto", "monto", "fecha_vencimiento", "estado")
    list_filter = ("estado", "fecha_vencimiento")
    search_fields = ("proveedor__nombre", "concepto", "numero_factura")
    date_hierarchy = "fecha_vencimiento"


@admin.register(ServicioPublico)
class ServicioPublicoAdmin(admin.ModelAdmin):
    list_display = ("tipo", "proveedor", "numero_cuenta", "activo")
    list_filter = ("tipo", "activo")
    search_fields = ("proveedor", "numero_cuenta")


@admin.register(PagoServicio)
class PagoServicioAdmin(admin.ModelAdmin):
    list_display = ("servicio", "periodo", "monto", "fecha_vencimiento", "estado")
    list_filter = ("estado", "servicio__tipo", "fecha_vencimiento")
    search_fields = ("servicio__proveedor", "numero_factura")
    date_hierarchy = "fecha_vencimiento"


@admin.register(Impuesto)
class ImpuestoAdmin(admin.ModelAdmin):
    list_display = ("tipo", "periodo", "monto", "fecha_vencimiento", "estado")
    list_filter = ("tipo", "estado", "fecha_vencimiento")
    search_fields = ("tipo", "periodo")
    date_hierarchy = "fecha_vencimiento"


from .admin_auditoria import *
