from flask_bcrypt import Bcrypt
import redis
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

bcrypt = Bcrypt()

# Retrieve Redis configurations with defaults
redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = os.getenv('REDIS_PORT', '6379')
redis_password = os.getenv('REDIS_PASSWORD', None)  # Can be None

# Ensure redis_port is a valid integer
try:
    redis_port = int(redis_port)
except ValueError:
    raise ValueError(f"Invalid REDIS_PORT: {redis_port}. Must be an integer.")

# Initialize Redis client
redis_client = redis.Redis(
    host=redis_host,
    port=redis_port,
    password=redis_password,
    ssl=True,
    ssl_cert_reqs=None
)

