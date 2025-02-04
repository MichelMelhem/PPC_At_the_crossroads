import random
import time
import os



def priority_traffic_gen(north_queue, south_queue, east_queue, west_queue, signal_event, pipe_path ):


    # Now create the named pipe (FIFO)
    if not os.path.exists(pipe_path):
        os.mkfifo(pipe_path)
        print("Named pipe created at:", pipe_path)
    else:
         print("Named pipe already exists.")

        

    while True:
        time.sleep(random.uniform(9,12))  # Random delay before next priority vehicle
        vehicle = {
            "type": "priority",
            "id": random.randint(1000, 9999),
            "source": random.choice(["North", "South", "East", "West"]),
            "destination": random.choice(["North", "South", "East", "West"])
        }

         # Notify lights process by writing the source direction
        try:
                with open(pipe_path, "w") as pipe:
                    pipe.write(vehicle["source"] + "\n")
                    pipe.flush()
        except Exception as e:
                print(f"Error writing to pipe: {e}")

            # Trigger the signal event to notify lights
        signal_event.set()
        
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

       
            print(f"🚦 Priority mode: ONLY ", vehicle["source"] ," is GREEN!")
            # Un seul véhicule prioritaire ne peut ètre traité à la fois
            while signal_event.is_set():
                ()



