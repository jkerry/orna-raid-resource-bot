from pymongo import MongoClient
from pprint import pprint

class Kingdom:
    def __init__(self, datasource, kingdom_id):
        self.kingdom_id = kingdom_id
        self.client = MongoClient(datasource)
        self.db = self.client.orna
        self.data = {
            'name': self.kingdom_id,
            'accumulated_orns': 0,
            'bank_pct': 0.0,
            'base_rotation_time_hours': 10,
            'daily_rotation_hours': 12
        }


    def load(self):
        print("Loading kingdom data for {}...".format(self.kingdom_id))
        result = self.db.kingdoms.find_one({'name': self.kingdom_id})
        pprint(result)
        self.data = result

    def save(self):
        result = self.db.kingdoms.replace_one({'name': self.kingdom_id}, self.data, upsert=True)
        print("Updated {} records.".format(result.modified_count))