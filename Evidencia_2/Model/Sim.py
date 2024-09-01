from Ontology import Drone, Camera, Guard

# Simulación del funcionamiento del modelo
import agentpy as ap
import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time

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

    def start_patrol(self):
        if self.current_pos == self.model.start_position and not self.flighting:
            print(f"$ Dron despega en {self.current_pos}")
            self.patrolling = True
            self.flighting = True
        elif self.current_pos == self.model.start_position and self.previous_pos == self.model.route[-2] and self.flighting and not self.is_dangerous and self.finish_route: 
            print(f"$ Dron desciende en {self.current_pos}")
            print(f"$ Dron se espera por 10 segundos")
            time.sleep(10)
        self.move_along_route()

    def move_along_route(self):
        # Simula un movimiento circular a lo largo de una ruta predefinida
        if self.current_pos in self.model.route:
            index = self.model.route.index(self.current_pos)
            self.previous_pos = self.current_pos
            self.current_pos = self.model.route[(index + 1) % len(self.model.route)]

        if self.current_pos == self.model.start_position:
            self.finish_route = True
            print(f"$ Dron terminó en su ruta")

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
        print(f"$ Dron se mueve de {self.current_pos} a {position}")
        self.previous_pos = self.current_pos
        self.current_pos = position


class CameraAgent(ap.Agent):
    def setup(self):
        self.owl_entity = Camera()
        #self.id = self.id

    def detect_movement(self):
        # Simular detección de movimiento
        if random.random() > 0.7:  # Simulación aleatoria de movimiento detectado
            certainty = random.uniform(0.5, 0.9)
            position = random.choice(self.model.route)
            #position = UnityFunctions.get_camera_position(self.id)
            print(f"- Cámara {self} detecta movimiento en {position} con certeza {certainty}")
            self.model.drone.receive_alert(certainty, position)

class GuardAgent(ap.Agent):
    def setup(self):
        self.owl_entity = Guard()

    def take_control(self, drone, certainty, danger):
        print(f"* Guardia toma control del dron con certeza {certainty} y peligro {danger}")
        danger = True if random.random() > 0.8 else False  # Simulación aleatoria de peligro
        if certainty > 0.7 and danger:
            self.trigger_alarm()
        else:
            self.false_alarm(drone)

    def trigger_alarm(self):
        print("* ¡Alarma general! Peligro detectado. Esperando por 5 segundos.")
        time.sleep(5)

    def false_alarm(self, drone):
        print("* Falsa alarma. El dron vuelve a su ruta.")
        drone.move_to(drone.previous_pos)

# Modelo de seguridad
class SecurityModel(ap.Model):
    def setup(self):
        self.drone = DroneAgent(self)
        self.cameras = ap.AgentList(self, 3, CameraAgent)
        self.guard = GuardAgent(self)

        # Ruta predefinida para el dron
        self.start_position = (0, 0)
        self.route = [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2), (2, 1), (2, 0), (1, 0), (0, 0)]  # Ejemplo de ruta en bucle

    def step(self):
        self.drone.start_patrol()
        for camera in self.cameras:
            camera.detect_movement()

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
    drone_positions = [model.drone.current_pos]  # La posición actual del dron
    drone_path.set_data(*zip(*[model.drone.previous_pos, model.drone.current_pos] if model.drone.previous_pos else [(0, 0)]))
    current_drone_pos.set_data(*zip(*drone_positions))

    # Actualizar la ruta del dron (línea discontinua)
    route_positions = model.route
    route_path.set_data(*zip(*route_positions))

    # Actualizar posiciones de las cámaras
    cam_positions = [(1, 1), (0.5, 0.5), (1.5, 1), (0.5, 1.5)]
    cx, cy = zip(*cam_positions)
    camera_pos.set_data(cx, cy)

    # Posición del guardia (no se mueve en este ejemplo)
    guard_pos.set_data([0], [0])

    # Steps
    #ax.set_title(f"Step: {frame}")
    # Verificar si se han agotado los pasos
    if frame == parameters['steps'] - 1:
        print("Se han agotado todos los pasos. No todas las bases están llenas de cajas.")
        print(f"Pasos totales: {model.t-1}")
        plt.close(fig)  

    return drone_path, current_drone_pos, camera_pos, guard_pos, route_path


# Animación
ani = animation.FuncAnimation(fig, update, frames=range(parameters['steps']), interval=500, repeat=False)
plt.legend()
plt.show()
