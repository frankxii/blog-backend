import json
from redis import StrictRedis

with open('blog_backend/env.json') as env:
    env_dict: dict = json.load(env)
    config: dict = env_dict['REDIS_INFO']

redis = StrictRedis(**config, decode_responses=True, health_check_interval=120)

with open('blog/Authority.json', 'rb') as authority_file:
    authority_config: list[dict] = json.load(authority_file)
