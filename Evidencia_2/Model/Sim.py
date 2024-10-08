from Ontology import Drone, Camera, Guard

import agentpy as ap
import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time

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
        self.previous_pos = None
        self.certainty = 0.0
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
        if self.current_pos in self.model.route:
            index = self.model.route.index(self.current_pos)
            self.previous_pos = self.current_pos
            self.current_pos = self.model.route[(index + 1) % len(self.model.route)]
            print(f"$ Dron se mueve a {self.current_pos}")
        if self.current_pos == self.model.start_position:
            self.end_route()

    def end_route(self):
        print(f"$ Dron terminó su ruta")
        print(f"$ Dron desciende en {self.current_pos}")
        print(f"$ Dron se espera por 10 segundos")
        self.flighting = False
        self.finish_route = False   
        time.sleep(10)

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
        
        # Terminó de investigar el dron
        self.investigating = False

    def move_to(self, position):
        print(f"$ Dron se mueve de {self.current_pos} a {position}")
        self.previous_pos = self.current_pos
        self.current_pos = position

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
        if random.random() > 0.7:
            certainty = random.uniform(0.5, 0.9)
            position = random.choice(self.model.route)
            print(f"- Cámara {self} detecta movimiento en {position} con certeza {certainty}")
            enviar_mensaje("dron", {"receive_alert": {"certainty": certainty, "position": position}})
            print("Mensajes Dron: ", mensajes["dron"], end="\n\n")

class GuardAgent(ap.Agent):
    def setup(self):
        self.owl_entity = Guard()

    def take_control(self, certainty, danger):
        print(f"* Guardia toma control del dron con certeza {certainty} y peligro {danger}")
        danger = True if random.random() > 0.8 else False
        if certainty > 0.7 and danger:
            self.trigger_alarm()
        else:
            self.false_alarm()

    def trigger_alarm(self):
        print("* ¡Alarma general! Peligro detectado. Esperando por 5 segundos.")
        enviar_mensaje("dron", {"return_to_route": True})
        print("Mensajes Dron: ", mensajes["dron"], end="\n\n")
        time.sleep(5)

    def false_alarm(self):
        print("* Falsa alarma. El dron vuelve a su ruta.")
        enviar_mensaje("dron", {"return_to_route": True})
        print("Mensajes Dron: ", mensajes["dron"], end="\n\n")

    def revisar_mensajes(self):
        mensajes_guardia = recibir_mensajes("guardia")
        for mensaje in mensajes_guardia:
            if "take_control" in mensaje:
                control = mensaje["take_control"]
                self.take_control(control["certainty"], control["is_dangerous"])

# Modelo de seguridad
class SecurityModel(ap.Model):
    def setup(self):
        self.drone = DroneAgent(self)
        self.cameras = ap.AgentList(self, 3, CameraAgent)
        self.guard = GuardAgent(self)

        # Ruta predefinida para el dron
        self.start_position = (0, 0)
        self.route = [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2), (2, 1), (2, 0), (1, 0), (0, 0)]
        self.steps = 0

    def step(self):
        self.steps += 1
        self.drone.start_patrol()
        self.drone.revisar_mensajes()
        self.guard.revisar_mensajes()
        for camera in self.cameras:
            camera.detect_movement()
        print(f"---------------Step {self.steps}----------------")

# Parámetros de la simulación
parameters = {
    'steps': 50,
}

# Ejecutar la simulación
model = SecurityModel(parameters)
model.setup()

# Visualización
fig, ax = plt.subplots()
drone_path, = ax.plot([], [], 'bo-', label="Drone Path")
current_drone_pos, = ax.plot([], [], 'ro', label="Current Drone Position")
camera_pos, = ax.plot([], [], 'rs', label="Cameras")
guard_pos, = ax.plot([], [], 'g^', label="Guard")
route_path, = ax.plot([], [], 'k--', label="Drone Route")

ax.set_xlim(-1, 4)
ax.set_ylim(-1, 4)

def update(frame):
    model.step()

    # Actualizar la posición del dron
    drone_positions = [model.drone.current_pos]
    drone_path.set_data(*zip(*[model.drone.previous_pos, model.drone.current_pos] if model.drone.previous_pos else [(0, 0)]))
    current_drone_pos.set_data(*zip(*drone_positions))

    # Actualizar la ruta del dron
    route_positions = model.route
    route_path.set_data(*zip(*route_positions))

    # Actualizar posiciones de las cámaras
    cam_positions = [(1, 1), (0.5, 0.5), (1.5, 1), (0.5, 1.5)]
    cx, cy = zip(*cam_positions)
    camera_pos.set_data(cx, cy)

    # Posición del guardia
    guard_pos.set_data([0], [0])

    if frame == parameters['steps'] - 1:
        print("Se han agotado todos los pasos.")
        plt.close(fig)  

    return drone_path, current_drone_pos, camera_pos, guard_pos, route_path


# Animación
ani = animation.FuncAnimation(fig, update, frames=range(parameters['steps']), interval=500, repeat=False)
plt.legend()
plt.show()
