from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Producto, Venta, Caja, MovimientoCaja
from .forms import ProductoForm, VentaForm
from .forms_caja import CajaAperturaForm, CajaCierreForm, MovimientoCajaForm
from django.urls import reverse
from django.db.models import Q, F
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView

# Permisos: solo admin/recepcionistas pueden gestionar productos/ventas


def is_staff(user):
    return (
        user.is_staff
        or user.groups.filter(name__in=["Recepcionistas", "Administradores"]).exists()
    )


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return (
            user.is_staff
            or user.groups.filter(
                name__in=["Recepcionistas", "Administradores"]
            ).exists()
        )


@login_required
@user_passes_test(is_staff)
def producto_create(request):
    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto creado correctamente.")
            return redirect("bar:productos_list")
    else:
        form = ProductoForm()
    return render(request, "bar/producto_form.html", {"form": form})


@login_required
@user_passes_test(is_staff)
def producto_edit(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto actualizado.")
            return redirect("bar:productos_list")
    else:
        form = ProductoForm(instance=producto)
    return render(
        request, "bar/producto_form.html", {"form": form, "producto": producto}
    )


@login_required
@user_passes_test(is_staff)
def producto_delete(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == "POST":
        producto.delete()
        messages.success(request, "Producto eliminado.")
        return redirect("bar:productos_list")
    return render(request, "bar/producto_confirm_delete.html", {"producto": producto})


@login_required
def ventas_list(request):
    ventas = Venta.objects.select_related("producto", "usuario").order_by("-fecha")
    productos = Producto.objects.all().order_by("nombre")
    usuarios = Venta.objects.values_list("usuario__username", flat=True).distinct()

    # Filtros avanzados
    producto_id = request.GET.get("producto")
    usuario = request.GET.get("usuario")
    fecha_inicio = request.GET.get("fecha_inicio")
    fecha_fin = request.GET.get("fecha_fin")
    search = request.GET.get("q", "")

    if producto_id:
        ventas = ventas.filter(producto_id=producto_id)
    if usuario:
        ventas = ventas.filter(usuario__username=usuario)
    if fecha_inicio:
        ventas = ventas.filter(fecha__date__gte=fecha_inicio)
    if fecha_fin:
        ventas = ventas.filter(fecha__date__lte=fecha_fin)
    if search:
        ventas = ventas.filter(producto__nombre__icontains=search)

    # Paginación
    from django.core.paginator import Paginator

    page_size = int(request.GET.get("page_size", 10))
    paginator = Paginator(ventas, page_size)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "bar/ventas_list.html",
        {
            "page_obj": page_obj,
            "productos": productos,
            "usuarios": usuarios,
            "producto_sel": producto_id,
            "usuario_sel": usuario,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "search": search,
            "page_size": page_size,
        },
    )


@login_required
@user_passes_test(is_staff)
def venta_create(request):
    if request.method == "POST":
        form = VentaForm(request.POST)
        if form.is_valid():
            venta = form.save(commit=False)
            venta.usuario = request.user
            producto = venta.producto
            if venta.cantidad > producto.stock:
                messages.error(request, "Stock insuficiente.")
            else:
                producto.stock -= venta.cantidad
                producto.save()
                venta.save()
                # Registrar movimiento de caja automáticamente
                caja = Caja.objects.filter(abierta=True).first()
                if caja:
                    MovimientoCaja.objects.create(
                        caja=caja,
                        venta=venta,
                        concepto=f"Venta de {producto.nombre} (x{venta.cantidad})",
                        monto=producto.precio * venta.cantidad,
                        usuario=request.user,
                    )
                messages.success(
                    request,
                    "Venta registrada, stock actualizado y movimiento de caja generado.",
                )
                return redirect("bar:ventas_list")
    else:
        form = VentaForm()
    return render(request, "bar/venta_form.html", {"form": form})


@login_required
@user_passes_test(is_staff)
def caja_abrir(request):
    caja_abierta = Caja.objects.filter(abierta=True).first()
    if caja_abierta:
        messages.warning(request, "Ya hay una caja abierta.")
        return redirect("bar:caja_detalle", caja_abierta.id)
    if request.method == "POST":
        form = CajaAperturaForm(request.POST)
        if form.is_valid():
            caja = form.save(commit=False)
            caja.usuario_apertura = request.user
            caja.save()
            messages.success(request, "Caja abierta correctamente.")
            return redirect("bar:caja_detalle", caja.id)
    else:
        form = CajaAperturaForm()
    return render(request, "bar/caja_abrir.html", {"form": form})


@login_required
@user_passes_test(is_staff)
def caja_cerrar(request, caja_id):
    caja = get_object_or_404(Caja, pk=caja_id, abierta=True)
    if request.method == "POST":
        form = CajaCierreForm(request.POST, instance=caja)
        if form.is_valid():
            caja = form.save(commit=False)
            caja.abierta = False
            caja.fecha_cierre = timezone.now()
            caja.usuario_cierre = request.user
            caja.save()
            messages.success(request, "Caja cerrada correctamente.")
            return redirect("bar:caja_detalle", caja.id)
    else:
        form = CajaCierreForm(instance=caja)
    return render(request, "bar/caja_cerrar.html", {"form": form, "caja": caja})


@login_required
@user_passes_test(is_staff)
def caja_detalle(request, caja_id):
    caja = get_object_or_404(Caja, pk=caja_id)
    movimientos = caja.movimientos.order_by("-fecha")
    return render(
        request, "bar/caja_detalle.html", {"caja": caja, "movimientos": movimientos}
    )


@login_required
@user_passes_test(is_staff)
def movimiento_caja_create(request, caja_id):
    caja = get_object_or_404(Caja, pk=caja_id, abierta=True)
    if request.method == "POST":
        form = MovimientoCajaForm(request.POST)
        if form.is_valid():
            movimiento = form.save(commit=False)
            movimiento.caja = caja
            movimiento.usuario = request.user
            movimiento.save()
            messages.success(request, "Movimiento registrado en caja.")
            return redirect("bar:caja_detalle", caja.id)
    else:
        form = MovimientoCajaForm()
    return render(
        request, "bar/movimiento_caja_form.html", {"form": form, "caja": caja}
    )


@login_required
@user_passes_test(is_staff)
def reporte_ventas(request):
    from django.db.models import Sum, Count

    ventas = Venta.objects.select_related("producto").order_by("-fecha")
    resumen = (
        ventas.values("producto__nombre")
        .annotate(
            total_vendido=Sum("cantidad"),
            total_ingresos=Sum(F("cantidad") * F("producto__precio")),
        )
        .order_by("-total_vendido")
    )
    total_ventas = ventas.count()
    total_ingresos = (
        ventas.aggregate(total=Sum(F("cantidad") * F("producto__precio")))["total"] or 0
    )
    return render(
        request,
        "bar/reporte_ventas.html",
        {
            "ventas": ventas[:50],
            "resumen": resumen,
            "total_ventas": total_ventas,
            "total_ingresos": total_ingresos,
        },
    )


@login_required
@user_passes_test(is_staff)
def reporte_stock(request):
    productos = Producto.objects.all().order_by("stock", "nombre")
    return render(request, "bar/reporte_stock.html", {"productos": productos})


class ProductoListCBV(StaffRequiredMixin, ListView):
    model = Producto
    template_name = "bar/productos_list.html"
    context_object_name = "productos"
    ordering = ["nombre"]
    paginate_by = 10  # Puedes ajustar el valor según preferencia

    def get_queryset(self):
        qs = super().get_queryset()
        categoria = self.request.GET.get("categoria", "")
        stock_filtro = self.request.GET.get("stock", "")
        UMBRAL_BAJO_STOCK = 5
        if categoria:
            qs = qs.filter(categoria=categoria)
        if stock_filtro == "bajo":
            qs = qs.filter(stock__lt=UMBRAL_BAJO_STOCK)
        elif stock_filtro == "normal":
            qs = qs.filter(stock__gte=UMBRAL_BAJO_STOCK)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        UMBRAL_BAJO_STOCK = 5
        context["categorias"] = Producto.CATEGORIAS
        context["categoria_sel"] = self.request.GET.get("categoria", "")
        context["stock_filtro"] = self.request.GET.get("stock", "")
        context["umbral_bajo_stock"] = UMBRAL_BAJO_STOCK
        context["bajo_stock_count"] = Producto.objects.filter(
            stock__lt=UMBRAL_BAJO_STOCK
        ).count()
        return context
