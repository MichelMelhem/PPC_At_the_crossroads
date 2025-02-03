import socket
import pickle
import curses
import time

def draw_intersection(stdscr, conn):
    stdscr.nodelay(True)  # Non-blocking input
    curses.curs_set(0)    # Hide cursor

    # Store the previous data to compare changes
    prev_data = None  

    while True:
        # Receive data from the coordinator
        try:
            data = pickle.loads(conn.recv(1024))
        except:
            data = prev_data  # Use previous data if there's no new data

        if data is None:
            continue  # Skip if there's no valid data

        # Only redraw if data has changed
        if data != prev_data:
            stdscr.clear()
            stdscr.border()

            # Intersection layout
            intersection = [
                "        N        ",
                "        |        ",
                "        |        ",
                "W ----[ ]---- E ",
                "        |        ",
                "        |        ",
                "        S        ",
            ]

            # Display intersection
            for i, line in enumerate(intersection):
                stdscr.addstr(i + 2, 10, line)

            # Display queue sizes
            stdscr.addstr(1, 15, f"N: {data['North']} cars")
            stdscr.addstr(4, 1, f"W: {data['West']} cars")
            stdscr.addstr(4, 25, f"E: {data['East']} cars")
            stdscr.addstr(7, 15, f"S: {data['South']} cars")
            stdscr.addstr(9, 10, f"Traffic Light: {data['lights']}", curses.A_BOLD)

            # Highlight priority vehicle if detected
            if data["priority"]:
                stdscr.addstr(11, 10, "🚑 Priority Vehicle Passing! 🚑", curses.A_BOLD)

            stdscr.refresh()
            prev_data = data  # Save the new data as previous

        time.sleep(0.5)

def display():
    while True:
        try:
            # Connect to the coordinator
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(("127.0.0.1", 65432))
            print("Connected to coordinator.")

            curses.wrapper(draw_intersection, client_socket)
        except ConnectionRefusedError:
            print("Coordinator not available. Retrying in 5 seconds...")
            time.sleep(5)
        except Exception as e:
            print(f"Error in display: {e}")
            break

if __name__ == "__main__":
    display()
