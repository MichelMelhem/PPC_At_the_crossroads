import random
import time


def normal_traffic_gen(north_queue, south_queue, east_queue, west_queue):
    while True:
        vehicle = {
            "type": "normal",
            "id": random.randint(1000, 9999),
            "source": random.choice(["North", "South", "East", "West"]),
            "destination": random.choice(["North", "South", "East", "West"])
        }
        if vehicle["source"] != vehicle["destination"]:
            match vehicle["source"]:
                case "North":
                    north_queue.put(vehicle)
                case "South":
                    south_queue.put(vehicle)
                case "East":
                    east_queue.put(vehicle)
                case "West":
                    west_queue.put(vehicle)
            print(f"Normal vehicle generated: {vehicle}")
        time.sleep(random.uniform(1,2))
