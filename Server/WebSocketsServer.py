import asyncio
import websockets
import json
import agentpy as ap
from matplotlib import pyplot as plt
import numpy as np
import matplotlib
import random
import time

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
        self.carrying_box = False
        self.owl_entity = Robot()
        self.direction = (0, 0)
        self.target_box = None
        self.target_base = None
        self.caja_carrying = None

    def step(self):
        if not self.carrying_box:
            self.buscar_caja()
        else:
            self.buscar_base()

    def buscar_caja(self):
        posiciones_vecinas = self.model.grid.neighbors(self, distance=1)
        for vecino in posiciones_vecinas:
            if isinstance(vecino, CajaAgent):
                self.move_towards(vecino)
                self.pick_box(vecino)
                return
        self.move_random()

    def buscar_base(self):
        posiciones_vecinas = self.model.grid.neighbors(self, distance=1)
        for vecino in posiciones_vecinas:
            if isinstance(vecino, BaseAgent) and vecino.box_count < 5:
                self.move_towards(vecino)
                self.drop_box(vecino)
                return
        self.move_random()

    def move_towards(self, target):
        target_pos = self.model.grid.positions[target]
        self_pos = self.model.grid.positions[self]
        movement = (target_pos[0] - self_pos[0], target_pos[1] - self_pos[1])
        self.direction = movement
        self.forward()

    def pick_box(self, caja):
        self.carrying_box = True
        self.caja_carrying = caja
        self.model.grid.remove_agents(caja)
        print(f"{self}: recogió una caja en {self.model.grid.positions[self]}")

    def drop_box(self, base):
        base.box_count += 1
        self.carrying_box = False
        self.caja_carrying.pos = self.model.grid.positions[self]
        self.caja_carrying = None
        print(f"{self}: dejó una caja en la base en {self.model.grid.positions[base]}")

    def move_random(self):
        self.direction = random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])
        self.forward()

    def forward(self):
        next_pos = tuple(np.add(self.model.grid.positions[self], self.direction))
        if not self.check_collision(next_pos) and next_pos not in self.model.obstacles:
            self.model.grid.move_by(self, self.direction)

    def check_collision(self, next_pos):
        vecinos = self.model.grid.neighbors(self, distance=1)
        for robot in vecinos:
            if isinstance(robot, RobotAgent):
                if self.model.grid.positions[robot] == next_pos:
                    if self.carrying_box and not robot.carrying_box:
                        return False
                    elif not self.carrying_box and robot.carrying_box:
                        return True
                    else:
                        return random.choice([True, False])
        return False

class CajaAgent(ap.Agent):
    def setup(self):
        self.pos = None

    def step(self):
        if self.pos is None:
            if self in self.model.grid.positions:
                self.pos = self.model.grid.positions[self]

class BaseAgent(ap.Agent):
    def setup(self):
        self.box_count = 0
        self.pos = None
        self.owl_entity = Base()

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

        # Definir obstáculos para crear pasillos verticales tipo supermercado
        self.obstacles = set()
        for x in range(self.p.M):
            for y in range(self.p.N):
                # Crear obstáculos excepto en las columnas que corresponden a los pasillos y las esquinas
                if y not in [2, 4, 6, 8] or x in [0, self.p.M-1]:  # Esquinas abiertas
                    continue
                self.obstacles.add((x, y))

        # No agregar agentes en posiciones de obstáculos
        empty_positions = list(set(self.grid.empty).difference(self.obstacles))

        self.grid.add_agents(self.robots, positions=random.sample(empty_positions, len(self.robots)))
        self.grid.add_agents(self.cajas, positions=random.sample(empty_positions, len(self.cajas)))
        self.grid.add_agents(self.bases, positions=random.sample(empty_positions, len(self.bases)))

    def step(self):
        self.robots.step()
        self.cajas.step()
        self.t += 1

# Parámetros del modelo
parameters = {
    'M': 10,
    'N': 10,
    'robots': 5,
    'cajas': 10,
    'bases': 2,
    'steps': 500,
}

# Crear modelo
model = WarehouseModel(parameters)
model.setup()

# Registrar el tiempo de inicio
start_time = time.time()

def todas_bases_completas(modelo):
    """ Verifica si todas las bases han alcanzado su capacidad máxima. """
    for base in modelo.bases:
        if base.box_count < 5:  # Suponiendo que la capacidad máxima es 5
            return False
    return True


async def handler(websocket, path):
    steps = 0
    while True:
        model.step()
        steps += 1

        duration = time.time() - start_time

        data = {
            'robots': [],
            'cajas': [],
            'bases': [],
            'duration': duration,
            'steps': model.t,
            'complete': False  # Por defecto, no está completo
        }

        for robot in model.robots:
            x, y = model.grid.positions[robot]
            robot_data = {
                'id': robot.id,
                'x': (x * 6) + 3,
                'y': -(y * 6) + 3,
                'carrying_box': robot.carrying_box
            }

            if robot.carrying_box and robot.caja_carrying is not None:
                robot_data['box_id'] = robot.caja_carrying.id

                data['cajas'].append({
                    'id': robot.caja_carrying.id,
                    'x': (x * 6) + 3,
                    'y': -(y * 6) + 3
                })

            data['robots'].append(robot_data)

        for caja in model.cajas:
            if caja in model.grid.positions and caja not in [robot.caja_carrying for robot in model.robots]:
                x, y = model.grid.positions[caja]
                data['cajas'].append({'id': caja.id, 'x': (x * 6) + 3, 'y': -(y * 6) + 3})
                
            elif caja not in model.grid.positions and caja.pos is not None:
                x, y = caja.pos
                data['cajas'].append({'x': (x*6) + 3, 'y': -(y * 6) + 3})

        for base in model.bases:
            x, y = model.grid.positions[base]
            data['bases'].append({'id': base.id, 'x': (x * 6) + 3, 'y': -(y * 6) + 3, 'box_count': base.box_count})

        # Verificar si todas las bases están completas
        if todas_bases_completas(model):
            data['complete'] = True
            print("Todas las bases están completas. Enviando mensaje final.")
            # Enviar mensaje final con tiempo total, pasos totales y estado de completado
            final_data = {
                'type': 'final',
                'duration': time.time() - start_time,
                'steps': model.t,
                'complete': True
            }
            await websocket.send(json.dumps(final_data))
            break

        # Verificar si se han agotado los pasos
        if steps >= parameters['steps']:
            print("Se han agotado todos los pasos. No todas las bases están llenas de cajas.")
            # Enviar mensaje final con tiempo total, pasos totales y estado de completado
            final_data = {
                'type': 'final',
                'duration': time.time() - start_time,
                'steps': model.t,
                'complete': False
            }
            await websocket.send(json.dumps(final_data))
            break

        await websocket.send(json.dumps(data))
        await asyncio.sleep(1)
    
    # Cerrar la conexión del WebSocket
    await websocket.close()

start_server = websockets.serve(handler, 'localhost', 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()