from multiprocessing import Queue
import pickle
import socket
import time

def coordinator(north_queue: Queue, south_queue: Queue, east_queue: Queue, west_queue: Queue, shared_state, event):
    # Set up a TCP server for communication with the display client
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("127.0.0.1", 65432))  # Bind to the address and port
    server_socket.listen(1)
    print("Coordinator waiting for display connection...")

    conn = None
    while True:
        # Accept the connection if not already connected
        if conn is None:
            conn, addr = server_socket.accept()
            print(f"Connected to display client at {addr}")

        # Get the current traffic light state
        light_state = shared_state["lights"]

        # Check if each direction has cars waiting
        n, s, e, w = not north_queue.empty(), not south_queue.empty(), not east_queue.empty(), not west_queue.empty()

        # Default data for display
        data = {
            "North": north_queue.qsize(),
            "South": south_queue.qsize(),
            "East": east_queue.qsize(),
            "West": west_queue.qsize(),
            "lights": light_state,
            "priority": False,  # Default: no priority vehicle
        }
        match light_state:
            case "North":
                vehicle = north_queue.get()
                if vehicle["type"] == "priority":
                    print(f"🚑 Priority vehicle n° {vehicle['id']} from North passed")
                    data["priority"] = True
                    shared_state["lights"] = "North-South"  # Resume normal flow
                    event.clear()
                else:
                    print(f"North goes: {vehicle['id']}")

            case "South":
                vehicle = south_queue.get()
                if vehicle["type"] == "priority":
                    print(f"🚑 Priority vehicle n° {vehicle['id']} from South passed")
                    data["priority"] = True
                    shared_state["lights"] = "North-South"  # Resume normal flow
                    event.clear()
                else:
                    print(f"South goes: {vehicle['id']}")

            case "East":
                vehicle = east_queue.get()
                if vehicle["type"] == "priority":
                    print(f"🚑 Priority vehicle n° {vehicle['id']} from East passed")
                    data["priority"] = True
                    shared_state["lights"] = "North-South"  # Resume normal flow
                    event.clear()
                else:
                    print(f"East goes: {vehicle['id']}")

            case "West":
                vehicle = west_queue.get()
                if vehicle["type"] == "priority":
                    print(f"🚑 Priority vehicle n° {vehicle['id']} from West passed")
                    data["priority"] = True
                    shared_state["lights"] = "North-South"  # Resume normal flow
                    event.clear()
                else:
                    print(f"West goes: {vehicle['id']}")

            case "North-South":
                # North must yield to East, but since East has a red light, North can go
                if n and (not e or light_state == "North-South"): 
                    vehicle = north_queue.get()
                    print("North goes:", vehicle["id"])

                # South must yield to West, but since West has a red light, South can go
                elif s and (not w or light_state == "North-South"):
                    vehicle = south_queue.get()
                    print("South goes:", vehicle["id"])

            case "East-West":
                # East must yield to South, but since South has a red light, East can go
                if e and (not s or light_state == "East-West"):
                    vehicle = east_queue.get()
                    print("East goes:", vehicle["id"])

                # West must yield to North, but since North has a red light, West can go
                elif w and (not n or light_state == "East-West"):
                    vehicle = west_queue.get()
                    print("West goes:", vehicle["id"])



        # Send data update to display
        try:
            conn.sendall(pickle.dumps(data))
        except (BrokenPipeError, ConnectionResetError):
            print("Display disconnected, waiting for reconnection...")
            conn = None  # Reset connection to accept a new client

        # Simulate time for cars to cross
        time.sleep(0.3)
