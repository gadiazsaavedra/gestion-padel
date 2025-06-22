try:
    import requests
except ImportError:
    requests = None
    
import json
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class WhatsAppService:
    """
    Servicio para enviar mensajes de WhatsApp usando diferentes proveedores
    Soporta: Twilio, WATI, CallMeBot (para pruebas)
    """
    
    def __init__(self):
        self.provider = getattr(settings, 'WHATSAPP_PROVIDER', 'callmebot')
        self.api_key = getattr(settings, 'WHATSAPP_API_KEY', '')
        self.phone_number = getattr(settings, 'WHATSAPP_PHONE_NUMBER', '')
        
    def send_message(self, to_phone, message):
        """
        Envía mensaje de WhatsApp
        Args:
            to_phone: Número de teléfono (formato: +5491123456789)
            message: Texto del mensaje
        """
        try:
            if self.provider == 'callmebot':
                return self._send_callmebot(to_phone, message)
            elif self.provider == 'twilio':
                return self._send_twilio(to_phone, message)
            elif self.provider == 'wati':
                return self._send_wati(to_phone, message)
            else:
                logger.warning(f"Proveedor WhatsApp no configurado: {self.provider}")
                return self._send_mock(to_phone, message)
                
        except Exception as e:
            logger.error(f"Error enviando WhatsApp: {e}")
            return False
    
    def _send_callmebot(self, to_phone, message):
        """
        CallMeBot - Servicio gratuito para pruebas
        Requiere configuración previa en WhatsApp
        """
        if not requests:
            logger.error("requests no disponible para CallMeBot")
            return self._send_mock(to_phone, message)
            
        # Limpiar número de teléfono
        phone = to_phone.replace('+', '').replace('-', '').replace(' ', '')
        
        url = "https://api.callmebot.com/whatsapp.php"
        params = {
            'phone': phone,
            'text': message,
            'apikey': self.api_key
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            logger.info(f"WhatsApp enviado a {to_phone}: {message[:50]}...")
            return True
        else:
            logger.error(f"Error CallMeBot: {response.status_code} - {response.text}")
            return False
    
    def _send_twilio(self, to_phone, message):
        """
        Twilio WhatsApp Business API
        """
        from twilio.rest import Client
        
        account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', '')
        auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', '')
        from_whatsapp = getattr(settings, 'TWILIO_WHATSAPP_NUMBER', '')
        
        client = Client(account_sid, auth_token)
        
        message = client.messages.create(
            body=message,
            from_=f'whatsapp:{from_whatsapp}',
            to=f'whatsapp:{to_phone}'
        )
        
        logger.info(f"Twilio WhatsApp enviado: {message.sid}")
        return True
    
    def _send_wati(self, to_phone, message):
        """
        WATI (WhatsApp Team Inbox)
        """
        if not requests:
            logger.error("requests no disponible para WATI")
            return self._send_mock(to_phone, message)
            
        url = f"https://live-server-{getattr(settings, 'WATI_INSTANCE_ID', '')}.wati.io/api/v1/sendSessionMessage"
        
        headers = {
            'Authorization': f"Bearer {getattr(settings, 'WATI_API_TOKEN', '')}",
            'Content-Type': 'application/json'
        }
        
        data = {
            'messageText': message,
            'phoneNumber': to_phone.replace('+', '')
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            logger.info(f"WATI WhatsApp enviado a {to_phone}")
            return True
        else:
            logger.error(f"Error WATI: {response.status_code} - {response.text}")
            return False
    
    def _send_mock(self, to_phone, message):
        """
        Mock para desarrollo - solo registra en logs
        """
        logger.info(f"📱 MOCK WhatsApp a {to_phone}: {message}")
        print(f"📱 WhatsApp SIMULADO:")
        print(f"   Para: {to_phone}")
        print(f"   Mensaje: {message}")
        print("-" * 50)
        return True

    def send_emparejamiento_notification(self, jugadores, emparejamiento):
        """
        Envía notificación de emparejamiento encontrado
        """
        dia = emparejamiento.dia.title()
        hora_inicio = emparejamiento.hora_inicio.strftime('%H:%M')
        hora_fin = emparejamiento.hora_fin.strftime('%H:%M')
        nivel = emparejamiento.nivel.title()
        
        # Lista de jugadores
        nombres_jugadores = [f"{j.nombre} {j.apellido}" for j in jugadores]
        lista_jugadores = "\n".join([f"• {nombre}" for nombre in nombres_jugadores])
        
        mensaje = f"""🎾 ¡EMPAREJAMIENTO ENCONTRADO!

📅 Día: {dia}
🕐 Horario: {hora_inicio} - {hora_fin}
🏆 Nivel: {nivel}

👥 Jugadores:
{lista_jugadores}

⏰ Tienes 24 horas para confirmar tu participación en la app.

¡Nos vemos en la cancha! 🎾"""

        # Enviar a cada jugador
        enviados = 0
        for jugador in jugadores:
            if jugador.telefono:
                # Formatear número si es necesario
                telefono = jugador.telefono
                if not telefono.startswith('+'):
                    telefono = f"+54{telefono}"  # Asumir Argentina
                
                if self.send_message(telefono, mensaje):
                    enviados += 1
        
        return enviados

    def send_confirmacion_completa(self, jugadores, emparejamiento):
        """
        Envía notificación cuando todos confirmaron
        """
        dia = emparejamiento.dia.title()
        hora_inicio = emparejamiento.hora_inicio.strftime('%H:%M')
        hora_fin = emparejamiento.hora_fin.strftime('%H:%M')
        
        # Lista de jugadores con teléfonos
        contactos = []
        for j in jugadores:
            if j.telefono:
                contactos.append(f"• {j.nombre} {j.apellido}: {j.telefono}")
        
        lista_contactos = "\n".join(contactos)
        
        # Información de reserva
        info_reserva = ""
        if hasattr(emparejamiento, 'reserva') and emparejamiento.reserva:
            reserva = emparejamiento.reserva
            info_reserva = f"""

🎾 ¡RESERVA CREADA AUTOMÁTICAMENTE!
📅 Fecha: {reserva.fecha.strftime('%d/%m/%Y')}
🕰️ Horario: {reserva.hora.strftime('%H:%M')}
🎾 Cancha: {reserva.cancha.nombre}
💰 Precio: ${reserva.precio}

ℹ️ La reserva está a nombre de {reserva.jugador.nombre} {reserva.jugador.apellido}"""
        else:
            info_reserva = """

💡 Sugerencia: Coordinen para reservar una cancha en el horario acordado."""
        
        mensaje = f"""🎉 ¡EMPAREJAMIENTO CONFIRMADO!

Todos los jugadores han confirmado su participación.

📅 {dia} {hora_inicio} - {hora_fin}

📞 Contactos para coordinar:
{lista_contactos}{info_reserva}

¡Que disfruten el partido! 🎾"""

        # Enviar a cada jugador
        enviados = 0
        for jugador in jugadores:
            if jugador.telefono:
                telefono = jugador.telefono
                if not telefono.startswith('+'):
                    telefono = f"+54{telefono}"
                
                if self.send_message(telefono, mensaje):
                    enviados += 1
        
        return enviados