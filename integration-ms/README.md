# Integration Microservice

Contains middleware endpoints for interop between backend and frontend.

Docker Hub: [minhi98/4006-integration](https://hub.docker.com/r/minhi98/4006-integration)

## Example Usage

### /User

```bash
# Read details of user by JWT Token
curl -X GET -H "Content-Type: application/json" -H "Authorization: Bearer ${TOKEN}" 127.0.0.1:5000/user

# Update Account Details by TOKEN and ID
curl -X PUT -H "Content-Type: application/json" -H "Authorization: Bearer ${TOKEN}" 127.0.0.1:5000/user/<id> -d '{"email": "<email>", "username": "<user>", "password": "<pass>", "address": "<addr>"}'

#  Deletes the current user's account
curl -X DELETE -H "Content-Type: application/json" -H "Authorization: Bearer ${TOKEN}" 127.0.0.1:5000/user/<id>

# Account Registration
curl -X POST -H "Content-Type: application/json" 127.0.0.1:5000/user/register -d '{"email": "<email>", "username":"<user>", "password":"<pass>", "address":"<addr>"}'

# User Login (returns JWT)
curl -X GET -H "Content-Type: application/json" 127.0.0.1:5000/user/login -d '{"username": "<username>", "password": "<password>"}'

# Logs out the user by blacklisting their current jwt
curl -X DELETE -H "Content-Type: application/json" -H "Authorization: Bearer ${TOKEN}" 127.0.0.1:5000/user/logout
```

### /Store

```bash
# Get a specific inventory item (such as for a product's page)
curl -X GET -H "Content-Type: application/json" 127.0.0.1:5000/store/<id>

# Get all inventory items (such as for catalogue pages)
curl -X GET -H "Content-Type: application/json" 127.0.0.1:5000/store

# Search for inventory items via a fuzzy match
curl -X GET -H "Content-Type: application/json" 127.0.0.1:5000/store/search/<query>
```

### /basket

```bash
# Returns details of currently logged in user (dependent on JWT)
curl -X GET -H "Content-Type: application/json" -H "Authorization: Bearer ${TOKEN}" 127.0.0.1:5000/basket/<id>

# Edit user's basket. A basket is made if none exist for the user_id.
curl -X PUT -H "Content-Type: application/json" -H "Authorization: Bearer ${TOKEN}" 127.0.0.1:5000/basket/1 -d '{"added_json": {"<id>":<quantity>}, "removed_json": {"<id>":<quantity>}}'

# Creates a new basket for the unique user's id (derived from their JWT email)
curl -X POST -H "Content-Type: application/json" -H "Authorization: Bearer ${TOKEN}" 127.0.0.1:5000/basket/<id>
```

### /orders

```bash
# Returns details of currently logged in user (dependent on JWT)
curl -X GET -H "Content-Type: application/json" -H "Authorization: Bearer ${TOKEN}" 127.0.0.1:5000/order/<user_id>

# Edits existing customer order
curl -X PUT -H "Content-Type: application/json" -H "Authorization: Bearer ${TOKEN}" 127.0.0.1:5000/order/<user_id> -d '{"order_no":"<order_no>", "order_note": "<new_note>", "order_basket": "<new_basket_dictionary>"}'
```
