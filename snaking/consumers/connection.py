import asyncio
import json
from typing import Optional, List, Union

from channels.generic.websocket import AsyncWebsocketConsumer

from ..game import Game, Direction
from ..rooms import Room


class ConnectionConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room: Optional[Room] = None
        self.games: List[Union[Game, dict]] = [
            {'user_id': None, 'apple': {}, 'snake': []},
            {'user_id': None, 'apple': {}, 'snake': []},
            {'user_id': None, 'apple': {}, 'snake': []},
            {'user_id': None, 'apple': {}, 'snake': []},
        ]

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
        self.games[user_id - 1] = Game()
        self.room = Room(name=room_name)

        await self.channel_layer.group_add(self.room.name, self.channel_name)

        future = asyncio.ensure_future(self.looper(user_id))

    async def looper(self, user_id):
        for i in range(1_000_000_000):
            if len(self.games[user_id - 1].received_directions) > 0:
                to = self.games[user_id - 1].received_directions.pop(0)
            else:
                to = self.games[user_id - 1].last_move

            self.games[user_id - 1].go(to)
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
        reverse_dir = Direction.get_inverse(self.games[user_id - 1].last_move)
        if (
                (direction != reverse_dir or len(self.games[user_id - 1].board.snake) < 2)
                and len(self.games[user_id - 1].received_directions) < 3
        ):
            self.games[user_id - 1].received_directions.append(direction)

    async def send_data(self, user_id):
        games = []
        for i, game in enumerate(self.games):
            if type(game) == dict:
                games.append(game)
            else:
                user_id = i + 1
                games.append({
                    'user_id': user_id,
                    'apple': self.games[user_id - 1].board.apple.to_json(),
                    'snake': list(map(
                        lambda x: x.to_json(), self.games[user_id - 1].board.snake
                    )),
                })

        await self.send(text_data=json.dumps({
            'room_name': self.room.name,
            'user_id': user_id,
            'games': games,
        }))

    @staticmethod
    async def players_in_group(channel_layer, room_group_name):
        group_key = channel_layer._group_key(room_group_name)
        consistent_hash = channel_layer.consistent_hash(room_group_name)
        async with channel_layer.connection(consistent_hash) as connection:
            return await connection.zcard(group_key)
