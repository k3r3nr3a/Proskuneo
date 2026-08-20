from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import CommonPasswordValidator
import re
from .models import Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'important']


def validate_password_complexity(value):
    """Valida la complejidad y seguridad de la contraseña"""

    # 1. Longitud mínima recomendada
    if len(value) < 8:
        raise ValidationError("La contraseña debe tener al menos 8 caracteres.")

    # 2. Longitud recomendada (deberías permitir hasta 64 o más)
    if len(value) > 512:
        raise ValidationError("La contraseña es demasiado larga.")

    # 3. Repeticiones de caracteres o secuencias simples
    if re.fullmatch(r'(.)\1{5,}', value):
        raise ValidationError("La contraseña no puede contener caracteres repetidos en exceso.")

    if re.fullmatch(r'(?:1234|abcd|qwer|asdf)+', value.lower()):
        raise ValidationError("La contraseña no puede ser una secuencia predecible.")

    # 4. Al menos una mayúscula
    if not any(char.isupper() for char in value):
        raise ValidationError("Debe contener al menos una letra mayúscula.")

    # 5. Al menos un carácter especial
    if not any(char in "!@#$%^&*()_+-=[]{}|;':,.<>?/`~" for char in value):
        raise ValidationError("Debe contener al menos un carácter especial.")

    # 6. Verifica si es una contraseña común (opcional)
    validator = CommonPasswordValidator()
    try:
        validator.validate(value)
    except ValidationError:
        raise ValidationError("La contraseña es demasiado común. Usa una más segura.")

class CustomSignupForm(UserCreationForm):
    username = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label="Nombre de usuario"
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"class": "form-control"}),
        label="Correo electrónico"
    )
    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        validators=[validate_password_complexity]
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )


    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        """ Verifica si el email ya está registrado """
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("Este correo ya está registrado.")
        return email

    def clean_password2(self):
        """ Verifica que las contraseñas coincidan y sean seguras """
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2:
            if password1 != password2:
                raise ValidationError("Las contraseñas no coinciden.")
            validate_password_complexity(password1)  # Revalidar seguridad

        return password2
