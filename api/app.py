import json

from flask import Flask, jsonify, request

from db import (
    get_all_products_from_db,
    get_product_by_id_from_db,
    insert_product_into_db,
    get_product_price_from_db,
    get_product_stock_from_db,
    decrease_stock,
    update_product_in_db,
    patch_product_in_db,
    
)
from cache import (
    get_cached_products,
    set_cached_products,
    clear_products_cache,
    set_cached_product,
    get_cached_product,
    _products_key,
    set_cached_price,
    set_cached_stock,
    
)

app = Flask(__name__)

@app.patch("/products/<int:product_id>")
def patch_product(product_id):

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "Missing JSON body"
        }), 400
    
    if ("price" in data
        and data["price"] < 0):

        return jsonify({
            "error": "Price can't be negative"
        }), 400
    
    if ("stock" in data
        and data["stock"] < 0):

        return jsonify({
            "error": "Stock can't be negative"
        }), 400
    
    product = patch_product_in_db(product_id, data)

    if product is None:
        return jsonify({
            "error": "Product not found"
        }), 404
    
    clear_products_cache(product_id)
    clear_products_cache()

    return jsonify(product), 200

@app.put("/products/<int:product_id>")
def update_product(product_id):

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "Missing JSON body"
        }), 400
    
    if "name" not in data:
        return jsonify({
            "error": "Name is required"
        }), 400
    
    if "price" not in data:
        return jsonify({
            "error": "Price is required"
        }), 400
    
    if "stock" not in data:
        return jsonify({
            "error": "Stock is required"
        }), 400
    
    if data["price"] < 0:
        return jsonify({
            "error": "Price can't be negative"
        }), 400
    
    if data["stock"] < 0:
        return jsonify({
            "error": "Stock can't be negative"
        }), 400
    
    product = update_product_in_db(product_id,
                                   data["name"],
                                   data["price"],
                                   data.get("category",
                                            "Uncategorized"
                                   ),
                                   data["stock"]
    )

    if product is None:
        return jsonify({
            "error": "Product not found"
        }), 404
    
    clear_products_cache(product_id)
    clear_products_cache()

    return jsonify(product), 200

@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/products")
def get_products():
    """
    Del 2:
    Den här endpointen hämtar redan produkter från PostgreSQL.

    Del 4:
    Studenterna ska senare bygga ut endpointen med Redis-cache.
    """
    # TODO Del 4 (Uppgift 12-15):
    # 1. Kontrollera Redis först med get_cached_products()
    # 2. Om cache finns: skriv ut "CACHE HIT" och returnera cachead JSON
    # 3. Om cache saknas: skriv ut "CACHE MISS" och läs från PostgreSQL
    # 4. Spara resultatet i Redis med set_cached_products()

    # products = get_all_products_from_db()
    category = request.args.get("category")
    sort = request.args.get("sort")

    cached_products = get_cached_products(category)
    print("CACHE CONTENT:", cached_products)

    if cached_products:
        print("CACHE HIT", flush=True)

        return jsonify(
            json.loads(cached_products)
        ), 200
    
    print("CACHE MISS", flush=True)
    
    products = get_all_products_from_db(category, sort)
    
    set_cached_products(
        json.dumps(products),
        category
    )
    return jsonify(products), 200


@app.get("/products/<int:product_id>")
def get_product(product_id):
    """
    Del 2:
    TODO (Uppgift 5 och 6).

    Förväntat beteende:
    - Om produkten finns: returnera produkten som JSON med 200 OK
    - Om produkten inte finns: returnera {"error": "Product not found"} med 404
    """
    cached_product = get_cached_product(product_id)

    if (not cached_product
        or "id" not in cached_product
    ):

        print(f"FULL CACHE MISS product:{product_id}", flush=True)

        product = get_product_by_id_from_db(product_id)

        if product is None:
            return jsonify({
                "error": "Product not found"
            }), 404
    
        set_cached_product(product)
        return jsonify(product), 200
    
    print(f"PARTIAL or FULL CACHE HIT product:{product_id}", flush=True)

    if "price" not in cached_product:

        print(f"PRICE CACHE MISS product:{product_id}", flush=True)

        price = get_product_price_from_db(product_id)

        if price is None:
            return jsonify({
                "error": "Product not found"
            }), 404
        
        cached_product["price"] = price
        set_cached_price(product_id, price)
    
    if "stock" not in cached_product:

        print(f"STOCK CACHE MISS product:{product_id}", flush=True)

        stock = get_product_stock_from_db(product_id)

        if stock is None:
            return jsonify({
                "error": "Product not found"
            }), 404
        
        cached_product["stock"] = stock
        set_cached_stock(product_id, stock)

    return jsonify(cached_product), 200



    # TODO: Implementera 404 Not Found om produkten inte existerar (Uppgift 6).
    # return jsonify({
    #     "message": "TODO: Implementera GET /products/{id} (Uppgift 5)",
    #     "product_id": product_id,
    #     "hint": "Använd get_product_by_id_from_db(product_id) i db.py"
    # }), 501


@app.post("/products")
def create_product():
    """
    Del 3:
    TODO (Uppgift 7-10).

    Förväntat beteende:
    - Läs JSON från requesten
    - Validera name och price
    - Avvisa saknat name, saknat price eller negativt price med 400 Bad Request
    - Spara produkten i PostgreSQL
    - Returnera skapad produkt med 201 Created
    - Del 5: Töm produktcachen efter lyckad insert (Uppgift 17)
    """
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "Missing JSON body"
        }), 400
    
    if "name" not in data:
        return jsonify({
            "error": "Name is required"
        }), 400
    
    if "price" not in data:
        return jsonify({
            "error": "Price is required"
        }), 400
    
    if data["price"] < 0:
        return jsonify({
            "error": "Price cannot be negative"
        }), 400
    
    product = insert_product_into_db(data)
    clear_products_cache()

    return jsonify(product), 201

    # TODO: Validera inkommande data och stoppa ogiltiga requests (Uppgift 10).
    # Exempel som ska ge 400:
    # {}
    # {"price": 999}
    # {"name": "Webcam"}
    # {"name": "Webcam", "price": -10}

    # TODO: Spara ny produkt i PostgreSQL med insert_product_into_db(data) (Uppgift 8).
    # TODO Del 5: Töm produktcachen med clear_products_cache() efter POST (Uppgift 17).

    # return jsonify({
    #     "message": "TODO: Implementera POST /products (Uppgift 7-9)",
    #     "received": data
    # }), 501


@app.get("/crash")
def crash():
    """
    Optional endpoint for discussing 500 Internal Server Error.
    """
    raise Exception("Simulated server error")


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({"error": "Internal server error"}), 500

@app.post("/products/<int:product_id>/purchase")
def purchase_product(product_id):

    new_stock = decrease_stock(product_id)

    if new_stock is None:
        return jsonify({
            "error": "Out of stock"
        }), 400
    
    set_cached_stock(product_id, new_stock)

    return jsonify({
        "message": "Purchase successful",
        "stock": new_stock
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
