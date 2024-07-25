from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from geopy.geocoders import Nominatim

GEOLOCATOR = Nominatim(user_agent="TensorFlirt")


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
    face: Optional[BoundingBox]
    user: Optional[BoundingBox]

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

        return cls(url=url, face=face, user=user)


@dataclass
class Job:
    """A user's job"""

    title: Optional[str]
    company: Optional[str]

    @classmethod
    def from_api_data(cls, data):
        """Creates a job from API data"""
        return cls(
            title=data.get("title", {}).get("name", None),
            company=data.get("company", {}).get("name", None),
        )


@dataclass
class User:
    """Represents the profile of a swipeable user"""

    id: str
    name: Optional[str]
    bio: Optional[str]
    distance: float
    birth_date: Optional[datetime]
    gender: str
    images: List[Image]
    jobs: List[Job]
    schools: List[str]
    location: Optional[dict]
    looking_for: Optional[str]

    @classmethod
    def from_api_data(cls, data, **kwargs):
        """Creates a User from the data received from the API"""

        return cls(
            id=data["_id"],
            name=data.get("name", None),
            bio=data.get("bio", None),
            distance=data.get("distance_mi", 0) / 1.60934,
            birth_date=(
                datetime.strptime(data["birth_date"], "%Y-%m-%dT%H:%M:%S.%fZ")
                if data.get("birth_date", False)
                else None
            ),
            gender=["Male", "Female", "Unknown"][data.get("gender", 2)],
            images=list(
                map(
                    Image.from_api_data,
                    data.get("photos", []),
                )
            ),
            jobs=list(
                map(
                    Job.from_api_data,
                    data.get("jobs", []),
                )
            ),
            schools=list(map(lambda school: school["name"], data.get("schools", []))),
            location=(
                GEOLOCATOR.reverse(f'{data["pos"]["lat"]}, {data["pos"]["lon"]}')
                if data.get("pos", False)
                else None
            ),
            looking_for=data.get("relationship_intent", {}).get("body_text", None),
            **kwargs,
        )

    def __repr__(self):
        return f"{self.id} - {self.name} ({self.birth_date.strftime('%d.%m.%Y')})"
