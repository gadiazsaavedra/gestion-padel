from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = 'Configura los roles y permisos del sistema'

    def handle(self, *args, **options):
        # Crear grupos
        admin_group, _ = Group.objects.get_or_create(name='Administrador')
        recep_group, _ = Group.objects.get_or_create(name='Recepcionista')
        jugador_group, _ = Group.objects.get_or_create(name='Jugador')
        
        self.stdout.write('✅ Grupos creados')
        
        # Asignar permisos básicos
        # Los permisos específicos se manejarán en las vistas
        
        self.stdout.write(self.style.SUCCESS('🎉 Roles configurados exitosamente'))