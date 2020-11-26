import math
from copy import deepcopy
from dataclasses import dataclass
from enum import Enum
from random import random
from typing import List

DEFAULT_ROW_NUM = 14
DEFAULT_COL_NUM = 20


@dataclass
class Point:
    row: int
    col: int

    def __eq__(self, other):
        return self.row == other.row and self.col == other.col

    def to_json(self):
        return {
            'x': self.col,
            'y': self.row,
        }


class Direction(Enum):
    UP = Point(-1, 0)
    RIGHT = Point(0, +1)
    DOWN = Point(+1, 0)
    LEFT = Point(0, -1)

    @staticmethod
    def from_str(string):
        if string.lower().startswith('u'): return Direction.UP
        elif string.lower().startswith('r'): return Direction.RIGHT
        elif string.lower().startswith('d'): return Direction.DOWN
        elif string.lower().startswith('l'): return Direction.LEFT


@dataclass
class Dimensions:
    rows: int = DEFAULT_ROW_NUM
    cols: int = DEFAULT_COL_NUM


DEFAULT_DIMENSIONS = Dimensions()


class CellStatus(Enum):
    EMPTY = 0
    SNAKE = 1
    APPLE = 2


@dataclass
class Cell:
    num: int
    status: CellStatus = CellStatus.EMPTY


class Row(list):

    def __init__(self, *args, **kwargs):
        super(Row, self).__init__(*args, **kwargs)


class Board(list):

    def __init__(self, *args, **kwargs):
        super(Board, self).__init__(*args, **kwargs)
        self.dimensions: Dimensions = Dimensions()
        tail = self.initialize()
        self.snake: List[Point] = [tail]
        self.apple: Point = self.new_apple()

    @property
    def snake_head(self) -> Point:
        return self.snake[0]

    @property
    def snake_tail(self) -> Point:
        return self.snake[-1]

    def clear_board(self):
        self.clear()
        self.extend(
            Row(
                Cell(num=cell_num)
                for cell_num in range(self.dimensions.cols)
            ) for _ in range(self.dimensions.rows)
        )

    def initialize(self) -> Point:
        self.clear_board()

        snake: Point = self.random_cell()
        self.edit_cell(snake.row, snake.col, CellStatus.SNAKE)

        return snake

    def new_apple(self):
        while (apple := self.random_cell()) in self.snake:
            continue
        self.edit_cell(apple.row, apple.col, CellStatus.APPLE)
        self.apple = apple
        return apple

    def random_cell(self) -> Point:
        row = math.floor(random() * self.dimensions.rows)
        col = math.floor(random() * self.dimensions.cols)
        return Point(row, col)

    def edit_cell(self, x: int, y: int, status: CellStatus):
        cell = self[x][y]
        cell.status = status


class MoveResult(Enum):
    DIE = 0
    RUN = 1
    EAT = 2


class Game:

    def __init__(self, *args, **kwargs, ):
        self.board: Board = Board()
        self.show()

    def move_snake(self, direction: Direction) -> MoveResult:
        head_point: Point = self.board.snake_head
        tail_cell: Cell = self.board[self.board.snake_tail.row][self.board.snake_tail.col]

        direction: Point = direction.value
        next_row = (head_point.row + direction.row) % self.board.dimensions.rows
        next_col = (head_point.col + direction.col) % self.board.dimensions.cols

        new_snake_cell: Cell = self.board[next_row][next_col]
        new_snake_point: Point = Point(next_row, next_col)

        tail_cell.status = CellStatus.EMPTY
        next_cell_after_removing_tail = deepcopy(new_snake_cell)

        move_result = self.move_result(next_cell_after_removing_tail)

        new_snake_cell.status = CellStatus.SNAKE
        if move_result == MoveResult.RUN:
            self.board.snake = [new_snake_point, *self.board.snake[:-1]]
        elif move_result == MoveResult.EAT:
            self.board.snake = [new_snake_point, *self.board.snake]
            tail_cell.status = CellStatus.SNAKE
            self.board.new_apple()

        return move_result

    def go(self, direction: Direction):
        move_result: MoveResult = self.move_snake(direction)
        if move_result == MoveResult.DIE:
            self.board.initialize()
        self.show()

    @staticmethod
    def move_result(new_snake_cell: Cell) -> MoveResult:
        if new_snake_cell.status == CellStatus.EMPTY:
            return MoveResult.RUN
        elif new_snake_cell.status == CellStatus.APPLE:
            return MoveResult.EAT
        elif new_snake_cell.status == CellStatus.SNAKE:
            return MoveResult.DIE

    def show(self):
        for row in self.board:
            for col in row:
                print(
                    'O' if col.status == CellStatus.EMPTY else
                    '-' if col.status == CellStatus.SNAKE else '+',
                    end=' '
                )
            print()

        print('----')
