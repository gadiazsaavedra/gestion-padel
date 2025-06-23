from django.core.management.base import BaseCommand
from club.models import Jugador, Reserva, Pago
from datetime import date, timedelta, time
import random


class Command(BaseCommand):
    help = 'Poblar datos simples para reportes'

    def handle(self, *args, **options):
        # Crear jugadores si no existen
        jugadores_data = [
            {'nombre': 'Carlos', 'apellido': 'Mendez', 'email': 'carlos.mendez@email.com', 'telefono': '1111111111', 'nivel': 'avanzado', 'genero': 'hombre'},
            {'nombre': 'Ana', 'apellido': 'Rodriguez', 'email': 'ana.rodriguez@email.com', 'telefono': '2222222222', 'nivel': 'intermedio', 'genero': 'mujer'},
            {'nombre': 'Luis', 'apellido': 'Garcia', 'email': 'luis.garcia@email.com', 'telefono': '3333333333', 'nivel': 'novato', 'genero': 'hombre'},
            {'nombre': 'Sofia', 'apellido': 'Martinez', 'email': 'sofia.martinez@email.com', 'telefono': '4444444444', 'nivel': 'avanzado', 'genero': 'mujer'},
            {'nombre': 'Diego', 'apellido': 'Lopez', 'email': 'diego.lopez@email.com', 'telefono': '5555555555', 'nivel': 'intermedio', 'genero': 'hombre'},
        ]

        for jug_data in jugadores_data:
            jugador, created = Jugador.objects.get_or_create(
                email=jug_data['email'],
                defaults=jug_data
            )
            if created:
                self.stdout.write(f'✓ Jugador creado: {jugador}')

        # Crear reservas y pagos de los últimos 7 días
        jugadores = list(Jugador.objects.all())
        
        for i in range(7):
            fecha = date.today() - timedelta(days=i)
            
            # Crear 3-8 reservas por día
            num_reservas = random.randint(3, 8)
            for j in range(num_reservas):
                jugador = random.choice(jugadores)
                hora = time(random.randint(8, 21), random.choice([0, 30]))
                monto = random.randint(3000, 8000)
                
                # Crear reserva única por jugador/fecha/hora
                reserva, created = Reserva.objects.get_or_create(
                    jugador=jugador,
                    fecha=fecha,
                    hora=hora,
                    defaults={
                        'estado': 'pagada',
                        'pago_total': monto,
                        'metodo_pago': random.choice(['efectivo', 'tarjeta', 'transferencia'])
                    }
                )
                
                if created:
                    # Crear pago correspondiente
                    Pago.objects.create(
                        jugador=jugador,
                        monto=monto,
                        fecha=fecha,
                        estado='pagado',
                        metodo=reserva.metodo_pago
                    )
                    self.stdout.write(f'✓ Reserva y pago creados: {jugador} - ${monto}')

        self.stdout.write('\n' + '='*50)
        self.stdout.write('RESUMEN DE DATOS CREADOS:')
        self.stdout.write(f'Jugadores: {Jugador.objects.count()}')
        self.stdout.write(f'Reservas: {Reserva.objects.count()}')
        self.stdout.write(f'Pagos: {Pago.objects.count()}')
        
        # Calcular totales
        total_ingresos = sum(p.monto for p in Pago.objects.filter(estado='pagado'))
        self.stdout.write(f'Total Ingresos: ${total_ingresos:,.2f}')
        self.stdout.write('='*50)

        self.stdout.write(
            self.style.SUCCESS('¡Datos simples para reportes poblados exitosamente!')
        )