import asyncio
import json
from typing import Optional

from channels.generic.websocket import AsyncWebsocketConsumer

from ..game import Game, Direction
from ..rooms import Room


class ConnectionConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room: Optional[Room] = None
        self.game: Game = Game()

    async def connect(self):
        room_name: str = self.scope['url_route']['kwargs']['room_name']
        players_in_group = await self.players_in_group(self.channel_layer, room_name)

        await self.accept()

        if not players_in_group < 4:
            await self.send(text_data=json.dumps({
                'message': 'room is full',
                'status': -1
            }))
            await self.close(code=-1)

        user_id = players_in_group + 1
        self.room = Room(name=room_name)

        await self.channel_layer.group_add(self.room.name, self.channel_name)

        future = asyncio.ensure_future(self.looper(user_id))

    async def looper(self, user_id):
        for i in range(1_000_000_000):
            self.game.go(self.game.last_direction)
            await self.send_data(user_id)
            await asyncio.sleep(0.18)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room.name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)

        await self.channel_layer.group_send(
            self.room.name,
            {
                'type': 'message',
                'message': text_data_json
            }
        )

    async def message(self, event):
        user_id, message = event['message']['user_id'], event['message']['message']
        direction = Direction.from_str(message)
        if direction != Direction.get_inverse(self.game.last_direction):
            self.game.last_direction = direction

    async def send_data(self, user_id):
        await self.send(text_data=json.dumps({
            'room_name': self.room.name,
            'user_id': user_id,
            'apple': self.game.board.apple.to_json(),
            'snake': list(map(lambda x: x.to_json(), self.game.board.snake)),
        }))

    @staticmethod
    async def players_in_group(channel_layer, room_group_name):
        group_key = channel_layer._group_key(room_group_name)
        consistent_hash = channel_layer.consistent_hash(room_group_name)
        async with channel_layer.connection(consistent_hash) as connection:
            return await connection.zcard(group_key)
