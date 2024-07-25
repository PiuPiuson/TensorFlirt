import argparse
import os
import requests

from matplotlib import pyplot as plt

from tqdm import tqdm
from time import sleep

from dotenv import load_dotenv
from random import random
import numpy as np

from modules.tinder.api import Api
from modules.tensor_flow.image_evaluator import ImageEvaluator

load_dotenv()

DEFAULT_OUTPUT_DIRECTORY = "images/downloaded"

ORIGINAL = "original"
FACES = "faces"
USERS = "users"
METADATA = "metadata"

FACE_THRESHOLD = 0.35
USER_THRESHOLD = 0.3


def remove_outliers(data):
    """
    Remove outliers from a numpy array of scores using the Interquartile Range (IQR) method.

    Args:
    data (numpy.ndarray): Array of scores.

    Returns:
    numpy.ndarray: Array with outliers removed.
    """
    quartile_1, quartile_3 = np.percentile(data, [25, 75])
    iqr = quartile_3 - quartile_1
    lower_bound = quartile_1 - (iqr * 1.5)
    upper_bound = quartile_3 + (iqr * 1.5)
    return data[(data >= lower_bound) & (data <= upper_bound)]


def main():
    auth_token = os.getenv("AUTH_TOKEN")
    if not auth_token:
        print(
            "AUTH_TOKEN not present in the .env file \nEnsure you have a .env file and that the AUTH_TOKEN key has the X-Auth-Token obtained from your browser"
        )
        return

    api = Api(auth_token)

    face_evaluator = ImageEvaluator("model/faces.keras")
    user_evaluator = ImageEvaluator("model/users.keras")

    nearby_users = api.get_nearby_users()

    for user in nearby_users:

        faces = []
        users = []
        originals = []

        for image in tqdm(
            user.images, leave=False, desc=f"Downloading images for {user.name}"
        ):
            if not image.face_box or not image.user_box:
                continue
            try:
                image.load()
                faces.append(image.get_face())
                users.append(image.get_user())
                originals.append(image.get_original())

            except requests.RequestException as e:
                print(f"Failed to download {image.url}: {str(e)}")
                continue

        face_results = face_evaluator.evaluate_images(faces)
        user_results = user_evaluator.evaluate_images(users)

        face_avg = np.mean(face_results)
        user_avg = np.mean(user_results)
        
        face_avg_no_outliers = np.mean(remove_outliers(face_results))
        user_avg_no_outliers = np.mean(remove_outliers(user_results))
        
        should_like_face = face_avg_no_outliers >= FACE_THRESHOLD
        should_like_user = user_avg_no_outliers >= USER_THRESHOLD
        should_like = should_like_face or should_like_user

        # Display images with scores using matplotlib
        fig, axs = plt.subplots(2, max(len(faces), len(users)), figsize=(20, 12))
        fig.suptitle(f"Results for {user.name}")

        for i, (face, score) in enumerate(zip(faces, face_results)):
            axs[0, i].imshow(face)
            axs[0, i].set_title(f"Face Score: {score:.3f}")
            axs[0, i].axis("off")
        axs[0, -1].text(
            1.05,
            0.5,
            f"Face Avg: {face_avg:.3f}\n\nAvg no outliers: {face_avg_no_outliers:.3f}",
            transform=axs[0, -1].transAxes,
            verticalalignment="center",
        )

        for i, (user, score) in enumerate(zip(originals, user_results)):
            axs[1, i].imshow(user)
            axs[1, i].set_title(f"User Score: {score:.3f}")
            axs[1, i].axis("off")
        axs[1, -1].text(
            1.05,
            0.5,
            f"User Avg: {user_avg:.3f}\n\nAvg no outliers: {user_avg_no_outliers:.3f}",
            transform=axs[1, -1].transAxes,
            verticalalignment="center",
        )
        
        fig.text(0.5, 0.01, f"Face: {should_like_face}          User: {should_like_user}           Like: {should_like}", ha="center", va="bottom", fontsize=20)

        plt.show()

        print("FACE", face_results)
        print("_________________")
        print("USER", user_results)


if __name__ == "__main__":
    main()
