from Agent import *
from collections import deque
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
from keras.layers import Dropout
from random import *
import numpy as np
from keras.models import load_model
import os
import time


class Brain:
    def __init__(self, name=None, learning_rate=0.001, epsilon_decay=0.9999, batch_size=30, memory_size=3000, agent=None):
        self.state_size = 8*agent.resolution*2
        self.action_size = agent.dol
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
            self.model.add(Dense(16, input_dim=self.state_size, activation='relu'))
            self.model.add(Dropout(rate=0.2))
            self.model.add(Dense(16, activation='relu'))
            self.model.add(Dropout(rate=0.2))
            self.model.add(Dense(self.action_size, activation='linear'))
            self.model.compile(loss='mse', optimizer=Adam(lr=self.learning_rate))

    def decay_epsilon(self):
        self.epsilon *= self.epsilon_decay

    def get_action(self, state, rand=True):
        # if rand and np.random.rand() <= self.epsilon:
        #     return randrange(self.action_size)
        value_in_1 = np.array(state['layer_x'])
        value_in_2 = np.array(state['type_x'])
        value_in = np.concatenate((value_in_1,value_in_2),axis=None)
        print(self.state_size)
        print(value_in)
        # Predict
        act_values = self.model.predict(value_in)
        action = np.argmax(act_values[0])
        return action

    def remember(self, state, action, reward, next_state, done):
        self.memory.append([state, action, reward, next_state, done])

    def learn(self, batch_size):

        batch_size = min(batch_size, len(self.memory))

        minibatch = random.sample(self.memory, batch_size)

        inputs = np.zeros((batch_size, self.state_size))
        outputs = np.zeros((batch_size, self.action_size))

        for i, (state, action, reward, next_state, done) in enumerate(minibatch):
            target = self.model.predict(state)[0]
            if done:
                target[action] = reward
            else:
                target[action] = reward + self.gamma * np.max(self.model.predict(next_state))

            inputs[i] = state
            outputs[i] = target

        return self.model.fit(inputs, outputs, epochs=1, verbose=0, batch_size=batch_size)

    def save(self, id=None, overwrite=False):
        name = 'model'
        if self.name:
            name += '-' + self.name
        else:
            name += '-' + str(time.time())
        if id:
            name += '-' + id
        self.model.save(name, overwrite=overwrite)