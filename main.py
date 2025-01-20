from multiprocessing import Process, Manager, Event
import time
import random
import socket
import pickle


def normal_traffic_gen(queue):
    while True:
        vehicle = {
            "type": "normal",
            "id": random.randint(1000, 9999),
            "source": random.choice(["North", "South", "East", "West"]),
            "destination": random.choice(["North", "South", "East", "West"])
        }
        if vehicle["source"] != vehicle["destination"]:
            queue.put(vehicle)
            print(f"Normal vehicle generated: {vehicle}")
        time.sleep(random.uniform(1, 3))


def priority_traffic_gen(queue, signal_event):
    while True:
        vehicle = {
            "type": "priority",
            "id": random.randint(1000, 9999),
            "source": random.choice(["North", "South", "East", "West"]),
            "destination": random.choice(["North", "South", "East", "West"])
        }
        if vehicle["source"] != vehicle["destination"]:
            queue.put(vehicle)
            signal_event.set()  # Notify the lights process
            print(f"Priority vehicle generated: {vehicle}")
        time.sleep(random.uniform(5, 10))


def lights(shared_state, signal_event):
    while True:
        if signal_event.is_set():
            print("Handling priority vehicle, setting lights.")
            shared_state["lights"] = "priority"
            time.sleep(3)
            signal_event.clear()
        else:
            shared_state["lights"] = "North-South"
            print("Lights: North-South green.")
            time.sleep(5)
            shared_state["lights"] = "East-West"
            print("Lights: East-West green.")
            time.sleep(5)


def coordinator(normal_queue, priority_queue, shared_state):
    while True:
        if not priority_queue.empty():
            vehicle = priority_queue.get()
            print(f"Processing priority vehicle: {vehicle}")
        elif not normal_queue.empty():
            vehicle = normal_queue.get()
            print(f"Processing normal vehicle: {vehicle}")
        time.sleep(1)


def display_server(shared_state, normal_queue, priority_queue):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("127.0.0.1", 65432))
    server_socket.listen(1)
    print("Traffic server started. Waiting for display connection...")

    conn, addr = server_socket.accept()
    print(f"Display connected from {addr}")

    try:
        while True:
            data = {
                "lights": shared_state["lights"],
                "normal_queue_size": normal_queue.qsize(),
                "priority_queue_size": priority_queue.qsize(),
            }
            conn.sendall(pickle.dumps(data))
            time.sleep(0.5)
    except Exception as e:
        print(f"Error in server: {e}")
    finally:
        conn.close()
        server_socket.close()


if __name__ == "__main__":
    import multiprocessing
    multiprocessing.set_start_method("fork")  # Use fork on macOS

    manager = Manager()
    normal_queue = manager.Queue()
    priority_queue = manager.Queue()
    shared_state = manager.dict({"lights": "North-South"})
    signal_event = manager.Event()  # Shared signal event

    processes = [
        Process(target=normal_traffic_gen, args=(normal_queue,)),
        Process(target=priority_traffic_gen, args=(priority_queue, signal_event)),
        Process(target=lights, args=(shared_state, signal_event)),
        Process(target=coordinator, args=(normal_queue, priority_queue, shared_state)),
        Process(target=display_server, args=(shared_state, normal_queue, priority_queue)),
    ]

    for p in processes:
        p.start()

    for p in processes:
        p.join()
