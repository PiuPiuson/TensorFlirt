import argparse
import os
import requests

from tqdm import tqdm
from time import sleep

from dotenv import load_dotenv
from random import random

from modules.tinder.api import Api

DEFAULT_OUTPUT_DIRECTORY = "images/downloaded"
UUID_FILE = "uuids.txt"

load_dotenv()


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
    os.makedirs(output_dir, exist_ok=True)

    api = Api(auth_token)

    print("Farming photos, use 'ctrl + c' to stop")

    # create the file if it doesn't exist
    uuid_file = open(os.path.join(output_dir, UUID_FILE), "a+", encoding="utf-8")
    uuid_file.close()

    batch_number = 0

    while True:
        nearby_users = api.get_nearby_users()

        for user in tqdm(nearby_users, desc=f"Processing batch {batch_number + 1}"):
            uuid_file = open(
                os.path.join(output_dir, UUID_FILE), "r+", encoding="utf-8"
            )
            found = any(user.id == line.strip() for line in uuid_file)
            if found:
                continue

            for i, image_url in enumerate(
                tqdm(
                    user.images, leave=False, desc=f"Downloading images for {user.name}"
                )
            ):
                try:
                    req = requests.get(image_url, stream=True, timeout=300)
                    if req.status_code != 200:
                        continue

                    with open(
                        os.path.join(output_dir, f"{user.id}_{user.name}_{i}.jpg"), "wb"
                    ) as image_file:
                        image_file.write(req.content)
                except requests.RequestException as e:
                    print(f"Failed to download {image_url}: {str(e)}")
                    continue

            uuid_file.write(f"{user.id}\n")
            sleep(random() * 2)

        batch_number += 1


if __name__ == "__main__":
    main()
