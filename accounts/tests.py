from django.urls import reverse
from django.contrib.auth import get_user_model
User = get_user_model()
from rest_framework.test import APITestCase


class AccountTests(APITestCase):
    def test_create_account(self):
        """
        Ensure we can create a new account object.
        """
        url = reverse('register')
        data = {
            'username': 'tsetset',
            'email': 'tsetset@gmail.com',
            'password': '123456'
        }
        response = self.client.post(url, data, format='json')

        self.assertTrue(response.status_code == 200)
        self.assertTrue('token' in response.data)
        self.assertTrue('user' in response.data)
        self.assertTrue(User.objects.filter(username='tsetset').exists())

    def test_not_allowing_duplicate_accounts(self):
        """
        Ensure we can not create duplicate account object.
        """
        user = User.objects.create_user('tsetset', 'tsetset2@gmail.com', '123456')

        url = reverse('register')
        data = {
            'username': 'tsetset',
            'email': 'tsetset@gmail.com',
            'password': '123456'
        }
        response = self.client.post(url, data, format='json')

        self.assertTrue(response.status_code == 400)
        self.assertTrue(response.data == {"username": [
            "A user with that username already exists."
        ]})
        self.assertFalse('token' in response.data)
        self.assertFalse('user' in response.data)

    def test_login_account(self):
        """
        Ensure we can log in to account .
        """
        user = User.objects.create_user('tsetset', 'tsetset@gmail.com', '123456')

        url = reverse('login')
        data = {
            'username': 'tsetset@gmail.com',
            'password': '123456'
        }
        response = self.client.post(url, data, format='json')

        self.assertTrue(response.status_code == 200)
        self.assertTrue('token' in response.data)

    def test_not_able_to_login_account_with_wrong_creds(self):
        """
        Ensure we can not able to log in with wrong creds .
        """
        url = reverse('login')
        data = {
            'username': 'tsetset@gmail.com',
            'password': '123456'
        }
        response = self.client.post(url, data, format='json')

        self.assertTrue(response.status_code == 400)
        self.assertTrue(response.data == {
            "non_field_errors": [
                "Unable to log in with provided credentials."
            ]
        })
        self.assertFalse('token' in response.data)
