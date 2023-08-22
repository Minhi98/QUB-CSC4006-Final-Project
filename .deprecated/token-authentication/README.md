# Token-Based Authentication

Central authentication microservice for backend or otherwise non-user-facing services.

- Docker Registry Image: [minhi98/4006-token-authentication](https://hub.docker.com/r/minhi98/4006-token-authentication)
- Demo Domain: `auth.csc4006.minhi.net`

Demo Authentication:

- Username: `Demo`
- Password: `123`
- Token: `HzDBAF1WGQRKHLCdSRdJMHODp542nB`

## Example Usages

### Users ('/user')

#### Create

```bash
curl -X POST -H "Content-Type: application/json" auth.csc4006.minhi.net/user -d '{"access_token": "<token>", "username": "<name>", "password": "<pass>"}'
```

#### Read

```bash
curl -X GET -H "Content-Type: application/json" auth.csc4006.minhi.net/user -d '{"access_token": "<token>", "username": "<username>"}'
```

#### Update

```bash
curl -X PUT -H "Content-Type: application/json" auth.csc4006.minhi.net/user -d '{"access_token": "<token>", "username": "<target_user>", "new_username": "<new_name>", "new_password": "<new_pass>"}'
```

#### Delete

```bash
curl -X DELETE -H "Content-Type: application/json" auth.csc4006.minhi.net/user -d '{"access_token": "<token>", "username": "<username>"}'
```

### Token Issuing ('/token')

#### Create

```bash
curl -X POST -H "Content-Type: application/json" auth.csc4006.minhi.net/token -d '{"username": "<your_username>", "password": "<your_pass>"}'
```

#### Delete

```bash
curl -X DELETE -H "Content-Type: application/json" auth.csc4006.minhi.net/token -d '{"access_token": "<token>", "target_token": "<token>"}'
```

```bash
curl -X DELETE -H "Content-Type: application/json" auth.csc4006.minhi.net/token -d '{"access_token": "<token>", "username": "<username>"}'
```

```bash
curl -X DELETE -H "Content-Type: application/json" auth.csc4006.minhi.net/token -d '{"access_token": "<token>", "username": "<userID>"}'
```

```bash
curl -X DELETE -H "Content-Type: application/json" auth.csc4006.minhi.net/token -d '{"access_token": "<token>", "username": "<username or userID>", "target_token": "<target_token>"}'
```
