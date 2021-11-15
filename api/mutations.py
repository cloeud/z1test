# Third party
import graphene
from graphql_jwt.decorators import login_required
from graphql_jwt.shortcuts import get_token

# Local
from .models import User, FollowRequest, Profile, Idea
from .types import UserType, FollowRequestType, IdeaType


class UserInput(graphene.InputObjectType):
    id = graphene.ID()
    username = graphene.String()
    email = graphene.String()
    password = graphene.String()


class FollowRequestInput(graphene.InputObjectType):
    id = graphene.ID()
    from_user = graphene.String()
    to_user = graphene.String()
    status = graphene.String()


class IdeaInput(graphene.InputObjectType):
    id = graphene.ID()
    text = graphene.String()
    visibility = graphene.String()
    user = graphene.String()


class CreateUser(graphene.Mutation):
    class Arguments:
        user_data = UserInput()

    user = graphene.Field(UserType)
    token = graphene.String()

    @staticmethod
    def mutate(root, info, user_data=None):
        user = User(
            username=user_data.username,
            email=user_data.email
        )
        user.set_password(user_data.password)
        user.save()

        # Once the user is created, the profile is created too
        profile = Profile(user=user)
        profile.save()

        # The token is obtained
        token = get_token(user)

        return CreateUser(user=user, token=token)


class CreateFollowRequest(graphene.Mutation):
    class Arguments:
        follow_request_data = FollowRequestInput()

    follow_request = graphene.Field(FollowRequestType)

    @staticmethod
    @login_required
    def mutate(root, info, follow_request_data=None):
        from_user = info.context.user
        to_user = User.objects.get(username=follow_request_data.to_user)
        # If the request was previously created, it will not be created again
        if not FollowRequest.objects.filter(from_user__username=from_user.username, to_user__username=to_user.username):
            follow_request = FollowRequest(
                from_user=from_user,
                to_user=to_user,
                status='pending'
            )
            follow_request.save()
            return CreateFollowRequest(follow_request=follow_request)
        else:
            return CreateFollowRequest(follow_request=None)


class CreateIdea(graphene.Mutation):
    class Arguments:
        idea_data = IdeaInput()

    idea = graphene.Field(IdeaType)

    @staticmethod
    @login_required
    def mutate(root, info, idea_data=None):
        idea = Idea(
            text=idea_data.text,
            visibility=idea_data.visibility,
            user=info.context.user
        )
        idea.save()
        return CreateIdea(idea=idea)


class UpdateUser(graphene.Mutation):
    class Arguments:
        user_data = UserInput()

    user = graphene.Field(UserType)

    @staticmethod
    @login_required
    def mutate(root, info, user_data=None):
        user = info.context.user
        email = user_data.get('email')
        password = user_data.get('password')
        username = user_data.get('username')

        if username:
            user.username = username
        if email:
            user.email = email
        if password:
            user.set_password(password)

        user.save()
        return UpdateUser(user=user)


class UpdateFollowRequest(graphene.Mutation):
    class Arguments:
        follow_request_data = FollowRequestInput()

    follow_request = graphene.Field(FollowRequestType)

    @staticmethod
    @login_required
    def mutate(root, info, follow_request_data=None):
        # Check the follow request exists
        follow_request = FollowRequest.objects.get(
            to_user__username=info.context.user.username,
            from_user__username=follow_request_data.from_user
        )
        if follow_request:
            # If the request was accepted or rejected, the update is not allowed
            if follow_request.status not in {'accepted', 'rejected'}:
                follow_request.status = follow_request_data.status
                # Add the follower and followed to their respective lists if the new status is accepted
                if follow_request_data.status == 'accepted':
                    from_user = User.objects.get(username=follow_request.from_user.username)
                    profile_from_user = Profile.objects.get(user__username=from_user.username)
                    profile_to_user = Profile.objects.get(user__username=info.context.user.username)
                    profile_to_user.followers.add(from_user)
                    profile_from_user.followed.add(info.context.user)
                follow_request.save()
                return UpdateFollowRequest(follow_request=follow_request)
            else:
                return UpdateFollowRequest(follow_request=follow_request)
        return UpdateFollowRequest(follow_request=None)


class UpdateIdea(graphene.Mutation):
    class Arguments:
        idea_data = IdeaInput(required=True)

    idea = graphene.Field(IdeaType)

    @staticmethod
    @login_required
    def mutate(root, info, idea_data):
        idea = Idea.objects.get(id=idea_data.id, user__username=info.context.user.username)
        text = idea_data.get('text')
        visibility = idea_data.get('visibility')
        if idea:
            if text:
                idea.text = text
            if visibility:
                idea.visibility = visibility
            idea.save()
            return UpdateIdea(idea=idea)
        return UpdateIdea(idea=None)


class DeleteUser(graphene.Mutation):

    user = graphene.Field(UserType)

    @staticmethod
    @login_required
    def mutate(root, info):
        user = User.objects.get(username=info.context.user.username)
        if user:
            user.delete()

        return DeleteUser(user=None)


class DeleteIdea(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    idea = graphene.Field(IdeaType)

    @staticmethod
    @login_required
    def mutate(root, info, id):
        idea = Idea.objects.get(pk=id, user__username=info.context.user.username)
        if idea:
            idea.delete()

        return DeleteIdea(idea=idea)


class DeleteFollower(graphene.Mutation):
    class Arguments:
        follower = graphene.String()

    followers = graphene.List(UserType)

    @staticmethod
    def mutate(root, info, follower):
        profile = Profile.objects.get(user__username=info.context.user.username)
        follower = User.objects.get(username=follower)
        profile.followers.remove(follower)
        profile_follower = Profile.objects.get(user__username=follower)
        profile_follower.followed.remove(info.context.user)
        return DeleteFollower(followers=profile.followers.all())


class DeleteFollowed(graphene.Mutation):
    class Arguments:
        followed = graphene.String()

    all_followed = graphene.List(UserType)

    @staticmethod
    def mutate(root, info, followed):
        profile = Profile.objects.get(user__username=info.context.user.username)
        followed = User.objects.get(username=followed)
        profile.followed.remove(followed)
        profile_followed = Profile.objects.get(user__username=followed)
        profile_followed.followers.remove(info.context.user)
        return DeleteFollowed(all_followed=profile.followed.all())
