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
        self.canvas.mainloop()
        self.t = 0

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
            for a in range(len(self.agents)):
                self.agents[a].next_movement()
                # self.agents[a].log_agent()
            self.canvas.delete('agent')
            self.agents_print()
            self.canvas.update()

            self.canvas.after(50)

    def get_state(self):
        return True

    def map_generator(self):
        self.map = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                row.append(choices([0, 1], weights=[10, 3])[0])
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
        self.run = False  # to stop While in simulation()
        self.window.destroy()

    def stop_simulation(self):
        self.run = False  # to stop While in simulation()
