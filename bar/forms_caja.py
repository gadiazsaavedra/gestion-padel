from django import forms
from .models import Caja, MovimientoCaja


class CajaAperturaForm(forms.ModelForm):
    class Meta:
        model = Caja
        fields = ["saldo_inicial"]
        widgets = {
            "saldo_inicial": forms.NumberInput(attrs={"min": 0, "step": 0.01}),
        }


class CajaCierreForm(forms.ModelForm):
    class Meta:
        model = Caja
        fields = ["saldo_final"]
        widgets = {
            "saldo_final": forms.NumberInput(attrs={"min": 0, "step": 0.01}),
        }


class MovimientoCajaForm(forms.ModelForm):
    class Meta:
        model = MovimientoCaja
        fields = ["concepto", "monto"]
        widgets = {
            "monto": forms.NumberInput(attrs={"min": 0, "step": 0.01}),
        }
