import agentpy as ap
from matplotlib import pyplot as plt
import numpy as np
import matplotlib
import matplotlib.animation as animation
import matplotlib.patches as patches
import time
import random
from AgentsObstacle import RobotAgent, CajaAgent, BaseAgent

# Cambiar el backend de Matplotlib
matplotlib.use('TkAgg') 

# Definición del Ambiente
class WarehouseModel(ap.Model):
    def setup(self):
        self.robots = ap.AgentList(self, self.p.robots, RobotAgent)
        self.cajas = ap.AgentList(self, self.p.cajas, CajaAgent)
        self.bases = ap.AgentList(self, self.p.bases, BaseAgent)

        self.grid = ap.Grid(self, (self.p.M, self.p.N), track_empty=True)

        # Definir obstáculos para crear pasillos verticales
        self.obstacles = set()
        for x in range(self.p.M):
            for y in range(self.p.N):
                # Crear obstáculos excepto en las columnas que corresponden a los pasillos y las esquinas
                if y not in [2, 4, 6, 8] or x in [0, self.p.M-1]: 
                    continue
                self.obstacles.add((x, y))


        # No agregar agentes en posiciones de obstáculos
        empty_positions = list(set(self.grid.empty).difference(self.obstacles))

        self.grid.add_agents(self.robots, positions=random.sample(empty_positions, len(self.robots)))
        self.grid.add_agents(self.cajas, positions=random.sample(empty_positions, len(self.cajas)))
        self.grid.add_agents(self.bases, positions=random.sample(empty_positions, len(self.bases)))

        self.start_time = time.time()  #

    def step(self):
        self.robots.step()
        self.cajas.step()
        self.t += 1  # Incrementar el tiempo del modelo

    def all_bases_full(self):
        """Verifica si todas las bases tienen 5 cajas."""
        return all(base.box_count >= 5 for base in self.bases)


def print_grid(model):
    """Imprimir la cuadrícula como una matriz 2D en la terminal."""
    grid_matrix = np.full((model.p.M, model.p.N), '.', dtype=str)
    
    # Establecer los robots
    for robot in model.robots:
        x, y = model.grid.positions[robot]
        grid_matrix[x, y] = 'R' if not robot.carrying_box else 'r'
    
    # Establecer las cajas
    for caja in model.cajas:
        if caja in model.grid.positions:
            x, y = model.grid.positions[caja]
            grid_matrix[x, y] = 'C'
    
    # Establecer las bases
    for base in model.bases:
        x, y = model.grid.positions[base]
        grid_matrix[x, y] = str(base.box_count)
    
    # Establecer los obstáculos
    for (x, y) in model.obstacles:
        grid_matrix[x, y] = 'X'
    
    # Imprimir el estado actual de la cuadrícula
    print(f"Step: {model.t}")
    for row in grid_matrix:
        print(' '.join(row))
    print()


def simple_animation_plot(model, ax):
    """Gráfico simple para verificar la animación con leyenda"""
    ax.clear()  # Limpia el gráfico antes de dibujar el siguiente cuadro

    # Crear una matriz para el gráfico
    grid_matrix = np.full((model.p.M, model.p.N), np.nan)  
    
    # Colocar los robots, cajas, bases y obstáculos en la matriz
    for robot in model.robots:
        x, y = model.grid.positions[robot]
        grid_matrix[x, y] = 0 if not robot.carrying_box else 0.5  # Robots sin caja (0) y con caja (0.5)
    
    for caja in model.cajas:
        if caja in model.grid.positions:
            x, y = model.grid.positions[caja]
            grid_matrix[x, y] = 1 
    
    for base in model.bases:
        x, y = model.grid.positions[base]
        grid_matrix[x, y] = 2 

    # Añadir los obstáculos a la matriz
    for (x, y) in model.obstacles:
        grid_matrix[x, y] = 3 

    # Mapa de colores
    cmap = matplotlib.colors.ListedColormap(['blue', 'lightblue', 'red', 'green', 'black'])
    bounds = [0, 0.5, 1, 2, 3, 4]
    norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)

    img = ax.imshow(grid_matrix, cmap=cmap, norm=norm)
    
    # Leyenda
    labels = ['Robot sin caja', 'Robot con caja', 'Caja', 'Base', 'Obstáculo']
    colors = ['blue', 'lightblue', 'red', 'green', 'black']
    patches = [matplotlib.patches.Patch(color=colors[i], label=labels[i]) for i in range(len(labels))]

    ax.legend(handles=patches, loc='upper left', bbox_to_anchor=(1, 1))
    
    # Tiempo transcurrido
    elapsed_time = time.time() - model.start_time
    ax.set_title(f"Step: {model.t}, Time: {elapsed_time:.2f}s")
    plt.draw()


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

fig, ax = plt.subplots()

def update(frame):
    model.step()
    simple_animation_plot(model, ax)
    print_grid(model)  # Imprimir la cuadrícula en la terminal

    # Verificar si todas las bases están llenas de cajas
    if model.all_bases_full():
        print("Todas las bases tienen 5 cajas. El programa ha terminado.")
        print(f"Tiempo total: {time.time() - model.start_time:.2f} segundos")
        print(f"Pasos totales: {model.t-1}")
        plt.close(fig)  # Cerrar la figura para terminar la animación
        return

    # Verificar si se han agotado los pasos
    if frame == parameters['steps'] - 1:
        print("Se han agotado todos los pasos. No todas las bases están llenas de cajas.")
        print(f"Tiempo total: {time.time() - model.start_time:.2f} segundos")
        print(f"Pasos totales: {model.t-1}")
        plt.close(fig)  # Cerrar la figura para terminar la animación

ani = animation.FuncAnimation(fig, update, frames=range(parameters['steps']), interval=300, repeat=False)
plt.show() 
