import requests

from dataclasses import dataclass
from typing import Optional

from io import BytesIO

import PIL.Image


@dataclass
class Image:
    """Represents a user image"""

    @dataclass
    class BoundingBox:
        """A bounding box for image cropping"""

        width_percent: float
        x_offset_percent: float
        height_percent: float
        y_offset_percent: float

        @classmethod
        def from_api_bounding_box(cls, data):
            """Creates a bounding box from data received from the API"""
            return cls(
                width_percent=data["width_pct"],
                x_offset_percent=data["x_offset_pct"],
                height_percent=data["height_pct"],
                y_offset_percent=data["y_offset_pct"],
            )

    url: str
    face_box: Optional[BoundingBox]
    user_box: Optional[BoundingBox]
    image: PIL.Image

    @classmethod
    def from_api_data(cls, data):
        """Creates an image from API data"""

        face = None
        user = None

        url = data["url"]

        try:
            face = Image.BoundingBox.from_api_bounding_box(data["crop_info"]["algo"])
        except KeyError:
            pass

        try:
            user = Image.BoundingBox.from_api_bounding_box(data["crop_info"]["user"])
        except KeyError:
            pass

        return cls(url=url, face_box=face, user_box=user, image=None)

    def _crop(self, bounding_box) -> PIL.Image:
        """Crops the image into a square from the given bounding box."""
        img_width, img_height = self.image.size

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
        return self.image.crop((left, top, right, bottom))

    def load(self):
        """Loads the URL image into the object"""
        req = requests.get(self.url, stream=True, timeout=300)
        if req.status_code != 200:
            raise requests.RequestException(f"Could not load image, status code {req.status_code}")

        image_bytes = BytesIO(req.content)
        self.image = PIL.Image.open(image_bytes)
        self.image = self.image.convert("RGB")

    def get_user(self) -> PIL.Image:
        """Gets the cropped image of the user, contained by the user bounding box"""
        if not self.user_box:
            raise ValueError("Image does not have user bounding box")

        return self._crop(self.user_box)

    def get_face(self) -> PIL.Image:
        """Gets the cropped image of the face, contained by the face bounding box"""
        if not self.face_box:
            raise ValueError("Image does not have face bounding box")

        return self._crop(self.face_box)

    def get_original(self) -> PIL.Image:
        """Gets the unmodified original image"""
        return self.image
