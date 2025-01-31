import time
import os

def lights(shared_state, signal_event,pipe_path):

    pipe_dir = os.path.dirname(pipe_path)
    if not os.path.exists(pipe_dir):
        os.makedirs(pipe_dir)  # Create the directory if it doesn't exist

    # Now create the named pipe (FIFO)
    if not os.path.exists(pipe_path):
        os.mkfifo(pipe_path)
        print("Named pipe created at:", pipe_path)
    else:
         print("Named pipe already exists.")

    while True:
        if signal_event.is_set():  #les feu nous informent qu'un vehicule prioritaire va passer
            try:
                with open(pipe_path, "r") as pipe:
                    priority_direction = pipe.readline().strip()

                if priority_direction:
                    print(f"🚦 Priority mode: ONLY {priority_direction} is GREEN!")

                    # Set only the priority vehicle's direction to green, others to red
                    shared_state["lights"] = priority_direction

                    time.sleep(5)  # Let priority vehicle pass
                    signal_event.clear()  # Reset the signal event
                    shared_state["lights"] = "North-South"  # Resume normal flow

            except Exception as e:
                print(f"Error reading pipe: {e}")

        else:  # Normal operation if no priority vehicle is present
            if shared_state["lights"] == "North-South":
                shared_state["lights"] = "East-West"
            else:
                shared_state["lights"] = "North-South"

            print(f"🚦 Normal Traffic light state: {shared_state['lights']}")
            time.sleep(10)  # Normal light cycle
