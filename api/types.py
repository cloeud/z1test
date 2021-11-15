import graphene
from graphene_django.types import DjangoObjectType
from api.models import User, FollowRequest, Idea


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ('username', 'email', 'password')


class FollowRequestType(DjangoObjectType):
    class Meta:
        model = FollowRequest
        fields = '__all__'


class IdeaType(DjangoObjectType):
    class Meta:
        model = Idea
        fields = '__all__'
