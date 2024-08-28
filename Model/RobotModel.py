import agentpy as ap
from matplotlib import pyplot as plt
import numpy as np
import matplotlib
import matplotlib.animation as animation
import matplotlib.patches as patches
import time
from Agents import RobotAgent, CajaAgent, BaseAgent

# Cambiar el backend de Matplotlib
matplotlib.use('TkAgg') 

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

        self.start_time = time.time()  # Tiempo de inicio del modelo

    def step(self):
        self.robots.step()
        self.cajas.step()
        self.t += 1  # Incrementar el tiempo del modelo por cada paso

    def all_bases_full(self):
        """Verifica si todas las bases tienen 5 cajas."""
        return all(base.box_count >= 5 for base in self.bases)


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
            grid_matrix[x, y] = 1  
    
    for base in model.bases:
        x, y = model.grid.positions[base]
        grid_matrix[x, y] = 2 

    # Mapa de colores (versión Saydrak)
    cmap = matplotlib.colors.ListedColormap(['blue', 'lightblue', 'red', 'green'])
    bounds = [0, 0.5, 1, 2, 3]
    norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)

    img = ax.imshow(grid_matrix, cmap=cmap, norm=norm)
    
    # Leyenda
    labels = ['Robot sin caja', 'Robot con caja', 'Caja', 'Base']
    colors = ['blue', 'lightblue', 'red', 'green']
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

# Crear y mostrar la animación
fig, ax = plt.subplots()

def update(frame):
    model.step()
    simple_animation_plot(model, ax)
    print_grid(model)  # Imprimir la cuadrícula en la terminal

    if model.all_bases_full():
        print("Todas las bases tienen 5 cajas. El programa ha terminado.")
        print(f"Tiempo total: {time.time() - model.start_time:.2f} segundos")
        print(f"Pasos totales: {model.t-1}")
        plt.close(fig)  # Cerrar la figura para terminar la animación

    # Verificar si se han agotado los pasos
    if frame == parameters['steps'] - 1:
        print("Se han agotado todos los pasos. No todas las bases están llenas de cajas.")
        print(f"Tiempo total: {time.time() - model.start_time:.2f} segundos")
        print(f"Pasos totales: {model.t-1}")
        plt.close(fig)  


ani = animation.FuncAnimation(fig, update, frames=range(parameters['steps']), interval=300, repeat=False)
plt.show()
