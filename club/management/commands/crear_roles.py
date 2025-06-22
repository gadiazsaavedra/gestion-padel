from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group


class Command(BaseCommand):
    help = "Crea los grupos Jugadores, Recepcionistas y Administradores si no existen."

    def handle(self, *args, **options):
        roles = ["Jugadores", "Recepcionistas", "Administradores"]
        for role in roles:
            group, created = Group.objects.get_or_create(name=role)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Grupo creado: {role}"))
            else:
                self.stdout.write(f"El grupo ya existía: {role}")
