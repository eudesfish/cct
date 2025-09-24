from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from django.contrib import messages
from .forms import LoginForm


# Verifica se é administrador
def is_admin(user):
    return user.groups.filter(name="Administrador").exists() or user.is_superuser

def is_supervisor(user):
    return user.groups.filter(name="Supervisão").exists()

# Verifica se o usuário é Administrador ou Supervisor
def is_admin_or_supervisor(user):
    return user.groups.filter(name__in=["Administrador", "Supervisão"]).exists() or user.is_superuser

# Login
def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("dashboard")
            else:
                form.add_error(None, "Usuário ou senha inválidos")
    else:
        form = LoginForm()
    return render(request, "usuarios/login.html", {"form": form})


# Logout
def logout_view(request):
    logout(request)
    return redirect("login")


# Listagem de usuários
@login_required
@user_passes_test(is_admin)
def lista_usuarios(request):
    usuarios = User.objects.all().order_by("username")
    return render(request, "usuarios/lista_usuarios.html", {"usuarios": usuarios})


# Criar usuário
@login_required
@user_passes_test(is_admin)
def criar_usuario(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        senha = request.POST.get("password")
        grupo_nome = request.POST.get("grupo")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Já existe um usuário com esse nome.")
        else:
            usuario = User.objects.create_user(username=username, email=email, password=senha)
            
            if grupo_nome:
                grupo = Group.objects.get(name=grupo_nome)
                usuario.groups.add(grupo)

            messages.success(request, "Usuário criado com sucesso.")
            return redirect("lista_usuarios")

    grupos = Group.objects.all()
    return render(request, "usuarios/form_usuario.html", {"grupos": grupos, "acao": "Criar"})


# Editar usuário
@login_required
@user_passes_test(is_admin)
def editar_usuario(request, user_id):
    usuario = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        usuario.username = request.POST.get("username")
        usuario.email = request.POST.get("email")
        senha = request.POST.get("password")
        grupo_nome = request.POST.get("grupo")

        if senha:
            usuario.set_password(senha)

        usuario.groups.clear()
        if grupo_nome:
            grupo = Group.objects.get(name=grupo_nome)
            usuario.groups.add(grupo)

        usuario.save()
        messages.success(request, "Usuário atualizado com sucesso.")
        return redirect("lista_usuarios")

    grupos = Group.objects.all()
    return render(
        request,
        "usuarios/form_usuario.html",
        {"usuario": usuario, "grupos": grupos, "acao": "Editar"},
    )


# Excluir usuário (exceto master)
@login_required
@user_passes_test(is_admin)
def excluir_usuario(request, user_id):
    usuario = get_object_or_404(User, id=user_id)

    if usuario.is_superuser:
        messages.error(request, "O usuário master não pode ser excluído.")
    else:
        usuario.delete()
        messages.success(request, "Usuário excluído com sucesso.")

    return redirect("lista_usuarios")
