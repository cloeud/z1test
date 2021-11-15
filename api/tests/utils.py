# Third party
from graphql_jwt.shortcuts import get_token

# Local
from api.models import User, Profile


# Functions to assist in test development
def create_user(username, email, password):
    user = User(username=username, email=email)
    user.set_password(password)
    user.save()

    profile = Profile(user=user)
    profile.save()

    token = get_token(user)

    return user, profile, token



