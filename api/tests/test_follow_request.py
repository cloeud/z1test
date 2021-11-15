import json
from graphene_django.utils.testing import GraphQLTestCase

from api.models import FollowRequest, Profile
from .utils import create_user


class TestIdea(GraphQLTestCase):

    @classmethod
    def setUpTestData(cls):
        cls.token_user1, cls.token_user2, cls.token_user3 = cls.create_data()

    def test_create_follow_request(self):
        # Do query
        response = self.query(
            '''
            mutation{
                createFollowRequest(followRequestData: {toUser: "user1"}){
                    followRequest{
                        fromUser{
                          username
                        }
                        toUser{
                          username
                        }
                        status
                    }
                }
            }
            ''',
            headers={'HTTP_AUTHORIZATION': f'JWT {self.token_user2}'}
        )
        content = json.loads(response.content)

        # Check response and database
        follow_request = FollowRequest.objects.get(from_user__username='user2', to_user__username='user1')
        self.assertResponseNoErrors(response)
        self.assertEqual(
            content['data']['createFollowRequest']['followRequest']['fromUser']['username'],
            follow_request.from_user.username
        )
        self.assertEqual(
            content['data']['createFollowRequest']['followRequest']['toUser']['username'],
            follow_request.to_user.username
        )
        self.assertEqual(
            content['data']['createFollowRequest']['followRequest']['status'],
            follow_request.status.upper()
        )

    def test_accept_follow_request(self):
        # Do query
        response = self.query(
            '''
            mutation{
                updateFollowRequest(followRequestData: {fromUser: "user1", status: "accepted"}){
                    followRequest{
                        fromUser{
                          username
                        }
                        toUser{
                          username
                        }
                        status
                    }
                }
            }
            ''',
            headers={'HTTP_AUTHORIZATION': f'JWT {self.token_user2}'}
        )
        content = json.loads(response.content)

        # Check response and database
        follow_request = FollowRequest.objects.get(from_user__username='user1', to_user__username='user2')
        profile1 = Profile.objects.get(user__username='user1')
        profile2 = Profile.objects.get(user__username='user2')
        followers_user2 = profile2.followers.values_list('username', flat=True)
        followed_user1 = profile1.followed.values_list('username', flat=True)
        self.assertResponseNoErrors(response)
        self.assertEqual(
            content['data']['updateFollowRequest']['followRequest']['status'],
            follow_request.status.upper()
        )
        self.assertEqual('user1' in followers_user2, True)
        self.assertEqual('user2' in followed_user1, True)

    def test_reject_follow_request(self):
        # Do query
        response = self.query(
            '''
            mutation{
                updateFollowRequest(followRequestData: {fromUser: "user1", status: "rejected"}){
                    followRequest{
                        fromUser{
                          username
                        }
                        toUser{
                          username
                        }
                        status
                    }
                }
            }
            ''',
            headers={'HTTP_AUTHORIZATION': f'JWT {self.token_user3}'}
        )
        content = json.loads(response.content)

        # Check response and database
        follow_request = FollowRequest.objects.get(from_user__username='user1', to_user__username='user3')
        profile1 = Profile.objects.get(user__username='user1')
        profile3 = Profile.objects.get(user__username='user3')
        followers_user3 = profile3.followers.values_list('username', flat=True)
        followed_user1 = profile1.followed.values_list('username', flat=True)
        self.assertResponseNoErrors(response)
        self.assertEqual(
            content['data']['updateFollowRequest']['followRequest']['status'],
            follow_request.status.upper()
        )
        self.assertEqual('user1' in followers_user3, False)
        self.assertEqual('user2' in followed_user1, False)

    def test_delete_follower(self):
        # Do query
        response = self.query(
            '''
            mutation{
                deleteFollower(follower: "user2"){
                    followers{
                        username
                    }
                }
            }
            ''',
            headers={'HTTP_AUTHORIZATION': f'JWT {self.token_user3}'}
        )

        # Check response and database
        self.assertResponseNoErrors(response)
        profile2 = Profile.objects.get(user__username='user2')
        profile3 = Profile.objects.get(user__username='user3')
        followers_user3 = profile3.followers.values_list('username', flat=True)
        followed_user2 = profile2.followed.values_list('username', flat=True)
        self.assertEqual('user2' in followers_user3, False)
        self.assertEqual('user3' in followed_user2, False)

    def test_delete_followed(self):
        # Do query
        response = self.query(
            '''
            mutation{
                deleteFollowed(followed: "user3"){
                    allFollowed{
                        username
                    }
                }
            }
            ''',
            headers={'HTTP_AUTHORIZATION': f'JWT {self.token_user2}'}
        )

        # Check response and database
        self.assertResponseNoErrors(response)
        profile2 = Profile.objects.get(user__username='user2')
        profile3 = Profile.objects.get(user__username='user3')
        followers_user3 = profile3.followers.values_list('username', flat=True)
        followed_user2 = profile2.followed.values_list('username', flat=True)
        self.assertEqual('user2' in followers_user3, False)
        self.assertEqual('user3' in followed_user2, False)

    @staticmethod
    def create_data():
        user1, profile1, token1 = create_user('user1', 'user1@gmail.com', 'user1')
        user2, profile2, token2 = create_user('user2', 'user2@gmail.com', 'user2')
        user3, profile3, token3 = create_user('user3', 'user3@gmail.com', 'user3')

        FollowRequest.objects.create(from_user=user1, to_user=user2, status='pending')
        FollowRequest.objects.create(from_user=user1, to_user=user3, status='pending')

        # User2 follow user3
        profile3.followers.add(user2)
        profile2.followed.add(user2)

        return token1, token2, token3
