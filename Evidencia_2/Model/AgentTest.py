import agentpy as ap
from Ontology import Drone, Camera, Guard
import random
import time
# import UnityFunctions
# import ComputationalVision

# Mensajes de simulación (usando un diccionario)
mensajes = {}

# Función para enviar un mensaje a un agente específico
def enviar_mensaje(destinatario, contenido):
    if destinatario not in mensajes:
        mensajes[destinatario] = []
    mensajes[destinatario].append(contenido)

# Función para procesar los mensajes de un agente específico
def recibir_mensajes(agente_id):
    if agente_id in mensajes:
        mensajes_recibidos = mensajes[agente_id]
        del mensajes[agente_id]  # Limpiar mensajes una vez procesados
        return mensajes_recibidos
    return []

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
        self.flighting = False
        self.finish_route = False
        self.in_control = False
        self.before_alert_pos = None
        self.investigating = False

    def start_patrol(self):
        if self.current_pos == self.model.start_position and not self.flighting:
            print(f"$ Dron despega en {self.current_pos}")
            self.patrolling = True
            self.flighting = True
        elif self.current_pos == self.model.start_position and self.previous_pos == self.model.route[-2] and self.flighting and not self.is_dangerous and self.finish_route: 
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
            #UnityFunctions.end_route()
            print(f"$ Dron terminó su ruta")
        pass

    def receive_alert(self, certainty, position):
        self.certainty = certainty
        self.target_pos = position
        #if self.certainty and not self.investigating:
        if self.certainty > 0.5:
            self.before_alert_pos = self.current_pos
            #self.investigating = True
            self.investigate()

    def investigate(self):
        # Se mueve a la posición objetivo y señala al guardia si es peligroso
        if self.current_pos != self.target_pos:
            self.move_to(self.target_pos)
        if self.certainty > 0.6:
            print(f"$ Dron en posición {self.current_pos} señala peligro al guardia por mensaje")
            enviar_mensaje("guardia", {"take_control": {"certainty": self.certainty, "is_dangerous": self.is_dangerous}})
            print("Mensajes Guardia: ", mensajes["guardia"], end="\n\n")

    def move_to(self, position):
        # Lógica de movimiento hacia una posición específica
        # Solo se regresaría a Unity que se mueva a la siguiente posición
        print(f"$ Dron se mueve de {self.current_pos} a {position}")
        self.previous_pos = self.current_pos
        self.current_pos = position
        #UnityFunctions.move_to_next_position(position)
        #self.investigate()?

    def revisar_mensajes(self):
        mensajes_drone = recibir_mensajes("dron")
        for mensaje in mensajes_drone:
            if "receive_alert" in mensaje:
                alerta = mensaje["receive_alert"]
                self.receive_alert(alerta["certainty"], alerta["position"])

            if "return_to_route" in mensaje:
                print(f"$ Dron regresa a su ruta en posición {self.current_pos}")
                self.investigating = False
                self.move_to(self.before_alert_pos)


class CameraAgent(ap.Agent):
    def setup(self):
        self.owl_entity = Camera()

    def detect_movement(self):
        # Simular detección de movimiento y llamar al dron si es necesario
        """
        result = ComputationalVision.camera_detection()
        if result['certainty'] > 0.5:
            position = self.model.grid.positions[self]
            enviar_mensaje("dron", {"receive_alert": {"certainty": certainty, "position": position}})

            #drone.move_to(UnityFunctions.get_camera_position(self))
            print(f"- {self}: Aviso al dron sobre una posible amenaza.")
            #print(f"- Cámara detecta movimiento en {self.model.grid.positions[self]} con certeza {result['certainty']}")
            print("Mensajes Dron: ", mensajes["dron"], end="\n\n")

            """
        pass

class GuardAgent(ap.Agent):
    def setup(self):
        self.owl_entity = Guard()

    def take_control(self, drone, certainty, danger):
        print(f"* Guardia toma control del dron con certeza {certainty} y peligro {danger}")
        #result = ComputationalVision.detect_danger() # Detectar peligro por visión computacional
        #danger = True if result['danger'] == true else False
        if certainty > 0.7 and danger:
            self.trigger_alarm()
        else:
            self.false_alarm(drone)

    def trigger_alarm(self):
        # Se regresa a Unity que se active la alarma
        #UnityFunctions.trigger_alarm()
        print("* ¡Alarma general! Peligro detectado.")
        enviar_mensaje("dron", {"return_to_route": True})
        print("Mensajes Dron: ", mensajes["dron"], end="\n\n")


    def false_alarm(self, drone):
        # Se regresa a Unity que fue falsa alarma y vuelva a la ruta
        #UnityFunctions.false_alarm()
        print("* Falsa alarma. El dron vuelve a su ruta.")
        enviar_mensaje("dron", {"return_to_route": True})
        print("Mensajes Dron: ", mensajes["dron"], end="\n\n")


    def revisar_mensajes(self):
        mensajes_guardia = recibir_mensajes("guardia")
        for mensaje in mensajes_guardia:
            if "take_control" in mensaje:
                control = mensaje["take_control"]
                self.take_control(control["certainty"], control["is_dangerous"])
