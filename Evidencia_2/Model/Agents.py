import agentpy as ap
from Ontology import Drone, Camera, Guard
import random
import time
# import UnityFunctions
# import ComputationalVision

class DroneAgent(ap.Agent):
    def setup(self):
        self.owl_entity = Drone()
        self.patrolling = False
        self.current_pos = (0, 0)
        #self.current_pos = UnityFunctions.get_dron_position()
        self.previous_pos = None
        self.certainty = 0.0
        # self.certainty = ComputationalVision.get_certainty()
        self.is_dangerous = False
        self.target_pos = None
        self.in_control = False

    """
    def start_patrol(self):
        if self.current_pos == self.model.start_position:
            self.patrolling = True
            self.move_along_route()
    """
    def start_patrol(self):
        if self.current_pos == self.model.start_position and not self.flighting:
            print(f"$ Dron despega en {self.current_pos}")
            self.patrolling = True
            self.flighting = True
        elif self.current_pos == self.model.start_position and self.flighting and not self.is_dangerous and self.finish_route: 
            print(f"$ Dron desciende en {self.current_pos}")
            print(f"$ Dron se espera por 10 segundos")
            time.sleep(10)
            #UnityFunctions.end_route()
        self.move_along_route()

    def move_along_route(self):
        # Movimiento en ruta predefinida
        # Solo se regresaría a Unity que se mueva a la siguiente posición
        # Lógica de movimiento...


        # Si la posición actual es la de inicio, se termina la ruta
        if self.current_pos == self.model.start_position:
            self.finish_route = True
            print(f"$ Dron terminó su ruta")
        pass

    def receive_alert(self, certainty, position):
        self.certainty = certainty
        self.target_pos = position
        if self.certainty > 0.5:
            self.investigate()

    def investigate(self):
        # Se mueve a la posición objetivo y señala al guardia si es peligroso
        if self.current_pos != self.target_pos:
            self.move_to(self.target_pos)
        if self.certainty > 0.6:
            print(f"$ Dron en posición {self.current_pos} señala peligro al guardia")
            self.signal_guard()

    def signal_guard(self):
        guard = self.model.guard
        guard.take_control(self, self.certainty, self.is_dangerous)


    def move_to(self, position):
        # Lógica de movimiento hacia una posición específica
        # Solo se regresaría a Unity que se mueva a la siguiente posición
        #UnityFunctions.move_to_next_position()
        print(f"$ Dron se mueve de {self.current_pos} a {position}")
        self.previous_pos = self.current_pos
        self.current_pos = position

class CameraAgent(ap.Agent):
    def setup(self):
        self.owl_entity = Camera()

    def detect_movement(self):
        # Simular detección de movimiento y llamar al dron si es necesario
        """
        result = ComputationalVision.camera_detection()
        if result['certainty'] > 0.5:
            drone = self.model.drone
            drone.investigating = True
            drone.previous_position = self.model.grid.positions[drone]
            drone.move_to(self.model.grid.positions[self])
            #drone.move_to(UnityFunctions.get_camera_position(self))
            print(f"- {self}: Aviso al dron sobre una posible amenaza.")
            print(f"- Cámara detecta movimiento en {self.model.grid.positions[self]} con certeza {result['certainty']}")
            """
        pass

class GuardAgent(ap.Agent):
    def setup(self):
        self.owl_entity = Guard()

    def take_control(self, drone, certainty, danger):
        print(f"* Guardia toma control del dron con certeza {certainty} y peligro {danger}")
        if certainty > 0.7 and danger:
            self.trigger_alarm()
        else:
            self.false_alarm(drone)

    def trigger_alarm(self):
        # Se regresa a Unity que se active la alarma
        #UnityFunctions.raise_alarm()
        print("* ¡Alarma general! Peligro detectado.")

    def false_alarm(self, drone):
        # Se regresa a Unity que fue falsa alarma y vuelva a la ruta
        #UnityFunctions.false_alarm()
        print("Falsa alarma. El dron vuelve a su ruta.")
        drone.move_to(drone.previous_pos)
