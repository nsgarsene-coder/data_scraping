CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    brand TEXT,
    title TEXT,
    price REAL,
    rating REAL,
    reviews TEXT,
    link TEXT,
    image TEXT,
    badge TEXT,
    scraped_at TEXT
);
``