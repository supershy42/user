from django.urls import path
from .views import (
    SendFriendRequestView,
    RespondToFriendRequestView,
    FriendListView,
    DeleteFriendView
)


urlpatterns = [
    path('request/', SendFriendRequestView.as_view(), name='request'),
    path('respond/', RespondToFriendRequestView.as_view(), name='respond'),
    path('list/', FriendListView.as_view(), name='list'),
    path('delete/', DeleteFriendView.as_view(), name='delete')
]