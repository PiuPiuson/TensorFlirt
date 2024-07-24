import os
from dotenv import load_dotenv

load_dotenv()

from modules.tinder.api import Api
from modules.tinder.user import User
from modules.tinder.account import Account


def main():
    auth_token = os.getenv("AUTH_TOKEN")
    if not auth_token:
        print(
            "AUTH_TOKEN not present in the .env file \nEnsure you have a .env file and that the AUTH_TOKEN key has the X-Auth-Token obtained from your browser"
        )
        return
    
    tinderApi = Api(auth_token)
    
    nearby_users = tinderApi.get_nearby_users()
    
    print(len(nearby_users))


if __name__ == "__main__":
    main()
