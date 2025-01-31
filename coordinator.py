from multiprocessing import Event, Queue
import time

def coordinator(north_queue : Queue, south_queue : Queue, east_queue : Queue, west_queue : Queue, shared_state, event : Event):
    while True:
        # Get the current traffic light state
        light_state = shared_state["lights"]

        # Check if each direction has cars waiting
        n, s, e, w = not north_queue.empty(), not south_queue.empty(), not east_queue.empty(), not west_queue.empty()
        
        # fonctionement execeptionel pour les vehicules prioritaires
        
        if light_state == "North" and n:
            vehicule = north_queue.get()
            if(vehicule["type"] == "priority"):
                print("🚑 Priority vehicule n°", vehicule["id"] ,"from north passed")
            else:
                print("North goes :" , vehicule["id"])
            event.clear()

        elif light_state == "South" and s:
            vehicule = south_queue.get()
            if(vehicule["type"] == "priority"):
                print("🚑  Priority vehicule n°", vehicule["id"] ,"from south passed")
            else:
                print("South goes :" , vehicule["id"])
            event.clear()

        elif light_state == "East" and e:
            vehicule = east_queue.get()
            if(vehicule["type"] == "priority"):
                print("🚑 Priority vehicule n°", vehicule["id"] ,"from east passed")
            else :
                print("East goes :" , vehicule["id"])
            event.clear()

        elif light_state == "West" and w:
            vehicule = west_queue.get()
            if(vehicule["type"] == "priority"):
                print("🚑 Priority vehicule n°", vehicule["id"] ,"from West passed")
            else:
                print("west goes :" , vehicule["id"])
            event.clear()
        
        #fonctionnement normal qui respecte la priorité à droite 
        
        elif light_state == "North-South":
            # North must yield to East, but since East has a red light, North can go
            if n and (not e or light_state == "North-South"): 
                vehicule = north_queue.get()
                print("North goes :" , vehicule["id"])

            # South must yield to West, but since West has a red light, South can go
            elif s and (not w or light_state == "North-South"):
                vehicule = south_queue.get()
                print("South goes :" , vehicule["id"])

        elif light_state == "East-West":
            # East must yield to South, but since South has a red light, East can go
            if e and (not s or light_state == "East-West"):
                vehicule = east_queue.get()
                print("East goes :" , vehicule["id"])

            # West must yield to North, but since North has a red light, West can go
            elif w and (not n or light_state == "East-West"):
                vehicule = west_queue.get()
                print("West goes :" , vehicule["id"])

        # Simulate time for cars to cross
        time.sleep(1)
