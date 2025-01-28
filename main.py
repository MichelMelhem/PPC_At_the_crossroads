from multiprocessing import Process, Manager
import time
import socket
import pickle

from coordinator import coordinator
from lights import lights
from normal_traffic_gen import normal_traffic_gen
from priority_traffic_gen import priority_traffic_gen




def display_server(shared_state, normal_queue, priority_queue):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("127.0.0.1", 65432))
    server_socket.listen(1)
    print("Traffic server started. Waiting for display connection...")

    while True:
        try:
            conn, addr = server_socket.accept()
            print(f"Display connected from {addr}")

            while True:
                try:
                    data = {
                        "lights": shared_state["lights"],
                        "normal_queue_size": normal_queue.qsize(),
                        "priority_queue_size": priority_queue.qsize(),
                    }
                    conn.sendall(pickle.dumps(data))
                    time.sleep(0.5)
                except (ConnectionResetError, BrokenPipeError) as e:
                    print(f"Connection lost: {e}")
                    break  # Break the inner loop to attempt reconnection
                except Exception as e:
                    print(f"Error in server: {e}")
                    break  # Break the inner loop to attempt reconnection

        except Exception as e:
            print(f"Error accepting connection: {e}")
            time.sleep(5)  # Wait before attempting to accept a new connection
        finally:
            if 'conn' in locals():
                conn.close()
                print("Connection closed. Waiting for a new connection...")

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
        Process(target=coordinator, args=(normal_queue, priority_queue)),
        Process(target=display_server, args=(shared_state, normal_queue, priority_queue)),
    ]

    for p in processes:
        p.start()

    for p in processes:
        p.join()
