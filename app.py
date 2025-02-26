from flask import Flask
from flask_restful import Api
from dotenv import load_dotenv
from auth import Register, Login, ValidateSession, Logout
from extensions import bcrypt

load_dotenv()


app = Flask(__name__)
api = Api(app)
bcrypt.init_app(app)


api.add_resource(Register, '/register')
api.add_resource(Login, '/login')
api.add_resource(ValidateSession, '/validate')
api.add_resource(Logout, '/logout')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
