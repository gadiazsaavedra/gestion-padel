from django.contrib import admin
from .models_auditoria import Auditoria


@admin.register(Auditoria)
class AuditoriaAdmin(admin.ModelAdmin):
    list_display = (
        "fecha",
        "usuario",
        "accion",
        "objeto_tipo",
        "objeto_id",
        "descripcion",
    )
    list_filter = ("accion", "usuario", "objeto_tipo", "fecha")
    search_fields = ("descripcion", "objeto_id", "usuario__username")
    date_hierarchy = "fecha"
    ordering = ("-fecha",)
