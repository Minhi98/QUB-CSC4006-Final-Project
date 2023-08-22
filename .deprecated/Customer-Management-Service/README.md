# Customer Management Microservice (CMS)

This CMS is a data model of the customer acccounts which are used to identify account specific details from other microservices (e.g. receipts).

- Docker Registry Image: [minhi98/4006-cms](https://hub.docker.com/r/minhi98/4006-cms)
- Demo Domain: cms.csc4006.minhi.net

## Example Usages

### Auth

Create

*As written permissions of Auth are admins only for administrative requests (i.e. changing permissions), otherwise a client can view and edit themselves (with limitations if they're non-admin clients).*

```bash
curl -X POST -H "Content-Type: application/json" cms.csc4006.minhi.net/auth -d '{"new_client_id": "non_admin_test", "new_client_secret": "non_admin_pass123"}'
```

```bash
curl -X POST -H "Content-Type: application/json" cms.csc4006.minhi.net/auth -d '{"id": "admin_test", "secret": "admin_pass123", "new_client_id": "new_admin", "new_client_secret": "admin_pass234", "admin": true}'
```

Read

```bash
curl -X GET -H "Content-Type: application/json" cms.csc4006.minhi.net/auth -d '{"id": "admin_test", "secret": "admin_pass123", "target": "non_admin_test"}'
```

```bash
curl -X GET -H "Content-Type: application/json" cms.csc4006.minhi.net/auth -d '{"id": "non_admin_test", "secret": "non_admin_pass123", "target": "non_admin_test"}'
```

Update

```bash
curl -X PUT -H "Content-Type: application/json" cms.csc4006.minhi.net/auth -d '{"id": "admin_test", "secret": "admin_pass123", "target": "non_admin_test", "new_client_id": "edit_test", "new_client_secret": "edit_pass", "admin": true}'
```

Delete

```bash
# intended to fail 
curl -X DELETE -H "Content-Type: application/json" cms.csc4006.minhi.net/auth -d '{"id": "non_admin_test", "secret": "non_admin_pass123", "target":"admin_test"}'
```

```bash
curl -X DELETE -H "Content-Type: application/json" cms.csc4006.minhi.net/auth -d '{"id": "admin_test", "secret": "admin_pass123", "target":"non_admin_test"}'
```

### Customer

Create

```bash
curl -X POST -H "Content-Type: application/json" cms.csc4006.minhi.net/customer/new_customer@test.com -d '{"id": "admin_test", "secret": "admin_pass123", "name": "new_test", "password": "123", "address": "bt12 123", "phonenumber": "123"}'
```

```bash
curl -X POST -H "Content-Type: application/json" cms.csc4006.minhi.net/customer/new_customer2@test.com -d '{"id": "admin_test", "secret": "admin_pass123", "name": "new_test", "password": "123", "encrypted": "True", "address": "bt12 123", "phonenumber": "123"}'
```

Read

```bash
curl -X GET -H "Content-Type: application/json" cms.csc4006.minhi.net/customer/new_customer@test.com -d '{"id": "admin_test", "secret": "admin_pass123"}'
```

Update

```bash
curl -X PUT -H "Content-Type: application/json" cms.csc4006.minhi.net/customer/new_customer2@test.com -d '{"id": "admin_test", "secret": "admin_pass123", "email": "edit_customer@test.com", "name": "new_test", "password": "123", "address": "bt12 123", "phonenumber": "123"}'
```

Delete

```bash
curl -X DELETE -H "Content-Type: application/json" cms.csc4006.minhi.net/customer/edit_customer@test.com -d '{"id": "admin_test", "secret": "admin_pass123"}'
```

### Customers

Read

```bash
curl -X GET -H "Content-Type: application/json" cms.csc4006.minhi.net/customers -d '{"id": "admin_test", "secret": "admin_pass123"}'
```
