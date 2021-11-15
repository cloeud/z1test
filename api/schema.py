# Third party
import graphene
import graphql_jwt
from graphql_jwt.decorators import login_required
from django.db.models import Q

# Local
from .models import User, FollowRequest, Idea, Profile
from .types import UserType, FollowRequestType, IdeaType
from .mutations import CreateUser, UpdateUser, DeleteUser, CreateFollowRequest, UpdateFollowRequest, CreateIdea, \
    UpdateIdea, DeleteIdea, DeleteFollower, DeleteFollowed


class Query(graphene.ObjectType):
    users = graphene.List(UserType)
    user = graphene.List(UserType, username=graphene.String())

    requests = graphene.List(FollowRequestType, status=graphene.String())

    ideas = graphene.List(IdeaType, username=graphene.String(), visibility=graphene.String())
    all_ideas = graphene.List(IdeaType)

    followers_by_user = graphene.List(UserType)
    followed_by_user = graphene.List(UserType)

    @login_required
    def resolve_users(self, info):
        if info.context.user.is_superuser:
            return User.objects.all()
        else:
            return None

    @login_required
    def resolve_user(self, info, **kwargs):
        username = kwargs.get('username')
        result = None

        if username is not None:
            result = User.objects.filter(username__icontains=username)

        return result

    @login_required
    def resolve_requests(self, info, **kwargs):
        status = kwargs.get('status')
        to_user = info.context.user.username

        if status is not None:
            result = FollowRequest.objects.filter(status=status, to_user__username=to_user)
        else:
            result = FollowRequest.objects.filter(to_user__username=to_user)

        return result

    @login_required
    def resolve_ideas(self, info, **kwargs):
        username = kwargs.get('username')
        visibility = kwargs.get('visibility')
        request_username = info.context.user.username

        if username is not None:
            is_follower = Profile.objects.filter(user__username=request_username, followed__username=username)
            if is_follower:
                result = Idea.objects.filter(
                    user__username=username,
                    visibility__in=['public', 'protected']
                ).order_by('-created_date')
            else:
                result = Idea.objects.filter(user__username=username, visibility='public').order_by('-created_date')
        elif visibility is not None:
            result = Idea.objects.filter(
                user__username=request_username,
                visibility=visibility
            ).order_by('-created_date')
        else:
            result = Idea.objects.filter(user__username=request_username).order_by('-created_date')

        return result

    @login_required
    def resolve_all_ideas(self, info, **kwargs):
        request_username = info.context.user.username
        request_profile = Profile.objects.get(user__username=request_username)
        followed_list = request_profile.followed.values_list('username', flat=True)
        ideas = Idea.objects.filter(
            Q(visibility='public')
            | Q(user__username=request_username)
            | Q(user__username__in=followed_list, visibility='protected')
        ).order_by('-created_date')

        return ideas


    @login_required
    def resolve_followers_by_user(self, info, **kwargs):
        username = info.context.user.username
        result = None

        if username:
            profile = Profile.objects.get(user__username=username)
            result = profile.followers.all()

        return result

    @login_required
    def resolve_followed_by_user(self, info, **kwargs):
        username = info.context.user.username
        result = None

        if username:
            profile = Profile.objects.get(user__username=username)
            result = profile.followed.all()

        return result


class Mutation(graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()

    create_user = CreateUser.Field()
    update_user = UpdateUser.Field()
    delete_user = DeleteUser.Field()

    create_follow_request = CreateFollowRequest.Field()
    update_follow_request = UpdateFollowRequest.Field()

    create_idea = CreateIdea.Field()
    update_idea = UpdateIdea.Field()
    delete_idea = DeleteIdea.Field()

    delete_follower = DeleteFollower.Field()
    delete_followed = DeleteFollowed.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
