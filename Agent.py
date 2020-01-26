from random import *
from math import *
import pandas as pd
from Brain import *


class Agent:
    def __init__(self, x, y, env):
        self.position_x = x
        self.position_y = y
        self.temp_position_x = x
        self.temp_position_y = y
        self.direction_x = randint(-1, 1)
        self.direction_y = randint(-1, 1)
        self.detection_range = 0
        self.resolution = 0
        self.dol = 8

    def init_radar(self):
        radar_init = []
        for x in range(8*self.resolution):
            radar_init.append([x, 0, 0])
        radar_init = pd.DataFrame(radar_init)
        radar_init.columns = ['sector', 'layer', 'type']
        return radar_init

    def next_movement(self, env):
        self.get_radar(env)
        self.next_direction()
        x = self.position_x + self.direction_x
        y = self.position_y + self.direction_y
        if env.possibles_movements(self.temp_position_x, self.temp_position_y) and\
                not (self.direction_x == 0 and self.direction_y == 0):
            self.temp_position_x = x
            self.temp_position_y = y
            if type(self) is Prey:
                return 1
            if type(self) is Hunter:
                return -1
        else:
            return -10

    @staticmethod
    def direction_to_coord(direction):
        if direction == 0:
            return 0, 1
        if direction == 1:
            return 1, 1
        if direction == 2:
            return 1, 0
        if direction == 3:
            return 1, -1
        if direction == 4:
            return 0, -1
        if direction == 5:
            return -1, -1
        if direction == 6:
            return -1, 0
        if direction == 7:
            return -1, 1

    def next_direction(self):
        direction = self.brain.get_action(self.radar, rand=True)
        self.direction_x, self.direction_y = self.direction_to_coord(direction)

    def get_radar(self, env):
        neighbour = self.get_neighbour(env)
        if not neighbour.empty:
            apparent_neighbour = neighbour.groupby(['sector']).min()
        else:
            apparent_neighbour = self.init_radar()
        print(type(self))
        print('apparent neighbour :')
        print(apparent_neighbour)
        print('init radar :')
        print(self.init_radar())
        self.radar = apparent_neighbour.merge(self.init_radar(), on='sector', how='right')
        self.radar = self.radar.sort_values('sector').fillna(0)
        print('radar :')
        print(self.radar)

    def manage_close_wall(self, apparent_neighbour):
        # work in progress
        return True

    def get_neighbour(self, env):
        neighbour = []
        min_range = -self.detection_range
        max_range = self.detection_range + 1
        for y in range(min_range, max_range):
            for x in range(min_range, max_range):
                if (y != 0 or x != 0) and (not env.possibles_movements(self.position_x + x, self.position_y + y)
                                           or env.is_agent(x, y)[0]):
                    unit = self.get_coord(x, y)
                    unit.append(env.what_type(x, y))
                    neighbour.append(unit)
        neighbour = pd.DataFrame(neighbour)
        if not neighbour.empty:
            neighbour.columns = ['layer', 'sector', 'type']
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
        return [layer, sector]

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
        self.detection_range = 1
        self.resolution = self.detection_range-1 if self.detection_range > 1 else 1
        self.radar = self.init_radar()
        self.get_radar(env)
        self.brain = Brain(agent=self)


class Prey(Agent):
    def __init__(self, x, y, env):
        super().__init__(x, y, env)
        self.health = 2
        self.detection_range = 1
        self.resolution = self.detection_range-1 if self.detection_range > 1 else 1
        self.radar = self.init_radar()
        self.get_radar(env)
        self.brain = Brain(agent=self)

