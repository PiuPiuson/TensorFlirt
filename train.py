import os

from tensorflow.keras.layers import Flatten, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import VGG16
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import ReduceLROnPlateau


# Directories
SOURCE_DIR = "images/classified"
OUTPUT_DIR = "model"
CATEGORIES = ["users", "faces"]

IMAGE_SIZE = 224


# Load data
def load_data(parent_directory):
    """Load images from parent directory, expecting 'positive' and 'negative' subfolders."""
    datagen = ImageDataGenerator(
        rescale=1.0 / 255,
        validation_split=0.2,
        rotation_range=40,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode="nearest",
    )

    train_generator = datagen.flow_from_directory(
        directory=parent_directory,
        target_size=(IMAGE_SIZE, IMAGE_SIZE),
        color_mode="rgb",
        batch_size=32,
        class_mode="binary",
        subset="training",
    )

    validation_generator = datagen.flow_from_directory(
        directory=parent_directory,
        target_size=(IMAGE_SIZE, IMAGE_SIZE),
        color_mode="rgb",
        batch_size=32,
        class_mode="binary",
        subset="validation",
    )

    return train_generator, validation_generator


# Define the CNN model
def create_model():
    base_model = VGG16(
        weights="imagenet", include_top=False, input_shape=(IMAGE_SIZE, IMAGE_SIZE, 3)
    )

    # Freeze the convolutional layers to retain the learned features
    for layer in base_model.layers:
        layer.trainable = False

    # Adding custom layers on top of VGG16
    x = Flatten()(base_model.output)
    x = Dense(1024, activation="relu")(x)
    x = Dropout(0.5)(x)
    x = Dense(1024, activation="relu")(x)
    x = Dropout(0.5)(x)
    output = Dense(1, activation="sigmoid")(x)

    return Model(inputs=base_model.input, outputs=output)


def main():
    for category in CATEGORIES:
        source_dir = os.path.join(SOURCE_DIR, category)

        train_generator, validation_generator = load_data(source_dir)
        model = create_model()

        model.compile(
            optimizer=Adam(learning_rate=0.0001),
            loss="binary_crossentropy",
            metrics=["accuracy"],
        )

        reduce_lr = ReduceLROnPlateau(
            monitor="val_loss", factor=0.2, patience=5, min_lr=0.00001
        )

        # Train the model
        history = model.fit(
            train_generator,
            steps_per_epoch=train_generator.samples // train_generator.batch_size,
            validation_data=validation_generator,
            validation_steps=validation_generator.samples
            // validation_generator.batch_size,
            epochs=30,
            callbacks=[reduce_lr],
        )

        # Save the trained model
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        model.save(os.path.join(OUTPUT_DIR, f"{category}.keras"))

    print("Models trained and saved successfully.")


if __name__ == "__main__":
    main()
