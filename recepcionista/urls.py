from django.urls import path
from . import views

app_name = "recepcionista"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("emparejador/", views.emparejador, name="emparejador"),
    path("notificaciones/", views.notificaciones, name="notificaciones"),
    path("reservas/", views.gestion_reservas, name="gestion_reservas"),
    path("stock/", views.gestion_stock, name="gestion_stock"),
    path("ventas/", views.ventas, name="ventas"),
    path("reportes/", views.reportes, name="reportes"),
    path("soporte/", views.soporte, name="soporte"),
    path("pagos/", views.pagos, name="pagos"),
    path("confirmar-pago/", views.confirmar_pago, name="confirmar_pago"),
]
