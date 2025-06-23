from django.core.management.base import BaseCommand
from club.models_finanzas import Empleado, PagoEmpleado
from django.contrib.auth.models import User
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Poblar empleados con datos de ejemplo'

    def handle(self, *args, **options):
        # Crear empleados
        empleados_data = [
            {
                'nombre': 'Juan',
                'apellido': 'Pérez',
                'dni': '12345678',
                'telefono': '1123456789',
                'email': 'juan.perez@club.com',
                'cargo': 'Recepcionista',
                'salario_base': 180000.00,
                'fecha_ingreso': date(2024, 1, 15),
            },
            {
                'nombre': 'María',
                'apellido': 'González',
                'dni': '87654321',
                'telefono': '1198765432',
                'email': 'maria.gonzalez@club.com',
                'cargo': 'Mantenimiento',
                'salario_base': 160000.00,
                'fecha_ingreso': date(2024, 3, 10),
            },
            {
                'nombre': 'Carlos',
                'apellido': 'Rodríguez',
                'dni': '11223344',
                'telefono': '1155667788',
                'email': 'carlos.rodriguez@club.com',
                'cargo': 'Instructor de Pádel',
                'salario_base': 200000.00,
                'fecha_ingreso': date(2023, 8, 5),
            },
            {
                'nombre': 'Ana',
                'apellido': 'Martínez',
                'dni': '44332211',
                'telefono': '1144556677',
                'email': 'ana.martinez@club.com',
                'cargo': 'Limpieza',
                'salario_base': 140000.00,
                'fecha_ingreso': date(2024, 2, 20),
            },
            {
                'nombre': 'Roberto',
                'apellido': 'Silva',
                'dni': '55667788',
                'telefono': '1133445566',
                'email': 'roberto.silva@club.com',
                'cargo': 'Seguridad',
                'salario_base': 170000.00,
                'fecha_ingreso': date(2023, 11, 12),
            }
        ]

        for emp_data in empleados_data:
            empleado, created = Empleado.objects.get_or_create(
                dni=emp_data['dni'],
                defaults=emp_data
            )
            if created:
                self.stdout.write(f'✓ Empleado creado: {empleado}')
                
                # Crear pago de salario del mes actual
                PagoEmpleado.objects.create(
                    empleado=empleado,
                    tipo='salario',
                    monto=empleado.salario_base,
                    fecha_pago=date.today(),
                    periodo='Enero 2025',
                    observaciones='Salario mensual'
                )
                self.stdout.write(f'  ✓ Pago creado para {empleado.nombre}')
            else:
                self.stdout.write(f'- Empleado ya existe: {empleado}')

        self.stdout.write(
            self.style.SUCCESS('¡Empleados poblados exitosamente!')
        )