import requests

from dataclasses import dataclass

from modules.tinder.account import Account
from modules.tinder.user import User
from modules.tinder.match import Match


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

    def get_account(self):
        """Gets the account of the current user"""
        data = requests.get(
            f"{BASE_URL}/v2/profile?include=account,user",
            headers={"X-Auth-Token": self._token},
            timeout=self._timeout,
        ).json()
        return Account.from_api_data(data["data"])

    def get_user(self, user_id):
        """Gets the details of a user with a given user_id. The user must be matched or else it returns 403"""
        data = requests.get(
            f"{BASE_URL}/user/{user_id}",
            headers={"X-Auth-Token": self._token},
            timeout=self._timeout,
        ).json()
        return User.from_api_data(data["results"])

    def matches(self, limit=10):
        """Gets the account matches limited by limit"""
        data = requests.get(
            f"{BASE_URL}/v2/matches?count={limit}",
            headers={"X-Auth-Token": self._token},
            timeout=self._timeout,
        ).json()
        return list(
            map(
                lambda match: User.from_api_data(match["person"]),
                data["data"]["matches"],
            )
        )

    @dataclass
    class LikeResult:
        """Holds the result of a like"""

        is_match: bool
        likes_remaining: int

    def like(self, user_id) -> LikeResult:
        """Likes the profile with the given user_id"""
        data = requests.post(
            f"{BASE_URL}/like/{user_id}",
            headers={"X-Auth-Token": self._token},
            timeout=self._timeout,
        ).json()

        return Api.LikeResult(data["match"], data["likes_remaining"])

    def dislike(self, user_id):
        """Passes the profile with the given user_id"""
        requests.post(
            f"{BASE_URL}/pass/{user_id}",
            headers={"X-Auth-Token": self._token},
            timeout=self._timeout,
        ).json()
        return True

    def get_nearby_users(self):
        """Gets nearby users. These are usually random and come in batches of ~20"""
        data = requests.get(
            f"{BASE_URL}/v2/recs/core",
            headers={"X-Auth-Token": self._token},
            timeout=self._timeout,
        ).json()

        users = []
        for result in data.get("data", {}).get("results", []):
            if "user" in result:
                user_data = result["user"]
                user_data["distance_mi"] = result.get("distance_mi", 0)
                user = User.from_api_data(user_data)
                users.append(user)
        return users

    def update_location(self, latitude, longitude):
        """
        Updates the location of the logged in user

        If called too often it can trigger a cool down period where the location is not updated for ~15min

        :param float latitude: The latitude in decimal format (eg. 35.9372)
        :param float longitude: The longitude in decimal format (eg. 22.47239)
        """
        requests.post(
            f"{BASE_URL}/v2/meta",
            headers={"X-Auth-Token": self._token},
            timeout=self._timeout,
            json={"lat": latitude, "lon": longitude},
        ).json()
        return True

    def get_matches(self, include_messages=True, count=100):
        """
        Gets the users that have matches with the account
        
        :param bool include_messages: whether to include users that have messaged
        :param int count: how many users to return
        """
        data = requests.get(
            f"{BASE_URL}/v2/matches?count={count}&message={1 if include_messages else 0}",
            headers={"X-Auth-Token": self._token},
            timeout=self._timeout,
        ).json()

        matches = []
        for result in data.get("data", {}).get("matches", []):
            user = Match.from_api_data(result)
            matches.append(user)
        return matches

    def get_fast_matches(self):
        """Gets fast matches for the account, eg. the users who have liked the account"""
        data = requests.get(
            f"{BASE_URL}/v2/fast-match",
            headers={"X-Auth-Token": self._token},
            timeout=self._timeout,
        ).json()

        users = []
        for result in data.get("data", {}).get("results", []):
            user = User.from_api_data(result["user"])
            users.append(user)
        return users
    
    def get_liked_users(self):
        """Gets fast users this account has liked"""
        data = requests.get(
            f"{BASE_URL}/v2/my-likes",
            headers={"X-Auth-Token": self._token},
            timeout=self._timeout,
        ).json()

        users = []
        for result in data.get("data", {}).get("results", []):
            user = User.from_api_data(result["user"])
            users.append(user)
        return users
