import os
import redis
import json

def get_redis_client():
    """
    Creates a Redis client.

    Redis is used in this lab to cache the product list for GET /products.
    """
    return redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        decode_responses=True,
    )
redis_client = get_redis_client()

def get_cached_product(product_id):
    
    product = {}
    
    meta = redis_client.get(
        f"product:{product_id}:meta"
    )

    if meta:
        product.update(json.loads(meta))

    price = redis_client.get(
        f"product:{product_id}:price"
    )

    if price:
        product.update(json.loads(price))

    stock = redis_client.get(
        f"product:{product_id}:stock"
    )

    if stock:
        product.update(json.loads(stock))

    return product if product else None
    
def set_cached_product(product):

    product_id = product["id"]

    redis_client.set(
        f"product:{product_id}:meta",
        json.dumps({
            "id": product["id"],
            "name": product["name"],
            "category": product["category"]
        }),
        ex=300
    )

    redis_client.set(
        f"product:{product_id}:price",
        json.dumps({
            "price": product["price"]
        }),
        ex=60
    )

    redis_client.set(
        f"product:{product_id}:stock",
        json.dumps({
            "stock": product["stock"]
        }),
        ex=10
    )
    
def get_cached_products(category=None,
                        search=None,
                        sort=None,
                        page=1,
                        limit=10
):
    return redis_client.get(
        _products_key(
            category,
            search,
            sort,
            page,
            limit
        )
    )
    
def set_cached_products(json_data, 
                        category=None,
                        search=None,
                        sort=None,
                        page=1,
                        limit=10
):
    
    redis_client.set(
        _products_key(
            category,
            search,
            sort,
            page,
            limit
        ),
        json_data,
        ex=60
    )

def clear_products_cache(category=None):
    """
    TODO:
    Används i Del 5 (Uppgift 17).

    Den ska ta bort nyckeln "products" från Redis efter POST /products.
    """
    # TODO: Implementera cache invalidation.
    # pass
    print("CLEARING CACHE")

    key = (
        f"products:{category}"
        if category
        else "products"
    )
    redis_client.delete(key)

def _products_key(category=None,
                  search=None,
                  sort=None,
                  page=1,
                  limit=10
):
    return (
        f"products:"
        f"category={category}:"
        f"search={search}:"
        f"sort={sort}:"
        f"page={page}:"
        f"limit={limit}"
    )

def clear_product_cache(product_id):

    redis_client.delete(
        f"product:{product_id}:meta"
    )

    redis_client.delete(
        f"product:{product_id}:price"
    )

    redis_client.delete(
        f"product:{product_id}:stock"
    )

def clear_products_cache():

    keys = redis_client.keys("products:*")

    if keys:
        redis_client.delete(*keys)

def set_cached_categories(json_data):

    redis_client.set("categories",
                     json_data,
                     ex=300
    )

def get_cached_categories():

    return redis_client.get("categories")

def clear_categories_cache():

    redis_client.delete("categories")

def set_cached_stock(product_id, stock):

    redis_client.set(
        f"product:{product_id}:stock",
        json.dumps({"stock": stock}),
        ex=10
    )

def set_cached_price(product_id, price):

    redis_client.set(
        f"product:{product_id}:price",
        json.dumps({"price": price}),
        ex=60
    )