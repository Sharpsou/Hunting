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
        self.brain.verbose_fit = False

    def categorizer_radar(self, env):
        self.side = (self.detection_range*2)+1
        plan_x_min = self.position_x-self.detection_range
        plan_x_max = self.position_x+self.detection_range
        plan_y_min = self.position_y-self.detection_range
        plan_y_max = self.position_y+self.detection_range

        radar_agents = np.zeros((env.height+1, env.width+1))
        radar_wall = env.map[plan_x_min:plan_x_max][plan_y_min:plan_y_max]
        print('env dimension')
        print(env.height, env.width)

        for agent in env.agents:
            if type(agent) is Prey:
                print('prey position')
                print(agent.position_x,agent.position_y)

                radar_agents[agent.position_x, agent.position_y] = 1
            if type(agent) is Hunter:
                print('hunter position')

                print(agent.position_x,agent.position_y)
                radar_agents[agent.position_x, agent.position_y] = -1
        radar_agents = radar_agents[plan_x_min:plan_x_max][plan_y_min:plan_y_max]
        value_in = np.concatenate((radar_wall, radar_agents), axis=None)
        value_in = np.asarray([value_in])
        self.radar = value_in

    def next_movement(self, env):
        done = False
        done_reward = 0
        self.categorizer_radar(env)
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
        # print('history acc')
        # print(self.history_acc)


class Hunter(Agent):
    def __init__(self, x, y, env):
        super().__init__(x, y, env)
        self.health = 1
        self.detection_range = 1
        self.resolution = 2 # self.detection_range  # self.detection_range-1 if self.detection_range > 1 else 1
        self.categorizer_radar(env)
        self.brain = Brain(name='Hunter', agent=self)


class Prey(Agent):
    def __init__(self, x, y, env):
        super().__init__(x, y, env)
        self.health = 2
        self.detection_range = 1
        self.resolution = 2 # self.detection_range  # self.detection_range-1 if self.detection_range > 1 else 1
        self.categorizer_radar(env)
        self.brain = Brain(name='Prey', agent=self)

