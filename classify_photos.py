import os
import argparse
import tkinter as tk

from PIL import ImageTk, Image
from tqdm import tqdm


DEFAULT_INPUT_DIRECTORY = "images/cropped"
DEFAULT_OUTPUT_DIRECTORY = "images/classified"

POSITIVE = "positive"
NEGATIVE = "negative"


class ImageClassifierApp:
    def __init__(
        self, root, source_folder, positive_folder, negative_folder, resize_height=500
    ):
        self.root = root
        self.source_folder = source_folder
        self.positive_folder = positive_folder
        self.negative_folder = negative_folder
        self.resize_height = resize_height
        self.current_index = 0
        self.history = []
        self.image_files = []

        if not os.path.exists(positive_folder):
            os.makedirs(positive_folder)
        if not os.path.exists(negative_folder):
            os.makedirs(negative_folder)

        self.already_classified_images = set(
            [f for f in os.listdir(self.positive_folder) if f.endswith(".jpg")]
            + [f for f in os.listdir(self.negative_folder) if f.endswith(".jpg")]
        )

        self.root.bind("<Right>", self.copy_to_positive)
        self.root.bind("<Left>", self.copy_to_negative)
        self.root.bind("<Control-z>", self.undo)

        self.label = tk.Label(root)
        self.label.pack()
        
        self.load_images()

        self.display_image()

    def load_images(self):
        source_images = [
            f for f in os.listdir(self.source_folder) if f.endswith(".jpg")
        ]

        preselected_negative = [image for image in source_images if "negative" in image]
        self.image_files = [
            image
            for image in source_images
            if "negative" not in image and image not in self.already_classified_images
        ]

        for image in tqdm(preselected_negative, desc="Copying pre-classified negatives"):
            src_path = os.path.join(self.source_folder, image)
            dst_path = os.path.join(self.negative_folder, image)

            image = Image.open(src_path).convert("L")
            image.save(dst_path)

    def resize_image(self, image):
        width, height = image.size
        new_height = self.resize_height
        new_width = int(new_height * width / height)
        return image.resize((new_width, new_height))

    def display_image(self):
        if 0 <= self.current_index < len(self.image_files):
            image_path = os.path.join(
                self.source_folder, self.image_files[self.current_index]
            )
            image = Image.open(image_path)
            image = self.resize_image(image)
            self.tk_image = ImageTk.PhotoImage(image)
            self.label.config(image=self.tk_image)
            self.root.title(
                f"Image Classifier - {self.image_files[self.current_index]} ({self.current_index + 1}/{len(self.image_files)})"
            )

    def copy_to_positive(self, event):
        self.copy_image(self.positive_folder)

    def copy_to_negative(self, event):
        self.copy_image(self.negative_folder)

    def copy_image(self, destination_folder):
        if 0 <= self.current_index < len(self.image_files):
            image_file = self.image_files[self.current_index]
            src_path = os.path.join(self.source_folder, image_file)
            dst_path = os.path.join(destination_folder, image_file)

            image = Image.open(src_path).convert("L")
            image.save(dst_path)

            self.history.append((self.current_index, destination_folder))
            self.current_index += 1
            self.display_image()

    def undo(self, event):
        if self.history:
            last_index, last_folder = self.history.pop()
            image_file = self.image_files[last_index]
            src_path = os.path.join(last_folder, image_file)
            os.remove(src_path)

            self.current_index = last_index
            self.display_image()


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
    args = parser.parse_args()

    input_dir = args.input_dir
    output_dir = args.output_dir

    positive_dir = os.path.join(output_dir, POSITIVE)
    negative_dir = os.path.join(output_dir, NEGATIVE)

    root = tk.Tk()
    app = ImageClassifierApp(root, input_dir, positive_dir, negative_dir, 1200)
    root.mainloop()


if __name__ == "__main__":
    main()
