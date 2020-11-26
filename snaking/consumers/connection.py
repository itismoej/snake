import json
from functools import reduce
from typing import Optional

from channels.generic.websocket import AsyncWebsocketConsumer

from ..rooms import RoomStore, Room
from ..game import Game, Direction

# store = RoomStore()


class ConnectionConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room: Optional[Room] = None
        self.game: Game = Game()

    async def connect(self):
        room_name: str = self.scope['url_route']['kwargs']['room_name']

        if not await self.players_in_group(self.channel_layer, room_name) < 4:
            await self.close(code=-1)

        self.room = Room(name=room_name)
        # self.game = Game()
        # store[self.room.name].append(self.room)

        await self.channel_layer.group_add(self.room.name, self.channel_name)
        await self.accept()

        await self.send(text_data=json.dumps({
            'room_name': self.room.name,
            'apple': self.game.board.apple.to_json(),
            'snake': list(map(lambda x: x.to_json(), self.game.board.snake)),
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room.name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        await self.channel_layer.group_send(
            self.room.name,
            {
                'type': 'message',
                'message': message
            }
        )

    async def message(self, event):
        message = event['message']
        direction = Direction.from_str(message)
        self.game.go(direction)

        await self.send(text_data=json.dumps({
            'room_name': self.room.name,
            'apple': self.game.board.apple.to_json(),
            'snake': list(map(lambda x: x.to_json(), self.game.board.snake)),
        }))

    @staticmethod
    async def players_in_group(channel_layer, room_group_name):
        group_key = channel_layer._group_key(room_group_name)
        consistent_hash = channel_layer.consistent_hash(room_group_name)
        async with channel_layer.connection(consistent_hash) as connection:
            return await connection.zcard(group_key)
