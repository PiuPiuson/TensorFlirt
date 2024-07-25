import argparse
import os
import requests
import pickle

from tqdm import tqdm
from time import sleep

from dotenv import load_dotenv
from random import random

from modules.tinder.api import Api

load_dotenv()

DEFAULT_OUTPUT_DIRECTORY = "images/downloaded"

ORIGINAL = "original"
FACES = "faces"
USERS = "users"
METADATA = "metadata"


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
                    image.load()

                    image_filename = f"{user_prefix}_{i}"

                    image.get_original().save(
                        os.path.join(original_dir, f"{image_filename}_original.jpg")
                    )

                    if image.face_box:
                        image.get_face().resize((250, 250)).save(
                            os.path.join(faces_dir, f"{image_filename}_face.jpg")
                        )

                    if image.user_box:
                        image.get_user().resize((400, 400)).save(
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
