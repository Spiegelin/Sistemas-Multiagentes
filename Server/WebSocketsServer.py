import asyncio
import websockets
import json
import agentpy as ap
from matplotlib import pyplot as plt
import numpy as np
import matplotlib
import matplotlib.animation as animation
import random
import time

# En postman ws://localhost:8765

# Ontología
from owlready2 import *

# Cambiar el backend de Matplotlib
matplotlib.use('TkAgg')  # O 'Qt5Agg', dependiendo de tu entorno

onto = get_ontology("file://onto.owl")
with onto:
    class Entity(Thing):
        pass

    class Robot(Entity):
        pass

    class Caja(Entity):
        pass

    class Base(Entity):
        pass

    class has_place(ObjectProperty):
        domain = [Entity]
        range = [Base]

    class has_position(DataProperty):
        domain = [Entity]
        range = [str]



class RobotAgent(ap.Agent):
    def setup(self):
        self.carrying_box = False  # El robot empieza sin llevar una caja
        self.owl_entity = Robot()  # Conectar con la ontología
        self.direction = (0, 0)  # Dirección actual del robot
        self.target_box = None  # Caja objetivo
        self.target_base = None  # Base objetivo
        self.caja_carrying = None  # Referencia a la caja que está llevando

    def step(self):
        # El robot primero busca una caja si no lleva una
        if not self.carrying_box:
            self.buscar_caja()
        else:
            self.buscar_base()

    def buscar_caja(self):
        # Revisa los 4 lados (N, S, E, O) para encontrar una caja
        posiciones_vecinas = self.model.grid.neighbors(self, distance=1)
        for vecino in posiciones_vecinas:
            if isinstance(vecino, CajaAgent):
                # Si encuentra una caja, se mueve hacia ella
                self.move_towards(vecino)
                self.pick_box(vecino)
                return
        # Si no encuentra una caja, se mueve aleatoriamente
        self.move_random()

    def buscar_base(self):
        # Revisa los 4 lados (N, S, E, O) para encontrar una base
        posiciones_vecinas = self.model.grid.neighbors(self, distance=1)
        for vecino in posiciones_vecinas:
            if isinstance(vecino, BaseAgent) and vecino.box_count < 5:
                # Si encuentra una base disponible, se mueve hacia ella
                self.move_towards(vecino)
                self.drop_box(vecino)
                return
        # Si no encuentra una base, se mueve aleatoriamente
        self.move_random()

    def move_towards(self, target):
        # Mueve el robot hacia un objetivo (caja o base)
        target_pos = self.model.grid.positions[target]
        self_pos = self.model.grid.positions[self]
        movement = (target_pos[0] - self_pos[0], target_pos[1] - self_pos[1])
        self.direction = movement
        self.forward()

    def pick_box(self, caja):
        # Recoger la caja y eliminarla del grid
        self.carrying_box = True
        self.caja_carrying = caja  # Guardar referencia de la caja
        self.model.grid.remove_agents(caja)
        print(f"{self}: recogió una caja en {self.model.grid.positions[self]}")

    def drop_box(self, base):
        # Dejar la caja en la base si hay espacio
        base.box_count += 1
        self.carrying_box = False
        self.caja_carrying = None  # Dejar de llevar la caja
        print(f"{self}: dejó una caja en la base en {self.model.grid.positions[base]}")

    def move_random(self):
        # Movimiento aleatorio si no hay cajas ni bases cercanas
        self.direction = random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])
        self.forward()

    def forward(self):
        # Mueve el robot en la dirección especificada, revisando colisiones
        if not self.check_collision():
            self.model.grid.move_by(self, self.direction)

    def check_collision(self):
        # Verificar colisiones con otros robots
        vecinos = self.model.grid.neighbors(self, distance=1)
        for robot in vecinos:
            if isinstance(robot, RobotAgent):
                if self.model.grid.positions[robot] == self.model.grid.positions[self]:
                    if self.carrying_box and not robot.carrying_box:
                        return False  # El robot con caja tiene prioridad
                    elif not self.carrying_box and robot.carrying_box:
                        return True  # El otro robot tiene prioridad
                    else:
                        return random.choice([True, False])  # Resolución aleatoria
        return False

class CajaAgent(ap.Agent):
    def setup(self):
        self.pos = None

    def step(self):
        # Asegurarnos de que la caja esté en la cuadrícula antes de intentar acceder a su posición
        if self.pos is None:
            if self in self.model.grid.positions:
                self.pos = self.model.grid.positions[self]

class BaseAgent(ap.Agent):
    def setup(self):
        self.box_count = 0  # Contador de cajas en la base
        self.pos = None  # Posición inicial de la base
        self.owl_entity = Base()  # Conectar con la ontología

    def step(self):
        if self.pos is None:
            self.pos = self.model.grid.positions[self]
            self.owl_entity.has_position = str(self.pos)

# Definición del Ambiente
class WarehouseModel(ap.Model):
    def setup(self):
        self.robots = ap.AgentList(self, self.p.robots, RobotAgent)
        self.cajas = ap.AgentList(self, self.p.cajas, CajaAgent)
        self.bases = ap.AgentList(self, self.p.bases, BaseAgent)

        self.grid = ap.Grid(self, (self.p.M, self.p.N), track_empty=True)

        self.grid.add_agents(self.robots, random=True, empty=True)
        self.grid.add_agents(self.cajas, random=True, empty=True)
        self.grid.add_agents(self.bases, random=True, empty=True)

    def step(self):
        self.robots.step()
        self.cajas.step()
        self.t += 1  # Incrementar el tiempo del modelo
# Parámetros del modelo
parameters = {
    'M': 10,
    'N': 10,
    'robots': 5,
    'cajas': 10,
    'bases': 2,
    'steps': 100,
}

# Crear modelo
model = WarehouseModel(parameters)
model.setup()  # Asegurar que se llame a la configuración inicial

# Registrar el tiempo de inicio
start_time = time.time()

async def handler(websocket, path):
    while True:
        # Avanzar un paso en el modelo
        model.step()

        # Calcular la duración del programa
        duration = time.time() - start_time

        # Preparar los datos para enviar
        data = {
            'robots': [],
            'cajas': [],
            'bases': [],
            'duration': duration,
            'steps': model.t,
        }

        for robot in model.robots:
            x, y = model.grid.positions[robot]
            data['robots'].append({'x': (x*6)+3, 'y': -(y*6)+3, 'carrying_box': robot.carrying_box})

            # Si el robot lleva una caja, enviar la posición de la caja
            if robot.carrying_box and robot.caja_carrying is not None:
                data['cajas'].append({'x': (x*6)+3, 'y': -(y*6)+3})  # La caja sigue la posición del robot

        for caja in model.cajas:
            if caja in model.grid.positions:
                x, y = model.grid.positions[caja]
                data['cajas'].append({'x': (x*6)+3, 'y': -(y*6)+3})

        for base in model.bases:
            x, y = model.grid.positions[base]
            data['bases'].append({'x': (x*6)+3, 'y': -(y*6)+3, 'box_count': base.box_count})

        # Enviar los datos en formato JSON
        await websocket.send(json.dumps(data))

        # Esperar un poco antes del siguiente envío
        await asyncio.sleep(1)

start_server = websockets.serve(handler, 'localhost', 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()