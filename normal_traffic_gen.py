import random
import time


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
