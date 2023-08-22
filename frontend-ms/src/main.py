import requests
import json
import ast

from vars import *
from forms import *
from decorators import base_template

from flask_bootstrap import Bootstrap5
from flask_wtf import CSRFProtect
from flask import Flask, render_template, request, redirect, url_for, make_response, flash

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY

bootstrap = Bootstrap5(app)
csrf = CSRFProtect(app)

def derive_page_nums(int_list: list, per_page: int) -> list:
    """ Index and Search Page function for generating the number of pagination pages """
    return [(int(x)//per_page)+1 for x in int_list[0::per_page]]

def get_jwt(request, decode: bool = False):
    """ Performs a get request for the user's JWT """
    jwt_cookie = request.cookies.get('loginJWT', None)
    if decode:
        jwt = {}
        if jwt_cookie:
            jwt = requests.get(
                url=f"{INTEGRATION}/user",
                headers=HEADERS|{"Authorization": f"Bearer {jwt_cookie}"}
            ).json()
        return jwt
    return jwt_cookie

def auth_redirect(request):
    """ JWT Validation, redirecting to index if invalid """
    jwt = get_jwt(request)
    jwt_id = get_jwt(request, decode=True).get("ID", None)
    if jwt_id is None:
        return redirect(url_for('index'))
    return jwt, jwt_id

@app.route('/', methods=['GET', 'POST'])
@base_template
def index(**kwargs):
    """
    Homepage and catalogue, showing catalogue via pagination
    """
    per_page = request.args.get('per_page', 9)
    current_page = int(request.args.get('page', 1))
    offset = (current_page-1) * per_page

    catalogue_json = requests.get(url=f"{INTEGRATION}/store", headers=HEADERS).json()
    if catalogue_json != {'message': 'Internal Server Error'}:
        for k,v in catalogue_json.items():
            # If the data loads as a string, an error has occurred and data needs to be set as placeholders
            if isinstance(v, str):
                catalogue_json[k]["metadata"] = {"images": ["https://via.placeholder.com/256.jpg"], "product_description": "An error has occurred with this product's internal formatting."}
                catalogue_json[k]["price"] = "Price Unavailable"
            else:
                catalogue_json[k]["metadata"] = json.loads(v.get("metadata", '{"images": ["https://via.placeholder.com/256.jpg"]}'))
                catalogue_json[k]["price"] = float(catalogue_json[k]["price"])
                
        current_page_catalogue = {k:v for k,v in catalogue_json.items() if int(k) in range(offset+1,offset+per_page+1)}

        pages = derive_page_nums(list(catalogue_json.keys()), per_page)
        if len(pages) == 1:
            pages = [1]

        return render_template(
            'index.html', **kwargs, 
            catalogue_json=current_page_catalogue, 
            per_page=per_page, 
            num_of_pages=pages,
            current_page=current_page,
            index_header="Our Catalogue"
        )
    else:
        return render_template(
            'index.html', **kwargs, 
            catalogue_json={}, 
            per_page=0, 
            num_of_pages=[],
            current_page=1,
            index_header="The store is inaccessible due to ongoing maintenance."
        )

@app.route('/search', methods=['GET', 'POST'])
@base_template
def search(**kwargs):
    """
    Search results page, showing results via pagination
    """
    query = request.args.get('query', None)
    if query is None:
        return redirect(url_for('index'))
    catalogue_json = requests.get(f"{INTEGRATION}/store/search/{query}").json()

    if catalogue_json != {'message': 'Internal Server Error'}:
        per_page = request.args.get('per_page', 9)
        current_page = int(request.args.get('page', 1))
        offset = (current_page-1) * per_page
        pages = derive_page_nums(list(catalogue_json.keys()), per_page)
        if len(pages) == 1:
            pages = [1]

        if not catalogue_json:
            catalogue_json = requests.get(f"{INTEGRATION}/store").json()

        for k,v in catalogue_json.items():
            # If the data loads as a string, an error has occurred and data needs to be set as placeholders
            if isinstance(v, str):
                catalogue_json[k]["metadata"] = {"images": ["https://via.placeholder.com/256.jpg"], "product_description": "An error has occurred with this product's internal formatting."}
                catalogue_json[k]["price"] = "Price Unavailable"
            else:
                catalogue_json[k]["metadata"] = json.loads(v.get("metadata", '{"images": ["https://via.placeholder.com/256.jpg"]}'))
                catalogue_json[k]["price"] = float(catalogue_json[k]["price"])
        
        current_page_catalogue = {k:v for k,v in catalogue_json.items() if int(k) in range(offset+1,offset+per_page+1)}

        return render_template(
            'index.html', **kwargs, 
            catalogue_json=current_page_catalogue, 
            per_page=per_page, 
            num_of_pages=pages,
            current_page=current_page,
            index_header=f"Search: {query}",
        )
    else:
        return render_template(
            'index.html', **kwargs, 
            catalogue_json={}, 
            per_page=0, 
            num_of_pages=[],
            current_page=1,
            index_header="The store is inaccessible due to ongoing maintenance."
        )



@app.route('/item/<id>', methods=['GET', 'POST'])
@base_template
def item(id, **kwargs):
    """
    Generates page for the item, the page template is filled out using metadata stored in the item datastore
    """
    item_json = requests.get(f"{INTEGRATION}/store/{id}").json()
    if item_json != {'message': 'Internal Server Error'}:
        item_key, item_values = list(item_json.items())[0]
        try:
            item_values["price"] = float(item_values["price"])
        except:
            item_values["price"] = "Price Unavailable"
        metadata = json.loads(item_values.get("metadata", {}))
        images = metadata.get("images", ["placeholder"])
        return render_template(
            'item.html', **kwargs, 
            item_key=item_key, 
            item_values=item_values, 
            metadata=metadata, 
            images=images,
            id=id
        )
    else:
        return redirect(url_for('index'))

@app.route('/user', methods=['GET', 'POST'])
@base_template
def user(**kwargs):
    """
    User profile page, primarily used to for modifying user information
    """
    jwt, id = auth_redirect(request=request)
    
    user_details = kwargs.get('user_details', None)
    delete_acc_form = DeleteAccountButton()
    change_acc_form = ChangeDetailsForm()

    # Delete button handler, sending a delete request, logging the user out and redirecting to the homepage
    if delete_acc_form.validate_on_submit() and delete_acc_form.delete_button.data:
        delete_response = requests.delete(
            url=f"{INTEGRATION}/user/{id}",
            headers=HEADERS|{"Authorization": f"Bearer {jwt}"},
        )
        if delete_response.status_code != 200:
            flash(f"{change_response.status_code} - An error has occurred.")
            return redirect(url_for('user'))
        logout_response = requests.delete(
            url=f"{INTEGRATION}/user/logout",
            headers=HEADERS|{"Authorization": f"Bearer {jwt}"}
        )
        if logout_response.status_code != 404:
            set_login_cookie = make_response(redirect(url_for('homepageRedirect')))
            set_login_cookie.delete_cookie('loginJWT')
            return set_login_cookie

    # Account change handler, sending a put request based on entered information
    if change_acc_form.validate_on_submit():
        new_username = change_acc_form.ch_username.data
        new_password = change_acc_form.ch_password.data
        new_email = change_acc_form.ch_email.data
        new_address = change_acc_form.ch_address.data
        new_data_json = {"ID": id}

        if new_username:
            new_data_json.update({"username": new_username})
        if new_email:
            new_data_json.update({"email": new_email})
        if new_password:
            new_data_json.update({"password": new_password})
        if new_address:
            new_data_json.update({"address": new_address})

        needs_new_jwt = bool(new_email)

        change_response = requests.put(
            url=f"{INTEGRATION}/user/{id}",
            headers=HEADERS|{"Authorization": f"Bearer {jwt}"},
            json=new_data_json
        )

        if change_response.status_code == 400:
            flash(f"{change_response.status_code} - An error has occurred.")
            return redirect(url_for('user'))
        elif change_response.status_code != 200:
            flash(f"{change_response.status_code} - An error has occurred.")

        if needs_new_jwt:
            logout_response = requests.delete(
                url=f"{INTEGRATION}/user/logout",
                headers=HEADERS|{"Authorization": f"Bearer {jwt}"}
            )
            if logout_response.status_code != 404:
                set_login_cookie = make_response(redirect(url_for('homepageRedirect')))
                set_login_cookie.delete_cookie('loginJWT')
                return set_login_cookie
        return redirect(url_for('user'))

    orders = requests.get(
        url=f"{INTEGRATION}/order/{id}",
        headers=HEADERS|{"Authorization": f"Bearer {jwt}"}
    ).json()
    for k in orders.keys():
        orders[k]["order_items"] = ast.literal_eval(orders[k]["order_items"])
        orders[k].pop("user_id")
    
    store_items = requests.get(
        url=f"{INTEGRATION}/store",
        headers=HEADERS|{"Authorization": f"Bearer {jwt}"}
    ).json()
    store_item_names = {k:v["name"] for k,v in store_items.items()}

    return render_template(
        'user.html', **kwargs,
        profile=user_details,
        delete_acc_form=delete_acc_form,
        change_acc_form=change_acc_form,
        order_history=orders,
        store_item_names=store_item_names
    )

@app.route('/basket', methods=['GET', 'POST'])
@base_template
def basket(**kwargs):
    """
    Basket page with basket item controls and a checkout 
    (implemented as emptying the basket with payment methods to be implemented by the person following the educational material)
    """
    jwt, jwt_id = auth_redirect(request=request)

    basket = requests.get(
        url=f"{INTEGRATION}/basket/{jwt_id}",
        headers=HEADERS|{"Authorization": f"Bearer {jwt}"}
    ).json()
    
    user_basket = {}
    basket_list = {}
    total_price = 0.00

    if basket:
        _,user_basket = list(basket.items())[0]
        basket_items = json.loads(user_basket["basket"])
        
        for item_id, quantity in basket_items.items():
            item_get = requests.get(f"{INTEGRATION}/store/{item_id}").json()[item_id]
            basket_item_price = float(item_get["price"]) * float(quantity)
            total_price = total_price + basket_item_price

            item_get["metadata"] = json.loads(item_get["metadata"])
            if "images" not in item_get["metadata"].keys():
                item_get["metadata"].update({"images": ["https://via.placeholder.com/256.jpg"]})
            elif "images" in item_get["metadata"].keys():
                if not item_get["metadata"]["images"]:
                    item_get["metadata"]["images"] = {"images": ["https://via.placeholder.com/256.jpg"]}
            
            basket_list.update({item_id:{"data": item_get, "quantity": quantity, "price_total": basket_item_price}})

    return render_template(
        'basket.html', **kwargs,
        total_price=total_price,
        user_basket=user_basket,
        basket_list=basket_list
    )

@app.route('/modifyCartItem', methods=['POST'])
@base_template
def modifyCartItem(**kwargs):
    """
    Modifies the user's cart by adding and removing items, or emptying the cart on checkouts - and registering checkouts to order histories.
    """
    jwt, jwt_id = auth_redirect(request=request)
    itemid = request.args.get('itemid', type=str)
    quantity = request.args.get('quantity', type=int)
    checkout = request.args.get('checkout', type=int, default=0)

    basket = requests.get(
        url=f"{INTEGRATION}/basket/{jwt_id}",
        headers=HEADERS|{"Authorization": f"Bearer {jwt}"}
    ).json()

    # If the user has no entry in the database, then send a couple requests to create one.
    # The put request for baskets creates an entry if one doesn't exist for the user, so just add and remove an item.
    if (not basket or (basket and str(jwt_id) not in [str(v['user_id']) for v in basket.values()])) and not checkout:
        requests.put(
            url=f"{INTEGRATION}/basket/{jwt_id}",
            headers=HEADERS|{"Authorization": f"Bearer {jwt}"},
            json={
                "added_json":{f"{itemid}":1}
            }
        )
        requests.put(
            url=f"{INTEGRATION}/basket/{jwt_id}",
            headers=HEADERS|{"Authorization": f"Bearer {jwt}"},
            json={
                "removed_json":{f"{itemid}":1}
            }
        )
        basket = requests.get(
            url=f"{INTEGRATION}/basket/{jwt_id}",
            headers=HEADERS|{"Authorization": f"Bearer {jwt}"}
        ).json()

    basket = next((v["basket"] for v in basket.values() if str(v["user_id"]) == str(jwt_id)), {})
    basket = json.loads(basket)
    
    # If they're checking out then remove all items from the basket and after send the entire basket to their order history as a new order.
    if checkout:
        for checkout_id, checkout_quantity in basket.items():
            requests.put(
                url=f"{INTEGRATION}/basket/{jwt_id}",
                headers=HEADERS|{"Authorization": f"Bearer {jwt}"},
                json={
                    "removed_json":{f"{checkout_id}":checkout_quantity}
                }
            )
        requests.post(
            url=f"{INTEGRATION}/order/{jwt_id}",
            headers=HEADERS|{"Authorization": f"Bearer {jwt}"},
            json={
                "order_note": "",
                "order_items": basket
            }
        )
        flash("Your order has been processed")
        return redirect(url_for('user'))

    # basket item quantity modification handlers
    if not checkout:
        if quantity == 1:
            requests.put(
                url=f"{INTEGRATION}/basket/{jwt_id}",
                headers=HEADERS|{"Authorization": f"Bearer {jwt}"},
                json={
                    "added_json":{f"{itemid}":1}
                }
            )
        if quantity == -1:
            requests.put(
                url=f"{INTEGRATION}/basket/{jwt_id}",
                headers=HEADERS|{"Authorization": f"Bearer {jwt}"},
                json={
                    "removed_json":{f"{itemid}":1}
                }
            )
        if quantity == 0:
            requests.put(
                url=f"{INTEGRATION}/basket/{jwt_id}",
                headers=HEADERS|{"Authorization": f"Bearer {jwt}"},
                json={
                    "removed_json":{f"{itemid}":basket[itemid]}
                }
            )
    
    return redirect(url_for('basket'))

@app.route('/userRegistration', methods=['GET', 'POST'])
@base_template
def userRegistration(**kwargs):
    registration_form = RegistrationForm()
    if registration_form.validate_on_submit():
        username = registration_form.regusername.data
        password = registration_form.regpassword.data
        email = registration_form.regemail.data
        address = registration_form.regaddress.data

        registration_response = requests.post(
            url=f"{INTEGRATION}/user/register",
            headers=HEADERS,
            json={
                "username": username,
                "email": email,
                "password": password,
                "address": address
            }
        )
        if registration_response.status_code != 200:
            flash("There was an error processing your registration, please try again in a few minutes.")
        else:
            login_response = requests.get(
                url=f"{INTEGRATION}/user/login",
                headers=HEADERS,
                json={
                    "username": username,
                    "password": password
                }
            )
            login_jwt = login_response.json()['token'][0] if login_response.status_code == 200 else None
            if login_response.status_code == 200:
                set_login_cookie = make_response(redirect(url_for('homepageRedirect')))
                set_login_cookie.set_cookie('loginJWT', login_jwt)
                return set_login_cookie

    return render_template(
        'registration.html', **kwargs,
        registration_form=registration_form
    )

@app.route('/homepageRedirect', methods=['GET', 'POST'])
@base_template
def homepageRedirect(**kwargs):
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5001", debug=True)
