import asyncio
import curses
import time
from random import choice, randint


def blinking_star(canvas):
    row, column = (4, 15)
    while True:
        curses.curs_set(False)
        canvas.addstr(row, column, '*', curses.A_DIM)
        canvas.refresh()
        time.sleep(2)
        canvas.addstr(row, column, '*')
        canvas.refresh()
        time.sleep(0.3)
        canvas.addstr(row, column, '*', curses.A_BOLD)
        canvas.refresh()
        time.sleep(0.5)
        canvas.addstr(row, column, '*')
        canvas.refresh()
        time.sleep(0.3)


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


def draw(canvas):
    curses.curs_set(False)
    canvas.border()
    row, column = curses.window.getmaxyx(canvas)

    coroutines = [blink(canvas, randint(1, row-2), randint(1, column-2), choice('+*.:')) for _ in range(200)]
    while True:
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

    # blinking_star(canvas)
    # canvas.addstr(row, column, 'PRESS START', curses.A_BOLD | curses.A_REVERSE | curses.A_BLINK)
    # canvas.refresh()
    # time.sleep(2)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
