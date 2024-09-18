-- Create Categories table
CREATE TABLE Categories (
    CategoryID INTEGER PRIMARY KEY AUTOINCREMENT,
    CategoryName TEXT NOT NULL UNIQUE,
    Description TEXT
);

-- Create Products table
CREATE TABLE Products (
    ProductID INTEGER PRIMARY KEY AUTOINCREMENT,
    ProductName TEXT NOT NULL,
    CategoryID INTEGER,
    Price DECIMAL(10, 2) NOT NULL CHECK (Price >= 0),
    StockQuantity INTEGER NOT NULL DEFAULT 0 CHECK (StockQuantity >= 0),
    Description TEXT,
    FOREIGN KEY (CategoryID) REFERENCES Categories(CategoryID)
);

-- Create Customers table
CREATE TABLE Customers (
    CustomerID INTEGER PRIMARY KEY AUTOINCREMENT,
    FirstName TEXT NOT NULL,
    LastName TEXT NOT NULL,
    Email TEXT NOT NULL UNIQUE,
    PhoneNumber TEXT,
    Address TEXT
);

-- Create Orders table
CREATE TABLE Orders (
    OrderID INTEGER PRIMARY KEY AUTOINCREMENT,
    CustomerID INTEGER NOT NULL,
    OrderDate DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    TotalAmount DECIMAL(10, 2) NOT NULL DEFAULT 0 CHECK (TotalAmount >= 0),
    Status TEXT NOT NULL DEFAULT 'Pending' CHECK (Status IN ('Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled')),
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID)
);

-- Create OrderItems table
CREATE TABLE OrderItems (
    OrderItemID INTEGER PRIMARY KEY AUTOINCREMENT,
    OrderID INTEGER NOT NULL,
    ProductID INTEGER NOT NULL,
    Quantity INTEGER NOT NULL CHECK (Quantity > 0),
    UnitPrice DECIMAL(10, 2) NOT NULL CHECK (UnitPrice >= 0),
    FOREIGN KEY (OrderID) REFERENCES Orders(OrderID),
    FOREIGN KEY (ProductID) REFERENCES Products(ProductID)
);

-- Insert sample data into Categories
INSERT INTO Categories (CategoryName, Description) VALUES
('Electronics', 'Electronic devices and accessories'),
('Clothing', 'Apparel and fashion items'),
('Books', 'Physical and digital books'),
('Home & Kitchen', 'Home appliances and kitchenware');

-- Insert sample data into Products
INSERT INTO Products (ProductName, CategoryID, Price, StockQuantity, Description) VALUES
('Smartphone X', 1, 699.99, 50, 'Latest model smartphone with advanced features'),
('Laptop Pro', 1, 1299.99, 30, 'High-performance laptop for professionals'),
('Classic T-Shirt', 2, 19.99, 100, 'Comfortable cotton t-shirt available in various colors'),
('Jeans', 2, 49.99, 75, 'Durable denim jeans for everyday wear'),
('Best-Selling Novel', 3, 24.99, 200, 'Award-winning fiction novel'),
('Cookbook', 3, 34.99, 60, 'Collection of gourmet recipes'),
('Coffee Maker', 4, 79.99, 40, 'Programmable coffee maker with built-in grinder'),
('Blender', 4, 59.99, 55, 'High-powered blender for smoothies and more');

-- Insert sample data into Customers
INSERT INTO Customers (FirstName, LastName, Email, PhoneNumber, Address) VALUES
('John', 'Doe', 'john.doe@email.com', '123-456-7890', '123 Main St, Anytown, USA'),
('Jane', 'Smith', 'jane.smith@email.com', '987-654-3210', '456 Elm St, Otherville, USA'),
('Bob', 'Johnson', 'bob.johnson@email.com', '555-123-4567', '789 Oak Ave, Somewhere, USA');

-- Insert sample data into Orders
INSERT INTO Orders (CustomerID, TotalAmount, Status) VALUES
(1, 749.98, 'Processing'),
(2, 109.97, 'Shipped'),
(3, 1359.98, 'Pending');

-- Insert sample data into OrderItems
INSERT INTO OrderItems (OrderID, ProductID, Quantity, UnitPrice) VALUES
(1, 1, 1, 699.99),
(1, 5, 2, 24.99),
(2, 3, 2, 19.99),
(2, 6, 1, 34.99),
(3, 2, 1, 1299.99),
(3, 7, 1, 59.99);

-- Create an index on the Products table for faster category-based queries
CREATE INDEX idx_products_category ON Products(CategoryID);

-- Create an index on the Orders table for faster customer-based queries
CREATE INDEX idx_orders_customer ON Orders(CustomerID);

-- Create a view for order summaries
CREATE VIEW OrderSummaries AS
SELECT
    o.OrderID,
    c.FirstName || ' ' || c.LastName AS CustomerName,
    o.OrderDate,
    o.TotalAmount,
    o.Status,
    COUNT(oi.OrderItemID) AS TotalItems
FROM
    Orders o
    JOIN Customers c ON o.CustomerID = c.CustomerID
    JOIN OrderItems oi ON o.OrderID = oi.OrderID
GROUP BY
    o.OrderID;

-- Create a trigger to update product stock quantity after an order is placed
CREATE TRIGGER update_stock_after_order
AFTER INSERT ON OrderItems
BEGIN
    UPDATE Products
    SET StockQuantity = StockQuantity - NEW.Quantity
    WHERE ProductID = NEW.ProductID;
END;

-- Create a trigger to update order total amount when items are added or modified
CREATE TRIGGER update_order_total
AFTER INSERT ON OrderItems
BEGIN
    UPDATE Orders
    SET TotalAmount = (
        SELECT SUM(Quantity * UnitPrice)
        FROM OrderItems
        WHERE OrderID = NEW.OrderID
    )
    WHERE OrderID = NEW.OrderID;
END;