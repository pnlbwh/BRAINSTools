


# conda list --export > requirements.txt. When you are ready to distribute your package to other users,
# they can easily duplicate your environment and the associated dependencies with
# conda create --name <envname> --file requirements.txt


import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'  # overcome issue of OMP: Error #15: Initializing libiomp5.dylib, but found libiomp5.dylib already initialized.

from time import time

from sklearn.model_selection import train_test_split

import keras

from keras import layers
from keras import optimizers

from keras.utils import plot_model

from keras.callbacks import TensorBoard


import numpy as np

lin = keras.Input(shape=(10,))

x =  np.random.rand(90000,10)
y = x * 2

X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.05)

l1 = layers.Dense(20, activation='relu')(lin)
l2 = layers.Dense(20, activation='relu')(l1)

lout = layers.Dense(10, activation='softmax')(l2)

model = keras.Model(lin,lout)
sgd = optimizers.SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
model.compile(loss='mean_squared_error', optimizer=sgd)

tensorboard = TensorBoard(log_dir="logs/{}".format(time()))

model.fit( X_train, y_train, epochs=100, batch_size=32, validation_split=0.2,
           verbose=1, callbacks=[tensorboard])

plot_model(model, show_shapes=True, show_layer_names=True,  to_file='model.png')
