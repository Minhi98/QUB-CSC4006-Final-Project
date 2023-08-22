from utilities import *

from flask_restful import Resource

class InventoryItem(Resource):
    def get(self, item_id):
        """
        Get a specific inventory item (such as for a product's page)

        Example: curl -X GET -H "Content-Type: application/json" 127.0.0.1:5000/store/<id>
        """
        item = get_store_inventory(("ID", item_id), unique_match=True)
        return item, 200

class InventoryItems(Resource):
    def get(self):
        """
        Get all inventory items (such as for catalogue pages)

        Example: curl -X GET -H "Content-Type: application/json" 127.0.0.1:5000/store
        """
        items = get_store_inventory()
        return items, 200

class InventorySearch(Resource):
    def get(self, search_query):
        """
        Search for inventory items via a fuzzy match
        - uses the basic partial match of get_store_inventory which just checks with name_var.startswith(query)

        Example: curl -X GET -H "Content-Type: application/json" 127.0.0.1:5000/store/search/<query>
        """
        items = get_store_inventory(("name", search_query), unique_match=False, partial_match=50)
        return items, 200