# Datastore

A generic storage handling microservice. Intended to be connected alongside a MYSQL DB of 1 specified table to perform CRUD requests with an external service (e.g. integration). The only hard requirement of this service is that the table must feature an ID column with the following constraints: INT NOT NULL AUTOINCREMENT PRIMARY KEY.

The use case of this is for simple storage microservices such as a table of products for an e-commerce website. More specific storage should have their own image, or be made as a unique tag of your storage microservice image (see token-authentication).

- Docker Registry Image: [minhi98/4006-datastore](https://hub.docker.com/minhi98/4006-datastore)

## Example Usage

Create

```bash
curl -X POST -H "Content-Type: application/json" 127.0.0.1:5000/data -d '{"test_field1":"test_str", "test_field2": 123}'
```

Read

```bash
# Gets table column names
curl -X GET -H "Content-Type: application/json" 127.0.0.1:5000/data -d '{"desc": true}'

# Gets row by ID
curl -X GET -H "Content-Type: application/json" 127.0.0.1:5000/data -d '{"ID": 2}'

# Gets all rows
curl -X GET -H "Content-Type: application/json" 127.0.0.1:5000/data -d '{}'
```

Update

```bash
# ID determines the row being updated, other parameters determine what data to update
curl -X PUT -H "Content-Type: application/json" 127.0.0.1:5000/data -d '{"ID": 2, "test_field1":"edit_str", "test_field2": 1234}'
```

Delete

```bash
curl -X DELETE -H "Content-Type: application/json" 127.0.0.1:5000/data -d '{"ID":1}'
```
