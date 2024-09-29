import asyncio
import curses
import time
from itertools import cycle
from pathlib import Path
from random import choice, randint


def get_frame_size(text):
    """Calculate size of multiline text fragment, return pair — number of rows and colums."""

    lines = text.splitlines()
    rows = len(lines)
    columns = max([len(line) for line in lines])
    return rows, columns


def get_frames():
    frames = []
    frame_file_paths = [Path('frames', f'rocket_frame{i + 1}.txt') for i in range(2)]
    for frame_file_path in frame_file_paths:
        with open(frame_file_path, 'r') as frame_file:
            frame = frame_file.readlines()
        frames.append(''.join(frame))
    return frames


async def animate_spaceship(canvas, row, column, frames):
    frame_iter = cycle(frames)
    row //= 2
    column //= 2
    rows_number, columns_number = canvas.getmaxyx()

    while True:
        rows_direction, columns_direction, space_pressed = read_controls(canvas)
        frame = next(frame_iter)
        frame_rows, frame_columns = get_frame_size(frame)
        new_row = row + rows_direction
        new_column = column + columns_direction

        if new_row <= 0:
            new_row = 0
        elif new_row >= rows_number - frame_rows:
            new_row = rows_number - frame_rows

        if new_column <= 0:
            new_column = 0
        elif new_column >= columns_number - frame_columns:
            new_column = columns_number - frame_columns

        row, column = new_row, new_column

        draw_frame(canvas, row, column, frame, False)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, frame, True)


def draw_frame(canvas, start_row, start_column, text, negative=False):
    """Draw multiline text fragment on canvas, erase text instead of drawing if negative=True is specified."""

    rows_number, columns_number = canvas.getmaxyx()
    for row, line in enumerate(text.splitlines(), round(start_row)):
        if row < 0:
            continue

        if row >= rows_number:
            break

        for column, symbol in enumerate(line, round(start_column)):
            if column < 0:
                continue

            if column >= columns_number:
                break

            if symbol == ' ':
                continue

            # Check that current position it is not in a lower right corner of the window
            # Curses will raise exception in that case. Don`t ask why…
            # https://docs.python.org/3/library/curses.html#curses.window.addch
            if row == rows_number - 1 and column == columns_number - 1:
                continue

            symbol = symbol if not negative else ' '
            canvas.addch(row, column, symbol)


async def fire(canvas, start_row, start_column, rows_speed=-0.5, columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def blink(canvas, row, column, symbol):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        for _ in range(20):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for _ in range(5):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)

        for _ in range(randint(0, 15)):
            await asyncio.sleep(0)


def read_controls(canvas):

    rows_direction = columns_direction = 0
    space_pressed = False

    while True:
        pressed_key_code = canvas.getch()

        if pressed_key_code == -1:

            # https://docs.python.org/3/library/curses.html#curses.window.getch
            break

        if pressed_key_code == UP_KEY_CODE:
            rows_direction = -1

        if pressed_key_code == DOWN_KEY_CODE:
            rows_direction = 1

        if pressed_key_code == RIGHT_KEY_CODE:
            columns_direction = 1

        if pressed_key_code == LEFT_KEY_CODE:
            columns_direction = -1

        if pressed_key_code == SPACE_KEY_CODE:
            space_pressed = True

    return rows_direction, columns_direction, space_pressed


def draw(canvas):
    frames = get_frames()
    curses.curs_set(False)
    canvas.nodelay(True)
    row, column = curses.window.getmaxyx(canvas)
    coroutines = [blink(canvas, randint(1, row - 2), randint(1, column - 2), choice('+*.:')) for _ in range(200)]
    coroutines.insert(0, fire(canvas, row // 2, column // 2, rows_speed=-1.5, columns_speed=0))
    coroutines.insert(0, animate_spaceship(canvas, row, column, frames))
    while True:
        canvas.border()
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
                if not coroutines:
                    break
        canvas.refresh()
        TIC_TIMEOUT = 0.1
        time.sleep(TIC_TIMEOUT)


if __name__ == '__main__':
    SPACE_KEY_CODE = 32
    LEFT_KEY_CODE = 260
    RIGHT_KEY_CODE = 261
    UP_KEY_CODE = 259
    DOWN_KEY_CODE = 258
    curses.update_lines_cols()
    curses.wrapper(draw)
