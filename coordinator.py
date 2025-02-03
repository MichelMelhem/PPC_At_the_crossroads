from multiprocessing import Event, Queue
import pickle
import socket
import time

def coordinator(north_queue: Queue, south_queue: Queue, east_queue: Queue, west_queue: Queue, shared_state, event: Event):
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

        # Exceptional case for priority vehicles
        processed = False  # Track if we processed a car
        if light_state == "North" and n:
            vehicle = north_queue.get()
            if vehicle["type"] == "priority":
                print(f"🚑 Priority vehicle n° {vehicle['id']} from North passed")
                data["priority"] = True
                shared_state["lights"] = "North-South"  # Resume normal flow
                event.clear()
            else:
                print(f"North goes: {vehicle['id']}")
            processed = True

        elif light_state == "South" and s:
            vehicle = south_queue.get()
            if vehicle["type"] == "priority":
                print(f"🚑 Priority vehicle n° {vehicle['id']} from South passed")
                data["priority"] = True
                shared_state["lights"] = "North-South"  # Resume normal flow
                event.clear()
            else:
                print(f"South goes: {vehicle['id']}")
            processed = True

        elif light_state == "East" and e:
            vehicle = east_queue.get()
            if vehicle["type"] == "priority":
                print(f"🚑 Priority vehicle n° {vehicle['id']} from East passed")
                data["priority"] = True
                shared_state["lights"] = "North-South"  # Resume normal flow
                event.clear()
            else:
                print(f"East goes: {vehicle['id']}")
            processed = True

        elif light_state == "West" and w:
            vehicle = west_queue.get()
            if vehicle["type"] == "priority":
                print(f"🚑 Priority vehicle n° {vehicle['id']} from West passed")
                data["priority"] = True
                shared_state["lights"] = "North-South"  # Resume normal flow
                event.clear()
            else:
                print(f"West goes: {vehicle['id']}")
            processed = True
            

        # Normal operation (right-hand rule priority)
        elif not processed:
            if light_state == "North-South":
                if n:
                    vehicle = north_queue.get()
                    print(f"North goes: {vehicle['id']}")
                    processed = True
                elif s:
                    vehicle = south_queue.get()
                    print(f"South goes: {vehicle['id']}")
                    processed = True
            elif light_state == "East-West":
                if e:
                    vehicle = east_queue.get()
                    print(f"East goes: {vehicle['id']}")
                    processed = True
                elif w:
                    vehicle = west_queue.get()
                    print(f"West goes: {vehicle['id']}")
                    processed = True

        # Send data update to display
        try:
            conn.sendall(pickle.dumps(data))
        except (BrokenPipeError, ConnectionResetError):
            print("Display disconnected, waiting for reconnection...")
            conn = None  # Reset connection to accept a new client

        # Simulate time for cars to cross
        time.sleep(1)
