from dataclasses import dataclass
from datetime import datetime

from modules.tinder.user import User


@dataclass
class Match:
    user: User
    id: str
    common_friend_count: int
    common_like_count: int
    match_date: datetime
    last_activity: datetime
    message_count: int
    pending: bool
    is_super_like: bool
    is_boost_match: bool
    is_dead: bool

    @classmethod
    def from_api_data(cls, data, **kwargs):
        """Creates a Match from data received from the API"""

        return cls(
            user=User.from_api_data(data["person"]),
            id=data["_id"],
            common_friend_count=data["common_friend_count"],
            common_like_count=data["common_like_count"],
            match_date=datetime.strptime(data["created_date"], "%Y-%m-%dT%H:%M:%S.%fZ"),
            last_activity=datetime.strptime(
                data["last_activity_date"], "%Y-%m-%dT%H:%M:%S.%fZ"
            ),
            message_count=data["message_count"],
            pending=data["pending"],
            is_super_like=data["is_super_like"],
            is_boost_match=data["is_boost_match"],
            is_dead=data["dead"],
        )
