import os
import shutil
import argparse
import tkinter as tk

from PIL import ImageTk, Image
from tqdm import tqdm


DEFAULT_INPUT_DIRECTORY = "images/downloaded"
DEFAULT_OUTPUT_DIRECTORY = "images/classified"

POSITIVE = "positive"
NEGATIVE = "negative"
ORIGINAL = "original"
FACES = "faces"
USERS = "users"


class ImageClassifierApp:
    def __init__(self, root, source_folder, destination_folder):
        self.root = root
        self.source_folder = source_folder
        self.destination_folder = destination_folder
        self.current_index = 0
        self.history = []
        self.image_files = []

        for folder in [ORIGINAL, FACES, USERS]:
            os.makedirs(
                os.path.join(self.destination_folder, folder, POSITIVE), exist_ok=True
            )
            os.makedirs(
                os.path.join(self.destination_folder, folder, NEGATIVE), exist_ok=True
            )

        self.already_classified_images = set(
            [
                f
                for f in os.listdir(
                    os.path.join(self.destination_folder, USERS, POSITIVE)
                )
                if f.endswith(".jpg")
            ]
            + [
                f
                for f in os.listdir(
                    os.path.join(self.destination_folder, USERS, NEGATIVE)
                )
                if f.endswith(".jpg")
            ]
        )

        self.root.bind("<Right>", self.move_current_to_positive)
        self.root.bind("<Left>", self.move_current_to_negative)
        self.root.bind("<Control-z>", self.undo)

        self.label = tk.Label(root)
        self.label.pack()

        self.load_images()

        self.display_image()

    def load_images(self):
        source_images = [
            f
            for f in os.listdir(os.path.join(self.source_folder, USERS))
            if f.endswith(".jpg")
        ]

        self.image_files = [
            image
            for image in source_images
            if image not in self.already_classified_images
        ]

    def display_image(self):
        if 0 <= self.current_index < len(self.image_files):
            image_path = os.path.join(
                self.source_folder, USERS, self.image_files[self.current_index]
            )
            image = Image.open(image_path)
            self.tk_image = ImageTk.PhotoImage(image)
            self.label.config(image=self.tk_image)
            self.root.title(
                f"Image Classifier ({self.current_index + 1}/{len(self.image_files)}) - {self.image_files[self.current_index]}"
            )

    def move_current_to_positive(self, event):
        self.move_current_image(POSITIVE)

    def move_current_to_negative(self, event):
        self.move_current_image(NEGATIVE)

    @staticmethod
    def move_image(
        image_file, source_folder, source_classification, dst_folder, dst_classification
    ):
        users_src_path = os.path.join(
            source_folder, USERS, source_classification, image_file
        )
        users_dst_path = os.path.join(dst_folder, USERS, dst_classification, image_file)

        shutil.move(users_src_path, users_dst_path)

        stripped_filename = image_file.replace("_user.jpg", "")

        faces_src_path = os.path.join(
            source_folder, FACES, source_classification, f"{stripped_filename}_face.jpg"
        )
        faces_dst_path = os.path.join(
            dst_folder,
            FACES,
            dst_classification,
            f"{stripped_filename}_face.jpg",
        )
        shutil.move(faces_src_path, faces_dst_path)

        original_src_path = os.path.join(
            source_folder,
            ORIGINAL,
            source_classification,
            f"{stripped_filename}_original.jpg",
        )
        original_dst_path = os.path.join(
            dst_folder,
            ORIGINAL,
            dst_classification,
            f"{stripped_filename}_original.jpg",
        )
        shutil.move(original_src_path, original_dst_path)

    def move_current_image(self, classification):
        if 0 <= self.current_index < len(self.image_files):
            image_file = self.image_files[self.current_index]

            self.move_image(
                image_file,
                self.source_folder,
                "",
                self.destination_folder,
                classification,
            )

            self.history.append((self.current_index, classification))
            self.current_index += 1
            self.display_image()

    def undo(self, event):
        if self.history:
            last_index, last_classification = self.history.pop()
            image_file = self.image_files[last_index]

            self.move_image(
                image_file,
                self.destination_folder,
                last_classification,
                self.source_folder,
                "",
            )

            self.current_index = last_index
            self.display_image()


def main():
    parser = argparse.ArgumentParser(
        description="Moves and classifies images from input_dir to output_dir"
    )
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
    args = parser.parse_args()

    input_dir = args.input_dir
    output_dir = args.output_dir

    root = tk.Tk()
    app = ImageClassifierApp(root, input_dir, output_dir)
    root.mainloop()


if __name__ == "__main__":
    main()
