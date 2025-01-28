import curses
import socket
import pickle
import time


def display_client():
    server_address = ("127.0.0.1", 65432)

    # Connect to the display server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect(server_address)
        print("Connected to the display server.")

        # Initialize curses
        stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        stdscr.keypad(True)

        try:
            while True:
                # Receive and deserialize data
                data = client_socket.recv(1024)
                if not data:
                    break
                traffic_data = pickle.loads(data)

                # Clear the screen
                stdscr.clear()

                # Display the traffic light status
                stdscr.addstr(0, 0, "Traffic Intersection Simulation")
                stdscr.addstr(2, 0, f"Current Traffic Light: {traffic_data['lights']}")

                # Display queue sizes
                stdscr.addstr(4, 0, f"Normal Vehicles in Queue: {traffic_data['normal_queue_size']}")
                stdscr.addstr(5, 0, f"Priority Vehicles in Queue: {traffic_data['priority_queue_size']}")
                
                stdscr.addstr(6, 0, "")  # Empty line
                stdscr.addstr(7, 0, "")  # Empty line

                # Draw a simple representation of the intersection
                draw_intersection(stdscr, traffic_data["lights"])

                # Refresh the screen
                stdscr.refresh()
                time.sleep(0.5)
        except Exception as e:
            print(f"Error in client: {e}")
        finally:
            # Restore terminal settings
            curses.nocbreak()
            stdscr.keypad(False)
            curses.echo()
            curses.endwin()

def draw_intersection(stdscr, lights_status):
    """
    Draws a simple representation of the intersection, 3 lines lower.
    """
    intersection_center = 10
    vertical_offset = 3  # Offset to move the graphic 3 lines lower

    # Horizontal road
    for i in range(5, 16):
        stdscr.addstr(intersection_center + vertical_offset, i, "-")

    # Vertical road
    for i in range(5, 16):
        stdscr.addstr(i + vertical_offset, intersection_center, "|")

    # Traffic light indicators
    if lights_status == "North-South":
        stdscr.addstr(5 + vertical_offset, intersection_center - 2, "G")  # Green for North
        stdscr.addstr(15 + vertical_offset, intersection_center - 2, "G")  # Green for South
        stdscr.addstr(intersection_center - 1 + vertical_offset, 5, "R")  # Red for West
        stdscr.addstr(intersection_center - 1 + vertical_offset, 15, "R")  # Red for East
    elif lights_status == "East-West":
        stdscr.addstr(5 + vertical_offset, intersection_center - 2, "R")  # Red for North
        stdscr.addstr(15 + vertical_offset, intersection_center - 2, "R")  # Red for South
        stdscr.addstr(intersection_center - 1 + vertical_offset, 5, "G")  # Green for West
        stdscr.addstr(intersection_center - 1 + vertical_offset, 15, "G")  # Green for East
    elif lights_status == "priority":
        stdscr.addstr(intersection_center + vertical_offset, intersection_center, "P")  # Priority vehicle in the center

if __name__ == "__main__":
    display_client()
