import os
import argparse
import shutil

from tqdm import tqdm

from modules.tensor_flow.person_detector import PersonDetector

DEFAULT_OUTPUT_DIRECTORY = "images/cropped"
DEFAULT_INPUT_DIRECTORY = "images/downloaded"
DEFAULT_MODEL = "https://tfhub.dev/tensorflow/efficientdet/lite2/detection/1"


def image_exists_in_folder(image_name, folder):
    for filename in os.listdir(folder):
        if image_name in filename:
            return True

    return False


def main():
    parser = argparse.ArgumentParser(description="Farms photos from nearby users")
    parser.add_argument(
        "--output_dir",
        "-o",
        default=DEFAULT_OUTPUT_DIRECTORY,
        help="Output directory to put images",
        dest="output_dir",
    )
    parser.add_argument(
        "--input_dir",
        "-i",
        default=DEFAULT_INPUT_DIRECTORY,
        help="Output directory to put images",
        dest="input_dir",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help="tfhub URL with person detector model to load",
        dest="model",
    )
    args = parser.parse_args()

    input_dir = args.input_dir
    output_dir = args.output_dir
    model = args.model

    os.makedirs(output_dir, exist_ok=True)

    detector = PersonDetector(model)

    image_files = [f for f in os.listdir(input_dir) if f.endswith(".jpg")]

    for image in tqdm(image_files, desc="Cropping images"):
        image_name = image.replace(".jpg", "")

        if image_exists_in_folder(image_name, output_dir):
            continue

        image_path = os.path.join(input_dir, image)

        person_images = detector.get_person_images(image_path)
        if len(person_images) == 0:
            shutil.copyfile(
                image_path, os.path.join(output_dir, f"{image_name}_negative.jpg")
            )

        for idx, person_image in enumerate(person_images):
            person_image.save(os.path.join(output_dir, f"{image_name}_{idx}.jpg"))


if __name__ == "__main__":
    main()
