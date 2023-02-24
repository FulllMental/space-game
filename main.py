import time
import asyncio
import curses


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


async def blink(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0)


def draw(canvas):
    curses.curs_set(False)
    canvas.border()
    row, column = (5, 20)

    coroutines = [blink(canvas, row, column + index * 2) for index in range(5)]
    while True:
        canvas.refresh()
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
                time.sleep(0.1)
            except StopIteration:
                coroutines.remove(coroutine)
                if not coroutines:
                    break

    # blinking_star(canvas)
    # canvas.addstr(row, column, 'PRESS START', curses.A_BOLD | curses.A_REVERSE | curses.A_BLINK)
    # canvas.refresh()
    # time.sleep(2)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
