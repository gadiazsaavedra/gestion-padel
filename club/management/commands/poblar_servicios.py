from django.core.management.base import BaseCommand
from club.models_finanzas import ServicioPublico, PagoServicio
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Poblar servicios públicos con pagos mensuales'

    def handle(self, *args, **options):
        # Crear servicios públicos
        servicios_data = [
            {
                'tipo': 'luz',
                'proveedor': 'Edesur SA',
                'numero_cuenta': '123456789',
            },
            {
                'tipo': 'agua',
                'proveedor': 'AySA',
                'numero_cuenta': '987654321',
            },
            {
                'tipo': 'gas',
                'proveedor': 'Metrogas',
                'numero_cuenta': '456789123',
            },
            {
                'tipo': 'internet',
                'proveedor': 'Telecom Argentina',
                'numero_cuenta': '789123456',
            },
            {
                'tipo': 'telefono',
                'proveedor': 'Movistar',
                'numero_cuenta': '321654987',
            },
            {
                'tipo': 'seguridad',
                'proveedor': 'Prosegur',
                'numero_cuenta': '654987321',
            }
        ]

        for serv_data in servicios_data:
            servicio, created = ServicioPublico.objects.get_or_create(
                tipo=serv_data['tipo'],
                proveedor=serv_data['proveedor'],
                defaults=serv_data
            )
            if created:
                self.stdout.write(f'✓ Servicio creado: {servicio}')
            else:
                self.stdout.write(f'- Servicio ya existe: {servicio}')

        # Crear pagos para cada servicio
        pagos_data = [
            {
                'tipo_servicio': 'luz',
                'proveedor': 'Edesur SA',
                'periodo': 'Enero 2025',
                'monto': 45000.00,
                'numero_factura': 'LUZ-001-2025',
                'dias_vencimiento': 15,
            },
            {
                'tipo_servicio': 'agua',
                'proveedor': 'AySA',
                'periodo': 'Enero 2025',
                'monto': 18000.00,
                'numero_factura': 'AGUA-001-2025',
                'dias_vencimiento': 20,
            },
            {
                'tipo_servicio': 'gas',
                'proveedor': 'Metrogas',
                'periodo': 'Enero 2025',
                'monto': 25000.00,
                'numero_factura': 'GAS-001-2025',
                'dias_vencimiento': 10,
            },
            {
                'tipo_servicio': 'internet',
                'proveedor': 'Telecom Argentina',
                'periodo': 'Enero 2025',
                'monto': 12000.00,
                'numero_factura': 'INT-001-2025',
                'dias_vencimiento': 25,
            },
            {
                'tipo_servicio': 'telefono',
                'proveedor': 'Movistar',
                'periodo': 'Enero 2025',
                'monto': 8000.00,
                'numero_factura': 'TEL-001-2025',
                'dias_vencimiento': 30,
            },
            {
                'tipo_servicio': 'seguridad',
                'proveedor': 'Prosegur',
                'periodo': 'Enero 2025',
                'monto': 35000.00,
                'numero_factura': 'SEG-001-2025',
                'dias_vencimiento': 5,
            }
        ]

        for pago_data in pagos_data:
            servicio = ServicioPublico.objects.get(
                tipo=pago_data['tipo_servicio'],
                proveedor=pago_data['proveedor']
            )
            
            pago, created = PagoServicio.objects.get_or_create(
                numero_factura=pago_data['numero_factura'],
                defaults={
                    'servicio': servicio,
                    'periodo': pago_data['periodo'],
                    'monto': pago_data['monto'],
                    'fecha_vencimiento': date.today() + timedelta(days=pago_data['dias_vencimiento']),
                    'estado': 'pendiente',
                }
            )
            if created:
                self.stdout.write(f'  ✓ Pago creado: {servicio.get_tipo_display()} - ${pago_data["monto"]}')
            else:
                self.stdout.write(f'  - Pago ya existe: {pago_data["numero_factura"]}')

        self.stdout.write(
            self.style.SUCCESS('¡Servicios públicos y pagos poblados exitosamente!')
        )