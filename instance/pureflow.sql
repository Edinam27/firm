-- products table schema
CREATE TABLE product (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    image_url VARCHAR(200),
    stock INTEGER DEFAULT 0,
    is_featured BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE product;

-- Insert statements (equivalent to what the Python code does)
INSERT INTO product (name, description, price, image_url, stock, is_featured) VALUES
('Natural Spring Water', 'Pure, refreshing spring water from pristine mountain sources.', 1.99, 'images/glass.jpg', 100, 1),
('Alkaline Water', 'pH balanced water with essential minerals for optimal hydration.', 2.49, 'images/glass.jpg', 80, 1),
('Mineral-Enhanced Water', 'Enhanced with natural minerals for a crisp, refreshing taste.', 2.29, 'images/glass.jpg', 90, 0),
('Electrolyte Water', 'Fortified with electrolytes for superior hydration and performance.', 2.99, 'images/glass.jpg', 75, 1),
('Mountain Stream Water', 'Sourced from high-altitude mountain streams for ultimate purity.', 2.19, 'images/glass.jpg', 85, 0),
('Premium Artesian Water', 'Naturally filtered through ancient rock layers for exceptional taste.', 3.49, 'images/glass.jpg', 60, 1);