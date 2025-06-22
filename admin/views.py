from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render


@staff_member_required
def admin_dashboard(request):
    return render(request, "admin/dashboard.html")


@staff_member_required
def admin_gestion_jugadores(request):
    return render(request, "admin/gestion_jugadores.html")


@staff_member_required
def admin_gestion_reservas(request):
    return render(request, "admin/gestion_reservas.html")


@staff_member_required
def admin_pagos(request):
    return render(request, "admin/pagos.html")


@staff_member_required
def admin_torneos(request):
    return render(request, "admin/torneos.html")


@staff_member_required
def admin_notificaciones(request):
    return render(request, "admin/notificaciones.html")


@staff_member_required
def admin_grupos(request):
    return render(request, "admin/grupos.html")


@staff_member_required
def admin_reportes(request):
    return render(request, "admin/reportes.html")


@staff_member_required
def admin_configuracion(request):
    return render(request, "admin/configuracion.html")


@staff_member_required
def admin_soporte(request):
    return render(request, "admin/soporte.html")


@staff_member_required
def admin_bar_stock(request):
    return render(request, "admin/bar_stock.html")
