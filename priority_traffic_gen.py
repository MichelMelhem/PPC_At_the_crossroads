from multiprocessing import Queue
import random
import time
import os



def priority_traffic_gen(north_queue, south_queue, east_queue, west_queue, signal_event, pipe_path ):

    # Ensure the named pipe exists
    if not os.path.exists(pipe_path):
        os.mkfifo(pipe_path)

    while True:
        time.sleep(random.uniform(4,5))  # Random delay before next priority vehicle
        vehicle = {
            "type": "priority",
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
            
            print(f"🚨 Priority vehicle generated from {vehicle['source']} to {vehicle['destination']} with id {vehicle['id']}!")

            # Notify lights process by writing the source direction
            try:
                with open(pipe_path, "w") as pipe:
                    pipe.write(vehicle["source"] + "\n")
                    pipe.flush()
            except Exception as e:
                print(f"Error writing to pipe: {e}")



            # Trigger the signal event to notify lights
            signal_event.set()


