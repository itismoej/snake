import math
from dataclasses import dataclass
from enum import Enum
from random import random
from typing import Tuple

DEFAULT_ROW_NUM = 5
DEFAULT_COL_NUM = 8


@dataclass
class Point:
    row: int
    col: int

    def __eq__(self, other):
        return self.row == other.row and self.col == other.col


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


class Direction(Enum):
    UP = Point(-1, 0)
    RIGHT = Point(0, +1)
    DOWN = Point(+1, 0)
    LEFT = Point(0, -1)


class Game:

    def __init__(
            self,
            *args,
            **kwargs,
    ):
        board, snake = self.new_board()
        self.board: Board = board
        self.snake: Point = snake

    def random_cell(self) -> Point:
        row = math.floor(random() * self.board.dimensions.rows)
        col = math.floor(random() * self.board.dimensions.cols)
        return Point(row, col)

    def new_board(self) -> Tuple[Board, Point]:
        board = Board(
            Row(
                Cell(num=cell_num)
                for cell_num in range(self.board.dimensions.cols)
            ) for _ in range(self.board.dimensions.rows)
        )

        snake: Point = self.random_cell()
        board = self.edit_cell(board, snake.row, snake.col, CellStatus.SNAKE)

        while (apple := self.random_cell()) == snake:
            continue
        board = self.edit_cell(board, apple.row, apple.col, CellStatus.APPLE)

        return board, snake

    @staticmethod
    def edit_cell(board: Board, x: int, y: int, status: CellStatus) -> Board:
        row = board[x]
        cell = row[y]
        cell.status = status
        return board

    def move_snake(self, direction: Direction):
        x = self.snake.row
        y = self.snake.col
        snake_cell = self.board[x][y]
        snake_cell.status = CellStatus.EMPTY

        direction = direction.value
        new_row = (x + direction.row) % self.board.dimensions.rows
        new_col = (y + direction.col) % self.board.dimensions.cols
        snake_cell = self.board[new_row][new_col]
        snake_cell.status = CellStatus.SNAKE
