# Importar módulos
import agentpy as ap
from matplotlib import pyplot as plt
import numpy as np
import matplotlib
import random
import warnings
import matplotlib.animation as animation

# Cambiar el backend de Matplotlib
matplotlib.use('TkAgg')  # O 'Qt5Agg', dependiendo de tu entorno

# Ontología
from owlready2 import *

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

# Definición de Agentes
class RobotAgent(ap.Agent):
    def setup(self):
        self.carrying_box = False  # El robot empieza sin llevar una caja
        self.owl_entity = Robot()  # Conectar con la ontología
        self.direction = (0, 0)  # Dirección actual del robot
        self.target_box = None  # Caja objetivo
        self.target_base = None  # Base objetivo

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
        self.model.grid.remove_agents(caja)
        print(f"{self}: recogió una caja en {self.model.grid.positions[self]}")

    def drop_box(self, base):
        # Dejar la caja en la base si hay espacio
        base.box_count += 1
        self.carrying_box = False
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

def print_grid(model):
    """Imprimir la cuadrícula como una matriz 2D en la terminal."""
    grid_matrix = np.full((model.p.M, model.p.N), '.', dtype=str)
    
    for robot in model.robots:
        x, y = model.grid.positions[robot]
        grid_matrix[x, y] = 'R' if not robot.carrying_box else 'r'
    
    for caja in model.cajas:
        if caja in model.grid.positions:
            x, y = model.grid.positions[caja]
            grid_matrix[x, y] = 'C'
    
    for base in model.bases:
        x, y = model.grid.positions[base]
        grid_matrix[x, y] = str(base.box_count)
    
    print(f"Step: {model.t}")
    for row in grid_matrix:
        print(' '.join(row))
    print()

def simple_animation_plot(model, ax):
    """Gráfico simple para verificar la animación con leyenda"""
    ax.clear()  # Limpia el gráfico antes de dibujar el siguiente cuadro

    # Crear una matriz para el gráfico
    grid_matrix = np.full((model.p.M, model.p.N), np.nan)  
    
    # Colocar los robots, cajas y bases en la matriz
    for robot in model.robots:
        x, y = model.grid.positions[robot]
        grid_matrix[x, y] = 0 if not robot.carrying_box else 0.5  # Robots sin caja (0) y con caja (0.5)
    
    for caja in model.cajas:
        if caja in model.grid.positions:
            x, y = model.grid.positions[caja]
            grid_matrix[x, y] = 1  # Las cajas tienen valor 1
    
    for base in model.bases:
        x, y = model.grid.positions[base]
        grid_matrix[x, y] = 2  # Las bases tienen valor 2

    # Crear un mapa de colores personalizado
    cmap = matplotlib.colors.ListedColormap(['blue', 'lightblue', 'red', 'green'])
    bounds = [0, 0.5, 1, 2, 3]
    norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)

    # Mostrar la cuadrícula sin usar vmin/vmax, ya que norm maneja los límites
    img = ax.imshow(grid_matrix, cmap=cmap, norm=norm)
    
    # Leyenda personalizada
    labels = ['Robot sin caja', 'Robot con caja', 'Caja', 'Base']
    colors = ['blue', 'lightblue', 'red', 'green']
    patches = [matplotlib.patches.Patch(color=colors[i], label=labels[i]) for i in range(len(labels))]

    # Añadir la leyenda al gráfico
    ax.legend(handles=patches, loc='upper left', bbox_to_anchor=(1, 1))
    ax.set_title(f"Step: {model.t}")
    plt.draw()





# Crear y mostrar la animación
fig, ax = plt.subplots()



def update(frame):
    model.step()
    simple_animation_plot(model, ax)
    print_grid(model)  # Imprimir la cuadrícula en la terminal

# Intervalo de 500 milisegundos (0.5 segundos) entre cuadros
# Intervalo de 300 milisegundos para una animación más fluida
ani = animation.FuncAnimation(fig, update, frames=range(parameters['steps']), interval=300, repeat=False)
plt.show()  # Muestra la animación
#plt.close(fig)  # Cerrar la figura para evitar la excepción
