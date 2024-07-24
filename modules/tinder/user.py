from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from geopy.geocoders import Nominatim

GEOLOCATOR = Nominatim(user_agent="TensorFlirt")


@dataclass
class User:
    """Represents the profile of a swipeable user"""

    id: str
    name: Optional[str]
    bio: Optional[str]
    distance: float
    birth_date: Optional[datetime]
    gender: str
    images: List[str]
    jobs: List[dict]
    schools: List[dict]
    location: Optional[dict]

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
            images=list(map(lambda photo: photo["url"], data.get("photos", []))),
            jobs=list(
                map(
                    lambda job: {
                        "title": job.get("title", {}).get("name"),
                        "company": job.get("company", {}).get("name"),
                    },
                    data.get("jobs", []),
                )
            ),
            schools=list(map(lambda school: school["name"], data.get("schools", []))),
            location=(
                GEOLOCATOR.reverse(f'{data["pos"]["lat"]}, {data["pos"]["lon"]}')
                if data.get("pos", False)
                else None
            ),
            **kwargs,
        )

    # def __repr__(self):
    #     return f"{self.id} - {self.name} ({self.birth_date.strftime('%d.%m.%Y')})"
