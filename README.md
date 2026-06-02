# Fun With SQL and API

A Flask REST API using PostgreSQL and Redis.

This project demonstrates:

* REST API development with Flask
* PostgreSQL database integration
* Redis caching
* Cache invalidation
* Partial cache refreshes
* Product inventory management

---

## Features

### Product Management

* Get all products
* Get a product by ID
* Create products
* Purchase products (decrease stock)
* Partially update products using PATCH

### Redis Caching

Product fields are cached separately:

| Field    | Cache Duration |
| -------- | -------------- |
| id       | 5 minutes      |
| name     | 5 minutes      |
| category | 5 minutes      |
| price    | 1 minute       |
| stock    | 10 seconds     |

Expired fields are refreshed individually from PostgreSQL without reloading the entire product.

---

## Requirements

### Docker

* Docker
* Docker Compose

### Local Development

* Python 3.12+
* PostgreSQL
* Redis

---

## Running the Application

Start all services:

```bash
docker compose up --build
```

The API will be available at:

```text
http://localhost:5001 #port 5000 should work but did not for me
```

---

## API Endpoints

### Health Check

```http
GET /health
```

Example:

```bash
curl http://localhost:5001/health
```

Response:

```json
{
  "status": "ok"
}
```

---

### Get All Products

```http
GET /products
```

Optional filters:

```http
GET /products?category=Electronics
GET /products?sort=price
GET /products?sort=price_desc
```

Example:

```bash
curl http://localhost:5001/products
```

---

### Get Product By ID

```http
GET /products/1
```

Example:

```bash
curl http://localhost:5001/products/1
```

---

### Create Product

```http
POST /products
```

Request Body:

```json
{
  "name": "Keyboard",
  "price": 99.99,
  "category": "Electronics",
  "stock": 10
}
```

Example:

```bash
curl -X POST http://localhost:5001/products \
-H "Content-Type: application/json" \
-d '{
  "name":"Keyboard",
  "price":99.99,
  "category":"Electronics",
  "stock":10
}'
```

---

### Purchase Product

Decreases stock by 1.

```http
POST /products/1/purchase
```

Example:

```bash
curl -X POST http://localhost:5001/products/1/purchase
```

Response:

```json
{
  "message": "Purchase successful",
  "stock": 9
}
```

---

### Update Product Fields

```http
PATCH /products/1
```

Update stock:

```json
{
  "stock": 25
}
```

Update price:

```json
{
  "price": 149.99
}
```

Update multiple fields:

```json
{
  "price": 149.99,
  "stock": 25
}
```

Example:

```bash
curl -X PATCH http://localhost:5001/products/1 \
-H "Content-Type: application/json" \
-d '{"stock":25}'
```

---

## Redis Cache Strategy

The API uses the Cache-Aside pattern.

### First Request

```text
Client
  ↓
Flask API
  ↓
PostgreSQL
  ↓
Redis Cache
```

### Cached Request

```text
Client
  ↓
Flask API
  ↓
Redis Cache
```

### Stock Cache Expired

```text
Client
  ↓
Flask API
  ↓
Redis Cache
  ↓
PostgreSQL (stock only)
```

### Price Cache Expired

```text
Client
  ↓
Flask API
  ↓
Redis Cache
  ↓
PostgreSQL (price only)
```

### Metadata Cache Expired

```text
Client
  ↓
Flask API
  ↓
PostgreSQL (full product)
```

---

## Project Structure

```text
.
├── app.py
├── db.py
├── cache.py
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## Future Improvements

* PUT endpoint
* DELETE endpoint
* Product categories table
* Order management
* Database transactions
* Authentication and authorization
* Pagination
* Search functionality
* Database indexing
* Rate limiting with Redis

---

## License

This project is intended for learning purposes and experimentation with Flask, PostgreSQL, Redis, and REST APIs.
