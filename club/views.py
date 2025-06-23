from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.contrib.admin.views.decorators import staff_member_required
from club.models import Reserva
from bar.models import Venta, Producto
from jugadores.models import Jugador
import json
from django.utils import timezone
from .models import (
    Jugador,
    Grupo,
    Reserva,
    Blog,
    Review,
    FAQ,
    BlogComentario,
    Torneo,
    PartidoTorneo,
    Ranking,
)
from .models_multimedia import Multimedia, Testimonio
from .forms import (
    JugadorForm,
    GrupoForm,
    ReservaForm,
    BlogForm,
    ReviewForm,
    PerfilJugadorForm,  # <-- importado
    DisponibilidadJugadorForm,
    CustomAuthenticationForm,
    RegistroJugadorForm,
)
from .models import DisponibilidadJugador
from .utils import (
    buscar_matches_y_notificar,
    enviar_email_activacion,
    get_sugerencias_usuario,
    notificar_inscripcion_torneo,
)
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from datetime import datetime
from django.db.models import Sum
from django.db import IntegrityError


def es_recepcionista_o_admin(user):
    return user.is_authenticated and (
        user.is_superuser
        or user.is_staff
        or user.groups.filter(name__in=["recepcionistas", "administradores"]).exists()
    )


# Vista de ejemplo para listar jugadores
def jugadores_list(request):
    query = request.GET.get("q", "")
    nivel = request.GET.get("nivel", "")
    genero = request.GET.get("genero", "")
    disponibilidad = request.GET.get("disponibilidad", "")
    jugadores = Jugador.objects.all()
    if query:
        jugadores = (
            jugadores.filter(nombre__icontains=query)
            | jugadores.filter(apellido__icontains=query)
            | jugadores.filter(email__icontains=query)
        )
    if nivel:
        jugadores = jugadores.filter(nivel=nivel)
    if genero:
        jugadores = jugadores.filter(genero=genero)
    if disponibilidad:
        # Suponiendo que disponibilidad es un string como 'lunes', 'martes', etc. en el JSONField
        jugadores = jugadores.filter(disponibilidad__icontains=disponibilidad)
    paginator = Paginator(jugadores.distinct(), 10)  # 10 jugadores por página
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        "club/jugadores_list.html",
        {
            "page_obj": page_obj,
            "query": query,
            "nivel": nivel,
            "genero": genero,
            "disponibilidad": disponibilidad,
            "niveles": Jugador.NIVELES,
            "generos": Jugador.GENEROS,
        },
    )


# Vista de ejemplo para crear un jugador
@login_required
@user_passes_test(es_recepcionista_o_admin)
def jugador_create(request):
    DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
    HORAS = [
        "08:00",
        "09:00",
        "10:00",
        "11:00",
        "12:00",
        "13:00",
        "14:00",
        "15:00",
        "16:00",
        "17:00",
        "18:00",
        "19:00",
        "20:00",
        "21:00",
        "22:00",
    ]
    if request.method == "POST":
        form = JugadorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "¡Jugador creado exitosamente!")
            return redirect("jugadores:list")
    else:
        form = JugadorForm()
    return render(
        request, "club/jugador_form.html", {"form": form, "dias": DIAS, "horas": HORAS}
    )


@login_required
@user_passes_test(es_recepcionista_o_admin)
def jugador_edit(request, pk):
    DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
    HORAS = [
        "08:00",
        "09:00",
        "10:00",
        "11:00",
        "12:00",
        "13:00",
        "14:00",
        "15:00",
        "16:00",
        "17:00",
        "18:00",
        "19:00",
        "20:00",
        "21:00",
        "22:00",
    ]
    jugador = get_object_or_404(Jugador, pk=pk)
    if request.method == "POST":
        form = JugadorForm(request.POST, instance=jugador)
        if form.is_valid():
            form.save()
            messages.success(request, "¡Jugador editado correctamente!")
            return redirect("jugadores:list")
    else:
        form = JugadorForm(instance=jugador)
    return render(
        request,
        "club/jugador_form.html",
        {"form": form, "editar": True, "dias": DIAS, "horas": HORAS},
    )


@login_required
@user_passes_test(es_recepcionista_o_admin)
def jugador_delete(request, pk):
    jugador = get_object_or_404(Jugador, pk=pk)
    if request.method == "POST":
        jugador.delete()
        messages.success(request, "Jugador eliminado correctamente.")
        return redirect("jugadores:list")
    return render(request, "club/jugador_confirm_delete.html", {"jugador": jugador})


@login_required
def perfil_jugador_edit(request):
    DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
    HORAS = [
        "08:00",
        "09:00",
        "10:00",
        "11:00",
        "12:00",
        "13:00",
        "14:00",
        "15:00",
        "16:00",
        "17:00",
        "18:00",
        "19:00",
        "20:00",
        "21:00",
        "22:00",
    ]
    if not hasattr(request.user, "jugador"):
        messages.error(request, "No tienes un perfil de jugador asociado.")
        return redirect("jugadores:list")
    jugador = request.user.jugador
    if request.method == "POST":
        form = PerfilJugadorForm(request.POST, instance=jugador)
        if form.is_valid():
            form.save()
            messages.success(request, "¡Perfil actualizado correctamente!")
            return redirect("perfil_jugador_edit")
    else:
        form = PerfilJugadorForm(instance=jugador)
    return render(
        request,
        "club/perfil_jugador_form.html",
        {"form": form, "perfil": True, "dias": DIAS, "horas": HORAS},
    )


@login_required
def dejar_review(request):
    if not hasattr(request.user, "jugador"):
        messages.error(request, "Debes tener perfil de jugador para dejar una review.")
        return redirect("homepage")
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.jugador = request.user.jugador
            review.save()
            messages.success(request, "¡Gracias por tu opinión!")
            return redirect("homepage")
    else:
        form = ReviewForm()
    return render(request, "club/dejar_review.html", {"form": form})


@login_required
def disponibilidad_jugador_view(request):
    jugador = request.user.jugador
    if request.method == "POST":
        # Actualiza el check de en_tinder
        en_tinder = bool(request.POST.get("en_tinder"))
        if jugador.en_tinder != en_tinder:
            jugador.en_tinder = en_tinder
            jugador.save()
        # Alta de nueva disponibilidad
        form = DisponibilidadJugadorForm(request.POST)
        if form.is_valid():
            nueva = form.save(commit=False)
            nueva.jugador = jugador
            nueva.save()
            messages.success(request, "Disponibilidad agregada correctamente.")
            return redirect("disponibilidad_jugador")
    else:
        form = DisponibilidadJugadorForm()
    disponibilidades = jugador.disponibilidades.all()
    return render(
        request,
        "club/disponibilidad_jugador_form.html",
        {"form": form, "jugador": jugador, "disponibilidades": disponibilidades},
    )


@login_required
def eliminar_disponibilidad(request, pk):
    jugador = request.user.jugador
    disp = get_object_or_404(DisponibilidadJugador, pk=pk, jugador=jugador)
    if request.method == "POST":
        disp.delete()
        messages.success(request, "Disponibilidad eliminada.")
    return redirect("disponibilidad_jugador")


@login_required
def homepage(request):
    multimedia = Multimedia.objects.filter(publicado=True).order_by("orden", "-fecha")
    testimonios = Testimonio.objects.filter(publicado=True).order_by("orden", "-fecha")
    reviews = Review.objects.all().order_by("-fecha")[:8]
    faqs = FAQ.objects.filter(publicado=True).order_by("orden", "id")
    return render(
        request,
        "club/homepage.html",
        {
            "multimedia": multimedia,
            "testimonios": testimonios,
            "reviews": reviews,
            "faqs": faqs,
        },
    )


def blog_list(request):
    posts = Blog.objects.select_related("autor").order_by("-destacado", "-fecha")
    paginator = Paginator(posts, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "club/blog_list.html", {"page_obj": page_obj})


def blog_detalle(request, pk):
    post = get_object_or_404(Blog, pk=pk)
    comentarios = post.comentarios.filter(publicado=True).order_by("-fecha")
    if request.method == "POST" and request.user.is_authenticated:
        texto = request.POST.get("texto", "").strip()
        if texto:
            BlogComentario.objects.create(blog=post, usuario=request.user, texto=texto)
            messages.success(request, "Comentario enviado.")
            return redirect("blog_detalle", pk=pk)
    return render(
        request, "club/blog_detalle.html", {"post": post, "comentarios": comentarios}
    )


def contacto_rapido(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        email = request.POST.get("email", "").strip()
        mensaje = request.POST.get("mensaje", "").strip()
        if nombre and email and mensaje:
            # Enviar email al club (ajusta el destinatario en settings)
            send_mail(
                subject=f"Contacto rápido de {nombre}",
                message=f"Nombre: {nombre}\nEmail: {email}\n\nMensaje:\n{mensaje}",
                from_email=None,
                recipient_list=["info@clubpadel.com"],
            )
            messages.success(request, "¡Mensaje enviado! Te responderemos pronto.")
        else:
            messages.error(request, "Completa todos los campos.")
    return redirect("homepage")


@staff_member_required
def dashboard(request):
    from django.db.models import Sum, Count, Q, F
    from django.db import models
    from club.models import Pago
    from datetime import timedelta
    
    hoy = timezone.localdate()
    # Filtros
    fecha_inicio = request.GET.get("fecha_inicio")
    fecha_fin = request.GET.get("fecha_fin")
    torneo_id = request.GET.get("torneo")
    torneos = Torneo.objects.all()

    # Rango de fechas para los gráficos (por defecto últimos 7 días)
    if fecha_inicio and fecha_fin:
        try:
            fecha_inicio_dt = timezone.datetime.strptime(
                fecha_inicio, "%Y-%m-%d"
            ).date()
            fecha_fin_dt = timezone.datetime.strptime(fecha_fin, "%Y-%m-%d").date()
        except Exception:
            fecha_inicio_dt = hoy - timezone.timedelta(days=6)
            fecha_fin_dt = hoy
    else:
        fecha_inicio_dt = hoy - timezone.timedelta(days=6)
        fecha_fin_dt = hoy
    
    # === MÉTRICAS FINANCIERAS ===
    # Ingresos de reservas del día
    ingresos_reservas_hoy = Pago.objects.filter(
        fecha=hoy, estado='pagado'
    ).aggregate(total=Sum('monto'))['total'] or 0
    
    # Ingresos de bar/kiosco del día
    from bar.models import Venta
    try:
        ventas_bar_hoy = Venta.objects.filter(fecha__date=hoy)
        ingresos_bar_hoy = sum(venta.total for venta in ventas_bar_hoy)
    except Exception:
        ingresos_bar_hoy = 0
    
    # Total ingresos del día
    ingresos_hoy = ingresos_reservas_hoy + ingresos_bar_hoy
    
    # Ingresos del mes
    inicio_mes = hoy.replace(day=1)
    ingresos_reservas_mes = Pago.objects.filter(
        fecha__gte=inicio_mes, fecha__lte=hoy, estado='pagado'
    ).aggregate(total=Sum('monto'))['total'] or 0
    
    try:
        ventas_bar_mes = Venta.objects.filter(
            fecha__date__gte=inicio_mes, fecha__date__lte=hoy
        )
        ingresos_bar_mes = sum(venta.total for venta in ventas_bar_mes)
    except Exception:
        ingresos_bar_mes = 0
    
    # Total ingresos del mes
    ingresos_mes = ingresos_reservas_mes + ingresos_bar_mes
    
    # Pagos pendientes
    pagos_pendientes = Pago.objects.filter(estado='pendiente').count()
    monto_pendiente = Pago.objects.filter(
        estado='pendiente'
    ).aggregate(total=Sum('monto'))['total'] or 0
    
    # Reservas por estado HOY
    reservas_hoy = {
        'ocupadas': Reserva.objects.filter(fecha=hoy, estado='ocupada').count(),
        'pagadas': Reserva.objects.filter(fecha=hoy, estado='pagada').count(),
        'canceladas': Reserva.objects.filter(fecha=hoy, estado='cancelada').count(),
    }
    
    # Top 5 jugadores por gasto (último mes)
    top_jugadores = Pago.objects.filter(
        fecha__gte=inicio_mes, estado='pagado'
    ).values(
        'jugador__nombre', 'jugador__apellido'
    ).annotate(
        total_gastado=Sum('monto')
    ).order_by('-total_gastado')[:5]
    
    # Horarios más populares (último mes)
    horarios_populares = Reserva.objects.filter(
        fecha__gte=inicio_mes, estado__in=['ocupada', 'pagada']
    ).values('hora').annotate(
        total_reservas=Count('id')
    ).order_by('-total_reservas')[:5]

    # Productos más vendidos del mes (temporalmente vacío hasta arreglar modelo)
    productos_top = []
    
    # Ventas por categoría del mes (temporalmente vacío hasta arreglar modelo)
    ventas_categoria = []
    
    # Métricas generales
    reservas_activas = (
        Reserva.objects.filter(fecha=hoy).exclude(estado="disponible").count()
    )
    ventas_hoy_count = Venta.objects.filter(fecha__date=hoy).count()
    jugadores_activos = Jugador.objects.count()
    productos_bajo_stock = Producto.objects.filter(stock_actual__lt=5).count()

    # Reservas por estado en rango
    dias = [
        fecha_inicio_dt + timezone.timedelta(days=i)
        for i in range((fecha_fin_dt - fecha_inicio_dt).days + 1)
    ]
    reservas_chart = {
        "type": "bar",
        "data": {
            "labels": [d.strftime("%d/%m") for d in dias],
            "datasets": [
                {
                    "label": "Ocupada",
                    "backgroundColor": "#facc15",
                    "data": [
                        Reserva.objects.filter(fecha=d, estado="ocupada").count()
                        for d in dias
                    ],
                },
                {
                    "label": "Pagada",
                    "backgroundColor": "#60a5fa",
                    "data": [
                        Reserva.objects.filter(fecha=d, estado="pagada").count()
                        for d in dias
                    ],
                },
            ],
        },
        "options": {"responsive": True, "plugins": {"legend": {"position": "top"}}},
    }
    # Ventas por día en rango
    ventas_chart = {
        "type": "line",
        "data": {
            "labels": [d.strftime("%d/%m") for d in dias],
            "datasets": [
                {
                    "label": "Ventas",
                    "backgroundColor": "#22c55e",
                    "borderColor": "#22c55e",
                    "fill": False,
                    "data": [Venta.objects.filter(fecha__date=d).count() for d in dias],
                }
            ],
        },
        "options": {"responsive": True, "plugins": {"legend": {"position": "top"}}},
    }
    # Asistencia semanal filtrada por torneo y fechas
    from django.db.models import Q

    partidos_qs = PartidoTorneo.objects.filter(
        fecha__date__gte=fecha_inicio_dt, fecha__date__lte=fecha_fin_dt
    )
    if torneo_id:
        partidos_qs = partidos_qs.filter(torneo_id=torneo_id)
    asistencia = {}
    for p in partidos_qs:
        for jugador in [p.jugador1, p.jugador2]:
            if jugador:
                nombre = (
                    jugador.get_full_name()
                    if hasattr(jugador, "get_full_name")
                    else str(jugador)
                )
                asistencia[nombre] = asistencia.get(nombre, 0) + 1
    asistencia_top = sorted(asistencia.items(), key=lambda x: x[1], reverse=True)[:7]
    asistencia_chart = {
        "type": "bar",
        "data": {
            "labels": [x[0] for x in asistencia_top],
            "datasets": [
                {
                    "label": "Partidos jugados",
                    "backgroundColor": "#38bdf8",
                    "data": [x[1] for x in asistencia_top],
                }
            ],
        },
        "options": {
            "indexAxis": "y",
            "responsive": True,
            "plugins": {"legend": {"display": False}},
        },
    }
    # Top 5 rendimiento filtrado por torneo
    ranking_qs = Ranking.objects.select_related("jugador")
    if torneo_id:
        ranking_qs = ranking_qs.filter(torneo_id=torneo_id)
    ranking_top = ranking_qs.order_by("-puntos")[:5]
    rendimiento_chart = {
        "type": "pie",
        "data": {
            "labels": [str(r.jugador) for r in ranking_top],
            "datasets": [
                {
                    "label": "Puntos",
                    "backgroundColor": [
                        "#f87171",
                        "#fbbf24",
                        "#34d399",
                        "#60a5fa",
                        "#a78bfa",
                    ],
                    "data": [r.puntos for r in ranking_top],
                }
            ],
        },
        "options": {"responsive": True, "plugins": {"legend": {"position": "top"}}},
    }
    
    # === GRÁFICOS FINANCIEROS ===
    # Ingresos diarios en el rango (Reservas + Bar)
    ingresos_chart = {
        "type": "line",
        "data": {
            "labels": [d.strftime("%d/%m") for d in dias],
            "datasets": [
                {
                    "label": "Reservas ($)",
                    "backgroundColor": "#3b82f6",
                    "borderColor": "#3b82f6",
                    "fill": False,
                    "data": [
                        float(Pago.objects.filter(
                            fecha=d, estado='pagado'
                        ).aggregate(total=Sum('monto'))['total'] or 0)
                        for d in dias
                    ],
                },
                {
                    "label": "Bar/Kiosco ($)",
                    "backgroundColor": "#10b981",
                    "borderColor": "#10b981",
                    "fill": False,
                    "data": [
                        float(sum(
                            v.total for v in Venta.objects.filter(fecha__date=d)
                        ) if Venta.objects.filter(fecha__date=d).exists() else 0)
                        for d in dias
                    ],
                }
            ],
        },
        "options": {
            "responsive": True, 
            "plugins": {"legend": {"position": "top"}},
            "scales": {
                "y": {
                    "beginAtZero": True,
                    "ticks": {
                        "callback": "function(value) { return '$' + value; }"
                    }
                }
            }
        },
    }
    
    # Productos más vendidos
    productos_chart = {
        "type": "bar",
        "data": {
            "labels": [p['producto__nombre'] for p in productos_top],
            "datasets": [
                {
                    "label": "Cantidad Vendida",
                    "backgroundColor": "#f59e0b",
                    "data": [p['total_vendido'] for p in productos_top],
                }
            ],
        },
        "options": {
            "indexAxis": "y",
            "responsive": True,
            "plugins": {"legend": {"display": False}},
        },
    }
    
    # Ventas por categoría
    categoria_chart = {
        "type": "pie",
        "data": {
            "labels": [v['producto__categoria'].title() for v in ventas_categoria],
            "datasets": [
                {
                    "label": "Ingresos ($)",
                    "backgroundColor": [
                        "#ef4444", "#f97316", "#eab308", "#22c55e", "#3b82f6"
                    ],
                    "data": [float(v['total_ingresos']) for v in ventas_categoria],
                }
            ],
        },
        "options": {"responsive": True, "plugins": {"legend": {"position": "right"}}},
    }
    
    # Top jugadores por gasto
    top_jugadores_chart = {
        "type": "bar",
        "data": {
            "labels": [f"{j['jugador__nombre']} {j['jugador__apellido']}" for j in top_jugadores],
            "datasets": [
                {
                    "label": "Gasto Total ($)",
                    "backgroundColor": "#3b82f6",
                    "data": [float(j['total_gastado']) for j in top_jugadores],
                }
            ],
        },
        "options": {
            "indexAxis": "y",
            "responsive": True,
            "plugins": {"legend": {"display": False}},
            "scales": {
                "x": {
                    "beginAtZero": True,
                    "ticks": {
                        "callback": "function(value) { return '$' + value; }"
                    }
                }
            }
        },
    }
    
    # Horarios más populares
    horarios_chart = {
        "type": "doughnut",
        "data": {
            "labels": [h['hora'].strftime('%H:%M') for h in horarios_populares],
            "datasets": [
                {
                    "label": "Reservas",
                    "backgroundColor": [
                        "#ef4444", "#f97316", "#eab308", "#22c55e", "#3b82f6"
                    ],
                    "data": [h['total_reservas'] for h in horarios_populares],
                }
            ],
        },
        "options": {"responsive": True, "plugins": {"legend": {"position": "right"}}},
    }
    return render(
        request,
        "club/dashboard.html",
        {
            # Métricas generales
            "reservas_activas": reservas_activas,
            "ventas_hoy": ventas_hoy_count,
            "jugadores_activos": jugadores_activos,
            "productos_bajo_stock": productos_bajo_stock,
            
            # Métricas financieras
            "ingresos_hoy": ingresos_hoy,
            "ingresos_mes": ingresos_mes,
            "ingresos_reservas_hoy": ingresos_reservas_hoy,
            "ingresos_bar_hoy": ingresos_bar_hoy,
            "ingresos_reservas_mes": ingresos_reservas_mes,
            "ingresos_bar_mes": ingresos_bar_mes,
            "pagos_pendientes": pagos_pendientes,
            "monto_pendiente": monto_pendiente,
            "reservas_hoy": reservas_hoy,
            "top_jugadores": top_jugadores,
            "horarios_populares": horarios_populares,
            "productos_top": productos_top,
            "ventas_categoria": ventas_categoria,
            
            # Gráficos existentes
            "reservas_chart": json.dumps(reservas_chart),
            "ventas_chart": json.dumps(ventas_chart),
            "asistencia_chart": json.dumps(asistencia_chart),
            "rendimiento_chart": json.dumps(rendimiento_chart),
            
            # Nuevos gráficos financieros
            "ingresos_chart": json.dumps(ingresos_chart),
            "top_jugadores_chart": json.dumps(top_jugadores_chart),
            "horarios_chart": json.dumps(horarios_chart),
            "productos_chart": json.dumps(productos_chart),
            "categoria_chart": json.dumps(categoria_chart),
            
            # Filtros
            "torneos": torneos,
            "fecha_inicio": fecha_inicio_dt,
            "fecha_fin": fecha_fin_dt,
            "torneo_id": int(torneo_id) if torneo_id else None,
        },
    )


@login_required
@user_passes_test(es_recepcionista_o_admin)
def panel_matchmaking(request):
    resultado = None
    metodo = None
    if request.method == "POST":
        metodo = request.POST.get("metodo")
        resultado = buscar_matches_y_notificar(metodo=metodo)
        messages.success(
            request, f"Se ejecutó el emparejador y se notificó por: {metodo}"
        )
    return render(
        request,
        "club/panel_matchmaking.html",
        {"resultado": resultado, "metodo": metodo},
    )


def torneos_list(request):
    torneos = Torneo.objects.all().order_by("-fecha_inicio")
    return render(request, "club/torneos_list.html", {"torneos": torneos})


def torneo_detalle(request, torneo_id):
    torneo = get_object_or_404(Torneo, pk=torneo_id)
    partidos = torneo.partidos.all().order_by("fecha")
    ranking = Ranking.objects.filter(torneo=torneo).order_by("-puntos")
    return render(
        request,
        "club/torneo_detalle.html",
        {"torneo": torneo, "partidos": partidos, "ranking": ranking},
    )


def ranking_general(request):
    # Ranking sumando puntos de todos los torneos activos
    ranking = (
        Ranking.objects.values("jugador__nombre", "jugador__apellido")
        .annotate(total_puntos=Sum("puntos"))
        .order_by("-total_puntos")
    )
    return render(request, "club/ranking_general.html", {"ranking": ranking})


from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .forms import CustomAuthenticationForm


def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect("dashboard")
        return redirect("homepage")
    if request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Redirección personalizada para administradores
            if user.is_staff:
                return redirect("dashboard")
            return redirect("homepage")
    else:
        form = CustomAuthenticationForm()
    return render(request, "registration/login.html", {"form": form})


def registro_jugador(request):
    if request.user.is_authenticated:
        return redirect("homepage")
    if request.method == "POST":
        form = RegistroJugadorForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False).user
                user.is_active = False
                user.save()
                form.save()  # Guarda el jugador con el user actualizado
                enviar_email_activacion(user, request)
                messages.success(
                    request,
                    "¡Registro exitoso! Revisa tu email para activar tu cuenta.",
                )
                return redirect("login")
            except IntegrityError:
                form.add_error(
                    "username", "El nombre de usuario ya está en uso. Elige otro."
                )
        # Si el formulario no es válido o hay error, sigue mostrando el form con errores
    else:
        form = RegistroJugadorForm()
    return render(request, "club/registro_jugador.html", {"form": form})


def activar_cuenta(request, uidb64, token):
    UserModel = get_user_model()
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = UserModel.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "¡Cuenta activada! Ya puedes iniciar sesión.")
        return redirect("login")
    else:
        messages.error(request, "El enlace de activación no es válido o ha expirado.")
        return redirect("login")


@login_required
def panel_usuario(request):
    jugador = getattr(request.user, "jugador", None)
    deuda = jugador.calcular_deuda() if jugador else 0
    estadisticas = {
        "partidos_jugados": 12,
        "partidos_ganados": 7,
        "partidos_perdidos": 5,
        "nivel": getattr(jugador, "nivel", "-") if jugador else "-",
        "deuda": deuda,
    }
    proximos_partidos = []  # Consulta tus reservas futuras aquí
    historial = []  # Consulta tus reservas pasadas aquí
    sugerencias = get_sugerencias_usuario(jugador) if jugador else []
    return render(
        request,
        "club/panel_usuario.html",
        {
            "estadisticas": estadisticas,
            "proximos_partidos": proximos_partidos,
            "historial": historial,
            "sugerencias": sugerencias,
        },
    )


@login_required
def reservar_desde_sugerencia(request):
    if request.method == "POST":
        jugador = getattr(request.user, "jugador", None)
        sugerencia = request.POST.get("sugerencia", "")
        # Intentar extraer fecha y hora de la sugerencia (formato esperado)
        import re

        fecha = None
        hora_inicio = None
        # Buscar día y hora en el texto
        dias = [
            "lunes",
            "martes",
            "miércoles",
            "jueves",
            "viernes",
            "sábado",
            "domingo",
        ]
        dia_encontrado = next((d for d in dias if d in sugerencia.lower()), None)
        hora_match = re.search(r"(\d{2}:\d{2})", sugerencia)
        if dia_encontrado and hora_match:
            # Calcular próxima fecha para ese día
            hoy = timezone.localdate()
            dias_idx = {d: i for i, d in enumerate(dias)}
            hoy_idx = hoy.weekday()
            sugerido_idx = dias_idx[dia_encontrado]
            delta = (sugerido_idx - hoy_idx) % 7
            fecha = hoy + timezone.timedelta(days=delta)
            hora_inicio = hora_match.group(1)
        if fecha and hora_inicio:
            # Crear reserva si hay disponibilidad
            existe = Reserva.objects.filter(fecha=fecha, hora=hora_inicio).exists()
            if not existe:
                Reserva.objects.create(
                    jugador=jugador,
                    fecha=fecha,
                    hora=hora_inicio,
                    estado="ocupada",
                )
                messages.success(
                    request,
                    f"Reserva creada para el {dia_encontrado.capitalize()} a las {hora_inicio}.",
                )
            else:
                messages.error(request, "Ya existe una reserva para ese horario.")
        else:
            messages.error(
                request,
                "No se pudo interpretar la sugerencia. Reserva manualmente desde la grilla.",
            )
    return redirect("panel_usuario")


@login_required
def inscribirse_torneo(request, torneo_id):
    torneo = get_object_or_404(Torneo, pk=torneo_id)
    jugador = getattr(request.user, "jugador", None)
    if not jugador:
        messages.error(request, "Debes tener un perfil de jugador para inscribirte.")
        return redirect("torneos_list")
    if torneo.jugadores.filter(id=jugador.id).exists():
        messages.info(request, "Ya estás inscripto en este torneo.")
    else:
        torneo.jugadores.add(jugador)
        notificar_inscripcion_torneo(jugador, torneo)
        messages.success(
            request, f"Te has inscripto correctamente en el torneo '{torneo.nombre}'."
        )
    return redirect("torneo_detalle", torneo_id=torneo.id)


def get_branding_config():
    from .models import BrandingConfig

    return BrandingConfig.objects.first()


from django.template import RequestContext
from django.utils.functional import SimpleLazyObject


def branding_context(request):
    return {"branding_config": SimpleLazyObject(get_branding_config)}
