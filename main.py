from multiprocessing import Process, Manager
import time
import socket
import pickle

from coordinator import coordinator
import display
from lights import lights
from normal_traffic_gen import normal_traffic_gen
from priority_traffic_gen import priority_traffic_gen



if __name__ == "__main__":
    import multiprocessing
    multiprocessing.set_start_method("fork")  # Use fork on macOS
    pipe_path = "./tmp/priority_pipe"

    manager = Manager()
    
    west_queue = manager.Queue()
    east_queue = manager.Queue()    
    north_queue = manager.Queue()
    south_queue = manager.Queue()
    
    shared_state = manager.dict({"lights": "North-South"})
    signal_event = manager.Event()  # Shared signal event

    processes = [
        Process(target=priority_traffic_gen, args=(north_queue,west_queue,east_queue,south_queue,signal_event, pipe_path)),
        Process(target=normal_traffic_gen, args=(north_queue,west_queue,east_queue,south_queue)),
        Process(target=lights, args=(shared_state, signal_event, pipe_path)),
        Process(target=coordinator, args=(north_queue,west_queue,east_queue,south_queue, shared_state, signal_event)),
    ]

    for p in processes:
        p.start()

    for p in processes:
        p.join()
