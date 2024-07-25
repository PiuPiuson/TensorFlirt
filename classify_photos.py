import os
import shutil
import argparse
import sys
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QVBoxLayout,
    QMessageBox
)
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt

from PIL import Image

DEFAULT_INPUT_DIRECTORY = "images/downloaded"
DEFAULT_OUTPUT_DIRECTORY = "images/classified"

POSITIVE = "positive"
NEGATIVE = "negative"
ORIGINAL = "original"
FACES = "faces"
USERS = "users"


class ImageClassifierApp(QWidget):
    def __init__(self, source_folder, destination_folder):
        super().__init__()
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

        self.init_ui()
        self.load_images()
        self.display_image()

    def init_ui(self):
        self.layout = QVBoxLayout()

        self.image_label = QLabel(self)
        self.layout.addWidget(self.image_label)

        self.setWindowTitle("Image Classifier")
        self.setLayout(self.layout)
        self.setFixedSize(800, 600)

        self.setMouseTracking(True)
        self.show()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Right:
            self.move_current_image(POSITIVE)
        elif event.key() == Qt.Key.Key_Left:
            self.move_current_image(NEGATIVE)
        elif (
            event.modifiers() & Qt.KeyboardModifier.ControlModifier
            and event.key() == Qt.Key.Key_Z
        ):
            self.undo()

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
            image = image.convert("RGB")
            qim = QImage(
                image.tobytes(), image.width, image.height, QImage.Format.Format_RGB888
            )
            pix = QPixmap.fromImage(qim)
            self.image_label.setPixmap(
                pix.scaled(800, 600, Qt.AspectRatioMode.KeepAspectRatio)
            )
            self.setWindowTitle(
                f"Image Classifier ({self.current_index + 1}/{len(self.image_files)}) - {self.image_files[self.current_index]}"
            )
        else:
            QMessageBox.information(
                self,
                "No More Images",
                "No more images to classify. The application will now close.",
            )
            self.image_label.clear()
            self.setWindowTitle("Image Classifier - Complete")
            self.close()

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

    def undo(self):
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
        help="Input directory from which to load images",
        dest="input_dir",
    )
    args = parser.parse_args()

    app = QApplication(sys.argv)
    ex = ImageClassifierApp(args.input_dir, args.output_dir)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
