import asyncio
import curses
import time
from itertools import cycle
from pathlib import Path
from random import choice, randint


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
    while True:
        frame = next(frame_iter)
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


def draw(canvas):
    frames = get_frames()
    curses.curs_set(False)
    row, column = curses.window.getmaxyx(canvas)
    coroutines = [blink(canvas, randint(1, row - 2), randint(1, column - 2), choice('+*.:')) for _ in range(200)]
    coroutines.insert(0, fire(canvas, row // 2, column // 2, rows_speed=-1.5, columns_speed=0))
    coroutines.insert(0, animate_spaceship(canvas, row // 2, column // 2, frames))
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
    curses.update_lines_cols()
    curses.wrapper(draw)
