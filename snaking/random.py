import random
from string import digits


def random_room_name():
    return ''.join(random.choices(digits, k=3))
