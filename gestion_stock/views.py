from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Producto, CategoriaProducto, MovimientoStock
from .forms import ProductoForm
from club.models_auditoria import Auditoria
from club.utils import notificar_inscripcion_torneo  # reutilizaremos notificaciones
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.db.models import Q


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


class ProductoListView(AdminRequiredMixin, ListView):
    model = Producto
    template_name = "gestion_stock/producto_list.html"
    context_object_name = "productos"

    def get_queryset(self):
        return super().get_queryset().select_related("categoria")


class ProductoCreateView(AdminRequiredMixin, CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = "gestion_stock/producto_form.html"
    success_url = reverse_lazy("gestion_stock:producto_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        Auditoria.objects.create(
            usuario=self.request.user,
            accion="stock",
            descripcion=f"Creación de producto: {form.instance.nombre}",
            objeto_id=str(form.instance.pk),
            objeto_tipo="Producto",
        )
        # Registrar en historial
        MovimientoStock.objects.create(
            producto=form.instance,
            cantidad=form.instance.stock_actual,
            stock_anterior=0,
            stock_nuevo=form.instance.stock_actual,
            tipo="entrada",
            motivo="Alta inicial",
            usuario=self.request.user,
        )
        # Alerta si stock bajo
        if form.instance.stock_actual <= (form.instance.stock_minimo or 0):
            notificar_inscripcion_torneo(
                self.request.user, f"Stock bajo: {form.instance.nombre}"
            )
        messages.success(self.request, "Producto creado correctamente.")
        return response


class ProductoUpdateView(AdminRequiredMixin, UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = "gestion_stock/producto_form.html"
    success_url = reverse_lazy("gestion_stock:producto_list")

    def form_valid(self, form):
        producto = self.get_object()
        stock_antes = producto.stock_actual
        response = super().form_valid(form)
        Auditoria.objects.create(
            usuario=self.request.user,
            accion="stock",
            descripcion=f"Edición de producto: {form.instance.nombre}",
            objeto_id=str(form.instance.pk),
            objeto_tipo="Producto",
        )
        # Registrar en historial
        cantidad_cambio = form.instance.stock_actual - stock_antes
        tipo = "ajuste"
        if cantidad_cambio > 0:
            tipo = "entrada"
        elif cantidad_cambio < 0:
            tipo = "salida"
        if cantidad_cambio != 0:
            MovimientoStock.objects.create(
                producto=form.instance,
                cantidad=cantidad_cambio,
                stock_anterior=stock_antes,
                stock_nuevo=form.instance.stock_actual,
                tipo=tipo,
                motivo="Modificación de stock",
                usuario=self.request.user,
            )
            # Alerta si stock bajo
            if form.instance.stock_actual <= (form.instance.stock_minimo or 0):
                notificar_inscripcion_torneo(
                    self.request.user, f"Stock bajo: {form.instance.nombre}"
                )
            # Alerta si movimiento inusual
            if abs(cantidad_cambio) > 50:  # umbral configurable
                notificar_inscripcion_torneo(
                    self.request.user,
                    f"Movimiento inusual de stock en {form.instance.nombre}: {cantidad_cambio}",
                )
        messages.success(self.request, "Producto actualizado correctamente.")
        return response


class ProductoDeleteView(AdminRequiredMixin, DeleteView):
    model = Producto
    template_name = "gestion_stock/producto_confirm_delete.html"
    success_url = reverse_lazy("gestion_stock:producto_list")

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        Auditoria.objects.create(
            usuario=request.user,
            accion="stock",
            descripcion=f"Eliminación de producto: {obj.nombre}",
            objeto_id=str(obj.pk),
            objeto_tipo="Producto",
        )
        # Registrar en historial
        MovimientoStock.objects.create(
            producto=obj,
            cantidad=-obj.stock_actual,
            stock_anterior=obj.stock_actual,
            stock_nuevo=0,
            tipo="salida",
            motivo="Eliminación de producto",
            usuario=request.user,
        )
        messages.success(self.request, "Producto eliminado correctamente.")
        return super().delete(request, *args, **kwargs)


@method_decorator(staff_member_required, name="dispatch")
class HistorialStockListView(ListView):
    model = MovimientoStock
    template_name = "gestion_stock/historial_stock_list.html"
    context_object_name = "movimientos"
    paginate_by = 30
    ordering = ["-fecha"]

    def get_queryset(self):
        qs = super().get_queryset().select_related("producto")
        producto = self.request.GET.get("producto")
        tipo = self.request.GET.get("tipo")
        usuario = self.request.GET.get("usuario")
        search = self.request.GET.get("q")
        if producto:
            qs = qs.filter(producto__nombre__icontains=producto)
        if tipo:
            qs = qs.filter(tipo=tipo)
        if usuario:
            qs = qs.filter(usuario__icontains=usuario)
        if search:
            qs = qs.filter(
                Q(producto__nombre__icontains=search)
                | Q(motivo__icontains=search)
                | Q(usuario__icontains=search)
            )
        return qs


@method_decorator(staff_member_required, name="dispatch")
class AlertasStockListView(ListView):
    model = MovimientoStock
    template_name = "gestion_stock/alertas_stock_list.html"
    context_object_name = "alertas"
    paginate_by = 30
    ordering = ["-fecha"]

    def get_queryset(self):
        qs = super().get_queryset().select_related("producto")
        search = self.request.GET.get("q")
        qs = qs.filter(
            Q(motivo__icontains="stock bajo") | Q(motivo__icontains="inusual")
        )
        if search:
            qs = qs.filter(
                Q(producto__nombre__icontains=search)
                | Q(motivo__icontains=search)
                | Q(usuario__icontains=search)
            )
        return qs
