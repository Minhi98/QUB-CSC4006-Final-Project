import json

from var import *
from security import *
from utilities import *
from request_jwt import *
from decorators import jwt_authenticate

from flask_restful import Resource, reqparse

class OrderHistoryResource(Resource):
    @jwt_authenticate
    def get(self, user_id):
        """
        Returns details of currently logged in user (dependent on JWT)
        
        Example: curl -X GET -H "Content-Type: application/json" -H "Authorization: Bearer ${TOKEN}" 127.0.0.1:5000/order/<user_id>
        """
        orders = get_orders()
        orders = {k:v for k, v in orders.items() if str(v["user_id"]) == user_id}
        return orders, 200
    
    @jwt_authenticate
    def put(self, user_id):
        """
        Edits existing customer order
        
        Example: curl -X PUT -H "Content-Type: application/json" -H "Authorization: Bearer ${TOKEN}" 127.0.0.1:5000/order/<user_id> -d '{"order_no":"<order_no>", "order_note": "<new_note>", "order_basket": "<new_basket_dictionary>"}'
        """
        registration_args = reqparse.RequestParser()
        registration_args.add_argument("order_no", type=str)
        registration_args.add_argument("new_note", type=str)
        registration_args.add_argument("new_basket", type=str)
        args = registration_args.parse_args()

        orders = get_orders()
        order = next(({k:v} for k, v in orders.items() if k == args["order_no"] and str(v["user_id"]) == user_id), {})

        response = requests.put(
            url=DatastoreURL(ORDERS),
            json={"ID": args["order_no"], "user_id": user_id, "order_note": args["new_note"], "order_items": args["new_basket"]},
            headers=HEADERS
        )

        return response.status_code
    
    @jwt_authenticate
    def post(self, user_id):
        """
        Adds a new customer order
        
        Example: curl -X POST -H "Content-Type: application/json" -H "Authorization: Bearer ${TOKEN}" 127.0.0.1:5000/order/<user_id> -d '{"order_note": "<note>", "order_items": "<basket_dictionary>"}'
        """
        registration_args = reqparse.RequestParser()
        registration_args.add_argument("order_note", type=str)
        registration_args.add_argument("order_items", type=str)
        args = registration_args.parse_args()

        if not args["order_items"]:
            return 400

        args["user_id"] = user_id

        response = requests.post(url=DatastoreURL(ORDERS), json=args, headers=HEADERS)

        return response.status_code