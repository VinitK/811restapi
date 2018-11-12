from db import db

class StoreModel(db.Model):
    
# start database definition
    __tablename__ = 'stores'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))

    items = db.relationship('ItemModel', lazy = "dynamic")
# end database definition

    def __init__(self, name):
        self.name = name
    
    def json(self):
        return {"id": self.id, "name": self.name, "items": [item.json() for item in self.items.all()]}

    @classmethod
    def find_by_name(cls, name): # classmethod to search in database by name

        return cls.query.filter_by(name=name).first()

    @classmethod
    def find_all(cls):
        return cls.query.all()

    def save_to_db(self): # method to save to database
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self): # method to delete from database
        db.session.delete(self)
        db.session.commit()