-- 1. Create Tables
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    city VARCHAR(50),
    country VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(customer_id),
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20),
    total_amount NUMERIC(10, 2)
);

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    unit_price NUMERIC(10, 2),
    stock_quantity INT
);

CREATE TABLE payments (
    payment_id SERIAL PRIMARY KEY,
    order_id INT REFERENCES orders(order_id),
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    payment_method VARCHAR(30),
    amount NUMERIC(10, 2)
);

-- 2. Insert Sample Data
INSERT INTO customers (full_name, email, city, country) VALUES
('Alice Dupont', 'alice@example.com', 'Paris', 'France'),
('Bob Smith', 'bob@example.com', 'London', 'UK'),
('Charlie Brown', 'charlie@example.com', 'New York', 'USA');

INSERT INTO products (product_name, category, unit_price, stock_quantity) VALUES
('Wireless Mouse', 'Electronics', 25.99, 150),
('Mechanical Keyboard', 'Electronics', 89.99, 75),
('Standing Desk', 'Furniture', 299.99, 20);

INSERT INTO orders (customer_id, status, total_amount) VALUES
(1, 'Completed', 115.98),
(2, 'Processing', 299.99),
(3, 'Completed', 25.99);

INSERT INTO payments (order_id, payment_method, amount) VALUES
(1, 'Credit Card', 115.98),
(2, 'PayPal', 299.99),
(3, 'Credit Card', 25.99);