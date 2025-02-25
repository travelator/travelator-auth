from flask_bcrypt import Bcrypt
import redis
import os
from dotenv import load_dotenv

load_dotenv()

bcrypt = Bcrypt()

redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST'),
    port=int(os.getenv('REDIS_PORT')),
    password=os.getenv('REDIS_PASSWORD'),
    ssl=True,
    ssl_cert_reqs=None
)
