from random import *
from math import *
import pandas as pd
from Brain import *
from numpy import arange
import numpy as np


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
        self.reward = 0
        self.done = False
        self.load = env.load
        self.history_acc = []

    def init_radar(self):
        radar_init = []
        for x in range(8*self.resolution):
            radar_init.append([x, 0, 0])
        radar_init = pd.DataFrame(radar_init)
        radar_init.columns = ['sector', 'layer', 'type']
        return radar_init

    def learn(self):
        self.brain.temp_remember(self.state, self.action, self.reward, self.done)
        self.brain.fit()

    def next_movement(self, env):
        done = False
        done_reward = 0
        self.get_radar(env)
        self.next_direction()
        x = self.position_x + self.direction_x
        y = self.position_y + self.direction_y
        if env.possibles_movements(x, y) and not (self.direction_x == 0 and self.direction_y == 0):
            self.temp_position_x = x
            self.temp_position_y = y
            for agent in env.agents:
                if type(agent) != type(self) and self.same_position(agent):
                    done = True
                    done_reward = 50
            if type(self) is Prey:
                return 1-done_reward+env.t, done
            if type(self) is Hunter:
                return -1+done_reward-env.t, done
        else:
            return -10, done

    def same_position(self, agent):
        if self.position_x == agent.position_x and self.position_y == agent.position_y:
            return True
        return False

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
        direction, self.action, self.state = self.brain.get_action(self.radar, rand=True)
        self.direction_x, self.direction_y = self.direction_to_coord(direction)

    def get_radar(self, env):
        neighbour = self.get_neighbour(env)
        if not neighbour.empty:
            apparent_neighbour = neighbour[['sector', 'layer']]
            apparent_neighbour_min_layer = apparent_neighbour.groupby(['sector']).min()
            apparent_neighbour_min_dist = apparent_neighbour_min_layer.merge(neighbour, on='sector', how='inner')
            apparent_neighbour_min_dist = apparent_neighbour_min_dist[['sector', 'layer_x', 'type']]
        else:
            apparent_neighbour_min_dist = self.init_radar()
        radar_tmp = apparent_neighbour_min_dist.merge(self.init_radar(), on='sector', how='right').drop_duplicates()
        radar_tmp = radar_tmp.sort_values('sector').fillna(0)
        radar_tmp_final = radar_tmp[['sector', 'type_x']].groupby(['sector']).max().merge(radar_tmp[['sector', 'layer_x']].drop_duplicates(), on='sector', how='inner')
        self.radar = radar_tmp_final[['layer_x', 'type_x']]

    def get_neighbour(self, env):
        neighbour = []
        min_range = -self.detection_range
        max_range = self.detection_range + 1
        for y in range(min_range, max_range):
            for x in range(min_range, max_range):
                if (y != 0 or x != 0) and (not env.possibles_movements(self.position_x + x, self.position_y + y)
                                           or env.is_agent(self.position_x + x, self.position_y + y)[0]):
                    layer = max(abs(x), abs(y))
                    delta_area = 0.5  # 0.1*layer if layer < 5 else 0.5
                    if delta_area != 0:
                        for range_x in arange(x-delta_area, x+delta_area, delta_area): # to scan area of unit
                            for range_y in arange(y-delta_area, y+delta_area, delta_area):  # to scan area of unit
                                sector = self.get_coord(range_x, range_y)
                                sector.append(layer)
                                sector.append(env.what_type(self.position_x + x, self.position_y + y))
                                neighbour.append(sector)
                    else:
                        sector = self.get_coord(x, y)
                        sector.append(layer)
                        sector.append(env.what_type(self.position_x + x, self.position_y + y))
                        neighbour.append(sector)

        neighbour = pd.DataFrame(neighbour)
        if not neighbour.empty:
            neighbour.columns = ['sector', 'layer', 'type']
        return neighbour

    def get_coord(self, x, y):
        distance = sqrt(y * y + x * x)
        if x != 0:
            orientation = (x / abs(x))
        else:
            orientation = 1
        angle = (acos(y / distance) * orientation)
        sector = [self.get_sector(angle, orientation)]
        return sector

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

    def evaluate_agent(self):
        inputs = np.zeros((len(self.brain.minibatch), self.brain.state_size))
        outputs = np.zeros((len(self.brain.minibatch), self.brain.action_size))
        for i, (state, action, reward, done) in enumerate(self.brain.minibatch):
            inputs[i] = state
            outputs[i] = action
        return self.brain.model.evaluate(inputs, outputs, verbose=0)

    def log_agent(self):
        print("type : ", type(self))
        print("position : ", self.position_x, self.position_y)
        print("direction : ", self.direction_x, self.direction_y)
        # print("radar :")
        # print(self.radar)
        print('done')
        print(self.done)
        print('reward')
        print(self.reward)
        print('action')
        print(self.action)
        print('state')
        print(self.state)
        print('epsilon')
        print(self.brain.epsilon)
        print('len memory')
        print(len(self.brain.memory))
        evaluation = self.evaluate_agent()
        print('eval')
        print(evaluation)
        print('history acc')
        print(self.history_acc)


class Hunter(Agent):
    def __init__(self, x, y, env):
        super().__init__(x, y, env)
        self.health = 1
        self.detection_range = 3
        self.resolution = 2 # self.detection_range  # self.detection_range-1 if self.detection_range > 1 else 1
        self.get_radar(env)
        self.brain = Brain(name='Hunter', agent=self)


class Prey(Agent):
    def __init__(self, x, y, env):
        super().__init__(x, y, env)
        self.health = 2
        self.detection_range = 3
        self.resolution = 2 # self.detection_range  # self.detection_range-1 if self.detection_range > 1 else 1
        self.get_radar(env)
        self.brain = Brain(name='Prey', agent=self)

