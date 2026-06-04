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
    delete_product_from_db,
    insert_category_into_db,
    get_all_categories_from_db,
    get_products_by_category_id,
    get_category_by_id,
    get_stats_from_db,
    
)
from cache import (
    get_cached_products,
    set_cached_products,
    clear_products_cache,
    clear_product_cache,
    set_cached_product,
    get_cached_product,
    _products_key,
    set_cached_price,
    set_cached_stock,
    get_cached_categories,
    set_cached_categories,
    clear_categories_cache,
    
)

app = Flask(__name__)

@app.get("/stats")
def get_stats():

    stats = get_stats_from_db()

    return jsonify(stats), 200

@app.get("/categories/<int:category_id>")
def get_category(category_id):

    category = get_category_by_id(category_id)

    if category is None:
        return jsonify({
            "error": "Category not found"
        }), 404
    
    return jsonify(category), 200

@app.get("/categories/<int:category_id>/products")
def get_category_products(category_id):

    products = get_products_by_category_id(category_id)
    return jsonify(products), 200

@app.post("/categories")
def create_category():

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "Missing JSON body"
        }), 400
    
    if "name" not in data:
        return jsonify({
            "error": "Name is required"
        }), 400
    
    category = insert_category_into_db(data["name"])
    clear_categories_cache()
    return jsonify(category), 201

@app.get("/categories")
def get_categories():
    
    cached_categories = get_cached_categories()

    if cached_categories:

        print("CATEGORIES CACHE HIT", flush=True)
        return jsonify(
            json.loads(cached_categories)
        ), 200
    
    print("CATEGORIES CACHE MISS", flush=True)

    categories = get_all_categories_from_db()

    set_cached_categories(
        json.dumps(categories)
    )

    return jsonify(categories), 200

@app.delete("/products/<int:product_id>")
def delete_product(product_id):

    product = delete_product_from_db(product_id)

    if product is None:
        return jsonify({
            "error": "Product not found"
        }), 404
    clear_products_cache(product_id)
    clear_products_cache()

    return jsonify({
        "message": "Product deleted",
        "product": product
    }), 200

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
    
    clear_product_cache(product_id)
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
    
    category = request.args.get("category")
    sort = request.args.get("sort")
    search = request.args.get("search")
        
    try:
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 10))
    except ValueError:
        return jsonify({
            "error": "page and limit must be integers"
        }), 400

    if page < 1:
        page = 1
    
    if limit < 1:
        limit = 10
    
    if limit > 100:
        limit = 100

    cached_products = get_cached_products(
        category,
        search,
        sort,
        page,
        limit
    )
    print("CACHE CONTENT:", cached_products)

    if cached_products:
        print("CACHE HIT", flush=True)

        return jsonify(
            json.loads(cached_products)
        ), 200
    
    print("CACHE MISS", flush=True)
    
    products = get_all_products_from_db(category, 
                                        sort, 
                                        search,
                                        page,
                                        limit
    )
    
    set_cached_products(
        json.dumps(products),
        category,
        search,
        sort,
        page,
        limit
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
