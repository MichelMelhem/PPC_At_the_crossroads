import time


def coordinator(normal_queue, priority_queue):
    while True:
        if not priority_queue.empty():
            vehicle = priority_queue.get()
            print(f"Processing priority vehicle: {vehicle}")
        elif not normal_queue.empty():
            vehicle = normal_queue.get()
            print(f"Processing normal vehicle: {vehicle}")
        time.sleep(1)
