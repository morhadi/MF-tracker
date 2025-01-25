import curses
from thefuzz import process

def main(stdscr):
    stdscr.clear()
    stdscr.refresh()
    stdscr.keypad(True)  # Enable special keys like backspace

    data = ["apple", "banana", "apricot", "kiwi", "grape", "grapefruit"]
    query = ""
    suggestions = []

    while True:
        stdscr.addstr(0, 0, "Search: " + query)
        stdscr.clrtoeol() #clear line after cursor

        if suggestions:
            for i, suggestion in enumerate(suggestions):
                stdscr.addstr(i + 1, 0, f"- {suggestion}")
                stdscr.clrtoeol() #clear line after cursor
        else:
            stdscr.addstr(1,0,"No Match Found")
            stdscr.clrtoeol() #clear line after cursor

        stdscr.refresh()

        key = stdscr.getch()

        if key in (curses.KEY_BACKSPACE, 127, 8):  # Handle backspace
            if query:
                query = query[:-1]
        elif key == 27:  # Escape key
            break
        elif key != -1:
            try:
                query += chr(key)
            except ValueError:
                pass #ignore non-printable characters

        suggestions = process.extract(query, data )
        suggestions = [s[0] for s in suggestions]

if __name__ == "__main__":
    curses.wrapper(main)