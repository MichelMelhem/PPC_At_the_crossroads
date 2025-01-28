

import random
import time


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
            print("Priority vehicle generated: {vehicle}")
        time.sleep(random.uniform(5, 10))


