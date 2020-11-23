import json
from channels.generic.websocket import AsyncWebsocketConsumer

from .random import random_room_name


class GameConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_name = random_room_name()
        self.room_group_name = f'game_{self.room_name}'

    async def connect(self):
        room_name = self.scope['url_route']['kwargs']['room_name']
        if room_name:
            self.room_name = room_name
            self.room_group_name = f'game_{self.room_name}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        await self.send(text_data=json.dumps({
            'room_name': self.room_name
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'message',
                'message': message
            }
        )

    async def message(self, event):
        message = event['message']

        await self.send(text_data=json.dumps({
            'message': f'we got your message!: "{message}"'
        }))
