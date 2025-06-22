from django.urls import path
from .views import (
    ProductoListView,
    ProductoCreateView,
    ProductoUpdateView,
    ProductoDeleteView,
    HistorialStockListView,
    AlertasStockListView,
)

app_name = "gestion_stock"

urlpatterns = [
    path("productos/", ProductoListView.as_view(), name="producto_list"),
    path("productos/nuevo/", ProductoCreateView.as_view(), name="producto_create"),
    path(
        "productos/<int:pk>/editar/",
        ProductoUpdateView.as_view(),
        name="producto_update",
    ),
    path(
        "productos/<int:pk>/eliminar/",
        ProductoDeleteView.as_view(),
        name="producto_delete",
    ),
    path("historial/", HistorialStockListView.as_view(), name="historial_stock"),
    path("alertas/", AlertasStockListView.as_view(), name="alertas_stock"),
]
