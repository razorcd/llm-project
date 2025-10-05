from tinydb import TinyDB, Query

class CourierRepository:
    tinydb: TinyDB

    def __init__(self, tinydb_file):
        self.tinydb = TinyDB(tinydb_file)

    def search(self, courier_id):
        result = self.tinydb.search(Query().index == courier_id)
        if result:
            return result[0]
        else:
            return None 