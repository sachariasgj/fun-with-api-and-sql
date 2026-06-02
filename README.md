# NovaStore API + Database + Cache Lab

This is a starter codebase for the exercise.
You will work with:

- Flask API
- PostgreSQL
- Redis
- Docker Compose
- Python requests client

## Architecture

The project contains four services:

- `api` - Flask backend API
- `db` - PostgreSQL database
- `redis` - Redis cache
- `client` - Python client that calls the API

## Start the project

Run this from the project root:

```bash
docker compose up --build
```

The API is available from your computer at:

```text
http://localhost:5001
```

Inside Docker, the client talks to the API at:

```text
http://api:5000
```

## Test API manually

Open in browser:

```text
http://localhost:5001/health
http://localhost:5001/products
```

Or use curl:

```bash
curl http://localhost:5001/health
curl http://localhost:5001/products
```

## Run the client

In a new terminal:

```bash
docker compose run --rm client
```

## Connect to PostgreSQL

```bash
docker exec -it novastore-db psql -U student -d novastore
```

Try:

```sql
SELECT * FROM products;
```

## Connect to Redis

```bash
docker exec -it novastore-redis redis-cli
```

Try:

```redis
KEYS *
GET products
```

## Övningens TODO

### Del 2

Implementera (Uppgift 5-6):

- `GET /products/{id}`
- `404 Not Found`

Files:

- `api/app.py`
- `api/db.py`

### Del 3

Implementera (Uppgift 7-10):

- `POST /products`
- `201 Created`
- `400 Bad Request`

Files:

- `api/app.py`
- `api/db.py`

### Del 4

Implementera Redis-cache för (Uppgift 12-15):

- `GET /products`
- `CACHE HIT`
- `CACHE MISS`

Files:

- `api/app.py`
- `api/cache.py`

### Del 5

Implementera cache invalidation efter (Uppgift 17):

- `POST /products`

Files:

- `api/app.py`
- `api/cache.py`

## Stop the project

```bash
docker compose down
```

To also remove volumes/data:

```bash
docker compose down -v
```
