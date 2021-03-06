from flask_restful import Resource, reqparse
from flask_jwt_extended import (
    jwt_required,
    jwt_optional,
    get_jwt_claims,
    get_jwt_identity,
    fresh_jwt_required)

from models.item import ItemModel

class Item(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument("price", type=float, required=True, help="This field can't be left blank.")
    parser.add_argument("store_id", type=int, required=True, help="Every id needs a store id.")

    @jwt_required
    def get(self, name): #get method
        
        item = ItemModel.find_by_name(name)
        if item:
            return item.json(), 200
        return {"message": "Item not found"}, 404

    @fresh_jwt_required
    def post(self, name): #post method

        if ItemModel.find_by_name(name):
            return {"message": "Item with name {} already exists.".format(name)}, 400
        
        data = Item.parser.parse_args()
        
        item = ItemModel(name, **data)

        try:
            item.save_to_db()
        except:
            return {"message": "Internal error inserting"}, 500

        return item.json(), 201

    @jwt_required
    def put(self, name): # put method

        data = Item.parser.parse_args()

        item = ItemModel.find_by_name(name)

        if item is None:
            item = ItemModel(name, **data)
        else:
            item.price = data["price"]
            item.store_id = data["store_id"]

        item.save_to_db()

        return item.json()

    @jwt_required
    def delete(self, name): # delete method
        
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {"message":"Admin Privilage Required."}, 401

        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()

        return {"message": "Item deleted."}


class ItemList(Resource):

    @jwt_optional
    def get(self): # get method
        user_id = get_jwt_identity()
        items = [item.json() for item in ItemModel.find_all()]
        if user_id:
            return {"items":items}
        return {"items": [item['name'] for item in items], "message":"Login for more information."}, 200