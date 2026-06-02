DROP TABLE IF EXISTS products;

CREATE TABLE products (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  price NUMERIC(10, 2) NOT NULL CHECK (price >= 0),
  category TEXT NOT NULL DEFAULT 'Uncategorized',
  stock INT NOT NULL DEFAULT 0 CHECK (stock >= 0),
  created_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO products (name, price, category, stock)
VALUES
  ('Laptop', 12990, 'Electronics', 5),
  ('Monitor', 2990, 'Electronics', 10),
  ('Keyboard', 799, 'Accessories', 20),
  ('Mouse', 399, 'Accessories', 30),
  ('Headset', 999, 'Audio', 15);
