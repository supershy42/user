from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()

class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, related_name="sent_requests", on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name="received_requests", on_delete=models.CASCADE)
    status = models.CharField(
        max_length=10,
        choices=[
            ('pending', 'Pending'),
            ('accepted', 'Accepted'),
            ('rejected', 'Rejected'),
        ],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                # 중복 요청 방지
                fields=['from_user', 'to_user'],
                name='unique_friend_request'
            )
        ]


class Friendship(models.Model):
    user1 = models.ForeignKey(User, related_name="friends_from", on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name="friends_to", on_delete=models.CASCADE)
    chatroom_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                # 한 쌍의 친구 관계는 한 번만 저장
                fields=['user1', 'user2'],
                name='unique_friendship'
            )
        ]
        
    def save(self, *args, **kwargs):
        if self.user1_id > self.user2_id:
            self.user1_id, self.user2_id = self.user2_id, self.user1_id
        super().save(*args, **kwargs)


class Block(models.Model):
    blocker = models.ForeignKey(User, related_name="blocker", on_delete=models.CASCADE)
    blocked = models.ForeignKey(User, related_name="blocked", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['blocker', 'blocked']