import time


def lights(shared_state, signal_event):
    while True:
        if signal_event.is_set():
            print("Handling priority vehicle, setting lights.")
            shared_state["lights"] = "priority"
            time.sleep(3)
            signal_event.clear()
        else:
            shared_state["lights"] = "North-South"
            print("Lights: North-South green.")
            time.sleep(5)
            shared_state["lights"] = "East-West"
            print("Lights: East-West green.")
            time.sleep(5)
