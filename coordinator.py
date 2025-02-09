from multiprocessing import Queue
import pickle
import socket
import time

def infer_direction(source, destination):
    """Determine whether the vehicle is going straight, left, or right."""
    opposite_directions = {"North": "South", "South": "North", "East": "West", "West": "East"}
    
    if destination == opposite_directions[source]:  
        return "straight"
    elif (source, destination) in [("North", "West"), ("South", "East"), ("East", "North"), ("West", "South")]:
        return "left"
    else:
        return "right"


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


        # Default data for display
        data = {
            "North": north_queue.qsize(),
            "South": south_queue.qsize(),
            "East": east_queue.qsize(),
            "West": west_queue.qsize(),
            "lights": light_state,
            "priority": False,  # Default: no priority vehicle
        }
        if event.is_set():
            match light_state:
                case "North":
                    vehicle = north_queue.get()
                    if vehicle["type"] == "priority":
                        print(f"🚑 Priority vehicle n° {vehicle['id']} from North passed")
                        data["priority"] = True
                        shared_state["lights"] = shared_state["lightsbeforepriority"]  # Resume normal flow
                        event.clear()
                    else:
                        print(f"North goes: {vehicle['id']}")

                case "South":
                    vehicle = south_queue.get()
                    if vehicle["type"] == "priority":
                        print(f"🚑 Priority vehicle n° {vehicle['id']} from South passed")
                        data["priority"] = True
                        shared_state["lights"] = shared_state["lightsbeforepriority"]  # Resume normal flow
                        event.clear()
                    else:
                        print(f"South goes: {vehicle['id']}")

                case "East":
                    vehicle = east_queue.get()
                    if vehicle["type"] == "priority":
                        print(f"🚑 Priority vehicle n° {vehicle['id']} from East passed")
                        data["priority"] = True
                        shared_state["lights"] = shared_state["lightsbeforepriority"]  # Resume normal flow
                        event.clear()
                    else:
                        print(f"East goes: {vehicle['id']}")

                case "West":
                    vehicle = west_queue.get()
                    if vehicle["type"] == "priority":
                        print(f"🚑 Priority vehicle n° {vehicle['id']} from West passed")
                        data["priority"] = True
                        shared_state["lights"] = shared_state["lightsbeforepriority"]  # Resume normal flow
                        event.clear()
                    else:
                        print(f"West goes: {vehicle['id']}")
        else:
            match light_state:
                case "North-South":
                    # Get vehicles
                    north_vehicle = north_queue.get() if not north_queue.empty() else None
                    south_vehicle = south_queue.get() if not south_queue.empty() else None

                    if north_vehicle:
                        north_direction = infer_direction(north_vehicle["source"], north_vehicle["destination"])
                        north_yields = north_direction == "left" and south_vehicle and infer_direction(south_vehicle["source"], south_vehicle["destination"]) == "straight"

                        if not north_yields:
                            print(f"North goes: {north_vehicle['id']} ({north_direction})")

                    if south_vehicle:
                        south_direction = infer_direction(south_vehicle["source"], south_vehicle["destination"])
                        if not (north_vehicle and north_yields):
                            print(f"South goes: {south_vehicle['id']} ({south_direction})")

                case "East-West":
                    # Get vehicles
                    east_vehicle = east_queue.get() if not east_queue.empty() else None
                    west_vehicle = west_queue.get() if not west_queue.empty() else None

                    if east_vehicle:
                        east_direction = infer_direction(east_vehicle["source"], east_vehicle["destination"])
                        east_yields = east_direction == "left" and west_vehicle and infer_direction(west_vehicle["source"], west_vehicle["destination"]) == "straight"

                        if not east_yields:
                            print(f"East goes: {east_vehicle['id']} ({east_direction})")

                    if west_vehicle:
                        west_direction = infer_direction(west_vehicle["source"], west_vehicle["destination"])
                        if not (east_vehicle and east_yields):
                            print(f"West goes: {west_vehicle['id']} ({west_direction})")



        # Send data update to display
        try:
            conn.sendall(pickle.dumps(data))
        except (BrokenPipeError, ConnectionResetError):
            print("Display disconnected, waiting for reconnection...")
            conn = None  # Reset connection to accept a new client

        # Simulate time for cars to cross
        time.sleep(0.3)
