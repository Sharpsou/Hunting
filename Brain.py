from Agent import *
from collections import deque
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam


class Brain:
    def __init__(self, agent):
        self.model = Sequential()
        self.model.add(Dense(16, input_dim=8*agent.resolution, activation='relu'))
        self.model.add(Dense(16, activation='relu'))
        self.model.add(Dense(4, activation='linear'))
        self.model.compile(loss='mse', optimizer='adam')