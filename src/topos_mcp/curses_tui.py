#!/usr/bin/env python3
"""
A minimal terminal-based TUI using Python's built-in curses module.
This demonstrates how to draw basic interface elements and respond to keyboard input.
Run: python src/topos_mcp/curses_tui.py
"""

import curses
import sys

def main(stdscr):
    # Clear screen
    curses.curs_set(0)  # hide cursor
    stdscr.clear()
    stdscr.nodelay(False)  # blocking keyboard reads
    stdscr.keypad(True)

    # Basic color setup if terminal supports it
    if curses.has_colors():
        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)

    # Window geometry
    rows, cols = stdscr.getmaxyx()

    # A function to draw the main screen
    def draw_ui():
        stdscr.bkgd(' ', curses.color_pair(1) if curses.has_colors() else 0)
        # Title or header line
        title_text = "Terminal TUI - Press 'q' to quit"
        stdscr.addstr(0, 0, title_text[:cols], curses.A_BOLD)

        # Some instructions
        instructions = [
            " ",
            "Press 'r' to refresh message, 'q' to quit.",
            "Press arrow keys to move cursor, just for demo."
        ]
        for i, line in enumerate(instructions, start=2):
            stdscr.addstr(i, 0, line[:cols], curses.color_pair(2) if curses.has_colors() else 0)

        # Draw a small box
        box_row, box_col = 7, 5
        box_height, box_width = 10, 40
        for r in range(box_height):
            if box_row + r >= rows:  # avoid out-of-bounds
                break
            for c in range(box_width):
                if box_col + c >= cols:
                    break
                if (r in [0, box_height - 1] or c in [0, box_width - 1]):
                    stdscr.addch(box_row + r, box_col + c, '#', curses.color_pair(2) if curses.has_colors() else 0)
                else:
                    stdscr.addch(box_row + r, box_col + c, ' ')

        stdscr.refresh()

    # Prepare initial UI
    cursor_row, cursor_col = 8, 8
    draw_ui()
    stdscr.move(cursor_row, cursor_col)

    # Main event loop
    while True:
        key = stdscr.getch()

        if key == ord('q'):
            break
        elif key == ord('r'):
            # For demonstration, just place a message inside the box
            msg = "Refreshed content."
            stdscr.addstr(9, 7, msg[:(cols - 8)], curses.A_BOLD)
            stdscr.refresh()
        elif key == curses.KEY_UP:
            if cursor_row > 1:
                cursor_row -= 1
            stdscr.move(cursor_row, cursor_col)
        elif key == curses.KEY_DOWN:
            if cursor_row < rows - 1:
                cursor_row += 1
            stdscr.move(cursor_row, cursor_col)
        elif key == curses.KEY_LEFT:
            if cursor_col > 0:
                cursor_col -= 1
            stdscr.move(cursor_row, cursor_col)
        elif key == curses.KEY_RIGHT:
            if cursor_col < cols - 1:
                cursor_col += 1
            stdscr.move(cursor_row, cursor_col)
        else:
            # Continue if unhandled key
            pass

def run_curses_tui():
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Error in curses TUI: {e}", file=sys.stderr)

if __name__ == "__main__":
    run_curses_tui()
