import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .redis_utils import (
    add_user_to_online_users,
    remove_user_from_online_users,
)

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # 사용자 ID 가져오기
        self.user_id = self.scope.get('user_id')
        if not self.user_id:
            await self.close()
            return
        
        # Redis에 사용자 추가
        self.group_name = f'notification_{self.user_id}'
        await add_user_to_online_users(self.user_id, self.channel_name)
        
        # 그룹에 WebSocket 연결 추가
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
    
    async def disconnect(self, close_code):
        # Redis에서 사용자 제거
        if self.user_id:
            await remove_user_from_online_users(self.user_id)
        
        # 그룹에서 WebSocket 연결 제거
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # WebSocket 클라이언트로부터 메시지 수신
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send(json.dumps({'error': 'Invalid JSON format'}))
            return

        notification_type = data.get('type')
        content = data.get('content')

        # 알림 타입별 처리
        if notification_type in ['friend_request', 'game_invitation']:
            await self.broadcast_message(notification_type, content)
        else:
            self.send(json.dumps({'error': 'Invalid notification type'}))
            
    async def reception_invitation(self, event):
        await self.send_json(event)
        
    async def tournament_start(self, event):
        await self.send_json(event)

    # 메시지를 그룹에 브로드캐스트
    async def broadcast_message(self, notification_type, content):
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'send_to_client',
                'notification_type': notification_type,
                'content': content
            }
        )

    # 메시지를 WebSocket 클라이언트에 전송
    async def send_to_client(self, event):
        await self.send(text_data=json.dumps({
            'notification_type': event['notification_type'],
            'content': event['content']
        }))
        
    async def send_json(self, message):
        try:
            json_message = json.dumps(message)
            await self.send(text_data=json_message)
        except (TypeError, ValueError) as e:
            error_message = {"type": "error", "message":"Invalid json format."}
            await self.send(text_data=json.dumps(error_message))