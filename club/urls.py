from django.urls import path, include
from . import views
from jugadores.views import notificaciones_panel, gestionar_grupo_sugerido
from reservas.views import (
    grilla_reservas,
    reservar_turno,
    detalle_reserva,
    editar_reserva,
    cancelar_reserva,
)
from .views_logout import custom_logout_view
from django.contrib.auth import views as auth_views
from django.http import JsonResponse


def username_disponible(request):
    username = request.GET.get("username", "")
    from django.contrib.auth.models import User

    disponible = not User.objects.filter(username=username).exists()
    return JsonResponse({"disponible": disponible})


urlpatterns = [
    path("", views.homepage, name="homepage"),
    path("jugadores/", include("jugadores.urls", namespace="jugadores")),
    path("jugadores/nuevo/", views.jugador_create, name="jugador_create"),
    path("jugadores/<int:pk>/editar/", views.jugador_edit, name="jugador_edit"),
    path("jugadores/<int:pk>/eliminar/", views.jugador_delete, name="jugador_delete"),
    path("perfil/editar/", views.perfil_jugador_edit, name="perfil_jugador_edit"),
    path("notificaciones/", notificaciones_panel, name="notificaciones_panel"),
    path(
        "grupos-sugeridos/<int:grupo_id>/<str:accion>/",
        gestionar_grupo_sugerido,
        name="gestionar_grupo_sugerido",
    ),
    path("reservas/", include("reservas.urls", namespace="reservas")),
    path("reservas/grilla/", grilla_reservas, name="grilla_reservas"),
    path(
        "reservas/reservar/<str:fecha>/<str:hora>/",
        reservar_turno,
        name="reservar_turno",
    ),
    path("reservas/detalle/<int:reserva_id>/", detalle_reserva, name="detalle_reserva"),
    path("reservas/editar/<int:reserva_id>/", editar_reserva, name="editar_reserva"),
    path(
        "reservas/cancelar/<int:reserva_id>/", cancelar_reserva, name="cancelar_reserva"
    ),
    # path("bar/", include("bar.urls", namespace="bar")),  # Temporalmente comentado
    path("review/nuevo/", views.dejar_review, name="dejar_review"),
    path("blog/", views.blog_list, name="blog_list"),
    path("blog/<int:pk>/", views.blog_detalle, name="blog_detalle"),
    path("contacto/", views.contacto_rapido, name="contacto_rapido"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path(
        "perfil/disponibilidad/",
        views.disponibilidad_jugador_view,
        name="disponibilidad_jugador",
    ),
    path(
        "perfil/disponibilidad/eliminar/<int:pk>/",
        views.eliminar_disponibilidad,
        name="eliminar_disponibilidad",
    ),
    path("panel/emparejador/", views.panel_matchmaking, name="panel_matchmaking"),
    path("accounts/login/", views.login_view, name="login"),
    path("login/", views.login_view, name="login"),
    path("logout/", custom_logout_view, name="logout"),
    path("registro/", views.registro_jugador, name="registro_jugador"),
    path("mi-panel/", views.panel_usuario, name="panel_usuario"),
    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(
            template_name="registration/password_reset_form.html"
        ),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="registration/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="registration/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="registration/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path("activar/<uidb64>/<token>/", views.activar_cuenta, name="activar_cuenta"),
    path(
        "reservar-desde-sugerencia/",
        views.reservar_desde_sugerencia,
        name="reservar_desde_sugerencia",
    ),
    path("torneos/", views.torneos_list, name="torneos_list"),
    path("torneos/<int:torneo_id>/", views.torneo_detalle, name="torneo_detalle"),
    path(
        "torneos/<int:torneo_id>/inscribirse/",
        views.inscribirse_torneo,
        name="inscribirse_torneo",
    ),
    path("ranking/", views.ranking_general, name="ranking_general"),
    path("ajax/username_disponible/", username_disponible, name="username_disponible"),
    path("club/", views.login_view, name="login_club"),
    path("recepcionista/", include("recepcionista.urls", namespace="recepcionista")),
]
