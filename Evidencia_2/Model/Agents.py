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
    
    # Solo agregar el mensaje si la lista está vacía
    if not mensajes[destinatario] and not len(mensajes[destinatario]) > 0:
        mensajes[destinatario].append(contenido)
    else:
        print(f"$ Mensaje ignorado: ya se tiene una alerta pendiente.")


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
            self.end_route()
        self.move_along_route()

    def move_along_route(self):
        # Movimiento en ruta predefinida
        # Solo se regresaría a Unity que se mueva a la siguiente posición
        # Lógica de movimiento...
        #if self.current_pos in self.model.route:
         #   index = self.model.route.index(self.current_pos)
          #  self.previous_pos = self.current_pos
           # self.current_pos = self.model.route[(index + 1) % len(self.model.route)]
            #print(f"$ Dron se mueve a {self.current_pos}")



        # Si la posición actual es la de inicio, se termina la ruta
        if self.current_pos == self.model.start_position:
            self.end_route()
        pass

    def end_route(self):
        print(f"$ Dron terminó su ruta")
        print(f"$ Dron desciende en {self.current_pos}")
        print(f"$ Dron se espera por 10 segundos")
        self.flighting = False
        self.finish_route = False   
        #UnityFunctions.end_route()

    def receive_alert(self, certainty, position):
        if not self.investigating:
            self.certainty = certainty
            self.target_pos = position

            # Si la certeza es mayor a 0.5 y no está investigando ya, se inicia una investigación
            if self.certainty > 0.5:
                self.before_alert_pos = self.current_pos
                self.investigating = True
                print(f"$ Posición del dron antes de investigar: {self.before_alert_pos}")
                self.investigate()

    def investigate(self):
        # Se mueve a la posición objetivo y señala al guardia si es peligroso
        if self.current_pos != self.target_pos:
            self.move_to(self.target_pos)

        #self.certainty = UnityFunctions.getCertainty()
        if self.certainty > 0.6:
            print(f"$ Dron en posición {self.current_pos} señala peligro al guardia por mensaje")
            enviar_mensaje("guardia", {"take_control": {"certainty": self.certainty, "is_dangerous": self.is_dangerous}})
            print("Mensajes Guardia: ", mensajes["guardia"], end="\n\n")
        else:
            print(f"$ Dron en posición {self.current_pos} no detectó peligro.")
            self.move_to(self.before_alert_pos)

    def move_to(self, position):
        # Lógica de movimiento hacia una posición específica
        # Solo se regresaría a Unity que se mueva a la siguiente posición
        print(f"$ Dron se mueve de {self.current_pos} a {position}")
        self.previous_pos = self.current_pos
        self.current_pos = position
        #UnityFunctions.move_to_next_position(position)

    def revisar_mensajes(self):
        if not self.investigating:
            mensajes_drone = recibir_mensajes("dron")
            for mensaje in mensajes_drone:
                if "receive_alert" in mensaje:
                    alerta = mensaje["receive_alert"]
                    self.receive_alert(alerta["certainty"], alerta["position"])
                
                if "return_to_route" in mensaje:
                    print(f"$ Dron regresa a su ruta en posición {self.before_alert_pos}")
                    self.investigating = False
                    self.move_to(self.before_alert_pos)


class CameraAgent(ap.Agent):
    def setup(self):
        self.owl_entity = Camera()

    def detect_movement(self):
        # Simular detección de maldad? y llamar al dron si es necesario
        """
        result = ComputationalVision.camera_detection()
        certainty = result['certainty']
        if certainty > 0.5:
            position = UnityFunctions.get_camera_position(self)
            enviar_mensaje("dron", {"receive_alert": {"certainty": certainty, "position": position}})
            print(f"- {self}: Aviso al dron sobre una posible amenaza en {position} con certeza {result['certainty']}.")
            print("Mensajes Dron: ", mensajes["dron"], end="\n\n")

            """
        pass

class GuardAgent(ap.Agent):
    def setup(self):
        self.owl_entity = Guard()

    def take_control(self, certainty, danger):
        print(f"* Guardia toma control del dron con certeza {certainty} y peligro {danger}")
        #result = ComputationalVision.detect_danger() # Detectar peligro por visión computacional
        # danger = True if result['danger'] == true else False
        if certainty > 0.7 and danger:
            self.trigger_alarm()
        else:
            self.false_alarm()

    def trigger_alarm(self):
        # Se regresa a Unity que se active la alarma
        #UnityFunctions.trigger_alarm()
        print("* ¡Alarma general! Peligro detectado.")
        enviar_mensaje("dron", {"return_to_route": True})
        print("Mensajes Dron: ", mensajes["dron"], end="\n\n")


    def false_alarm(self):
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
