import os
import hashlib

from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager

from resources.user import UserRegister, UserLogin, User
from resources.item import Item, ItemList
from resources.store import Store, StoreList

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'SECRET_KEY'
api = Api(app)


@app.before_first_request
def create_tables():
    db.create_all()


jwt = JWTManager(app)
app.config['JWT_AUTH_HEADER_PREFIX'] = 'Bearer'

@jwt.user_claims_loader
def add_claims_to_jwt(identity):
    identity = str(identity).encode()
    print(hashlib.sha1(identity).hexdigest())
    if hashlib.sha1(identity).hexdigest() == '356a192b7913b04c54574d18c28d46e6395428ab':    # Not considered safe, testing purposes only : should be in a config file
        return {'is_admin': True}
    return {'is_admin': False}

api.add_resource(Store, '/store/<string:name>')
api.add_resource(Item, '/item/<string:name>')
api.add_resource(StoreList, '/stores')
api.add_resource(ItemList, '/items')
api.add_resource(UserRegister, '/register')
api.add_resource(User, '/user/<int:user_id>')
api.add_resource(UserLogin, '/login')


if __name__ == '__main__':          # Prevents app from running multiple time
    from db import db
    db.init_app(app)
    app.run(port=3000, debug=True)
