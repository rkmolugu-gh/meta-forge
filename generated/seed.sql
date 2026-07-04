Here are sample `INSERT` SQL statements to seed the tables: `Person`, `Passport`, `Customer`, `Order`, `Product`, and `Supplier`. These assume standard table schemas with common relationships (e.g., `Customer` has a `Person` and `Passport`, `Order` has a `Customer`, etc.). Adjust column names and data types as needed for your actual schema.

---

### 1. `Person` Table
```sql
INSERT INTO Person (first_name, last_name, date_of_birth, email, phone, address)
VALUES 
    ('John', 'Doe', '1985-03-15', 'john.doe@example.com', '+1234567890', '123 Main St, New York, NY'),
    ('Jane', 'Smith', '1990-07-22', 'jane.smith@example.com', '+0987654321', '456 Oak Ave, Los Angeles, CA'),
    ('Bob', 'Johnson', '1978-11-30', 'bob.johnson@example.com', '+1122334455', '789 Pine Rd, Chicago, IL'),
    ('Alice', 'Williams', '1982-05-10', 'alice.williams@example.com', '+6677889900', '321 Maple Dr, Houston, TX');
```

---

### 2. `Passport` Table
```sql
INSERT INTO Passport (person_id, passport_number, issue_date, expiry_date, country_of_issue)
VALUES 
    (1, 'P12345678', '2020-01-15', '2030-01-14', 'USA'),
    (2, 'P87654321', '2019-06-20', '2029-06-19', 'Canada'),
    (3, 'P55555555', '2021-03-10', '2031-03-09', 'UK'),
    (4, 'P99999999', '2022-08-05', '2032-08-04', 'Australia');
```

---

### 3. `Customer` Table
```sql
INSERT INTO Customer (person_id, customer_type, membership_level, created_at)
VALUES 
    (1, 'Individual', 'Gold', '2023-01-10'),
    (2, 'Individual', 'Silver', '2023-02-15'),
    (3, 'Business', 'Platinum', '2023-03-20'),
    (4, 'Individual', 'Bronze', '2023-04-25');
```

---

### 4. `Supplier` Table
```sql
INSERT INTO Supplier (company_name, contact_person, phone, email, address, country)
VALUES 
    ('TechGadgets Inc.', 'Michael Brown', '+1112223333', 'michael@techgadgets.com', '100 Innovation Ave, San Francisco, CA', 'USA'),
    ('GlobalParts Ltd.', 'Sarah Lee', '+4445556666', 'sarah@globalparts.com', '200 Industrial Park, London, UK', 'UK'),
    ('EcoSupply Co.', 'David Kim', '+8889990000', 'david@ecosupply.com', '300 Greenway Blvd, Sydney, Australia', 'Australia'),
    ('QuickDeliver Inc.', 'Emily Chen', '+6667778888', 'emily@quickdeliver.com', '400 Express Way, Toronto, ON', 'Canada');
```

---

### 5. `Product` Table
```sql
INSERT INTO Product (product_name, description, price, supplier_id, stock_quantity, category)
VALUES 
    ('Laptop Pro X1', 'High-performance laptop with 16GB RAM', 1299.99, 1, 50, 'Electronics'),
    ('Wireless Mouse', 'Ergonomic wireless mouse with 2.4GHz', 29.99, 1, 100, 'Electronics'),
    ('Steel Chair', 'Durable office chair with lumbar support', 149.99, 2, 30, 'Furniture'),
    ('Eco Notebook', 'Recycled paper notebook, 100 pages', 4.99, 3, 200, 'Office Supplies'),
    ('USB-C Hub', 'Multi-port USB-C hub with HDMI', 39.99, 1, 75, 'Electronics'),
    ('Organic Coffee', 'Fair-trade organic coffee beans', 12.99, 4, 150, 'Food'),
    ('LED Desk Lamp', 'Adjustable brightness LED lamp', 24.99, 2, 60, 'Electronics'),
    ('Eco-Friendly Pen', 'Biodegradable pen made from bamboo', 1.99, 3, 300, 'Office Supplies');
```

---

### 6. `Order` Table
```sql
INSERT INTO [Order] (customer_id, order_date, total_amount, status, shipping_address)
VALUES 
    (1, '2023-05-01', 1329.98, 'Shipped', '123 Main St, New York, NY'),
    (2, '2023-05-05', 34.98, 'Delivered', '456 Oak Ave, Los Angeles, CA'),
    (3, '2023-05-10', 149.99, 'Processing', '789 Pine Rd, Chicago, IL'),
    (4, '2023-05-15', 17.98, 'Cancelled', '321 Maple Dr, Houston, TX'),
    (1, '2023-05-20', 24.99, 'Delivered', '123 Main St, New York, NY');
```

---

### Notes:
- `person_id` and `customer_id` are assumed to be foreign keys referencing `Person` and `Customer` respectively.
- `supplier_id` references `Supplier`.
- `order_date` is a `DATE` or `DATETIME` field.
- `status` in `Order` could be `Pending`, `Processing`, `Shipped`, `Delivered`, `Cancelled`, etc.
- Adjust `table names`, `column names`, and `data types` based on your actual database schema.

Let me know if you'd like to include `OrderItem` or `ProductSupplier` tables as well!