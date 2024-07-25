import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array


class ImageEvaluator:
    def __init__(self, model_path, target_size=(224, 224)):
        """
        Initialize the ImageEvaluator with a path to a model and optional target image size.

        Args:
        model_path (str): Path to the trained model.
        target_size (tuple): Desired size (width, height) as expected by the model.
        """
        self.model = self.load_trained_model(model_path)
        self.target_size = target_size

    def load_trained_model(self, model_path):
        """
        Load a trained Keras model from the specified path.
        """
        try:
            model = load_model(model_path)
            print("Model loaded successfully.")
            return model
        except RuntimeError as e:
            print(f"Error loading model: {e}")
            return None

    def _preprocess_images(self, images):
        """
        Preprocess a list of PIL.Image objects: resize and convert them to numpy arrays.

        Args:
        images (list): List of PIL.Image objects.

        Returns:
        numpy.ndarray: Array of preprocessed image data.
        """
        processed_images = []
        for img in images:
            if img.size != self.target_size:
                img = img.resize(self.target_size)
            img_array = img_to_array(img)
            img_array /= 255.0  # Normalize to 0-1
            processed_images.append(img_array)

        return np.array(processed_images)

    def evaluate_images(self, images):
        """
        Evaluate a list of images using the loaded model and return the predictions.

        Args:
        images (list): List of PIL.Image objects to evaluate.

        Returns:
        list: Predictions made by the model.
        """
        if self.model is None:
            print("Model is not loaded.")
            return []

        # Preprocess the images
        images_preprocessed = self._preprocess_images(images)

        # Make predictions
        predictions = self.model.predict(images_preprocessed)
        return predictions.flatten()
