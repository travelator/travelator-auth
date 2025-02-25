from flask import Flask
from flask_restful import Api
from flask_bcrypt import Bcrypt
import redis
import os
from dotenv import load_dotenv
from auth import Register, Login, ValidateSession, Logout

load_dotenv()

redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST'),
    port=os.getenv('REDIS_PORT'),
    password=os.getenv('REDIS_PASSWORD'),
)

app = Flask(__name__)
api = Api(app)
bcrypt = Bcrypt(app)


api.add_resource(Register, '/register')
api.add_resource(Login, '/login')
api.add_resource(ValidateSession, '/validate')
api.add_resource(Logout, '/logout')


if __name__ == '__main__':
    app.run(debug=True)
