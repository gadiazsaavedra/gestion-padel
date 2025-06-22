from django import forms
from django.core.exceptions import ValidationError
import re
from .models import Jugador, Grupo, Reserva, Blog, Review, DisponibilidadJugador, Pago
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import User
import unicodedata
from django.utils.text import slugify


class JugadorForm(forms.ModelForm):
    username = forms.CharField(
        label="Usuario",
        max_length=150,
        required=True,
        help_text="Nombre de usuario único para iniciar sesión.",
    )
    email = forms.EmailField(
        label="Email", required=True, help_text="Correo electrónico único."
    )

    class Meta:
        model = Jugador
        fields = [
            "username",
            "nombre",
            "apellido",
            "email",
            "telefono",
            "nivel",
            "genero",
            "avatar",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields["username"].initial = self.instance.user.username
            self.fields["email"].initial = self.instance.user.email

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        qs = User.objects.filter(username=username)
        if self.instance and self.instance.user:
            qs = qs.exclude(pk=self.instance.user.pk)
        if qs.exists():
            raise ValidationError("Ya existe un usuario con ese nombre de usuario.")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        qs = User.objects.filter(email=email)
        if self.instance and self.instance.user:
            qs = qs.exclude(pk=self.instance.user.pk)
        if qs.exists():
            raise ValidationError("Ya existe un usuario registrado con este email.")
        return email

    def save(self, commit=True):
        jugador = super().save(commit=False)
        username = self.cleaned_data.get("username")
        email = self.cleaned_data.get("email")
        if jugador.user:
            user = jugador.user
            user.username = username
            user.email = email
            user.save()
        if commit:
            jugador.save()
            self.save_m2m()
        return jugador

    def clean_telefono(self):
        telefono = self.cleaned_data["telefono"]
        # Permite solo números, espacios, +, -, paréntesis
        if not re.match(r"^[\d\s\-\+\(\)]+$", telefono):
            raise ValidationError(
                "El teléfono solo puede contener números y símbolos válidos (+, -, espacio, paréntesis)."
            )
        if len(re.sub(r"\D", "", telefono)) < 8:
            raise ValidationError("El teléfono debe tener al menos 8 dígitos.")
        return telefono


class PerfilJugadorForm(forms.ModelForm):
    class Meta:
        model = Jugador
        fields = [
            "en_tinder",
        ]


class GrupoForm(forms.ModelForm):
    class Meta:
        model = Grupo
        fields = ["jugadores", "nivel", "genero", "disponibilidad"]


class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = [
            "grupo",
            "fecha",
            "hora",
            "estado",
            "pago_total",
            "pago_parcial",
            "metodo_pago",
        ]


class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ["titulo", "contenido"]


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["jugador", "comentario", "puntaje"]


class DisponibilidadJugadorForm(forms.ModelForm):
    class Meta:
        model = DisponibilidadJugador
        fields = ["dia", "hora_inicio", "hora_fin", "nivel", "preferencia_genero"]
        widgets = {
            "dia": forms.Select(attrs={"class": "w-full border rounded p-2"}),
            "hora_inicio": forms.TimeInput(
                attrs={"type": "time", "class": "w-full border rounded p-2"}
            ),
            "hora_fin": forms.TimeInput(
                attrs={"type": "time", "class": "w-full border rounded p-2"}
            ),
            "nivel": forms.Select(attrs={"class": "w-full border rounded p-2"}),
            "preferencia_genero": forms.Select(
                attrs={"class": "w-full border rounded p-2"}
            ),
        }


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "block w-full rounded border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500 mt-1",
                "placeholder": "Usuario",
                "autofocus": True,
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "block w-full rounded border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500 mt-1",
                "placeholder": "Contraseña",
                "id": "id_password",
            }
        )
    )


class RegistroJugadorForm(forms.ModelForm):
    username = forms.CharField(
        label="Usuario",
        max_length=150,
        required=False,
        help_text="Puedes dejarlo vacío y se sugerirá uno automáticamente.",
    )
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput)
    email = forms.EmailField(label="Email")

    class Meta:
        model = Jugador
        fields = ["nombre", "apellido", "telefono", "nivel", "genero"]

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if not username:
            # Sugerir username a partir de nombre y apellido
            nombre = self.cleaned_data.get("nombre", "")
            apellido = self.cleaned_data.get("apellido", "")
            base = slugify(f"{nombre}.{apellido}")[:20] or "jugador"
            username = base
            i = 1
            while User.objects.filter(username=username).exists():
                username = f"{base}{i}"
                i += 1
            self.cleaned_data["username"] = username
        user_exists = User.objects.filter(username__iexact=username).exists()
        jugador_exists = Jugador.objects.filter(
            user__username__iexact=username
        ).exists()
        if user_exists and jugador_exists:
            raise forms.ValidationError(
                "Ya existe una cuenta y un jugador registrados con este usuario."
            )
        elif user_exists:
            raise forms.ValidationError(
                "Ya existe una cuenta registrada con este usuario."
            )
        elif jugador_exists:
            raise forms.ValidationError(
                "Ya existe un jugador registrado con este usuario."
            )
        return username

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        user_exists = User.objects.filter(email__iexact=email).exists()
        jugador_exists = Jugador.objects.filter(email__iexact=email).exists()
        if user_exists and jugador_exists:
            raise forms.ValidationError(
                "Ya existe una cuenta y un jugador registrados con este email."
            )
        elif user_exists:
            raise forms.ValidationError(
                "Ya existe una cuenta registrada con este email."
            )
        elif jugador_exists:
            raise forms.ValidationError(
                "Ya existe un jugador registrado con este email."
            )
        return email

    def save(self, commit=True):
        username = self.cleaned_data["username"]
        user = User.objects.create_user(
            username=username,
            password=self.cleaned_data["password"],
            email=self.cleaned_data["email"],
        )
        jugador = super().save(commit=False)
        jugador.user = user
        jugador.email = self.cleaned_data["email"]
        if commit:
            jugador.save()
        return jugador


class PagoJugadorForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = ["monto", "metodo", "referencia"]
        widgets = {
            "monto": forms.NumberInput(
                attrs={"class": "w-full border rounded p-2", "min": "0", "step": "0.01"}
            ),
            "metodo": forms.TextInput(
                attrs={
                    "class": "w-full border rounded p-2",
                    "placeholder": "Efectivo, transferencia, etc.",
                }
            ),
            "referencia": forms.TextInput(
                attrs={
                    "class": "w-full border rounded p-2",
                    "placeholder": "N° comprobante, etc.",
                }
            ),
        }

    def clean_monto(self):
        monto = self.cleaned_data["monto"]
        if monto <= 0:
            raise forms.ValidationError("El monto debe ser mayor a cero.")
        return monto


class CambioPasswordForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "w-full border rounded p-2"
