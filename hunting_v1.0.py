from tkinter import *
import numpy as np
from random import *


class Environment:
    def __init__(self, height, width, nb_hunter, nb_prey):
        self.first_loop = True
        self.state = True
        self.height = height
        self.width = width
        self.nb_hunter = nb_hunter
        self.nb_prey = nb_prey
        self.display()  # create window's attribute
        self.event()
        self.map_generator()
        self.agents_generator()
        self.canvas.mainloop()

    def possibles_movements(self, x, y):
        if (0 <= x <= self.width-1 and 0 <= y <= self.height-1) and self.map[y][x] != 1:
            return True
        else:
            return False

    def simulation(self, event):
        while self.state:
            # check all Agent to know next movements
            for a in range(len(self.agents)):
                self.agents[a].next_movement(self)
            self.canvas.delete('agent')
            self.agents_print()
            self.canvas.update()
            self.canvas.after(50)

    def map_generator(self):
        self.map = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                row.append(choices([0, 1], weights=[10, 2])[0])
            self.map.append(row)
        self.map_print()

    def map_print(self):
        # distance between rows and columns
        vertical_dist = 920 / self.height
        horizontal_dist = 1280 / self.width
        # rows
        for y in range(self.height):
            self.canvas.create_line(0, (y+1)*vertical_dist, 1280, (y+1)*vertical_dist)
            self.canvas.pack()
        # columns
        for x in range(self.width):
            self.canvas.create_line((x+1)*horizontal_dist, 0, (x+1)*horizontal_dist, 920)
            self.canvas.pack()
        self.units_print()

    def agents_generator(self):
        self.agents = []
        for h in range(self.nb_hunter):
            hunt_x = randint(int((self.width-1)/2), self.width-1)
            hunt_y = randint(int((self.height-1)/2), self.height-1)
            self.agents.append(Hunter(hunt_x, hunt_y))
        for p in range(self.nb_prey):
            prey_x = randint(0, int((self.width - 1) / 2))
            prey_y = randint(0, int((self.height - 1) / 2))
            self.agents.append(Prey(prey_x, prey_y))
        self.agents_print()

    def agents_print(self):
        for agent in self.agents:
            self.agent_print(agent)

    def units_print(self):
        for y in range(self.height):
            for x in range(self.width):
                self.unit_print(x, y)

    def unit_print(self, x, y):
        vertical_dist = 920 / self.height
        horizontal_dist = 1280 / self.width
        if self.map[y][x] == 1:
            self.canvas.create_rectangle(x * horizontal_dist,
                                         y * vertical_dist,
                                         (x + 1) * horizontal_dist,
                                         (y + 1) * vertical_dist, fill='black')
            self.canvas.pack()

    def agent_print(self, agent):
        vertical_dist = 920 / self.height
        horizontal_dist = 1280 / self.width
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
        self.window.geometry('1700x960')
        self.canvas = Canvas(self.window, width=1280, height=920, bg='grey')
        self.canvas.pack()
        self.quitLabel = Label(self.window, text="Press Q to quit")
        self.quitLabel.pack()

    def event(self):
        self.canvas.bind_all('<q>', self.quit)  # quit
        self.canvas.bind_all('<s>', self.simulation)  # simulation

    def quit(self, event):
        print(event)
        self.state = False  # to stop While in simulation()
        self.window.destroy()


class Agent:
    def __init__(self, x, y):
        self.position_x = x
        self.position_y = y
        self.direction_x = randint(-1, 1)
        self.direction_y = randint(-1, 1)

    def next_movement(self, env):
        self.next_direction(env)
        x = self.position_x + self.direction_x
        y = self.position_y + self.direction_y
        if env.possibles_movements(x, y) and (self.direction_x != 0 or self.direction_y != 0):
            env.unit_print(x, y)
            self.position_x = x
            self.position_y = y
        else:
            self.direction_x = randint(-1, 1)  # random move because no algo implemented
            self.direction_y = randint(-1, 1)  #

    def next_direction(self, env):
        # neural network here!!!
        None


class Hunter(Agent):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.health = 100
        self.detection_range = 50


class Prey(Agent):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.health = 100
        self.detection_range = 50


test = Environment(40, 40, 2, 2)


