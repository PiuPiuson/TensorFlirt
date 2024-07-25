import argparse
import os
import requests
import pickle

from tqdm import tqdm
from time import sleep
from io import BytesIO
from PIL import Image

from dotenv import load_dotenv
from random import random

from modules.tinder.api import Api
import modules.tinder.user as tinder_user

load_dotenv()

DEFAULT_OUTPUT_DIRECTORY = "images/downloaded"

ORIGINAL = "original"
FACES = "faces"
USERS = "users"
METADATA = "metadata"


def crop_image(image: Image, bounding_box: tinder_user.Image.BoundingBox) -> Image:
    """Crops an Image into a square from the given bounding box."""
    img_width, img_height = image.size

    # Calculate initial bounding box dimensions
    left = bounding_box.x_offset_percent * img_width
    top = bounding_box.y_offset_percent * img_height
    right = left + bounding_box.width_percent * img_width
    bottom = top + bounding_box.height_percent * img_height

    # Determine the size of the bounding box
    box_width = right - left
    box_height = bottom - top

    # Calculate the size of the largest possible square
    square_size = max(box_width, box_height)

    # Calculate new left, top, right, and bottom to center the square in the original bounding box
    left += (box_width - square_size) / 2
    right = left + square_size
    top += (box_height - square_size) / 2
    bottom = top + square_size

    # Ensure the new coordinates are within the image bounds
    left = max(0, min(left, img_width))
    right = max(0, min(right, img_width))
    top = max(0, min(top, img_height))
    bottom = max(0, min(bottom, img_height))

    # Crop the image to these new bounds
    return image.crop((left, top, right, bottom))


def crop_to_square(image: Image) -> Image:
    """Crops the given image to a square shape centered on the middle of the image."""

    width, height = image.size

    # Determine the size of the square (it will be the smaller dimension of the image)
    square_size = min(width, height)

    # Calculate the left, upper, right, and lower coordinates to get a centered square
    left = (width - square_size) / 2
    top = (height - square_size) / 2
    right = (width + square_size) / 2
    bottom = (height + square_size) / 2

    # Crop the image
    cropped_image = image.crop((left, top, right, bottom))

    return cropped_image


def main():
    auth_token = os.getenv("AUTH_TOKEN")
    if not auth_token:
        print(
            "AUTH_TOKEN not present in the .env file \nEnsure you have a .env file and that the AUTH_TOKEN key has the X-Auth-Token obtained from your browser"
        )
        return

    parser = argparse.ArgumentParser(description="Farms photos from nearby users")
    parser.add_argument(
        "--output_dir",
        "-o",
        default=DEFAULT_OUTPUT_DIRECTORY,
        help="Output directory to put images",
        dest="output_dir",
    )
    args = parser.parse_args()

    output_dir = args.output_dir
    original_dir = os.path.join(output_dir, ORIGINAL)
    faces_dir = os.path.join(output_dir, FACES)
    users_dir = os.path.join(output_dir, USERS)
    metadata_dir = os.path.join(output_dir, METADATA)

    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(original_dir, exist_ok=True)
    os.makedirs(faces_dir, exist_ok=True)
    os.makedirs(users_dir, exist_ok=True)
    os.makedirs(metadata_dir, exist_ok=True)

    api = Api(auth_token)

    print("Farming photos, use 'ctrl + c' to stop")

    batch_number = 0

    while True:
        nearby_users = api.get_nearby_users()

        for user in tqdm(nearby_users, desc=f"Processing batch {batch_number + 1}"):
            user_prefix = f"{user.id}_{user.name}"
            user_file = os.path.join(metadata_dir, f"{user_prefix}.pkl")

            # User already farmed
            if os.path.isfile(user_file):
                continue

            for i, image in enumerate(
                tqdm(
                    user.images, leave=False, desc=f"Downloading images for {user.name}"
                )
            ):
                try:
                    req = requests.get(image.url, stream=True, timeout=300)
                    if req.status_code != 200:
                        continue

                    image_filename = f"{user_prefix}_{i}"

                    image_bytes = BytesIO(req.content)
                    original_image = Image.open(image_bytes)
                    original_image = original_image.convert('RGB')
                    original_image.save(
                        os.path.join(original_dir, f"{image_filename}_original.jpg")
                    )

                    if image.face:
                        face_image = crop_image(original_image, image.face)
                        face_image = face_image.resize((250, 250))
                        face_image.save(
                            os.path.join(faces_dir, f"{image_filename}_face.jpg")
                        )

                    if image.user:
                        user_image = crop_image(original_image, image.user)
                        user_image = crop_to_square(user_image).resize((400, 400))
                        user_image.save(
                            os.path.join(users_dir, f"{image_filename}_user.jpg")
                        )

                except requests.RequestException as e:
                    print(f"Failed to download {image.url}: {str(e)}")
                    continue

            with open(user_file, "wb") as file:
                pickle.dump(user, file)

            sleep(random() * 2)

        batch_number += 1


if __name__ == "__main__":
    main()
