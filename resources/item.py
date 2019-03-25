from flask_restful import Resource, Api, reqparse
from flask_jwt_extended import (
    jwt_required, jwt_optional, 
    get_jwt_claims, 
    get_jwt_identity, 
    fresh_jwt_required
)

from models.item import ItemModel


class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('store_id',
                        type=int,
                        required=True,
                        help="Store id is required"
                        )
    parser.add_argument('price',
                        type=float,
                        required=True,
                        help="Price is required"
                        )

    def get(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            return item.json()
        return {'message': 'Item not found'}, 404

    @fresh_jwt_required
    def post(self, name):
        if ItemModel.find_by_name(name):
            return {'message': "An item with the name '{}' already exists".format(name)}, 400

        data = Item.parser.parse_args()

        item = ItemModel(name, **data)

        try:
            item.save_to_db()
        except:
            return {'message': 'An error occured while inserting the item'}, 500

        return item.json(), 201

    @jwt_required
    def delete(self, name):
        item = ItemModel.find_by_name(name)

        if item:
            item.delete_from_db()

        return {'message': "Item '{}' deleted".format(name)}, 201

    @jwt_required
    def put(self, name):
        data = Item.parser.parse_args()

        item = ItemModel.find_by_name(name)

        if item is None:
            item = ItemModel(name, **data)
        else:
            item.price = data['price']

        item.save_to_db()

        return item.json()


class ItemList(Resource):
    
    @jwt_optional
    def get(self):
        user_id = get_jwt_identity()
        items = [item.json() for item in ItemModel.find_all()]

        if user_id:
            return {'items': items}, 200
        return {
            'items': [item['name'] for item in items],
            'message': 'Login for more data'
        }, 200
