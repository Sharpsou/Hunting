from random import *
from math import *
import pandas as pd
from tkinter import *
from random import *
from math import *
from collections import deque
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam


class Environment:
    def __init__(self, height, width, ratio,  nb_hunter, nb_prey):
        self.height = height
        self.width = width
        self.nb_hunter = nb_hunter
        self.nb_prey = nb_prey
        self.window_width = 1280 / ratio
        self.window_height = 920 / ratio
        self.window_marge = 420 / ratio
        self.display()  # create window's attribute
        self.map_generator()
        self.agents_generator()
        self.canvas.mainloop()

    def possibles_movements(self, x, y):
        if (0 <= x <= self.width - 1 and 0 <= y <= self.height - 1) and self.map[y][x] != 1:
            return True
        else:
            return False

    def simulation(self):
        self.state = True
        while self.state:
            # check all Agent to know next movements
            for a in range(len(self.agents)):
                self.agents[a].next_direction(self)
                self.agents[a].next_movement(self)
                # self.agents[a].log_agent()
            self.canvas.delete('agent')
            self.agents_print()
            self.canvas.update()
            self.canvas.after(50)

    def map_generator(self):
        self.map = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                row.append(choices([0, 1], weights=[10, 5])[0])
            self.map.append(row)
        self.map_print()

    def map_print(self):
        # distance between rows and columns
        vertical_dist = self.window_height / self.height
        horizontal_dist = self.window_width / self.width
        # rows
        for y in range(self.height):
            self.canvas.create_line(0, (y + 1) * vertical_dist, self.window_width, (y + 1) * vertical_dist)
            self.canvas.pack()
        # columns
        for x in range(self.width):
            self.canvas.create_line((x + 1) * horizontal_dist, 0, (x + 1) * horizontal_dist, self.window_height)
            self.canvas.pack()
        self.units_print()

    def agents_generator(self):
        self.agents = []
        for h in range(self.nb_hunter):
            hunt_x = randint(int((self.width - 1) / 2), self.width - 1)
            hunt_y = randint(int((self.height - 1) / 2), self.height - 1)
            self.agents.append(Hunter(hunt_x, hunt_y, self))

        for p in range(self.nb_prey):
            prey_x = randint(0, int((self.width - 1) / 2))
            prey_y = randint(0, int((self.height - 1) / 2))
            self.agents.append(Prey(prey_x, prey_y, self))
        self.agents_print()

    def agents_print(self):
        for agent in self.agents:
            self.agent_print(agent)

    def units_print(self):
        for y in range(self.height):
            for x in range(self.width):
                self.unit_print(x, y)

    def unit_print(self, x, y):
        vertical_dist = self.window_height / self.height
        horizontal_dist = self.window_width / self.width
        if self.map[y][x] == 1:
            self.canvas.create_rectangle(x * horizontal_dist,
                                         y * vertical_dist,
                                         (x + 1) * horizontal_dist,
                                         (y + 1) * vertical_dist, fill='black')
            self.canvas.pack()

    def agent_print(self, agent):
        vertical_dist = self.window_height / self.height
        horizontal_dist = self.window_width / self.width
        color = "green"
        if type(agent) is Hunter:
            color = "red"
        if type(agent) is Prey:
            color = "blue"
        self.canvas.create_rectangle(agent.position_x * horizontal_dist,
                                     agent.position_y * vertical_dist,
                                     (agent.position_x + 1) * horizontal_dist,
                                     (agent.position_y + 1) * vertical_dist, fill=color, tags='agent')

        self.canvas.pack()

    def display(self):
        self.window = Tk()
        self.window.title('Hunt 1.0')
        geometry = str(int(self.window_width + self.window_marge)) + \
                   'x' + \
                   str(int(self.window_height + self.window_marge/2))
        self.window.geometry(geometry)
        self.canvas = Canvas(self.window, width=self.window_width, height=self.window_height, bg='grey')
        self.canvas.pack()
        self.interface()

    def interface(self):
        self.button_simulation = Button(self.window, text="Simulation", command=self.simulation)
        self.button_stop = Button(self.window, text="Stop", command=self.stop_simulation)
        self.quit = Button(self.window, text="Quit", command=self.quit)
        # pack button
        self.button_simulation.pack(side=LEFT, expand=True, fill=BOTH)
        self.button_stop.pack(side=LEFT, expand=True, fill=BOTH)
        self.quit.pack(side=LEFT, expand=True, fill=BOTH)

    def quit(self):
        self.state = False  # to stop While in simulation()
        self.window.destroy()

    def stop_simulation(self):
        self.state = False  # to stop While in simulation()


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


class Brain:
    def __init__(self, agent):
        self.model = Sequential()
        self.model.add(Dense(16, input_dim=8*agent.resolution, activation='relu'))
        self.model.add(Dense(16, activation='relu'))
        self.model.add(Dense(4, activation='linear'))
        self.model.compile(loss='mse', optimizer='adam')


test = Environment(9, 12, 4, 1, 1)
