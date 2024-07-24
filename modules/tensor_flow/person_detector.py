import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
from PIL import Image


class ObjectDetector:
    def __init__(self, model_url):
        """Loads the TensorFlow model from TensorFlow Hub."""
        self.detector = hub.load(model_url)

    def detect(self, image_tensor):
        """Runs the model and returns a dictionary of detection outputs."""
        # Run the detector and unpack the tuple
        detection_boxes, detection_scores, detection_classes, num_detections = (
            self.detector(image_tensor)
        )

        # Convert each tensor to numpy array
        return {
            "detection_boxes": detection_boxes.numpy()[0],
            "detection_scores": np.atleast_1d(detection_scores.numpy()[0]),
            "detection_classes": np.atleast_1d(detection_classes.numpy()[0]).astype(
                int
            ),
            "num_detections": int(num_detections.numpy()[0]),  # Convert to int
        }


class ImageProcessor:
    @staticmethod
    def load_image_into_tensor(image_path):
        """Reads an image from file, converts it to a tensor."""
        image = Image.open(image_path)
        image = image.convert("RGB")  # Ensure image is in RGB format
        image_np = np.array(image)
        image_tensor = tf.convert_to_tensor(image_np, dtype=tf.uint8)[tf.newaxis, ...]
        return image_tensor, image

    @staticmethod
    def extract_objects(
        image, boxes, class_ids, scores, target_class_id, score_threshold
    ):
        """Extracts objects of a specific class from the image based on detection results."""
        object_images = []
        
        scores = np.atleast_1d(scores)
        class_ids = np.atleast_1d(class_ids)
        
        for box, score, class_id in zip(boxes, scores, class_ids):
            if score > score_threshold and class_id == target_class_id:
                ymin, xmin, ymax, xmax = box
                cropped_image = image.crop(
                    (
                        xmin,
                        ymin,
                        xmax,
                        ymax,
                    )
                )
                object_images.append(cropped_image)
        return object_images


class PersonDetector:
    def __init__(self, model_url):
        self.object_detector = ObjectDetector(model_url)
        self.person_class_id = 1  # COCO dataset class ID for person
        self.score_threshold = 0.5

    def get_person_images(self, image_path):
        """Detect persons in an image and extract their images."""
        image_tensor, original_image = ImageProcessor.load_image_into_tensor(image_path)
        output_dict = self.object_detector.detect(image_tensor)

        boxes = output_dict["detection_boxes"]
        class_ids = output_dict["detection_classes"][0].astype(int)
        scores = output_dict["detection_scores"][0]

        person_images = ImageProcessor.extract_objects(
            original_image,
            boxes,
            class_ids,
            scores,
            self.person_class_id,
            self.score_threshold,
        )
            
        return person_images
