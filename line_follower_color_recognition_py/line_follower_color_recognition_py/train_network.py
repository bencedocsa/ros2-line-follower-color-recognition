# Import the necessary packages
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Activation, Flatten, Dense, Conv2D, MaxPooling2D, Input, Dropout
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.optimizers.schedules import ExponentialDecay
from tensorflow.keras.callbacks import ReduceLROnPlateau, ModelCheckpoint
from tensorflow.keras.utils import to_categorical
from tensorflow.keras import __version__ as keras_version
from tensorflow.compat.v1 import ConfigProto
from tensorflow.compat.v1 import InteractiveSession
from tensorflow.random import set_seed
import tensorflow as tf
from sklearn.model_selection import train_test_split
from imutils import paths
import numpy as np
import random
import cv2
import os
import matplotlib.pyplot as plt
from numpy.random import seed

# Set image size
image_size = 24

config = ConfigProto()
config.gpu_options.allow_growth = True
session = InteractiveSession(config=config)

# Fix every random seed to make the training reproducible
seed(1)
set_seed(2)
random.seed(42)

print("[INFO] Version:")
print("Tensorflow version: %s" % tf.__version__)
keras_version = str(keras_version).encode('utf8')
print("Keras version: %s" % keras_version)

def build_model(width, height, depth):
    inputShape = (height, width, depth)
    inputs = Input(inputShape)

    # first set of CONV => RELU => POOL layers
    x = Conv2D(20, (3, 3), padding="same")(inputs)
    x = Activation("relu")(x)
    x = MaxPooling2D(pool_size=(2, 2), strides=(2, 2))(x)

    # Optional Dropout after first pool (small value)
    x = Dropout(0.25)(x)

    # second set of CONV => RELU => POOL layers
    x = Conv2D(50, (3, 3), padding="same")(x)
    x = Activation("relu")(x)
    x = MaxPooling2D(pool_size=(2, 2), strides=(2, 2))(x)

    # Optional Dropout again
    x = Dropout(0.25)(x)

    # first (and only) set of FC => RELU layers
    x = Flatten()(x)
    x = Dense(500)(x)
    x = Activation("relu")(x)

    # Dropout after fully connected (higher value)
    x = Dropout(0.5)(x)

    # Outputs
    direction_output = Dense(
        3,
        activation="softmax",
        name="direction_output"
    )(x)
    color_output = Dense(
        3,
        activation="softmax",
        name="color_output"
    )(x)

    # Creating model
    model = Model(inputs=inputs,outputs=[direction_output, color_output])

    # return the constructed network architecture
    return model

    
dataset = '..//training_images'
# initialize the data and labels
print("[INFO] loading images and labels...")
data = []
direction_labels = []
color_labels = []

direction_dict = {
    "forward": 0,
    "right": 1,
    "left": 2
}
color_dict = {
    "red": 0,
    "green": 1,
    "blue": 2
}
 
# grab the image paths and randomly shuffle them
imagePaths = sorted(list(paths.list_images(dataset)))
random.shuffle(imagePaths)
# loop over the input images
for imagePath in imagePaths:
    # load the image, pre-process it, and store it in the data list
    image = cv2.imread(imagePath)
    image = cv2.resize(image, (image_size, image_size))
    image = img_to_array(image)
    data.append(image)
    # extract the labels
    path_parts = imagePath.split(os.path.sep)
    direction = path_parts[-2]
    color = path_parts[-3]

    direction_labels.append(direction_dict[direction])
    color_labels.append(color_dict[color])
    
    
# scale the raw pixel intensities to the range [0, 1]
data = np.array(data, dtype="float") / 255.0
direction_labels = np.array(direction_labels)
color_labels = np.array(color_labels)
 
# one-hot encoding
direction_labels = to_categorical(direction_labels, num_classes=3)
color_labels = to_categorical(color_labels, num_classes=3)

# partition the data into training and testing splits using 75% of
# the data for training and the remaining 25% for testing
(trainX, testX, trainDirectionY, testDirectionY, trainColorY, testColorY) = train_test_split(data, direction_labels, color_labels, test_size=0.25, random_state=42)

# initialize the number of epochs to train for, initial learning rate,
# and batch size
EPOCHS  = 40
INIT_LR = 0.001
BS      = 32

# initialize the model
print("[INFO] compiling model...")
model = build_model(width=image_size, height=image_size, depth=3)
opt = Adam(learning_rate=INIT_LR)
model.compile(
    optimizer=opt,
    loss={
        "direction_output": "categorical_crossentropy",
        "color_output": "categorical_crossentropy"
    },
    metrics={
        "direction_output": "accuracy",
        "color_output": "accuracy"
    }
)
 
# print model summary
model.summary()

# checkpoint the best model
checkpoint_filepath = "..//network_model//model.best.keras"
checkpoint = ModelCheckpoint(checkpoint_filepath, monitor = 'val_loss', verbose=1, save_best_only=True, mode='min')

# set a learning rate annealer
reduce_lr = ReduceLROnPlateau(monitor='val_loss', patience=3, verbose=1, factor=0.5, min_lr=1e-6)

# callbacks
callbacks_list=[reduce_lr, checkpoint]

# train the network
print("[INFO] training network...")
history = model.fit(
    trainX,
    {
        "direction_output": trainDirectionY,
        "color_output": trainColorY
    },
    validation_data=(
        testX,
        {
            "direction_output": testDirectionY,
            "color_output": testColorY
        }
    ),
    batch_size=BS,
    epochs=EPOCHS,
    callbacks=callbacks_list,
    verbose=1
)
 
# save the model
print("[INFO] serializing network...")
model.save("..//network_model//model.keras")

# plot results
plt.xlabel('Epoch Number')
plt.ylabel("Loss / Accuracy Magnitude")
plt.plot(history.history['direction_output_accuracy'], label="direction_acc")
plt.plot(history.history['val_direction_output_accuracy'], label="val_direction_acc")
plt.plot(history.history['color_output_accuracy'], label="color_acc")
plt.plot(history.history['val_color_output_accuracy'], label="val_color_acc")
plt.plot(history.history['loss'], label="loss")
plt.plot(history.history['val_loss'], label="val_loss")
plt.legend()
plt.savefig('..//network_model//model_training')
plt.show()