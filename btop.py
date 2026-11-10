import curses
import time

import psutil


def _add_text(screen, row: int, column: int, text: str, width: int, style: int = 0) -> None:
    if row < 0 or row >= screen.getmaxyx()[0] or width <= 0:
        return
    try:
        screen.addnstr(row, column, str(text), width, style)
    except curses.error:
        pass


def run_dashboard(process, server_process, get_console_logs, send_command, ram: str) -> None:
    def draw(screen):
        curses.curs_set(1)
        screen.keypad(True)
        screen.timeout(100)
        if curses.has_colors():
            curses.start_color()
            curses.use_default_colors()
            curses.init_pair(1, curses.COLOR_CYAN, -1)
            curses.init_pair(2, curses.COLOR_GREEN, -1)
            curses.init_pair(3, curses.COLOR_YELLOW, -1)

        command = ""
        while process.poll() is None:
            height, width = screen.getmaxyx()
            screen.erase()
            header_style = curses.color_pair(1) | curses.A_BOLD if curses.has_colors() else curses.A_BOLD
            screen.addnstr(0, 0, "Minecraft Server | ketik perintah, Enter untuk kirim", max(0, width - 1), header_style)
            if height > 1:
                screen.hline(1, 0, curses.ACS_HLINE, max(0, width - 1))

            compact = width < 72 or height < 14
            try:
                memory = server_process.memory_info().rss
                cpu_percent = server_process.cpu_percent(interval=None)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                memory, cpu_percent = 0, 0

            memory_mb = memory / (1024 * 1024)
            left_lines = [
                "Resource Monitor",
                "Status: Berjalan",
                f"PID: {process.pid}",
                f"CPU: {cpu_percent:.1f}%",
                f"RAM: {memory_mb:.2f} MB ({memory_mb / 1024:.2f} GB)",
                f"Alokasi: {ram}",
            ]

            if compact:
                for index, line in enumerate(left_lines):
                    _add_text(screen, 2 + index, 0, line, width - 1)
                log_start = 9
                log_column = 0
            else:
                divider = min(max(25, width // 3), width - 20)
                _add_text(screen, 2, 1, "Resource Monitor", divider - 2, header_style)
                _add_text(screen, 2, divider + 2, "Server Console", width - divider - 4, header_style)
                for index, line in enumerate(left_lines[1:], start=3):
                    _add_text(screen, index, 1, line, divider - 2)
                for row in range(2, height - 2):
                    try:
                        screen.addch(row, divider, curses.ACS_VLINE)
                    except curses.error:
                        pass
                log_start = 3
                log_column = divider + 2

            command_row = height - 1
            log_end = command_row - 2
            log_count = max(0, log_end - log_start + 1)
            logs = get_console_logs()
            for index, line in enumerate(logs[-log_count:] if log_count else []):
                _add_text(screen, log_start + index, log_column, line, width - log_column - 1)

            prompt = "Command > "
            visible_width = max(0, width - len(prompt) - 1)
            visible_command = command[-visible_width:] if visible_width else ""
            _add_text(screen, command_row, 0, prompt + visible_command, width - 1, curses.A_REVERSE)
            try:
                screen.move(command_row, min(len(prompt) + len(visible_command), max(0, width - 1)))
                screen.refresh()
            except curses.error:
                pass

            try:
                key = screen.get_wch()
            except curses.error:
                time.sleep(0.05)
                continue

            if key in ("\n", "\r", curses.KEY_ENTER):
                value = command.strip()
                if value:
                    send_command(value)
                command = ""
            elif key in (curses.KEY_BACKSPACE, "\b", "\x7f"):
                command = command[:-1]
            elif key == "\x15":
                command = ""
            elif key == "\x03":
                raise KeyboardInterrupt
            elif isinstance(key, str) and key.isprintable():
                command += key

    curses.wrapper(draw)