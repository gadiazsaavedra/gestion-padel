from django import forms
from .models import Venta, DetalleVenta
from gestion_stock.models import Producto


class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ['metodo_pago', 'observaciones']
        widgets = {
            'observaciones': forms.Textarea(attrs={'rows': 2})
        }


class DetalleVentaForm(forms.ModelForm):
    class Meta:
        model = DetalleVenta
        fields = ['producto', 'cantidad']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo mostrar productos activos con stock
        self.fields['producto'].queryset = Producto.objects.filter(
            activo=True, stock_actual__gt=0
        )
    
    def clean(self):
        cleaned_data = super().clean()
        producto = cleaned_data.get('producto')
        cantidad = cleaned_data.get('cantidad')
        
        if producto and cantidad:
            if not producto.puede_vender(cantidad):
                raise forms.ValidationError(
                    f'Stock insuficiente. Disponible: {producto.stock_actual}'
                )
        
        return cleaned_data


class ProductoBusquedaForm(forms.Form):
    busqueda = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Buscar por nombre o SKU...',
            'class': 'form-control'
        })
    )
    categoria = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label='Todas las categorías'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from gestion_stock.models import CategoriaProducto
        self.fields['categoria'].queryset = CategoriaProducto.objects.filter(activo=True)
