import json
from graphene_django.utils.testing import GraphQLTestCase
from django.db.models import Q

from api.models import Idea, Profile
from .utils import create_user


class TestIdea(GraphQLTestCase):

    @classmethod
    def setUpTestData(cls):
        cls.token_user1, cls.token_user2, cls.token_user3 = cls.create_data()

    def test_create_idea(self):
        # Do query
        response = self.query(
            '''
            mutation{
                createIdea(ideaData: {text:"new_idea", visibility:"public"}){
                    idea{
                        text
                        visibility
                        user{
                          username
                        }
                    }
                }
            }
            ''',
            headers={'HTTP_AUTHORIZATION': f'JWT {self.token_user1}'}
        )
        content = json.loads(response.content)

        # Check response and database
        idea = Idea.objects.get(text=content['data']['createIdea']['idea']['text'])
        self.assertResponseNoErrors(response)
        self.assertEqual(content['data']['createIdea']['idea']['visibility'], idea.visibility.upper())
        self.assertEqual(content['data']['createIdea']['idea']['text'], idea.text)

    def test_update_visibility(self):
        # Do query
        response = self.query(
            '''
            mutation updateIdea($visibility: String!){
                updateIdea(ideaData: {id: 1, visibility: $visibility}){
                    idea{
                        text
                        visibility
                        user{
                          username
                        }
                    }
                }
            }
            ''',
            variables={'visibility': 'public'},
            headers={'HTTP_AUTHORIZATION': f'JWT {self.token_user1}'}
        )
        content = json.loads(response.content)

        # Check response and database
        idea = Idea.objects.get(id=1)
        self.assertResponseNoErrors(response)
        self.assertEqual(content['data']['updateIdea']['idea']['visibility'], idea.visibility.upper())

    def test_delete_idea(self):
        # Do query
        response = self.query(
            '''
            mutation{
                deleteIdea(id: 1){
                    idea{
                        text
                    }
                }
            }
            ''',
            headers={'HTTP_AUTHORIZATION': f'JWT {self.token_user1}'}
        )

        # Check response and database
        self.assertResponseNoErrors(response)
        deleted_idea = Idea.objects.filter(id=1).first()
        self.assertEqual(None, deleted_idea)

    def test_get_ideas_from_a_user(self):
        """ An user (user1) wants to get all its ideas """
        # Do query
        response = self.query(
            '''
            {
                ideas{
                    text
                    visibility
                    user{
                        username
                    }
                }
            }
            ''',
            headers={'HTTP_AUTHORIZATION': f'JWT {self.token_user1}'}
        )
        content = json.loads(response.content)

        # Check response and database
        self.assertResponseNoErrors(response)
        ideas = Idea.objects.filter(user__username='user1')
        self.assertEqual(len(ideas), len(content['data']['ideas']))
        self.assertEqual('user1', content['data']['ideas'][0]['user']['username'])

    def test_get_from_other_user(self):
        """ An user (user1) wants to get the ideas from a followed user (user2) """
        # Do query
        response = self.query(
            '''
            {
                ideas(username: "user2"){
                    text
                    visibility
                    user{
                        username
                    }
                }
            }
            ''',
            headers={'HTTP_AUTHORIZATION': f'JWT {self.token_user1}'}
        )
        content = json.loads(response.content)

        # Check response and database
        self.assertResponseNoErrors(response)
        ideas = Idea.objects.filter(
            Q(user__username='user2', visibility='public')
            | Q(user__username='user2', visibility='protected')
        ).order_by('-created_date')
        self.assertEqual(len(ideas), len(content['data']['ideas']))
        self.assertEqual('user2', content['data']['ideas'][0]['user']['username'])

    def test_get_all_ideas(self):
        """
        An user (user1) wants to get all the ideas, its own,
        public from all the users and protected from its followed users
        """
        # Do query
        response = self.query(
            '''
            {
                allIdeas{
                    text
                    visibility
                    user{
                        username
                    }
                }
            }
            ''',
            headers={'HTTP_AUTHORIZATION': f'JWT {self.token_user1}'}
        )
        content = json.loads(response.content)

        # Check response and database
        self.assertResponseNoErrors(response)
        request_profile = Profile.objects.get(user__username='user1')
        followed_list = request_profile.followed.values_list('username', flat=True)
        ideas = Idea.objects.filter(
            Q(visibility='public')
            | Q(user__username='user1')
            | Q(user__username__in=followed_list, visibility='protected')
        ).order_by('-created_date')
        self.assertEqual(len(ideas), len(content['data']['allIdeas']))

    @staticmethod
    def create_data():
        user1, profile1, token1 = create_user('user1', 'user1@gmail.com', 'user1')
        user2, profile2, token2 = create_user('user2', 'user2@gmail.com', 'user2')
        user3, profile3, token3 = create_user('user3', 'user3@gmail.com', 'user3')

        # User1 follow user2 and user3, user2 follow user3
        profile1.followed.add(user2)
        profile1.followed.add(user3)
        profile2.followers.add(user1)
        profile3.followers.add(user1)
        profile2.followed.add(user3)
        profile3.followers.add(user2)

        Idea.objects.create(user=user1, text='idea1 from user1', visibility='private')
        Idea.objects.create(user=user1, text='idea2 from user1', visibility='public')
        Idea.objects.create(user=user2, text='idea1 from user2', visibility='protected')
        Idea.objects.create(user=user3, text='idea1 from user3', visibility='protected')

        return token1, token2, token3
