from Agent import *
from tkinter import *
from random import *


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
        self.t = 0
        self.canvas.mainloop()

    def possibles_movements(self, x, y):
        if (0 <= x <= self.width - 1 and 0 <= y <= self.height - 1) and self.map[y][x] != 1:
            return True
        else:
            return False

    def simulation(self):
        self.run = True
        while self.run:
            self.t += 1
            # check all Agent to know next movements
            for agent in self.agents:
                agent.next_movement(self)
                # self.agents[a].log_agent()
            self.canvas.delete('agent')
            self.sync_agents()
            self.agents_print()
            self.canvas.update()

            self.canvas.after(1)

    def log_agents(self):
        for agent in self.agents:
            agent.log_agent()

    def reinit_agents(self):
        for agent in self.agents:
            agent.brain.shuffle_weights()

    def sync_agents(self):
        for agent in self.agents:
            agent.position_x = agent.temp_position_x
            agent.position_y = agent.temp_position_y

    def get_state(self):
        return True

    def map_generator(self):
        self.map = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                row.append(choices([0, 1], weights=[10, 1])[0])
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

    def is_agent(self, x, y):
        for agent in self.agents:
            if agent.position_x == x and agent.position_y == y:
                return [True, agent]
        return [False, None]

    def what_type(self, x, y):
        if self.is_agent(x, y)[0]:
            if type(self.is_agent(x, y)[1]) is Prey:
                return 2
            if type(self.is_agent(x, y)[1]) is Hunter:
                return 3
        else:
            return 1

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
        self.button_reinit_agent = Button(self.window, text="Reinit agent", command=self.reinit_agents)
        self.button_log_agents = Button(self.window, text="Log agents", command=self.log_agents)
        # pack button
        self.button_simulation.pack(side=LEFT, expand=True, fill=BOTH)
        self.button_stop.pack(side=LEFT, expand=True, fill=BOTH)
        self.quit.pack(side=LEFT, expand=True, fill=BOTH)
        self.button_reinit_agent.pack(side=LEFT, expand=True, fill=BOTH)
        self.button_log_agents.pack(side=LEFT, expand=True, fill=BOTH)

    def quit(self):
        self.run = False  # to stop While in simulation()
        self.window.destroy()

    def stop_simulation(self):
        self.run = False  # to stop While in simulation()
