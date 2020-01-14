from Agent import *
from collections import deque
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
from random import *
import numpy as np

class Brain:
    def __init__(self, name=None, learning_rate=0.001, epsilon_decay=0.9999, batch_size=30, memory_size=3000, agent=None):
        self.state_size = 8*agent.resolution
        self.action_size = 4
        self.gamma = 0.9
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = epsilon_decay
        self.learning_rate = learning_rate
        self.memory = deque(maxlen=memory_size)
        self.batch_size = batch_size

        self.name = name
        if name is not None and os.path.isfile("model-" + name):
            self.model = load_model("model-" + name)
        else:
            self.model = Sequential()
            self.model.add(Dense(16, input_dim=8 * agent.resolution, activation='relu'))
            self.model.add(Dense(16, activation='relu'))
            self.model.add(Dense(4, activation='linear'))
            self.model.compile(loss='mse', optimizer=Adam(lr=self.learning_rate))

    def decay_epsilon(self):
        self.epsilon *= self.epsilon_decay

    def get_best_action(self, state, rand=True):
        if rand and np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)

        # Predict the reward value based on the given state
        act_values = self.model.predict(np.array(state))

        # Pick the action based on the predicted reward
        action = np.argmax(act_values[0])
        return action

