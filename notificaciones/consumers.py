import json
from channels.generic.websocket import AsyncWebsocketConsumer


class NotificacionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_authenticated:
            self.group_name = f"notificaciones_{self.scope['user'].id}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        # Este consumer solo envía notificaciones, no recibe mensajes del cliente
        pass

    async def enviar_notificacion(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "mensaje": event["mensaje"],
                    "tipo": event.get("tipo", "info"),
                }
            )
        )
