# import json

# try:
#     import redis

#     redis_client = redis.Redis(
#         host="localhost",
#         port=6379,
#         decode_responses=True
#     )

#     redis_client.ping()
#     REDIS_AVAILABLE = True
#     print("Redis connected")

# except Exception:
#     REDIS_AVAILABLE = False
#     redis_client = None
#     print("Using local cache")

# LOCAL_CACHE = {}


# def get_cache(key):
#     if REDIS_AVAILABLE:
#         try:
#             data = redis_client.get(key)
#             return json.loads(data) if data else None
#         except:
#             return None
#     return LOCAL_CACHE.get(key)


# def set_cache(key, value, ttl=1800):
#     if REDIS_AVAILABLE:
#         try:
#             redis_client.setex(key, ttl, json.dumps(value))
#         except:
#             pass
#     else:
#         LOCAL_CACHE[key] = value

import redis
import json
import os

redis_client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)

print("Redis connected")


def get_cache(key):
    try:
        value = redis_client.get(key)
        if value:
            return json.loads(value)
    except:
        return None


def set_cache(key, value, ttl=1800):
    try:
        redis_client.setex(
            key,
            ttl,
            json.dumps(value)
        )
    except:
        pass