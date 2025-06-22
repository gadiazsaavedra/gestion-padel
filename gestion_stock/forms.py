from django import forms
from .models import Producto


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        exclude = ["fecha_alta", "ultima_modificacion"]
        widgets = {
            "nombre": forms.TextInput(
                attrs={"class": "block w-full form-input rounded border-gray-300 mb-2"}
            ),
            "descripcion": forms.Textarea(
                attrs={
                    "class": "block w-full form-textarea rounded border-gray-300 mb-2",
                    "rows": 3,
                }
            ),
            "categoria": forms.Select(
                attrs={"class": "block w-full form-select rounded border-gray-300 mb-2"}
            ),
            "precio_venta": forms.NumberInput(
                attrs={"class": "block w-full form-input rounded border-gray-300 mb-2"}
            ),
            "precio_costo": forms.NumberInput(
                attrs={"class": "block w-full form-input rounded border-gray-300 mb-2"}
            ),
            "stock_actual": forms.NumberInput(
                attrs={"class": "block w-full form-input rounded border-gray-300 mb-2"}
            ),
            "stock_minimo": forms.NumberInput(
                attrs={"class": "block w-full form-input rounded border-gray-300 mb-2"}
            ),
            "activo": forms.CheckboxInput(
                attrs={"class": "form-checkbox h-5 w-5 text-blue-600"}
            ),
        }
