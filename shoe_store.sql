-- cправочник ролей
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

-- пользователи
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    role_id INTEGER NOT NULL,
    full_name VARCHAR(150) NOT NULL,
    login VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    CONSTRAINT fk_users_role FOREIGN KEY (role_id) REFERENCES roles(id)
);
CREATE INDEX idx_users_role ON users(role_id);

-- поставщики
CREATE TABLE suppliers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

-- производители
CREATE TABLE manufacturers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

-- категории товаров
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT
);

-- товары
CREATE TABLE products (
    article VARCHAR(20) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    unit VARCHAR(10) NOT NULL,
    price NUMERIC(10,2) NOT NULL,
    supplier_id INTEGER NOT NULL,        
    manufacturer_id INTEGER NOT NULL,    
    category_id INTEGER NOT NULL,        
    discount INTEGER DEFAULT 0,
    stock_quantity INTEGER NOT NULL,
    description TEXT,
    photo VARCHAR(255),
    CONSTRAINT fk_products_supplier FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE RESTRICT,
    CONSTRAINT fk_products_manufacturer FOREIGN KEY (manufacturer_id) REFERENCES manufacturers(id) ON DELETE RESTRICT,
    CONSTRAINT fk_products_category FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT
);
CREATE INDEX idx_products_supplier ON products(supplier_id);
CREATE INDEX idx_products_manufacturer ON products(manufacturer_id);
CREATE INDEX idx_products_category ON products(category_id);

-- пункты выдачи
CREATE TABLE pickup_points (
    id SERIAL PRIMARY KEY,
    address VARCHAR(200) UNIQUE NOT NULL
);

-- статусы заказов
CREATE TABLE order_statuses (
    id SERIAL PRIMARY KEY,
    name VARCHAR(20) UNIQUE NOT NULL,
    display_order INTEGER,
    color_code VARCHAR(7)
);

-- заказы
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    order_number INTEGER UNIQUE NOT NULL,
    order_date DATE NOT NULL,
    delivery_date DATE NOT NULL,
    pickup_point_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    pickup_code VARCHAR(20) NOT NULL,
    status_id INTEGER NOT NULL,
    CONSTRAINT fk_orders_pickup_point FOREIGN KEY (pickup_point_id) REFERENCES pickup_points(id),
    CONSTRAINT fk_orders_user FOREIGN KEY (user_id) REFERENCES users(id),
    CONSTRAINT fk_orders_status FOREIGN KEY (status_id) REFERENCES order_statuses(id)
);
CREATE INDEX idx_orders_pickup_point ON orders(pickup_point_id);
CREATE INDEX idx_orders_user ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status_id);

-- состав заказа
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL,
    product_article VARCHAR(20) NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    CONSTRAINT fk_order_items_order FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    CONSTRAINT fk_order_items_product FOREIGN KEY (product_article) REFERENCES products(article) ON DELETE RESTRICT
);
CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_order_items_product ON order_items(product_article);