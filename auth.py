import re
from flask_restful import Resource, reqparse
from flask import request
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from token_generation import generate_token, validate_token
from extensions import bcrypt, redis_client

load_dotenv()

url: str = os.getenv("PROJECT_URL")
key: str = os.getenv("API_KEY")

supabase: Client = create_client(url, key)


# Function to validate email
def is_valid_email(email):
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email)


# Function to validate password
def is_valid_password(password):
    if len(password) < 8:
        return "Password must be at least 8 characters long."
    if not any(char.isdigit() for char in password):
        return "Password must contain at least one number."
    if not any(char.isupper() for char in password):
        return "Password must contain at least one uppercase letter."
    if not any(char in "!@#$%^&*()_+-=[]{}|;':\",.<>?/`~" for char in password):
        return "Password must contain at least one special character."
    return None  # Password is valid


class Register(Resource):
    def get(self):
        return {"message": "Use a POST request to register a user."}, 200

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        args = parser.parse_args()

        # Validate Email
        if not is_valid_email(args['email']):
            return {"error": "Invalid email format."}, 400

        # Validate Password
        password_error = is_valid_password(args['password'])
        if password_error:
            return {"error": password_error}, 400

        hashed_password = bcrypt.generate_password_hash(args['password']).decode('utf-8')

        try:
            result = supabase.table('users').insert({
                'email': args['email'],
                'password': hashed_password
            }).execute()

            if len(result.data) > 0:
                user_id = result.data[0]['id']  # Assuming Supabase auto-generates 'id'
                return {
                    "message": "User registered successfully",
                    "user_id": user_id  # Return user_id to frontend
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
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return {'message': 'Missing Authorization header'}, 401
        token = auth_header.split(' ')[1]  # Assumes 'Bearer <token>'
        email = validate_token(token)
        if email:
            stored_token = redis_client.get(f"session:{email}")
            if stored_token and stored_token.decode('utf-8') == token:
                return {'message': 'Valid session'}, 200
        return {'message': 'Invalid session'}, 401


class Logout(Resource):
    def post(self):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return {'message': 'Missing Authorization header'}, 401
        token = auth_header.split(' ')[1]  # Assumes 'Bearer <token>'
        email = validate_token(token)
        if email:
            redis_client.delete(f"session:{email}")
            return {'message': 'Logged out successfully'}, 200
        return {'message': 'Invalid session'}, 401
