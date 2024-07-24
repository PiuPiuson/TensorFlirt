import requests

from user import User
from person import Person


BASE_URL = "https://api.gotinder.com"
DEFAULT_TIMEOUT = 300


class Api:
    """
    Deals with the tinder API

    :param str token: X-Auth-Token obtained from browser
    """

    def __init__(self, token, timeout=DEFAULT_TIMEOUT):
        self._token = token
        self._timeout = timeout

    def getUser(self):
        data = requests.get(
            f"{BASE_URL}/v2/profile?include=account%2Cuser",
            headers={"X-Auth-Token": self._token},
            timeout=self._timeout,
        ).json()
        return User.from_api_data(data)

    def matches(self, limit=10):
        data = requests.get(
            BASE_URL + f"/v2/matches?count={limit}",
            headers={"X-Auth-Token": self._token},
            timeout=self._timeout,
        ).json()
        return list(
            map(
                lambda match: Person.from_api_data(match["person"]),
                data["data"]["matches"],
            )
        )

    def like(self, user_id):
        data = requests.get(
            BASE_URL + f"/like/{user_id}",
            headers={"X-Auth-Token": self._token},
            timeout=self._timeout,
        ).json()
        return {"is_match": data["match"], "liked_remaining": data["likes_remaining"]}

    def dislike(self, user_id):
        requests.get(
            BASE_URL + f"/pass/{user_id}",
            headers={"X-Auth-Token": self._token},
            timeout=self._timeout,
        ).json()
        return True

    def nearby_persons(self):
        data = requests.get(
            BASE_URL + "/v2/recs/core",
            headers={"X-Auth-Token": self._token},
            timeout=self._timeout,
        ).json()
        return list(
            map(
                lambda user: Person.from_api_data(user["user"]), data["data"]["results"]
            )
        )
