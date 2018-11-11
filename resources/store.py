from flask_restful import Resource, reqparse
from flask_jwt import jwt_required

from models.store import StoreModel

class Store(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument("name", type=str, required=True, help="This field can't be left blank.")

    @jwt_required()
    def get(self, name): #get method
        
        store = StoreModel.find_by_name(name)
        if store:
            return store.json(), 200
        return {"message": "Store not found"}, 404

    @jwt_required()
    def post(self, name): #post method

        if StoreModel.find_by_name(name):
            return {"message": "Store with name {} already exists.".format(name)}, 400
        
        store = StoreModel(name)

        try:
            store.save_to_db()
        except:
            return {"message": "Internal error inserting"}, 500

        return store.json(), 201

    @jwt_required()
    def put(self, name): # put method

        data = Store.parser.parse_args()

        store = StoreModel.find_by_name(name)

        if store is None:
            store = StoreModel(name)
        elif StoreModel.find_by_name(**data) is None:
            store.name = data["name"]

        store.save_to_db()

        return store.json()

    @jwt_required()
    def delete(self, name): # delete method

        store = StoreModel.find_by_name(name)
        if store:
            store.delete_from_db()

        return {"message": "Item deleted."}


class StoreList(Resource):

    @jwt_required()
    def get(self): # get method

        return {"stores" : list(map(lambda x: x.json(), StoreModel.query.all()))}