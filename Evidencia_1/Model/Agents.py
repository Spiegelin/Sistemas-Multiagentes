import agentpy as ap
import random
from Ontology import Robot, Caja, Base

class RobotAgent(ap.Agent):
    def setup(self):
        self.carrying_box = False
        self.owl_entity = Robot()
        self.direction = (0, 0)
        self.target_box = None
        self.target_base = None

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
        self.model.grid.remove_agents(caja)
        print(f"{self}: recogió una caja en {self.model.grid.positions[self]}")

    def drop_box(self, base):
        base.box_count += 1
        self.carrying_box = False
        print(f"{self}: dejó una caja en la base en {self.model.grid.positions[base]}")

    def move_random(self):
        self.direction = random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])
        self.forward()

    def forward(self):
        if not self.check_collision():
            self.model.grid.move_by(self, self.direction)

    def check_collision(self):
        vecinos = self.model.grid.neighbors(self, distance=1)
        for robot in vecinos:
            if isinstance(robot, RobotAgent):
                if self.model.grid.positions[robot] == self.model.grid.positions[self]:
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
