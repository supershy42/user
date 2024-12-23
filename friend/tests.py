from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from .models import FriendRequest, Friendship
from django.contrib.auth import get_user_model
from unittest.mock import patch
from rest_framework_simplejwt.tokens import RefreshToken
from unittest.mock import patch

User = get_user_model()

class FriendRequestTest(APITestCase):
    def setUp(self):
        self.client = APIClient()  # APIClient 선언
        self.user1 = User.objects.create_user(email="user1@example.com", password="password1", nickname="user1")
        self.user2 = User.objects.create_user(email="user2@example.com", password="password1", nickname="user2")
        
        # JWT 토큰 생성 및 헤더 추가
        refresh = RefreshToken.for_user(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
        
    def test_send_friend_request_success(self):
        # 친구 요청 성공
        url = reverse('request')
        data = {'to_user_id': self.user2.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(FriendRequest.objects.count(), 1)

    def test_send_friend_request_duplicate(self):
        # 중복된 친구 요청
        FriendRequest.objects.create(from_user=self.user1, to_user=self.user2)
        url = reverse('request')
        data = {'to_user_id': self.user2.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)


class RespondToFriendRequestTest(APITestCase):
    def setUp(self):
        self.client = APIClient()  # APIClient 선언
        self.user1 = User.objects.create_user(email="user1@example.com", password="password1", nickname="user1")
        self.user2 = User.objects.create_user(email="user2@example.com", password="password1", nickname="user2")
        
        # JWT 토큰 생성 및 헤더 추가
        refresh = RefreshToken.for_user(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')

    # TODO: 에러 수정 필요
    @patch('config.services.get_chatroom')
    def test_accept_friend_request_success(self, mock_get_chatroom):
        # 친구 요청 수락
        mock_get_chatroom.return_value = {'chatroom_id': 1}
        
        friend_request = FriendRequest.objects.create(from_user=self.user2, to_user=self.user1)
        url = reverse('respond')
        data = {'friend_request_id': friend_request.id, 'action': 'accept'}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Friendship.objects.count(), 1)
        self.assertEqual(Friendship.objects.first().user1.id, min(self.user1.id, self.user2.id))
        self.assertEqual(Friendship.objects.first().user2.id, max(self.user1.id, self.user2.id))


class FriendListTest(APITestCase):
    def setUp(self):
        self.client = APIClient()  # APIClient 선언
        self.user1 = User.objects.create_user(email="user1@example.com", password="password1", nickname="user1")
        self.user2 = User.objects.create_user(email="user2@example.com", password="password1", nickname="user2")
        
        # JWT 토큰 생성 및 헤더 추가
        refresh = RefreshToken.for_user(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')

    # TODO: 에러 수정 필요
    def test_friend_list_with_friends(self):
        # 친구 목록 조회
        Friendship.objects.create(user1=self.user1, user2=self.user2)
        url = reverse('list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.user2.id)

    @patch('friend.views.get_friends_list', return_value=None)
    def test_friend_list_none(self, mock_get_friends_list):
        # 친구 목록이 None인 경우
        mock_get_friends_list.return_value = None
        url = reverse('list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['message'], "Friends list is not initialized or unavailable.")