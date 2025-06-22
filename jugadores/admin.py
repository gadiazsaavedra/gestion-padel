from django.contrib import admin
from .models import GrupoSugerido, Notificacion


@admin.register(GrupoSugerido)
class GrupoSugeridoAdmin(admin.ModelAdmin):
    list_display = ("id", "nivel", "genero", "fecha_sugerencia")
    list_filter = ("nivel", "genero", "fecha_sugerencia")
    filter_horizontal = ("jugadores",)


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ("destinatario", "mensaje", "leida", "fecha_creacion")
    list_filter = ("leida", "fecha_creacion")
    search_fields = ("destinatario__username", "mensaje")
