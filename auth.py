from flask_restful import Resource, reqparse
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from token_generation import generate_token, validate_token
from extensions import bcrypt, redis_client

load_dotenv()

url: str = os.getenv("PROJECT_URL")
key: str = os.getenv("API_KEY")

supabase: Client = create_client(url, key)


class Register(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        args = parser.parse_args()
        hashed_password = (bcrypt.generate_password_hash(args['password']).
                           decode('utf-8'))

        try:
            result = supabase.table('users').insert({
                'email': args['email'],
                'password': hashed_password
            }).execute()

            if len(result.data) > 0:
                return {
                    "message": "User registered successfully"
                }, 201
            else:
                return {"message": "Failed to register user"}, 400
        except Exception as e:
            return {"error": str(e)}, 400


class Login(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        args = parser.parse_args()

        try:
            result = (supabase.table('users')
                      .select("email", "password")
                      .eq("email", args['email'])
                      .execute())

            if len(result.data) == 0:
                return {"error": "User not found"}, 401

            user = result.data[0]
            stored_password = user['password']

            if bcrypt.check_password_hash(stored_password, args['password']):
                token = generate_token(user['email'])
                redis_client.setex(f"session:{user['email']}", 86400, token)
                return {"token": token}, 200
            else:
                return {"message": "Wrong password"}, 401
        except Exception as e:
            return {"error": str(e)}, 400


class ValidateSession(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('token', location='headers', required=True)
        args = parser.parse_args()

        email = validate_token(args['token'])
        if email:
            stored_token = redis_client.get(f"session:{email}")
            if stored_token and stored_token.decode('utf-8') == args['token']:
                return {'message': 'Valid session'}, 200
        return {'message': 'Invalid session'}, 401


class Logout(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('token', location='headers', required=True)
        args = parser.parse_args()

        email = validate_token(args['token'])
        if email:
            redis_client.delete(f"session:{email}")
            return {'message': 'Logged out successfully'}, 200
        return {'message': 'Invalid session'}, 401
