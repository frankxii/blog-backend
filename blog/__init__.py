import json
from redis import Redis

with open('blog_backend/env.json') as env:
    env_dict: dict = json.load(env)
    config: dict = env_dict['REDIS_INFO']

redis = Redis(**config, decode_responses=True)
