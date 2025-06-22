from django.urls import path
from . import views

app_name = "reservas"

urlpatterns = [
    path("grilla/", views.grilla_reservas, name="grilla"),
    path("reservar/", views.reservar_turno, name="reservar_turno"),
    # Agrega aquí otras vistas de reservas si es necesario
]
