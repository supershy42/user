import redis.asyncio as redis
from django.conf import settings

redis_client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)

ONLINE_USERS_KEY = 'online_users'
USER_CHANNELS_KEY = 'user_channels'

async def add_user_to_online_users(user_id, channel_name):
    await redis_client.sadd(ONLINE_USERS_KEY, user_id)
    await redis_client.hset(USER_CHANNELS_KEY, user_id, channel_name)
    
async def get_channel_name(user_id):
    channel_name = await redis_client.hget(USER_CHANNELS_KEY, user_id)
    return channel_name.decode("utf-8") if channel_name else None

async def remove_user_from_online_users(user_id):
    await redis_client.srem(ONLINE_USERS_KEY, user_id)
    await redis_client.hdel(USER_CHANNELS_KEY, user_id)