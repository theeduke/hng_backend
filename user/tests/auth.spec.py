from django.utils import timezone
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from django.test import TestCase


from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from userorganization.models import CustomUser, Organisation
from userorganization.token_utils import generate_access_token  # Updated import
import uuid

class TokenGenerationTestCase(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='testuser@example.com',
            password='password123',
            first_name='Test',
            last_name='User'
        )

    def test_generate_access_token(self):
        access_token = generate_access_token(self.user)
        decoded_token = AccessToken(access_token)

        self.assertEqual(decoded_token['userId'], str(self.user.userId))
        self.assertEqual(decoded_token['email'], self.user.email)
        self.assertTrue('issued_at' in decoded_token)
        self.assertTrue('expiry' in decoded_token)
        self.assertLessEqual(decoded_token['issued_at'], timezone.now().timestamp())

class OrganisationAccessTestCase(APITestCase):

    def setUp(self):
        self.user1 = CustomUser.objects.create_user(
            email='user1@example.com',
            password='password123',
            first_name='User',
            last_name='One'
        )
        self.user2 = CustomUser.objects.create_user(
            email='user2@example.com',
            password='password123',
            first_name='User',
            last_name='Two'
        )
        self.organisation = Organisation.objects.create(name="User One's Organisation")
        self.organisation.users.add(self.user1)

    # def test_user_cannot_access_other_users_organisation(self):
    #     # Authenticate user2 and try to access user1's organisation
    #     self.client.force_authenticate(user=self.user2)
    #     response = self.client.get(f'/api/organisations/{self.organisation.orgId}')
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class UserOrganisationTestCase(APITestCase):

    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.user_data = {
            'email': 'testuser@example.com',
            'password': 'password123',
            'first_name': 'Test',
            'last_name': 'User'
        }

    def test_register_user_successfully_with_default_organisation(self):
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('accessToken', response.data['data'])
        self.assertIn('user', response.data['data'])
        self.assertEqual(response.data['data']['user']['email'], self.user_data['email'])
        self.assertEqual(response.data['data']['user']['first_name'], self.user_data['first_name'])
        self.assertEqual(response.data['data']['user']['last_name'], self.user_data['last_name'])
        self.assertTrue(Organisation.objects.filter(name="Test's Organisation").exists())

    def test_login_user_successfully(self):
        self.client.post(self.register_url, self.user_data, format='json')
        response = self.client.post(self.login_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('accessToken', response.data['data'])
        self.assertIn('user', response.data['data'])
        self.assertEqual(response.data['data']['user']['email'], self.user_data['email'])

    def test_register_user_fails_if_required_fields_missing(self):
        for field in ['first_name', 'last_name', 'email', 'password']:
            user_data = self.user_data.copy()
            del user_data[field]
            response = self.client.post(self.register_url, user_data, format='json')
            self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
            self.assertIn('errors', response.data)

    def test_register_user_fails_if_duplicate_email(self):
        self.client.post(self.register_url, self.user_data, format='json')
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIn('errors', response.data)

    # def test_register_user_fails_if_duplicate_userId(self):
    #     # Register the first user with a unique userId
    #     user_id = str(uuid.uuid4())
    #     self.user_data['userId'] = user_id
    #     response = self.client.post(self.register_url, self.user_data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Attempt to register a second user with the same userId
        new_user_data = self.user_data.copy()
        new_user_data['email'] = "newemail@example.com"
        response = self.client.post(self.register_url, new_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIn('errors', response.data)


# from django.test import TestCase
# from django.contrib.auth import get_user_model
# from rest_framework.test import APIClient
# from userorganization.models import Organisation

# class OrganisationAccessControlTest(TestCase):
#     def setUp(self):
#         self.client = APIClient()
#         self.user1 = CustomUser.objects.create_user(
#             email='user1@example.com',
#             password='password123',
#             first_name='Sam',
#             last_name='One',
#             phone='0799481925'
#         )
#         self.user2 = CustomUser.objects.create_user(
#             email='user2@example.com',
#             password='password123',
#             first_name='Man',
#             last_name='Two',
#             phone='0756881924'
#         )
#         self.organisation1 = Organisation.objects.create(
#             name='Sam Organisation'
#         )
#         self.organisation2 = Organisation.objects.create(
#             name='Man Organisation'
#         )
#         self.organisation1.users.add(self.user1)
#         self.organisation2.users.add(self.user2)

#     def test_user_cannot_see_other_organisation_data(self):
#         self.client.force_authenticate(user=self.user1)
#         response = self.client.get(f'/api/organisations/{self.organisation2.orgId}/')
#         self.assertEqual(response.status_code, 403)

# #end-to-end test
# import pytest
# from django.urls import reverse
# from rest_framework.test import APIClient
# from django.contrib.auth import get_user_model

# @pytest.fixture
# def client():
#     return APIClient()

# @pytest.mark.django_db
# def test_register_user_successfully(client):
#     response = client.post(reverse('register'), {
#         'first_name': 'John',
#         'last_name': 'Doe',
#         'email': 'john@example.com',
#         'password': 'password123'
#     })
#     assert response.status_code == 201
#     assert response.data['status'] == 'success'
#     assert 'access' in response.data['data']['tokens']

# @pytest.mark.django_db
# def test_login_user_successfully(client):
#     user = get_user_model().objects.create_user(
#         email='john@example.com',
#         password='password123',
#         first_name='John',
#         last_name='Doe'
#     )
#     response = client.post(reverse('login'), {
#         'email': 'john@example.com',
#         'password': 'password123'
#     })
#     assert response.status_code == 200
#     assert 'access' in response.data['data']['tokens']

# @pytest.mark.django_db
# def test_register_user_missing_fields(client):
#     response = client.post(reverse('register'), {
#         'first_name': 'John',
#         'email': 'john@example.com',
#         'password': 'password123'
#     })
#     assert response.status_code == 422
#     assert 'last_name' in response.data['errors']

# @pytest.mark.django_db
# def test_register_duplicate_email(client):
#     user = get_user_model().objects.create_user(
#         email='john@example.com',
#         password='password123',
#         first_name='John',
#         last_name='Doe'
#     )
#     response = client.post(reverse('register'), {
#         'first_name': 'John',
#         'last_name': 'Doe',
#         'email': 'john@example.com',
#         'password': 'password123'
#     })
#     assert response.status_code == 422
#     assert 'email' in response.data['errors']


# from django.test import TestCase
# from rest_framework.test import APIClient
# from rest_framework import status
# from userorganization.models import CustomUser, Organisation
# import uuid

# class UserOrganisationTestCase(TestCase):
#     def setUp(self):
#         self.client = APIClient()
#         self.register_url = '/auth/register'
#         self.login_url = '/auth/login'
#         self.user_data = {
#             "email": "testuser@example.com",
#             "password": "testpassword",
#             "first_name": "John",
#             "last_name": "Doe",
#             "phone": "1234567890",
#             "userId": str(uuid.uuid4())
#         }

#     def test_register_user_successfully_with_default_organisation(self):
#         response = self.client.post(self.register_url, self.user_data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertIn('accessToken', response.data['data'])
#         self.assertIn('user', response.data['data'])
#         user = CustomUser.objects.get(email=self.user_data['email'])
#         self.assertIsNotNone(user)
#         organisation_name = f"{user.first_name}'s Organisation"
#         self.assertTrue(Organisation.objects.filter(name=organisation_name).exists())

#     def test_login_user_successfully(self):
#         self.client.post(self.register_url, self.user_data, format='json')
#         login_data = {
#             "email": self.user_data['email'],
#             "password": self.user_data['password']
#         }
#         response = self.client.post(self.login_url, login_data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertIn('accessToken', response.data['data'])
#         self.assertIn('user', response.data['data'])

#     def test_register_user_fails_if_required_fields_missing(self):
#         required_fields = ['first_name', 'last_name', 'email', 'password']
#         for field in required_fields:
#             user_data = self.user_data.copy()
#             user_data.pop(field)
#             response = self.client.post(self.register_url, user_data, format='json')
#             self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
#             self.assertIn('errors', response.data)

#     def test_register_user_fails_if_duplicate_email(self):
#         self.client.post(self.register_url, self.user_data, format='json')
#         response = self.client.post(self.register_url, self.user_data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
#         self.assertIn('errors', response.data)

#     # def test_register_user_fails_if_duplicate_userId(self):
#     #     user_id = str(uuid.uuid4())
#     #     self.user_data['userId'] = user_id
#     #     self.client.post(self.register_url, self.user_data, format='json')
#     #     new_user_data = self.user_data.copy()
#     #     new_user_data['email'] = "newemail@example.com"
#     #     new_user_data['userId'] = user_id
#     #     response = self.client.post(self.register_url, new_user_data, format='json')
#     #     self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
#     #     self.assertIn('errors', response.data)
        
#     def test_register_user_fails_if_duplicate_userId(self):
#         user_id = str(uuid.uuid4())
#         self.user_data['userId'] = user_id
#         # Register the first user
#         self.client.post(self.register_url, self.user_data, format='json')
        
#         # Prepare data for the second user with the same userId
#         new_user_data = self.user_data.copy()
#         new_user_data['email'] = "newemail@example.com"  # Ensure the email is different
#         new_user_data['userId'] = user_id  # Explicitly set the same userId
        
#         # Attempt to register the second user
#         response = self.client.post(self.register_url, new_user_data, format='json')
        
#         # Verify the response indicates a duplicate userId issue
#         self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
#         self.assertIn('errors', response.data)
#         # user_id = str(uuid.uuid4())
#         # self.user_data['userId'] = user_id
#         # # Register the first user
#         # self.client.post(self.register_url, self.user_data, format='json')
        
#         # # Prepare data for the second user with the same userId
#         # new_user_data = self.user_data.copy()
#         # new_user_data['email'] = "newemail@example.com"  # Ensure the email is different
#         # new_user_data['userId'] = user_id  # Explicitly set the same userId
        
#         # # Attempt to register the second user
#         # response = self.client.post(self.register_url, new_user_data, format='json')
        
#         # # Verify the response indicates a duplicate userId issue
#         # self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
#         # self.assertIn('errors', response.data)



