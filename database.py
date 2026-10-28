import sqlite3
import os
import time
from typing import Dict, Any, List, Tuple

DB_PATH = os.path.join(os.path.dirname(__file__), "sales_data.db")

def init_db():
    """Initializes the SQLite database with rich e-commerce sample data."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create tables
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS categories (
        category_id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_name TEXT NOT NULL UNIQUE,
        description TEXT
    );

    CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT NOT NULL,
        category_id INTEGER NOT NULL,
        price REAL NOT NULL,
        stock_quantity INTEGER NOT NULL,
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (category_id) REFERENCES categories (category_id)
    );

    CREATE TABLE IF NOT EXISTS customers (
        customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        city TEXT,
        country TEXT DEFAULT 'USA',
        joined_date TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        order_date TEXT NOT NULL,
        total_amount REAL NOT NULL,
        status TEXT CHECK(status IN ('Completed', 'Pending', 'Cancelled', 'Shipped')) DEFAULT 'Completed',
        FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
    );

    CREATE TABLE IF NOT EXISTS order_items (
        item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders (order_id),
        FOREIGN KEY (product_id) REFERENCES products (product_id)
    );

    CREATE TABLE IF NOT EXISTS reviews (
        review_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        customer_id INTEGER NOT NULL,
        rating INTEGER CHECK(rating BETWEEN 1 AND 5),
        comment TEXT,
        review_date TEXT NOT NULL,
        FOREIGN KEY (product_id) REFERENCES products (product_id),
        FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
    );
    """)

    # Seed data if categories is empty
    cursor.execute("SELECT COUNT(*) FROM categories")
    if cursor.fetchone()[0] == 0:
        _seed_sample_data(cursor)

    conn.commit()
    conn.close()

def _seed_sample_data(cursor: sqlite3.Cursor):
    """Populates realistic multi-month data for analytical queries."""
    categories = [
        (1, "Electronics", "Smartphones, laptops, accessories, and smart devices"),
        (2, "Apparel & Fashion", "Clothing, footwear, and designer accessories"),
        (3, "Home & Kitchen", "Furniture, cookery, and smart home appliances"),
        (4, "Books & Stationery", "Best-sellers, educational books, and notebooks"),
        (5, "Fitness & Sports", "Gym gear, outdoor recreation, and sports equipment")
    ]
    cursor.executemany("INSERT INTO categories (category_id, category_name, description) VALUES (?, ?, ?)", categories)

    products = [
        (1, "UltraBook Pro 15", 1, 1299.99, 45, "2023-11-10"),
        (2, "Noise-Cancelling Headphones", 1, 249.50, 110, "2023-12-01"),
        (3, "OLED Smart TV 55-inch", 1, 799.00, 30, "2024-01-05"),
        (4, "Mechanical Gaming Keyboard", 1, 129.99, 85, "2024-01-15"),
        (5, "Wireless Ergonomic Mouse", 1, 49.99, 150, "2024-01-20"),
        (6, "Classic Denim Jacket", 2, 89.90, 70, "2023-10-12"),
        (7, "Merino Wool Sweater", 2, 65.00, 55, "2023-11-18"),
        (8, "Running Performance Sneakers", 2, 119.99, 90, "2024-01-10"),
        (9, "Cotton Crewneck T-Shirt (3-Pack)", 2, 34.50, 200, "2024-02-01"),
        (10, "Stainless Steel Espresso Machine", 3, 349.99, 25, "2023-12-10"),
        (11, "Ceramic Cookware 10-Piece Set", 3, 189.00, 40, "2024-01-08"),
        (12, "Air Purifier HEPA 400", 3, 159.99, 60, "2024-01-22"),
        (13, "Memory Foam Contour Pillow", 3, 45.00, 120, "2024-02-12"),
        (14, "Designing Data-Intensive Applications", 4, 49.99, 80, "2023-09-01"),
        (15, "Clean Code by Robert C. Martin", 4, 42.50, 95, "2023-09-15"),
        (16, "Atomic Habits by James Clear", 4, 21.99, 160, "2023-10-01"),
        (17, "Adjustable Dumbbell Set 50lbs", 5, 299.00, 35, "2023-11-20"),
        (18, "Pro Yoga Mat Non-Slip", 5, 39.99, 140, "2024-01-10"),
        (19, "Trail Running Hydration Backpack", 5, 68.00, 50, "2024-02-05"),
        (20, "GPS Smart Sports Watch", 5, 199.99, 65, "2024-02-18")
    ]
    cursor.executemany("INSERT INTO products (product_id, product_name, category_id, price, stock_quantity, created_at) VALUES (?, ?, ?, ?, ?, ?)", products)

    customers = [
        (1, "Sophia Turner", "sophia.turner@example.com", "New York", "USA", "2023-08-15"),
        (2, "Liam Johnson", "liam.j@example.com", "San Francisco", "USA", "2023-09-02"),
        (3, "Emma Rodriguez", "emma.r@example.com", "Austin", "USA", "2023-10-12"),
        (4, "Noah Kim", "noah.kim@example.com", "Seattle", "USA", "2023-10-25"),
        (5, "Olivia Martinez", "olivia.m@example.com", "Chicago", "USA", "2023-11-05"),
        (6, "James Wilson", "james.w@example.com", "Boston", "USA", "2023-11-19"),
        (7, "Ava Patel", "ava.patel@example.com", "Denver", "USA", "2023-12-01"),
        (8, "Lucas Brown", "lucas.b@example.com", "Miami", "USA", "2024-01-03"),
        (9, "Mia Davis", "mia.d@example.com", "Los Angeles", "USA", "2024-01-15"),
        (10, "Ethan Clark", "ethan.c@example.com", "Portland", "USA", "2024-02-01")
    ]
    cursor.executemany("INSERT INTO customers (customer_id, full_name, email, city, country, joined_date) VALUES (?, ?, ?, ?, ?, ?)", customers)

    # Multi-month orders across 2024-01 to 2024-04
    orders = [
        (1, 1, "2024-01-12", 1549.49, "Completed"),
        (2, 2, "2024-01-15", 799.00, "Completed"),
        (3, 3, "2024-01-18", 179.98, "Completed"),
        (4, 4, "2024-01-22", 1299.99, "Completed"),
        (5, 5, "2024-01-28", 238.99, "Completed"),
        (6, 6, "2024-02-02", 349.99, "Completed"),
        (7, 7, "2024-02-08", 418.99, "Completed"),
        (8, 8, "2024-02-14", 71.98, "Completed"),
        (9, 1, "2024-02-20", 379.50, "Completed"),
        (10, 9, "2024-02-25", 249.50, "Completed"),
        (11, 2, "2024-03-03", 299.00, "Completed"),
        (12, 10, "2024-03-10", 179.98, "Completed"),
        (13, 3, "2024-03-15", 94.49, "Completed"),
        (14, 4, "2024-03-21", 509.98, "Completed"),
        (15, 5, "2024-03-29", 1449.49, "Completed"),
        (16, 6, "2024-04-02", 199.99, "Completed"),
        (17, 7, "2024-04-10", 137.99, "Completed"),
        (18, 8, "2024-04-14", 349.99, "Completed"),
        (19, 9, "2024-04-20", 108.00, "Completed"),
        (20, 10, "2024-04-25", 848.99, "Completed")
    ]
    cursor.executemany("INSERT INTO orders (order_id, customer_id, order_date, total_amount, status) VALUES (?, ?, ?, ?, ?)", orders)

    order_items = [
        (1, 1, 1, 1, 1299.99),
        (2, 1, 2, 1, 249.50),
        (3, 2, 3, 1, 799.00),
        (4, 3, 4, 1, 129.99),
        (5, 3, 5, 1, 49.99),
        (6, 4, 1, 1, 1299.99),
        (7, 5, 8, 2, 119.99),
        (8, 6, 10, 1, 349.99),
        (9, 7, 17, 1, 299.00),
        (10, 7, 8, 1, 119.99),
        (11, 8, 9, 1, 34.50),
        (12, 8, 18, 1, 39.99),
        (13, 9, 2, 1, 249.50),
        (14, 9, 4, 1, 129.99),
        (15, 10, 2, 1, 249.50),
        (16, 11, 17, 1, 299.00),
        (17, 12, 6, 2, 89.90),
        (18, 13, 14, 1, 49.99),
        (19, 13, 16, 2, 21.99),
        (20, 14, 11, 1, 189.00),
        (21, 14, 12, 2, 159.99),
        (22, 15, 1, 1, 1299.99),
        (23, 15, 12, 1, 159.99),
        (24, 16, 20, 1, 199.99),
        (25, 17, 6, 1, 89.90),
        (26, 17, 14, 1, 49.99),
        (27, 18, 10, 1, 349.99),
        (28, 19, 19, 1, 68.00),
        (29, 19, 18, 1, 39.99),
        (30, 20, 3, 1, 799.00),
        (31, 20, 5, 1, 49.99)
    ]
    cursor.executemany("INSERT INTO order_items (item_id, order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?, ?)", order_items)

    reviews = [
        (1, 1, 1, 5, "Blazing fast laptop, exceeded my development expectations!", "2024-01-20"),
        (2, 2, 9, 5, "Best noise cancellation I have ever used on flights.", "2024-03-01"),
        (3, 3, 2, 4, "Picture quality is crisp, sound is decent for the price.", "2024-01-25"),
        (4, 4, 3, 5, "Tactile clicks are so satisfying for typing all day.", "2024-01-26"),
        (5, 8, 5, 4, "Great arch support and very lightweight for jogging.", "2024-02-15"),
        (6, 10, 6, 5, "Café quality espresso every single morning at home.", "2024-02-28"),
        (7, 14, 4, 5, "The ultimate handbook for distributed backend systems.", "2024-03-25"),
        (8, 17, 7, 5, "Compact dumbbells that save so much gym floor space.", "2024-02-26"),
        (9, 20, 8, 4, "Accurate GPS tracking and battery lasts over a week.", "2024-04-28")
    ]
    cursor.executemany("INSERT INTO reviews (review_id, product_id, customer_id, rating, comment, review_date) VALUES (?, ?, ?, ?, ?, ?)", reviews)

def get_db_connection() -> sqlite3.Connection:
    """Returns a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_schema_summary() -> str:
    """Returns a schema summary string specifically formatted for LLM prompts."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [row["name"] for row in cursor.fetchall()]

    schema_lines = []
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table});")
        columns = cursor.fetchall()
        col_strs = [f"{col['name']} ({col['type']})" for col in columns]
        
        # Check foreign keys
        cursor.execute(f"PRAGMA foreign_key_list({table});")
        fks = cursor.fetchall()
        fk_strs = [f"FK {fk['from']} -> {fk['table']}({fk['to']})" for fk in fks]

        line = f"Table: {table}\n  Columns: {', '.join(col_strs)}"
        if fk_strs:
            line += f"\n  Relationships: {', '.join(fk_strs)}"
        schema_lines.append(line)

    conn.close()
    return "\n\n".join(schema_lines)

def get_schema_details() -> Dict[str, Any]:
    """Returns detailed schema metadata for the frontend Schema Explorer."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    table_names = [row["name"] for row in cursor.fetchall()]

    tables = []
    for name in table_names:
        cursor.execute(f"PRAGMA table_info({name});")
        columns_info = cursor.fetchall()

        cursor.execute(f"PRAGMA foreign_key_list({name});")
        fks_info = {fk["from"]: {"target_table": fk["table"], "target_column": fk["to"]} for fk in cursor.fetchall()}

        cursor.execute(f"SELECT COUNT(*) as count FROM {name};")
        row_count = cursor.fetchone()["count"]

        # Fetch up to 3 sample rows
        cursor.execute(f"SELECT * FROM {name} LIMIT 3;")
        sample_rows = [dict(r) for r in cursor.fetchall()]

        columns = []
        for col in columns_info:
            col_name = col["name"]
            columns.append({
                "name": col_name,
                "type": col["type"],
                "not_null": bool(col["notnull"]),
                "is_primary_key": bool(col["pk"]),
                "foreign_key": fks_info.get(col_name)
            })

        tables.append({
            "name": name,
            "row_count": row_count,
            "columns": columns,
            "sample_rows": sample_rows
        })

    conn.close()
    return {
        "engine": "SQLite",
        "database_name": "sales_data.db",
        "tables": tables
    }

def execute_readonly_query(sql: str, max_rows: int = 500) -> Dict[str, Any]:
    """
    Executes a read-only query safely and measures execution duration.
    """
    start_time = time.perf_counter()
    
    # Connect with read-only URI mode to enforce database level lock
    uri_path = f"file:{os.path.abspath(DB_PATH)}?mode=ro"
    try:
        conn = sqlite3.connect(uri_path, uri=True, timeout=5.0)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(sql)
        description = cursor.description
        if not description:
            conn.close()
            return {
                "columns": [],
                "rows": [],
                "row_count": 0,
                "execution_time_ms": round((time.perf_counter() - start_time) * 1000, 2),
                "message": "Query executed successfully. (No tabular result returned)"
            }

        columns = [d[0] for d in description]
        fetched_rows = cursor.fetchmany(max_rows)
        rows = [list(r) for r in fetched_rows]
        total_fetched = len(rows)

        conn.close()
        exec_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return {
            "columns": columns,
            "rows": rows,
            "row_count": total_fetched,
            "execution_time_ms": exec_ms,
            "truncated": total_fetched >= max_rows
        }
    except Exception as e:
        exec_ms = round((time.perf_counter() - start_time) * 1000, 2)
        raise RuntimeError(f"Database execution error: {str(e)}")
