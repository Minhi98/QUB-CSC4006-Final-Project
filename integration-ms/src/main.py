from flask import Flask
from flask_restful import Api

from var import *

from modules.user import *
from modules.store import *
from modules.baskets import *
from modules.orders import *

app = Flask(__name__)
api = Api(app)

assert JWT_SERVICE["SECRET"], "JWT_SECRET must be set. It is critical for JWT Token encode/decode."
app.config["JWT_SECRET_KEY"] = JWT_SERVICE["SECRET"]

api.add_resource(CurrentUser, '/user')
api.add_resource(UserSpecific, '/user/<string:user_id>')
api.add_resource(UserRegistration, '/user/register')
api.add_resource(UserLogin, '/user/login')
api.add_resource(UserLogout, '/user/logout')

api.add_resource(InventoryItems, '/store')
api.add_resource(InventoryItem, '/store/<string:item_id>')
api.add_resource(InventorySearch, '/store/search/<string:search_query>')

api.add_resource(UserBasket, '/basket/<string:user_id>')
api.add_resource(OrderHistoryResource, '/order/<string:user_id>')

if __name__ == "__main__":
    # Only run flask for development "flask --app main.py --debug run"
    app.run(host="0.0.0.0", port="5000", debug=True)