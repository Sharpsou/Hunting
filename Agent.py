from random import *
from math import *
import pandas as pd
from Brain import *

class Agent:
    def __init__(self, x, y, env):
        self.position_x = x
        self.position_y = y
        self.direction_x = randint(-1, 1)
        self.direction_y = randint(-1, 1)
        self.detection_range = 0
        self.resolution = 0

    def next_movement(self, env):
        x = self.position_x + self.direction_x
        y = self.position_y + self.direction_y
        if env.possibles_movements(x, y) and not (self.direction_x == 0 and self.direction_y == 0):
            self.position_x = x
            self.position_y = y
        else:
            self.next_direction(env)
        self.get_radar(env)

    def next_direction(self, env):
        self.direction_x = randint(-1, 1)  # random move because no algo implemented
        self.direction_y = randint(-1, 1)

    def get_radar(self, env):
        neighbour = self.get_neighbour(env)
        if not neighbour.empty:
            apparent_neighbour = neighbour.groupby(['sector']).min()
        else:
            apparent_neighbour = pd.DataFrame([[]])
        self.radar = apparent_neighbour
        # self.radar = neighbour.merge(radar_init, on='sector', how='right')

    def manage_close_wall(self, apparent_neighbour):
        # work in progress
        return True

    def get_neighbour(self, env):
        neighbour = []
        min_range = -self.detection_range
        max_range = self.detection_range + 1
        for y in range(min_range, max_range):
            for x in range(min_range, max_range):
                if (y != 0 or x != 0) and not env.possibles_movements(self.position_x + x, self.position_y + y):
                    neighbour.append(self.get_coord(x, y))
        neighbour = pd.DataFrame(neighbour)
        if not neighbour.empty:
            neighbour.columns = ['layer', 'sector', 'x', 'y']
        return neighbour

    def get_coord(self, x, y):
        layer = max(abs(x), abs(y))
        distance = sqrt(y * y + x * x)
        if x != 0:
            orientation = (x / abs(x))
        else:
            orientation = 1
        angle = (acos(y / distance) * orientation)
        sector = self.get_sector(angle, orientation)
        return [layer, sector, x, y]

    def get_sector(self, angle, orientation):
        sector_half_length = pi / (self.resolution * 8)
        sector_start = [-sector_half_length, sector_half_length]
        if orientation == 1:
            sector = 0
        else:
            sector = 8 * self.resolution
        while not sector_start[0] <= angle < sector_start[1]:
            if orientation == 1:
                sector_start[0] += 2 * sector_half_length
                sector_start[1] += 2 * sector_half_length
                sector += 1
            else:
                sector_start[0] -= 2 * sector_half_length
                sector_start[1] -= 2 * sector_half_length
                sector -= 1

        return sector

    def log_agent(self):
        print("type : ", type(self))
        print("position : ", self.position_x, self.position_y)
        print("direction : ", self.direction_x, self.direction_y)
        print("radar :")
        print(self.radar)


class Hunter(Agent):
    def __init__(self, x, y, env):
        super().__init__(x, y, env)
        self.health = 1
        self.detection_range = 2
        self.resolution = self.detection_range
        self.get_radar(env)
        self.brain = Brain(self)


class Prey(Agent):
    def __init__(self, x, y, env):
        super().__init__(x, y, env)
        self.health = 2
        self.detection_range = 2
        self.resolution = self.detection_range
        self.get_radar(env)
        self.brain = Brain(self)