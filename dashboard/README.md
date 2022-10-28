# Grafana Dashboard

1. Install docker and docker-compose

2. Run

```
docker-compose up -d
```

3. Go to http://localhost:3000.

4. Login:

```
username: user
password: pass
```

5. Go to Settings (bottom left) > Data Sources > Add data Source > PostgresQL

6. Fill in

```
Host: db:5432
Database: deload
User: postgres
Password: password
TLS/SSL method: disabled
```

7. Press Save & test

8. Create a dashboard under "Dashboards" (left column)
