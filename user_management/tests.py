from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from .models import User, EmailVerificationCode
from .serializers import UserProfileSerializer
from rest_framework_simplejwt.tokens import RefreshToken


class NicknameCheckTest(APITestCase):
    def setUp(self):
        self.url = reverse('nickname-check')
        self.existing_user = User.objects.create_user(
            email='existing@example.com',
            nickname='existinguser',
            password='password123'
        )
    
    def test_nickname_available(self):
        data = {'nickname': 'newnickname'}
        response = self.client.post(self.url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("ok", response.data["message"])

    def test_nickname_unavailable(self):
        data = {'nickname': 'existinguser'}
        response = self.client.post(self.url, data)
        
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)


class EmailCheckTest(APITestCase):

    def setUp(self):
        self.url = reverse('email-check')
        self.existing_user = User.objects.create_user(
            email='existing@example.com',
            nickname='existinguser',
            password='password123'
        )

    def test_send_code_to_new_email(self):
        data = {'email': 'newuser@example.com'}
        response = self.client.post(self.url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Verification code sent", response.data["message"])
    
    def test_send_code_to_existing_email(self):
        data = {'email': self.existing_user.email}
        response = self.client.post(self.url, data)
        
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)


class UserRegisterTest(APITestCase):
    def setUp(self):
        self.url = reverse('register-complete')
        self.email = 'user@example.com'
        self.nickname = 'newuser'
        self.password = 'Password123!'
        self.code = '123456'

        EmailVerificationCode.objects.create(
            email=self.email,
            code=self.code
        )

    def test_register_successful(self):
        data = {
            'email': self.email,
            'nickname': self.nickname,
            'password': self.password,
            'code': self.code
        }
        response = self.client.post(self.url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user_exists = User.objects.filter(email=self.email).exists()
        self.assertTrue(user_exists)

    def test_invalid_code(self):
        data = {
            'email': self.email,
            'nickname': self.nickname,
            'password': self.password,
            'code': '111111'
        }
        response = self.client.post(self.url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserLoginTest(APITestCase):
    def setUp(self):
        # 테스트 사용자 생성
        self.user = User.objects.create_user(
            email = 'testuser@example.com',
            nickname = 'test',
            password = 'Testpass123!',
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

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('Invalid credentials', str(response.data))
        

class UserProfileViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='activeuser@example.com',
            nickname='ActiveUser',
            password='password123',
        )
        self.client = APIClient()
        
        # JWT 토큰 생성 및 헤더 추가
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')

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