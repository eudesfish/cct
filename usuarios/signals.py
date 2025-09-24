from django.db.models.signals import post_migrate
from django.contrib.auth.models import Group, Permission
from django.dispatch import receiver

@receiver(post_migrate)
def criar_grupos(sender, **kwargs):
    if sender.name == "usuarios":  # garante que roda só quando esse app é migrado
        # Grupo Administrador → acesso total
        admin_group, created = Group.objects.get_or_create(name="Administrador")
        if created:
            admin_group.permissions.set(Permission.objects.all())

        # Grupo Supervisão → apenas leitura
        supervisao_group, created = Group.objects.get_or_create(name="Supervisão")
        if created:
            permissoes = Permission.objects.filter(codename__startswith="view")
            supervisao_group.permissions.set(permissoes)

@receiver(post_migrate)
def create_user_groups(sender, **kwargs):
    Group.objects.get_or_create(name='Administrador')
    Group.objects.get_or_create(name='Supervisor')