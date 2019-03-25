from flask_restful import Resource, reqparse
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token, 
    jwt_refresh_token_required, 
    get_jwt_identity,
    jwt_required,
    get_raw_jwt
)

from models.user import UserModel

from blacklist import BLACKLIST

_user_parser = reqparse.RequestParser()
_user_parser.add_argument('username',
                          type=str,
                          required=True,
                          help="Username is required"
                          )
_user_parser.add_argument('password',
                          type=str,
                          required=True,
                          help="Password is required"
                          )


class UserRegister(Resource):

    def post(self):
        data = _user_parser.parse_args()

        if UserModel.find_by_username(data['username']):
            return {"message": "User {} already exists".format(data['username'])}, 400

        user = UserModel(**data)

        user.save_to_db()

        return {"message": "User created successfully"}, 201


class User(Resource):

    @classmethod
    def get(cls, user_id):
        user = UserModel.find_by_id(user_id)

        if not user:
            return {'message': 'User not found'}, 404
        return user.json()

    @classmethod
    def delete(cls, user_id):
        user = UserModel.find_by_id(user_id)

        if not user:
            return {'message': 'User not found'}, 404
        return user.delete_from_db()


class UserLogin(Resource):

    @classmethod
    def post(self):
        data = _user_parser.parse_args()

        user = UserModel.find_by_username(data['username'])

        if user and safe_str_cmp(user.password, data['password']):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(user.id)
            return {
                'access_token': access_token,
                'refresh_token': refresh_token
            }, 200


class UserLogout(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti'] 
        BLACKLIST.add(jti)
        return {'message': 'Successfully logged out'}


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {'access_token': new_token}, 200