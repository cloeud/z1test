import json
from graphene_django.utils.testing import GraphQLTestCase

from api.models import User
from .utils import create_user


class TestUser(GraphQLTestCase):
    def setUp(self):
        self.token_user1 = self.create_data()

    def test_create_user(self):
        # Do query
        response = self.query(
            '''
            mutation{
                createUser(userData: {username:"test", email:"test@gmail.com", password:"test"}){
                    user{
                      username
                      email,
                      password
                    }
                    token
                }
            }
            '''
        )
        content = json.loads(response.content)

        # Check response and database
        user = User.objects.get(username=content['data']['createUser']['user']['username'])
        self.assertResponseNoErrors(response)
        self.assertEqual(content['data']['createUser']['user']['username'], user.username)
        self.assertEqual(content['data']['createUser']['user']['email'], user.email)

    def test_create_duplicate_username(self):
        # Do query
        response = self.query(
            '''
            mutation{
                createUser(userData: {username:"user1", email:"new_email@gmail.com", password:"new_password"}){
                    user{
                      username
                      email,
                      password
                    }
                    token
                }
            }
            '''
        )

        # Check response
        self.assertResponseHasErrors(response)

    def test_update_password(self):
        # Do query
        response = self.query(
            '''
            mutation updateUser($password: String!){
                updateUser(userData: {password: $password}){
                    user{
                      username
                      email,
                      password
                    }
                }
            }
            ''',
            variables={'password': 'new_password'},
            headers={'HTTP_AUTHORIZATION': f'JWT {self.token_user1}'}
        )

        # Check response
        self.assertResponseNoErrors(response)

    def test_delete_user(self):
        # Do query
        response = self.query(
            '''
            mutation{
                deleteUser{
                    user{
                        username
                    }
                }
            }
            ''',
            headers={'HTTP_AUTHORIZATION': f'JWT {self.token_user1}'}
        )

        # Check response and database
        self.assertResponseNoErrors(response)
        deleted_user = User.objects.filter(username='user1').first()
        self.assertEqual(None, deleted_user)

    def test_login(self):
        response = self.query(
            '''
            mutation tokenAuth($username: String!, $password: String!){
                tokenAuth(username: $username, password: $password){
                    token
                }
            }
            ''',
            variables={'username': 'user1', 'password': 'user1'}
        )
        content = json.loads(response.content)

        return content['data']['tokenAuth']['token']

    @staticmethod
    def create_data():
        user1, profile1, token1 = create_user('user1', 'user1@gmail.com', 'user1')

        return token1

