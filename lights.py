import time
import os

def lights(shared_state, signal_event,pipe_path):


    while True:
        if signal_event.is_set():  #les feu nous informent qu'un vehicule prioritaire va passer
            try:
                with open(pipe_path, "r") as pipe:
                    priority_direction = pipe.readline().strip()

                if priority_direction:
                    # Set only the priority vehicle's direction to green, others to red
                    shared_state["lights"] = priority_direction

                  

            except Exception as e:
                print(f"Error reading pipe: {e}")

        else:  # Normal operation if no priority vehicle is present
            if shared_state["lights"] == "North-South":
                shared_state["lights"] = "East-West"
            else:
                shared_state["lights"] = "North-South"

            print(f"🚦 Normal Traffic light state: {shared_state['lights']}")
            time.sleep(10)  # Normal light cycle
