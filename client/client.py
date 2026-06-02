import os
import requests

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5001")


def print_response(title, response):
    print("\n" + "=" * 60)
    print(title)
    print("Status:", response.status_code)

    try:
        print("JSON:", response.json())
    except Exception:
        print("Text:", response.text)


def main():
    # Health check
    response = requests.get(f"{API_BASE_URL}/health")
    print_response("GET /health", response)

    # Product list
    response = requests.get(f"{API_BASE_URL}/products")
    print_response("GET /products", response)

    if response.status_code == 200:
        products = response.json()
        print("\nProducts:")
        for product in products:
            print(f"- {product['id']}: {product['name']} ({product['price']} kr)")

    # Del 2:
    # Uncomment after implementing GET /products/{id}
    # response = requests.get(f"{API_BASE_URL}/products/1")
    # print_response("GET /products/1", response)

    # Del 2:
    # Uncomment after implementing 404
    # response = requests.get(f"{API_BASE_URL}/products/999")
    # print_response("GET /products/999", response)

    # Del 3:
    # Uncomment after implementing POST /products
    # new_product = {
    #     "name": "Webcam",
    #     "price": 899,
    #     "category": "Accessories",
    #     "stock": 12
    # }
    # response = requests.post(f"{API_BASE_URL}/products", json=new_product)
    # print_response("POST /products", response)

    # Del 3:
    # Uncomment after implementing 400
    # invalid_product = {"name": "Broken Product", "price": -10}
    # response = requests.post(f"{API_BASE_URL}/products", json=invalid_product)
    # print_response("POST /products invalid", response)


if __name__ == "__main__":
    main()
