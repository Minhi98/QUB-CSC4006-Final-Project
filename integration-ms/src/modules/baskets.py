import json

from var import *
from security import *
from utilities import *
from request_jwt import *
from decorators import jwt_authenticate

from flask_restful import Resource, reqparse

class UserBasket(Resource):
    """
    Endpoints for the user's basket. 
    Requires a user_id value for comparison between the token subject and the ID.
    """

    @jwt_authenticate
    def get(self, user_id):
        """
        Returns details of currently logged in user (dependent on JWT)
        
        Example: curl -X GET -H "Content-Type: application/json" -H "Authorization: Bearer ${TOKEN}" 127.0.0.1:5000/basket/<id>
        """
        
        baskets = get_baskets()
        user_basket = next(({k:v} for k, v in baskets.items() if str(v["user_id"]) == user_id), {})
        
        return user_basket, 200
    
    @jwt_authenticate
    def put(self, user_id):
        """
        Edit user's basket.
        A basket is made if none exist for the user_id.

        added_json      ::  JSON string that contain key value pairs of product IDs and their quantities.
        removed_json    ::  JSON string that contain key value pairs of product IDs and their quantities.

        For both parameters, json in the form of: {'unique_item_id': 'quantity_value'}
        This endpoint assumes duplicate item ids in parameters are bad requests.

        Example: curl -X PUT -H "Content-Type: application/json" -H "Authorization: Bearer ${TOKEN}" 127.0.0.1:5000/basket/1 -d '{"added_json": {"<id>":<quantity>}, "removed_json": {"<id>":<quantity>}}'
        """

        basket_args = reqparse.RequestParser()
        basket_args.add_argument("added_json", type=dict, default={})
        basket_args.add_argument("removed_json", type=dict, default={})
        args = basket_args.parse_args()

        # Bad request if no data provided
        if not args["added_json"] and not args["removed_json"]:
            return 400

        added_items = args.get("added_json", {})
        removed_items = args.get("removed_json", {})
        
        # Bad request if duplicate keys
        if set(added_items.keys()).intersection(set(removed_items.keys())):
            return 400

        # Make a basket if one doesn't exist
        basket = get_baskets(("user_id", user_id), unique_match=True)
        if not basket:
            requests.post(
                url=DatastoreURL(BASKETS), 
                json={"user_id": user_id, "basket": json.dumps({}, default=str)}, 
                headers=HEADERS
            )

        baskets = get_baskets()
        user_basket = next(({k:v} for k, v in baskets.items() if str(v["user_id"]) == user_id), {})
        basket_id, basket = list(user_basket.items())[0]
        basket = json.loads(basket["basket"])

        for item_id_key, item_quantity in added_items.items():
            # id's not in the list are effectively 0, otherwise set it to the total
            if item_id_key not in basket.keys():
                basket.update({item_id_key: item_quantity})
            else:
                basket[item_id_key] = basket[item_id_key] + item_quantity

        for item_id_key, item_quantity in removed_items.items():
            # can't remove what doesn't exist, so skip.
            if item_id_key not in basket.keys():
                pass
            else:
                # calculate new quantity, delete from basket if 0 or less
                new_quantity = basket[item_id_key] - item_quantity
                if new_quantity <= 0:
                    del basket[item_id_key]
                else:
                    basket[item_id_key] = new_quantity

        response = requests.put(
            url=DatastoreURL(BASKETS),
            json={"ID": basket_id, "user_id": user_id, "basket": json.dumps(basket, default=str)},
            headers=HEADERS
        )
        return basket, response.status_code
    
    @jwt_authenticate
    def post(self, user_id):
        """
        Creates a new basket for the unique user's id (derived from their JWT email)

        Example: curl -X POST -H "Content-Type: application/json" -H "Authorization: Bearer ${TOKEN}" 127.0.0.1:5000/basket/<id>
        """

        basket = get_baskets(("user_id", user_id), unique_match=True)
        if basket:
            return 400

        response = requests.post(
            url=DatastoreURL(BASKETS), 
            json={"user_id": user_id, "basket": json.dumps({}, default=str)}, 
            headers=HEADERS
        )

        return response.status_code
        