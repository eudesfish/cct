from django import forms
from django.contrib.auth.models import User, Group

class LoginForm(forms.Form):
    username = forms.CharField(label="Usuário")
    password = forms.CharField(widget=forms.PasswordInput, label="Senha")


class UsuarioForm(forms.ModelForm):
    senha = forms.CharField(widget=forms.PasswordInput, label="Senha")
    grupo = forms.ModelChoiceField(queryset=Group.objects.all(), required=True, label="Perfil")

    class Meta:
        model = User
        fields = ['username', 'email', 'senha', 'grupo']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["senha"])
        if commit:
            user.save()
            user.groups.set([self.cleaned_data["grupo"]])
        return user
