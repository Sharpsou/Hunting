from Agent import *
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
from keras.layers import Dropout
from random import *
import numpy as np
from keras.models import load_model
import os
import time
import pandas as pd



class Brain:
    def __init__(self, name=None, learning_rate=0.001, epsilon_decay=0.9999, batch_size=30, memory_size=3000, agent=None):
        self.state_size = 8*agent.resolution*2
        self.action_size = agent.dol
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = epsilon_decay
        self.learning_rate = learning_rate
        self.memory = []  # deque(maxlen=memory_size)
        self.batch_size = batch_size

        self.name = name
        if name is not None and os.path.isfile("model-" + name):
            self.model = load_model("model-" + name)
        else:
            self.model = Sequential()
            self.model.add(Dense(16*agent.resolution, input_dim=self.state_size, activation='relu'))
            self.model.add(Dropout(rate=0.2))
            self.model.add(Dense(16, activation='relu'))
            self.model.add(Dropout(rate=0.2))
            self.model.add(Dense(16, activation='relu'))
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
        value_layer_in = np.array(state['layer_x'])
        value_type_in = np.array(state['type_x'])
        value_in = np.concatenate((value_layer_in, value_type_in), axis=None)
        value_in = np.asarray([value_in])

        # Predict
        act_values = self.model.predict(value_in)
        action = np.argmax(act_values[0])
        return action, act_values, value_in

    def remember(self, state, action, reward, done):
        self.memory.append([state, action, reward, done])

    def takeSecond(self, elem):
        return elem[2]

    def fit(self, batch_size=30):
        # memory = pd.DataFrame(self.memory)
        # print('memory')
        # print(self.memory)
        batch_size = min(batch_size, len(self.memory))
        # print(batch_size)
        # memory = self.memory.sort(key=lambda x: x[2])

        # random list

        # sort list with key
        self.memory.sort(key=self.takeSecond)
        # print(self.memory)
        # memory = sorted(self.memory, key=itemgetter(2))
        minibatch = self.memory[-batch_size:]
        # minibatch = memory.head(batch_size)
        # print(minibatch)
        # minibatch = list(minibatch)
        # print(minibatch)
        inputs = np.zeros((batch_size, self.state_size))
        outputs = np.zeros((batch_size, self.action_size))


        for i, (state, action, reward, done) in enumerate(minibatch):
            # target = action  # self.model.predict(state)[0]
            # if done:
            #     target[action] = reward
            # else:
            #     target[action] = reward + self.gamma * np.max(self.model.predict(next_state))

            # value_layer_in = np.array(state['layer_x'])
            # value_type_in = np.array(state['type_x'])
            # value_in = np.concatenate((value_layer_in, value_type_in), axis=None)
            # value_in = np.asarray([value_in])

            inputs[i] = state
            outputs[i] = action
            # print('inputs')
            # print(inputs)
            # print('outputs')
            # print(outputs)
        # print('fit')
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

    def shuffle_weights(self, weights=None):
        if weights is None:
            weights = self.model.get_weights()
        weights = [np.random.permutation(w.flat).reshape(w.shape) for w in weights]
        # Faster, but less random: only permutes along the first dimension
        # weights = [np.random.permutation(w) for w in weights]
        self.model.set_weights(weights)