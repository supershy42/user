from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import User
from .serializers import UserProfileSerializer

class UserRegistrationTest(APITestCase):

    def setUp(self):
        # 초기 사용자 생성으로 중복 테스트 준비
        self.existing_user_data = {
            'nickname': 'testuser',
            'email': 'testuser@example.com',
            'password': 'Testpass123!'
        }
        User.objects.create_user(**self.existing_user_data)

    def test_user_registration_success(self):
        # 정상적인 회원가입 테스트
        data = {
            'nickname': 'newuser',
            'email': 'newuser@example.com',
            'password': 'Newpass123!'
        }

        url = reverse('register')
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("Registration successful", response.data.get("message", ""))

        user_exists = User.objects.filter(email=data['email']).exists()
        self.assertTrue(user_exists)

    def test_user_registration_duplicate_email(self):
        # 중복 이메일로 회원가입 시도
        data = {
            'nickname': 'uniqueuser',
            'email': self.existing_user_data['email'],  # 중복 이메일
            'password': 'Testpass123!'
        }

        url = reverse('register')
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertIn("already exists", response.data["email"][0])

    def test_user_registration_duplicate_nickname(self):
        # 중복 닉네임으로 회원가입 시도
        data = {
            'nickname': self.existing_user_data['nickname'],  # 중복 닉네임
            'email': 'uniqueuser@example.com',
            'password': 'Testpass123!'
        }

        url = reverse('register')
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("nickname", response.data)
        self.assertIn("This nickname is already taken.", response.data["nickname"][0])  # 예상 메시지로 수정


class UserLoginTest(APITestCase):
    def setUp(self):
        # 테스트 사용자 생성
        self.user = User.objects.create_user(
            email = 'testuser@example.com',
            nickname = 'test',
            password = 'Testpass123!',
            is_active = True
        )

    def test_login_success(self):
        # 정상적인 자격 증명으로 로그인
        data = {
            'email': 'testuser@example.com',
            'password': 'Testpass123!'
        }
        url = reverse('login')
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_invalid_credentials(self):
        # 잘못된 자격 증명으로 로그인 시도
        data = {
            'email': 'testuser@example.com',
            'password': 'WrongPassword'
        }
        url = reverse('login')
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Invalid credentials', str(response.data))
        

class UserProfileViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='activeuser@example.com',
            nickname='ActiveUser',
            password='password123',
            is_active=True
        )

    def get_user_profile_url(self, user_id):
        return reverse('user-profile', kwargs={'user_id': user_id})

    def test_retrieve_user_profile(self):
        url = self.get_user_profile_url(self.user.id)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = UserProfileSerializer(self.user)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_nonexistent_user_profile(self):
        url = self.get_user_profile_url(9999)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_response_contains_expected_fields(self):
        url = self.get_user_profile_url(self.user.id)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_fields = {'email', 'nickname', 'avatar'}
        self.assertEqual(set(response.data.keys()), expected_fields)