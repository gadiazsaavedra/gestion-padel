from django.core.management.base import BaseCommand
from club.models_finanzas import Proveedor, PagoProveedor
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Poblar proveedores con facturas de ejemplo'

    def handle(self, *args, **options):
        # Crear proveedores
        proveedores_data = [
            {
                'nombre': 'Distribuidora Deportiva SA',
                'cuit': '30-12345678-9',
                'telefono': '1145678901',
                'email': 'ventas@distribuidora.com',
                'direccion': 'Av. Corrientes 1234, CABA',
                'contacto': 'Roberto Fernández',
            },
            {
                'nombre': 'Suministros Club SRL',
                'cuit': '30-87654321-2',
                'telefono': '1198765432',
                'email': 'admin@suministros.com',
                'direccion': 'San Martín 567, Buenos Aires',
                'contacto': 'María López',
            },
            {
                'nombre': 'Mantenimiento Integral SA',
                'cuit': '30-11223344-5',
                'telefono': '1155667788',
                'email': 'contacto@mantenimiento.com',
                'direccion': 'Belgrano 890, CABA',
                'contacto': 'Carlos Ruiz',
            }
        ]

        for prov_data in proveedores_data:
            proveedor, created = Proveedor.objects.get_or_create(
                cuit=prov_data['cuit'],
                defaults=prov_data
            )
            if created:
                self.stdout.write(f'✓ Proveedor creado: {proveedor}')
            else:
                self.stdout.write(f'- Proveedor ya existe: {proveedor}')

        # Crear facturas para cada proveedor
        facturas_data = [
            {
                'proveedor_cuit': '30-12345678-9',
                'concepto': 'Pelotas de pádel x 50 unidades',
                'monto': 75000.00,
                'numero_factura': 'FAC-001-2025',
                'dias_vencimiento': 30,
            },
            {
                'proveedor_cuit': '30-12345678-9',
                'concepto': 'Raquetas Wilson x 10 unidades',
                'monto': 120000.00,
                'numero_factura': 'FAC-002-2025',
                'dias_vencimiento': 45,
            },
            {
                'proveedor_cuit': '30-87654321-2',
                'concepto': 'Productos de limpieza',
                'monto': 25000.00,
                'numero_factura': 'B-0001-2025',
                'dias_vencimiento': 15,
            },
            {
                'proveedor_cuit': '30-87654321-2',
                'concepto': 'Bebidas para bar x 100 unidades',
                'monto': 45000.00,
                'numero_factura': 'B-0002-2025',
                'dias_vencimiento': 20,
            },
            {
                'proveedor_cuit': '30-11223344-5',
                'concepto': 'Reparación sistema de iluminación',
                'monto': 85000.00,
                'numero_factura': 'SRV-001-2025',
                'dias_vencimiento': 10,
            }
        ]

        for fact_data in facturas_data:
            proveedor = Proveedor.objects.get(cuit=fact_data['proveedor_cuit'])
            
            factura, created = PagoProveedor.objects.get_or_create(
                numero_factura=fact_data['numero_factura'],
                defaults={
                    'proveedor': proveedor,
                    'concepto': fact_data['concepto'],
                    'monto': fact_data['monto'],
                    'fecha_factura': date.today(),
                    'fecha_vencimiento': date.today() + timedelta(days=fact_data['dias_vencimiento']),
                    'estado': 'pendiente',
                }
            )
            if created:
                self.stdout.write(f'  ✓ Factura creada: {fact_data["concepto"]} - ${fact_data["monto"]}')
            else:
                self.stdout.write(f'  - Factura ya existe: {fact_data["numero_factura"]}')

        self.stdout.write(
            self.style.SUCCESS('¡Proveedores y facturas poblados exitosamente!')
        )