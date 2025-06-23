from django.core.management.base import BaseCommand
from club.models_finanzas import Impuesto
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Poblar impuestos con fechas de vencimiento'

    def handle(self, *args, **options):
        # Crear impuestos con diferentes períodos y vencimientos
        impuestos_data = [
            {
                'tipo': 'iva',
                'periodo': 'Diciembre 2024',
                'monto': 85000.00,
                'dias_vencimiento': 5,  # Vence pronto
            },
            {
                'tipo': 'iva',
                'periodo': 'Enero 2025',
                'monto': 92000.00,
                'dias_vencimiento': 35,  # Próximo mes
            },
            {
                'tipo': 'ganancias',
                'periodo': '4to Trimestre 2024',
                'monto': 150000.00,
                'dias_vencimiento': 15,
            },
            {
                'tipo': 'ingresos_brutos',
                'periodo': 'Diciembre 2024',
                'monto': 45000.00,
                'dias_vencimiento': 8,
            },
            {
                'tipo': 'ingresos_brutos',
                'periodo': 'Enero 2025',
                'monto': 48000.00,
                'dias_vencimiento': 38,
            },
            {
                'tipo': 'monotributo',
                'periodo': 'Enero 2025',
                'monto': 25000.00,
                'dias_vencimiento': 20,
            },
            {
                'tipo': 'municipal',
                'periodo': 'Enero 2025',
                'monto': 35000.00,
                'dias_vencimiento': 12,
            }
        ]

        for imp_data in impuestos_data:
            # Crear identificador único combinando tipo y período
            identificador = f"{imp_data['tipo']}_{imp_data['periodo'].replace(' ', '_')}"
            
            impuesto, created = Impuesto.objects.get_or_create(
                tipo=imp_data['tipo'],
                periodo=imp_data['periodo'],
                defaults={
                    'monto': imp_data['monto'],
                    'fecha_vencimiento': date.today() + timedelta(days=imp_data['dias_vencimiento']),
                    'estado': 'vencido' if imp_data['dias_vencimiento'] < 0 else 'pendiente',
                }
            )
            
            if created:
                estado_texto = "VENCIDO" if impuesto.estado == 'vencido' else "Pendiente"
                vencimiento = impuesto.fecha_vencimiento.strftime('%d/%m/%Y')
                self.stdout.write(
                    f'✓ Impuesto creado: {impuesto.get_tipo_display()} {impuesto.periodo} - '
                    f'${impuesto.monto} - Vence: {vencimiento} ({estado_texto})'
                )
            else:
                self.stdout.write(f'- Impuesto ya existe: {impuesto}')

        # Mostrar resumen
        total_pendiente = sum(
            imp.monto for imp in Impuesto.objects.filter(estado='pendiente')
        )
        total_vencido = sum(
            imp.monto for imp in Impuesto.objects.filter(estado='vencido')
        )
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write(f'RESUMEN DE IMPUESTOS:')
        self.stdout.write(f'Total Pendiente: ${total_pendiente:,.2f}')
        self.stdout.write(f'Total Vencido: ${total_vencido:,.2f}')
        self.stdout.write(f'TOTAL: ${total_pendiente + total_vencido:,.2f}')
        self.stdout.write('='*50)

        self.stdout.write(
            self.style.SUCCESS('¡Impuestos poblados exitosamente!')
        )