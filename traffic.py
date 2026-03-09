import cv2
import numpy as np
import os
import sys
import tensorflow as tf

from sklearn.model_selection import train_test_split

EPOCHS = 10
IMG_WIDTH = 30
IMG_HEIGHT = 30
NUM_CATEGORIES = 43
TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) not in [2, 3]:
        sys.exit("Usage: python traffic.py data_directory [model.h5]")

    # Get image arrays and labels for all image files
    images, labels = load_data(sys.argv[1])

    # Split data into training and testing sets
    labels = tf.keras.utils.to_categorical(labels)
    x_train, x_test, y_train, y_test = train_test_split(
        np.array(images), np.array(labels), test_size=TEST_SIZE
    )

    # Get a compiled neural network
    model = get_model()

    # Fit model on training data
    model.fit(x_train, y_train, epochs=EPOCHS)

    # Evaluate neural network performance
    model.evaluate(x_test, y_test, verbose=2)

    # Save model to file
    if len(sys.argv) == 3:
        filename = sys.argv[2]
        model.save(filename)
        print(f"Model saved to {filename}.")


def load_data(data_dir):
    """
    Load image data from directory `data_dir`.

    Assume `data_dir` has one directory named after each category, numbered
    0 through NUM_CATEGORIES - 1. Inside each category directory will be some
    number of image files.

    Return tuple `(images, labels)`. `images` should be a list of all
    of the images in the data directory, where each image is formatted as a
    numpy ndarray with dimensions IMG_WIDTH x IMG_HEIGHT x 3. `labels` should
    be a list of integer labels, representing the categories for each of the
    corresponding `images`.
    """

    images = []
    labels = []

    print("Loading: ", end="")

    # Loop through every category (specified by folder name)
    for label in range(NUM_CATEGORIES):

        folder_path = os.path.join(data_dir, str(label))

        # Loop through all the files in current category
        for filename in os.listdir(folder_path):

            # Form a path for one image
            img_path = os.path.join(folder_path, filename)

            # Read the image as a numpy ndarray
            raw_img = cv2.imread(img_path)
            assert raw_img is not None, f"file {filename} could not be read"

            # Resize image to specification
            img = cv2.resize(
                raw_img, (IMG_WIDTH, IMG_HEIGHT), interpolation=cv2.INTER_AREA
            )

            # Add resized image along with its label to the array
            images.append(img)
            labels.append(label)

        print(f"{folder_path} ", end="")

    print("\nLoading finished!")
    return (images, labels)


def get_model():
    """
    Returns a compiled convolutional neural network model. Assume that the
    `input_shape` of the first layer is `(IMG_WIDTH, IMG_HEIGHT, 3)`.
    The output layer should have `NUM_CATEGORIES` units, one for each category.
    """

    # fmt: off
    # Specify model for a convolutional neural network
    model = tf.keras.models.Sequential(
        [
            # Define the input shape (seperated here to avoid Pylance errors)
            tf.keras.layers.Input(shape=(IMG_WIDTH, IMG_HEIGHT, 3)),

            # Add a 2D convolution layer with max-pooling
            tf.keras.layers.Conv2D(
                filters=32,
                kernel_size=(3, 3),
                activation="relu",
                padding="same",
            ),
            tf.keras.layers.MaxPooling2D(pool_size=(2, 2)),

            # Add another 2D convolution layer with max-pooling, now with
            #  double the # of filters due to previously pooled input data
            tf.keras.layers.Conv2D(
                filters=64,
                kernel_size=(3, 3),
                activation="relu",
                padding="same",
            ),
            tf.keras.layers.MaxPooling2D(pool_size=(2, 2)),

            # Flatten the result for rest of the network
            tf.keras.layers.Flatten(),

            # Add a hidden layer with dropout, again doubling the # of inputs
            tf.keras.layers.Dense(128, activation="relu"),
            tf.keras.layers.Dropout(0.5),
            
            # Add an output layer
            # softmax activation creates a probability distribution
            tf.keras.layers.Dense(NUM_CATEGORIES, activation="softmax"),
        ]
    )
    # fmt: on

    # Compile the model: define loss function and some optimizer
    # During training, judge the model performance by accuracy
    model.compile(
        loss="categorical_crossentropy", optimizer="adam", metrics=["accuracy"]
    )

    return model


if __name__ == "__main__":
    main()
