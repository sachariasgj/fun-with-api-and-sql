import os
from decimal import Decimal

import psycopg2
import psycopg2.extras
import redis


def get_connection():
    """
    Creates a new PostgreSQL connection.

    In a real production API you would usually use connection pooling.
    For this beginner lab, a simple connection per request is easier to understand.
    """
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "novastore"),
        user=os.getenv("DB_USER", "student"),
        password=os.getenv("DB_PASSWORD", "student"),
    )

def _convert_product(row):
    """
    Converts a database row into a JSON-friendly dictionary.

    PostgreSQL NUMERIC values become Decimal in Python, so we convert price to float.
    """
    if row is None:
        return None

    product = dict(row)

    if isinstance(product.get("price"), Decimal):
        product["price"] = float(product["price"])

    if product.get("created_at") is not None:
        product["created_at"] = product["created_at"].isoformat()

    return product

def get_all_categories_from_db():

    query = """
        SELECT
            c.id,
            c.name,
            COUNT(p.id) AS product_count
        FROM categories c
        LEFT JOIN products p
        ON p.category_id = c.id
        GROUP BY
            c.id,
            c.name
        ORDER BY c.name;
    """

    with get_connection() as conn:
        with conn.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor
        ) as cur:
            
            cur.execute(query)
            rows = cur.fetchall()
    categories = []

    for row in rows:
        category = dict(row)

        category["product_count"] = int(
            category["product_count"]
        )
        categories.append(category)
    
    return categories

def get_all_products_from_db(category=None, 
                             sort=None, 
                             search=None,
                             page=1,
                             limit=10
):
    
    order_clause = "ORDER BY p.id"

    if sort == "price":
        order_clause = "ORDER BY p.price ASC"
    elif sort == "price_desc":
        order_clause = "ORDER BY p.price DESC"

    conditions = []
    params = []

    if category:
        conditions.append(
            "c.name = %s"
        )
        params.append(category)

    if search:
        conditions.append(
            "p.name ILIKE %s"
        )
        params.append(f"%{search}%")
    
    where_clause = ""
    offset = (page - 1) * limit
    params.append(limit)
    params.append(offset)

    if conditions:
        where_clause = (
            "WHERE "
            + " AND ".join(conditions)
        )
    
    
    query = f"""
        SELECT
            p.id,
            p.name,
            p.price,
            c.name AS category,
            p.stock,
            p.created_at
        FROM products p
        JOIN categories c
        ON p.category_id = c.id
        {where_clause}
        {order_clause}
        LIMIT %s
        OFFSET %s
    """

    with get_connection() as conn:
        with conn.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor 
        ) as cur:
            
            cur.execute(query, params)
            rows = cur.fetchall()

    return [_convert_product(row) for row in rows]

def get_products_by_category_id(category_id):

    query = """
        SELECT
            p.id,
            p.name,
            p.price,
            c.name AS category,
            p.stock,
            p.created_at
        FROM products p
        JOIN categories c
        ON p.category_id = c.id
        WHERE c.id = %s
        ORDER BY p.id;
    """

    with get_connection() as conn:
        with conn.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor
        ) as cur:
            
            cur.execute(query, (category_id,))
            rows = cur.fetchall()

    return [_convert_product(row)
            for row in rows]

def get_category_by_id(category_id):

    query = """
        SELECT
            c.id,
            c.name,
            COUNT(p.id) AS product_count
        FROM categories c
        LEFT JOIN products p
        ON p.category_id = c.id
        WHERE c.id = %s
        GROUP BY
            c.id,
            c.name;
    """

    with get_connection() as conn:
        with conn.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor
        ) as cur:
            
            cur.execute(query, (category_id,))
            row = cur.fetchone()

    if row is None:
        return None
    
    row["product_count"] = int(row["product_count"])
    return dict(row)

def get_product_stock_from_db(product_id):

    query = """
        SELECT stock
        FROM products
        WHERE id = %s;
    """
    
    with get_connection() as conn:
        with conn.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor
        ) as cur:
            
            cur.execute(query, (product_id,))
            row = cur.fetchone()
        
        if row is None:
            return None
        
        return row["stock"]

def get_product_price_from_db(product_id):

    query = """
        SELECT price
        FROM products
        WHERE id = %s;
    """
    
    with get_connection() as conn:
        with conn.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor
        ) as cur:
            
            cur.execute(query, (product_id,))
            row = cur.fetchone()
        
        if row is None:
            return None
        
        return float(row["price"])

def get_product_by_id_from_db(product_id):
    
    query = """
        SELECT 
            p.id, 
            p.name, 
            p.price, 
            c.name AS category, 
            p.stock, 
            p.created_at
        FROM products p
        JOIN categories c
        ON p.category_id = c.id
        WHERE p.id = %s;
    """
    
    with get_connection() as conn:
        with conn.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor
        ) as cur:
            
            cur.execute(query, (product_id,))
            row = cur.fetchone()
    return _convert_product(row)

def insert_product_into_db(product):
   
    query = """
        INSERT INTO products 
        (name, price, category, stock)
        VALUES (%s, %s, %s, %s)
        RETURNING 
            id, 
            name, 
            price, 
            category, 
            stock, 
            created_at;
    """

    with get_connection() as conn:
        with conn.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor
        ) as cur:
            
            cur.execute(
                query,
                (
                    product["name"],
                    product["price"],
                    product.get("category", "Uncategorized"),
                    product.get("stock", 0),
                )
            )
            row = cur.fetchone()

    return _convert_product(row)

def insert_category_into_db(name):

    query = """
        INSERT INTO categories(name)
        VALUES (%s)
        RETURNING
            id,
            name;
    """

    with get_connection() as conn:
        with conn.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor
        ) as cur:
            
            cur.execute(query, (name,))
            row = cur.fetchone()
    return dict(row)

def decrease_stock(product_id):

    query = """
        UPDATE products
        SET stock = stock - 1
        WHERE id = %s
        AND stock > 0
        RETURNING stock;
    """

    with get_connection() as conn:
        with conn.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor
        ) as cur:
            
            cur.execute(query, (product_id,))
            row = cur.fetchone()
        
        if row is None:
            return None
        
        return row["stock"]
    
def update_product_in_db(product_id,
                         name,
                         price,
                         category,
                         stock
):
    
    query = """
        UPDATE products
        SET
            name = %s,
            price = %s,
            category = %s,
            stock = %s
        WHERE id = %s
        RETURNING
            id,
            name,
            price,
            category,
            stock,
            created_at;
    """

    with get_connection() as conn:
        with conn.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor
        ) as cur:
            
            cur.execute(
                query,
                (
                    name,
                    price,
                    category,
                    stock,
                    product_id
                )
            )
            row = cur.fetchone()
    
    return _convert_product(row)

def patch_product_in_db(product_id, data):

    allowed_fields = {
        "name",
        "price",
        "category",
        "stock"
    }

    updates = []
    values = []

    for field, value in data.items():
        if field not in allowed_fields:
            continue

        updates.append(f"{field} = %s")
        values.append(value)
    
    if not updates:
        return None
    
    values.append(product_id)

    query = f"""
        UPDATE products
        SET {", ".join(updates)}
        WHERE id = %s
        RETURNING
            id,
            name,
            price,
            category,
            stock,
            created_at;
    """

    with get_connection() as conn:
        with conn.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor
        ) as cur:
            
            cur.execute(query, values)
            row = cur.fetchone()
    
    return _convert_product(row)

def get_stats_from_db():

    query = """
        SELECT
            COUNT(*) AS total_products,
            COALESCE(SUM(stock), 0) AS total_stock,
            COALESCE(AVG(price), 0) AS average_price,
            COALESCE(MIN(price), 0) AS cheapest_price,
            COALESCE(MAX(price), 0) AS most_expensive_price
        FROM products;
    """

    with get_connection() as conn:
        with conn.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor
        ) as cur:
            
            cur.execute(query)
            product_stats = cur.fetchone()

            cur.execute("""
                SELECT COUNT(*) AS total_categories
                FROM categories;
            """)

            category_stats = cur.fetchone()

    return {
        "total_products":int(product_stats["total_products"]),
        "total_categories": int(category_stats["total_categories"]),
        "total_stock": int(product_stats["total_stock"]),
        "average_price": float(product_stats["average_price"]),
        "cheapest_price": float(product_stats["cheapest_price"]),
        "most_expensive_price": float(product_stats["most_expensive_price"])
    }

def delete_product_from_db(product_id):

    query = """
        DELETE FROM products
        WHERE id = %s
        RETURNING
            id,
            name,
            price,
            category,
            stock,
            created_at;
    """

    with get_connection() as conn:
        with conn.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor
        ) as cur:
            
            cur.execute(query, (product_id,))

            row = cur.fetchone()

    return _convert_product(row)