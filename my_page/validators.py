from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re


def validate_password_complexity(value):
    """Valida que la contraseña tenga al menos una mayúscula, un número y un carácter especial."""
    if not re.search(r'[A-Z]', value):
        raise ValidationError("La contraseña debe contener al menos una letra mayúscula.")
    if not re.search(r'[0-9]', value):
        raise ValidationError("La contraseña debe contener al menos un número.")
    if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', value):
        raise ValidationError("La contraseña debe contener al menos un carácter especial.")
    if len(value) < 8:
        raise ValidationError("La contraseña debe tener al menos 8 caracteres.")


class CustomSignupForm(forms.ModelForm):
    password1 = forms.CharField(
        widget=forms.PasswordInput,
        validators=[validate_password_complexity],
        label="Contraseña"
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput,
        label="Confirmar contraseña"
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        """Verifica que el email sea único."""
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise ValidationError("Este correo electrónico ya está registrado.")
        return email

    def clean(self):
        """Verifica que las contraseñas coincidan."""
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError({"password2": "Las contraseñas no coinciden."})

        return cleaned_data

    def save(self, commit=True):
        """Guarda el usuario con la contraseña correctamente encriptada."""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
