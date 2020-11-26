from collections import defaultdict
from typing import Optional

from .random import random_room_name


class Room(list):

    def __init__(self, name=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not name:
            name = random_room_name()
        self.name = name
        self.games = []


class RoomStore(defaultdict):

    instance: Optional[dict[str, list[Room]]] = None

    def __new__(cls) -> dict[str, list[Room]]:
        if not cls.instance:
            cls.instance = defaultdict(list)
        return cls.instance
