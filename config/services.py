import aiohttp
from config.settings import CHAT_SERVICE

# 채팅 서비스의 채팅방 생성 API 호출
async def get_chatroom(user1_id, user2_id, token):
    request_url = f'{CHAT_SERVICE}create/'
    headers  = {'Authorization': f'Bearer {token}'}
    payload = {"user1_id": user1_id, "user2_id": user2_id}
    
    async with aiohttp.ClientSession() as session:
        async with session.post(request_url, json=payload, headers=headers, timeout=10) as response:
            if response.status == 201: # 채팅방 생성 성공
                return await response.json()
            return None


# 채팅 서비스의 채팅방 삭제 API 호출
async def delete_chatroom(chatroom_id, token):
    request_url = f'{CHAT_SERVICE}delete/'
    headers = {'Authorization': f'Bearer {token}'}
    payload = {"chatroom_id": chatroom_id}
    
    async with aiohttp.ClientSession() as session:
        async with session.post(request_url, json=payload, headers=headers, timeout=10) as response:
            if response.status == 204: # 채팅방 삭제 성공
                return True
            return None