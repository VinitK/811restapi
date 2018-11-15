import sqlite3
from flask_restful import Resource, reqparse
from models.user import UserModel
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    jwt_refresh_token_required,
    get_jwt_identity,
    get_raw_jwt)
from blacklist import BLACKLIST


        
_user_parser = reqparse.RequestParser()
_user_parser.add_argument("username", type=str, required=True, help="This field cannot be left blank.")
_user_parser.add_argument("password", type=str, required=True, help="This field cannot be left blank.")

class UserRegister(Resource):
    
    def post(self):
        
        data = _user_parser.parse_args()

        if UserModel.find_by_username(data["username"]):
            return {"message": "User does not exist."}, 400

        user = UserModel(**data)
        user.save_to_db()

        return {"message": "User created successfully."}, 201


class User(Resource):
    @jwt_required
    def get(self, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": "User not found"}, 404
        return user.json()

    @jwt_required
    def delete(self, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message":"User not found"}, 404
        user.delete_from_db()
        return {"message": "User deleted."}, 200

class UserList(Resource):

    @jwt_required
    def get(self): # get method
        return {"items":[user.json() for user in UserModel.find_all()]}

class UserLogin(Resource):

    @classmethod
    def post(cls):
        data = _user_parser.parse_args() #get data from parser
        user = UserModel.find_by_username(data["username"]) #find user in database
        if user and safe_str_cmp(user.password, data["password"]):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(user.id) #check password
            return {
                "access_token":access_token,
                "refresh_token":refresh_token
            }, 200 #return access and refresh token
        
        return {"message": "invalid credentials"}, 401


class UserLogout(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti'] # jti is 'jwt id', a unique identifier for jwt
        BLACKLIST.add(jti)
        return {"message":"successfully logged out."}, 200


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}, 200