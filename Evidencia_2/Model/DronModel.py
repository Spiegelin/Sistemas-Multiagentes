import agentpy as ap
from Agents import DroneAgent, CameraAgent, GuardAgent
#from UnityFunctions import get_start_position, get_route

class SecurityModel(ap.Model):
    def setup(self):
        self.drone = DroneAgent(self)
        self.cameras = ap.AgentList(self, 3, CameraAgent)
        self.guard = GuardAgent(self)

        # Ruta predefinida para el dron, la manda unity
        self.start_position = (0, 0)
        #self.start_position = get_start_position() # Se manda a llamar a la función que obtiene la posición de inicio
        self.route = [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2), (2, 1), (2, 0), (1, 0), (0, 0)]  # Ejemplo de ruta en bucle
        #self.route = get_route()
        self.steps = 0

    def step(self):
        self.steps += 1
        self.drone.start_patrol()
        self.drone.revisar_mensajes()
        self.guard.revisar_mensajes()
        for camera in self.cameras:
            camera.detect_movement()

        print(f"---------------Step {self.steps}----------------")