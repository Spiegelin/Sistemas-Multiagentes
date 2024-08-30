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
matplotlib.use('TkAgg')

# Cargar o crear la ontología
onto = get_ontology("file://onto.owl")
with onto:
    class Entity(Thing):
        pass

    class Dron(Entity):
        pass

    class Camara(Entity):
        pass

    class Guardia(Entity):
        pass

    class has_position(DataProperty):
        domain = [Entity]
        range = [str]

class DronAgent(ap.Agent):
    def setup(self):
        self.investigating = False
        self.owl_entity = Dron()
        self.route = [(0,0), (1,1), (2,2), (3,3)]  # Ruta predefinida
        self.current_position = 0
        self.previous_position = None

    def step(self):
        if self.investigating:
            self.investigar()
        else:
            self.patrullar()

    def patrullar(self):
        if self.current_position < len(self.route):
            next_pos = self.route[self.current_position]
            self.move_to(next_pos)
            self.current_position += 1
        else:
            self.aterrizar()
            self.current_position = 0
            self.model.schedule_after(self, self.despegar, delay=10)

    def aterrizar(self):
        print(f"{self}: Aterrizando en {self.model.grid.positions[self]}")

    def despegar(self):
        print(f"{self}: Despegando y comenzando la patrulla de nuevo.")
        self.patrullar()

    def investigar(self):
        result = computationalVision()
        if result['certainty'] > 0.6:
            self.notify_guard(result)
        else:
            self.return_to_patrol()

    def notify_guard(self, result):
        guard = self.model.guard
        guard.take_control(self, result)
        self.investigating = False

    def return_to_patrol(self):
        self.move_to(self.previous_position)
        self.investigating = False
        print(f"{self}: Regresando a patrullar después de una falsa alarma.")

    def move_to(self, position):
        self.model.grid.move_to(self, position)
        print(f"{self}: Moviéndose a {position}")

class CamaraAgent(ap.Agent):
    def step(self):
        result = computationalVision()
        if result['certainty'] > 0.5:
            dron = self.model.dron
            dron.investigating = True
            dron.previous_position = self.model.grid.positions[dron]
            dron.move_to(self.model.grid.positions[self])
            print(f"{self}: Aviso al dron sobre una posible amenaza.")

class GuardiaAgent(ap.Agent):
    def setup(self):
        self.owl_entity = Guardia()

    def take_control(self, dron, result):
        print(f"{self}: Tomando control del dron para investigar.")
        if result['certainty'] > 0.7 and result['isDangerous']:
            self.raise_alarm()
        else:
            self.false_alarm()
            dron.return_to_patrol()

    def raise_alarm(self):
        print(f"{self}: Alarma general activada. Peligro detectado.")

    def false_alarm(self):
        print(f"{self}: Falsa alarma. No se detectó ningún peligro.")

# Función simulada de visión computacional
def computationalVision():
    return {
        'isDangerous': random.choice([True, False]),
        'certainty': random.uniform(0.4, 0.8),
        'object': random.choice(['fight', 'suspicious_movement', 'nothing'])
    }

# Definición del Modelo
class SurveillanceModel(ap.Model):
    def setup(self):
        self.dron = DronAgent(self)
        self.camaras = ap.AgentList(self, 3, CamaraAgent)
        self.guard = GuardiaAgent(self)

        self.grid = ap.Grid(self, (10, 10), track_empty=True)
        self.grid.add_agents([self.dron], [(0, 0)])
        self.grid.add_agents(self.camaras, positions=[(2, 2), (5, 5), (7, 7)])

    def step(self):
        self.dron.step()
        self.camaras.step()

# Actualizar el servidor WebSocket
async def handler(websocket, path):
    model = SurveillanceModel({})
    model.setup()
    
    while True:
        model.step()

        # Recolectar y enviar datos a Unity
        data = {
            'dron_position': model.grid.positions[model.dron],
            'camaras': [{'position': model.grid.positions[c]} for c in model.camaras],
            'guard_control': False
        }
        
        await websocket.send(json.dumps(data))
        await asyncio.sleep(1)

start_server = websockets.serve(handler, 'localhost', 8765)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
