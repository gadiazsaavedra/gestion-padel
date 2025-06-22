from django.urls import path
from . import views
from club.views import jugadores_list
from .views import PanelJugadorView

app_name = "jugadores"

urlpatterns = [
    path("panel/", PanelJugadorView.as_view(), name="panel_jugador"),
    path("sugerir-grupo/", views.sugerir_grupo, name="sugerir_grupo"),
    path("mis-reservas/", views.mis_reservas, name="mis_reservas"),
    path("pagos/", views.pagos_jugador, name="pagos_jugador"),
    path("ranking/", views.ranking, name="ranking"),
    path(
        "notificaciones/", views.notificaciones_jugador, name="notificaciones_jugador"
    ),
    path(
        "notificaciones/marcar-leida/<int:notificacion_id>/",
        views.marcar_notificacion_leida,
        name="marcar_notificacion_leida",
    ),
    path(
        "notificaciones/marcar-todas-leidas/",
        views.marcar_todas_notificaciones_leidas,
        name="marcar_todas_notificaciones_leidas",
    ),
    path("perfil/", views.perfil_jugador, name="perfil_jugador"),
    path("emparejamiento/", views.emparejamiento, name="emparejamiento"),
    path("ejecutar-emparejamiento/", views.ejecutar_emparejamiento, name="ejecutar_emparejamiento"),
    path("confirmar-emparejamiento/<int:emparejamiento_id>/", views.confirmar_emparejamiento, name="confirmar_emparejamiento"),
    path("procesar-pago/", views.procesar_pago, name="procesar_pago"),
    path("cancelar-reserva/", views.cancelar_reserva, name="cancelar_reserva"),
    path("", jugadores_list, name="list"),
]
