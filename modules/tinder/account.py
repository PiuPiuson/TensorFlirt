from typing import List
from dataclasses import dataclass

from modules.tinder.user import User


@dataclass
class Account(User):
    """Represents the profile of the current logged in user"""

    email: str
    phone_number: str
    age_min: int
    age_max: int
    max_distance: int
    gender_filter: List[str]

    @classmethod
    def from_api_data(cls, data, **kwargs):
        """Creates an Account from the data received from the API"""

        email = data["account"].get("account_email", None)
        phone_number = data["account"].get("account_phone_number", None)
        age_min = data["user"]["age_filter_min"]
        age_max = data["user"]["age_filter_max"]
        max_distance = data["user"]["distance_filter"]
        gender_filter = ["Male", "Female"][data["user"]["gender_filter"]]

        return super().from_api_data(
            data["user"],
            email=email,
            phone_number=phone_number,
            age_max=age_max,
            age_min=age_min,
            max_distance=max_distance,
            gender_filter=gender_filter,
            **kwargs,
        )

    def __repr__(self):
        # Extend the representation to include the new fields
        person_repr = super().__repr__()
        return f"{person_repr}, Email: {self.email}, Phone: {self.phone_number}"
