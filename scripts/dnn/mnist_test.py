import tensorflow as tf
import numpy as np
import os

from keras.datasets import mnist
from keras import models
from keras import layers
from keras import losses
from keras.utils import to_categorical

from keras import optimizers
from keras import metrics
from keras import activations
from keras.callbacks import TensorBoard


class TrainValTensorBoard(TensorBoard):
  def __init__(self, log_dir='./logs', **kwargs):
    # Make the original `TensorBoard` log to a subdirectory 'training'
    training_log_dir = os.path.join(log_dir, 'training')
    super(TrainValTensorBoard, self).__init__(training_log_dir, **kwargs)

    # Log the validation metrics to a separate subdirectory
    self.val_log_dir = os.path.join(log_dir, 'validation')

  def set_model(self, model):
    # Setup writer for validation metrics
    self.val_writer = tf.summary.FileWriter(self.val_log_dir)
    super(TrainValTensorBoard, self).set_model(model)

  def on_epoch_end(self, epoch, logs=None):
    # Pop the validation logs and handle them separately with
    # `self.val_writer`. Also rename the keys so that they can
    # be plotted on the same figure with the training metrics
    logs = logs or {}
    val_logs = {k.replace('val_', ''): v for k, v in logs.items() if k.startswith('val_')}
    for name, value in val_logs.items():
      summary = tf.Summary()
      summary_value = summary.value.add()
      summary_value.simple_value = value.item()
      summary_value.tag = name
      self.val_writer.add_summary(summary, epoch)
    self.val_writer.flush()

    # Pass the remaining logs to `TensorBoard.on_epoch_end`
    logs = {k: v for k, v in logs.items() if not k.startswith('val_')}
    super(TrainValTensorBoard, self).on_epoch_end(epoch, logs)

  def on_train_end(self, logs=None):
    super(TrainValTensorBoard, self).on_train_end(logs)
    self.val_writer.close()




(train_images, train_labels), (test_images, test_labels) = mnist.load_data()

train_images = train_images.reshape((60000,28*28))
train_images = train_images.astype('float32')/ 255.0
train_labels = to_categorical(train_labels)

test_images = test_images.reshape((10000,28*28))
test_images = test_images.astype('float32')/ 255.0
test_labels = to_categorical(test_labels)

def myrelu(x):
  return activations.relu(x, alpha=0.1, max_value=None, threshold=0.0)

fav_activation = activations.relu

network = models.Sequential()
network.add(layers.Dense(512, activation=fav_activation,input_shape=(28*28,)))
network.add(layers.Dense(10,activation='softmax'))

network.compile(optimizer='rmsprop',
                loss=losses.categorical_crossentropy,
                metrics=['accuracy'])

#network.fit(train_images, train_labels, epochs=5, batch_size=128)


network.fit(train_images, train_labels, epochs=5,
          batch_size=128,
          validation_data=(test_images, test_labels),
          callbacks=[TrainValTensorBoard(write_graph=False)])

#test_loss , test_acc = network.evaluate(test_images, test_labels)
#print('test_acc: ', test_acc)

#digit = test_images[4].reshape(28,28)
#import matplotlib.pyplot as plt
#plt.imshow(digit, cmap=plt.cm.binary)
#plt.show()
