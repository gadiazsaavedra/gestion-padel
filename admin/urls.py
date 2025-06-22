from django.urls import path
from . import views

urlpatterns = [
    path("", views.admin_dashboard, name="admin_dashboard"),
    path("jugadores/", views.admin_gestion_jugadores, name="admin_gestion_jugadores"),
    path("reservas/", views.admin_gestion_reservas, name="admin_gestion_reservas"),
    path("pagos/", views.admin_pagos, name="admin_pagos"),
    path("torneos/", views.admin_torneos, name="admin_torneos"),
    path("bar-stock/", views.admin_bar_stock, name="admin_bar_stock"),
    path("notificaciones/", views.admin_notificaciones, name="admin_notificaciones"),
    path("grupos/", views.admin_grupos, name="admin_grupos"),
    path("reportes/", views.admin_reportes, name="admin_reportes"),
    path("configuracion/", views.admin_configuracion, name="admin_configuracion"),
    path("soporte/", views.admin_soporte, name="admin_soporte"),
]
