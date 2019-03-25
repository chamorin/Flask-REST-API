from flask_restful import Resource, Api, reqparse
from flask_jwt_extended import jwt_required, get_jwt_claims

from models.store import StoreModel


class Store(Resource):
    parser = reqparse.RequestParser()

    def get(self, name):
        store = StoreModel.find_by_name(name)
        if store:
            return store.json()
        return {'message': 'Store not found'}, 404

    @jwt_required
    def post(self, name):
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'message': 'Admin privilege required'}, 401

        if StoreModel.find_by_name(name):
            return {'message': "A store with the name '{}' already exists".format(name)}, 400

        store = StoreModel(name)
        try:
            store.save_to_db()
        except:
            return {'message': 'An error occured while inserting the store'}, 500

        return store.json(), 201

    @jwt_required
    def delete(self, name):
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'message': 'Admin privilege required'}, 401

        store = StoreModel.find_by_name(name)

        if store:
            store.delete_from_db()

        return {'message': "Store '{}' deleted".format(name)}, 201


class StoreList(Resource):

    def get(self):
        return {'stores': [store.json() for store in StoreModel.query.all()]}
