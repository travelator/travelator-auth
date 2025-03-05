from flask_restful import Resource, reqparse
from flask import request, jsonify
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from token_generation import generate_token, validate_token
from extensions import bcrypt, redis_client
import re

load_dotenv()

url: str = os.getenv("PROJECT_URL")
key: str = os.getenv("API_KEY")

supabase: Client = create_client(url, key)


def is_valid_email(email):
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email)


def is_valid_password(password):
    if len(password) < 8:
        return "Password must be at least 8 characters long."
    if not any(char.isdigit() for char in password):
        return "Password must contain at least one number."
    if not any(char.isupper() for char in password):
        return "Password must contain at least one uppercase letter."
    if not any(char
               in "!@#$%^&*()_+-=[]{}|;':\",.<>?/`~" for char in password):
        return "Password must contain at least one special character."
    return None  # Password is valid


class Register(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("email", type=str, required=True)
        parser.add_argument("password", type=str, required=True)
        args = parser.parse_args()
        hashed_password = bcrypt.generate_password_hash(
            args["password"]
        ).decode("utf-8")

        if not is_valid_email(args['email']):
            return {"error": "Invalid email format."}, 400

        password_error = is_valid_password(args['password'])
        if password_error:
            return {"error": password_error}, 400

        try:
            result = (
                supabase.table("users")
                .insert({"email": args["email"], "password": hashed_password})
                .execute()
            )

            if len(result.data) > 0:
                user = result.data[0]
                token = generate_token(user["user_id"])
                redis_client.setex(f"session:{user['user_id']}", 86400, token)
                resp = jsonify({
                    "message": "User registered and logged in successfully",
                    "token": token
                })
                resp.set_cookie(
                    "token",
                    token,
                    max_age=86400,
                    httponly=True,
                    secure=True,
                    samesite="None",
                )
                return resp
            else:
                return {"message": "Failed to register user"}, 400
        except Exception as e:
            return {"error": str(e)}, 400


class Login(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("email", type=str, required=True)
        parser.add_argument("password", type=str, required=True)
        args = parser.parse_args()

        try:
            result = (
                supabase.table("users")
                .select("user_id", "email", "password")
                .eq("email", args["email"])
                .execute()
            )

            if len(result.data) == 0:
                return {"error": "User not found"}, 401

            user = result.data[0]
            stored_password = user["password"]

            if bcrypt.check_password_hash(stored_password, args["password"]):
                token = generate_token(user["user_id"])
                redis_client.setex(f"session:{user['user_id']}", 86400, token)
                resp = jsonify({"token": token})
                resp.set_cookie(
                    "token",
                    token,
                    max_age=86400,
                    httponly=True,
                    secure=True,
                    samesite="None",
                )
                return resp
            else:
                return {"message": "Wrong password"}, 401
        except Exception as e:
            return {"error": str(e)}, 400


class ValidateSession(Resource):
    def get(self):
        token = request.cookies.get("token")
        if not token:
            print("no token")
            return {"message": "Missing token cookie"}, 401
        user_id = validate_token(token)
        if user_id:
            stored_token = redis_client.get(f"session:{user_id}")
            if stored_token and stored_token.decode("utf-8") == token:
                return {"message": "Valid session", "user_id": user_id}, 200
        return {"message": "Invalid session"}, 401


class Logout(Resource):
    def post(self):
        token = request.cookies.get("token")
        if not token:
            return {"message": "Missing token cookie"}, 401
        user_id = validate_token(token)
        if user_id:
            redis_client.delete(f"session:{user_id}")
            resp = jsonify({"message": "Logged out successfully"})
            resp.delete_cookie("token")
            return resp
        return {"message": "Invalid session"}, 401
