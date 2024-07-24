from typing import List
from dataclasses import dataclass

from person import Person


@dataclass
class User(Person):
    """Represents the profile of the current logged in user"""

    email: str
    phone_number: str
    age_min: int
    age_max: int
    max_distance: int
    gender_filter: List[str]

    @classmethod
    def from_api_data(cls, data):
        """Creates a User from the data received from the API"""

        person_instance = super().from_api_data(data)

        email = data.get("email", None)
        phone_number = data.get("phone_number", None)
        age_min = data["user"]["age_filter_min"]
        age_max = data["user"]["age_filter_max"]
        max_distance = data["user"]["distance_filter"]
        gender_filter = ["Male", "Female"][data["user"]["gender_filter"]]

        return cls(
            id=person_instance.id,
            name=person_instance.name,
            bio=person_instance.bio,
            distance=person_instance.distance,
            birth_date=person_instance.birth_date,
            gender=person_instance.gender,
            images=person_instance.images,
            jobs=person_instance.jobs,
            schools=person_instance.schools,
            location=person_instance.location,
            email=email,
            phone_number=phone_number,
            age_max=age_max,
            age_min=age_min,
            max_distance=max_distance,
            gender_filter=gender_filter,
        )

    def __repr__(self):
        # Extend the representation to include the new fields
        person_repr = super().__repr__()
        return f"{person_repr}, Email: {self.email}, Phone: {self.phone_number}"
