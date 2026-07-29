#!/usr/bin/env python3
"""SVS Stock App – Databasis opstelling en saad data"""
import sqlite3, hashlib, os

DB_PATH = os.path.join(os.path.expanduser('~'), 'svs_stock.db')

SCHEMA = """
CREATE TABLE IF NOT EXISTS salons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    logo_path TEXT DEFAULT '',
    active INTEGER DEFAULT 1
);
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    name TEXT NOT NULL,
    role TEXT NOT NULL,
    salon_id INTEGER,
    FOREIGN KEY (salon_id) REFERENCES salons(id)
);
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    rsp REAL DEFAULT 0,
    image_path TEXT DEFAULT '',
    active INTEGER DEFAULT 1
);
CREATE TABLE IF NOT EXISTS stock_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    salon_id INTEGER NOT NULL,
    pack_date TEXT NOT NULL,
    status TEXT DEFAULT 'draft',
    notes TEXT DEFAULT '',
    created_at TEXT DEFAULT (datetime('now')),
    submitted_at TEXT,
    packed_at TEXT,
    received_at TEXT,
    FOREIGN KEY (salon_id) REFERENCES salons(id)
);
CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    quantity REAL DEFAULT 1,
    note TEXT DEFAULT '',
    packed INTEGER DEFAULT 0,
    received INTEGER DEFAULT 0,
    FOREIGN KEY (order_id) REFERENCES stock_orders(id)
);
CREATE TABLE IF NOT EXISTS towel_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    salon_id INTEGER NOT NULL,
    week_date TEXT NOT NULL,
    towel_type TEXT NOT NULL,
    sent INTEGER DEFAULT 0,
    collected INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (salon_id) REFERENCES salons(id)
);
"""

def hash_pw(password):
    salt = os.urandom(16).hex()
    h = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
    return f"{salt}:{h}"

SALONS = [
    ('BB', 'Bronberg'),
    ('BV', 'Bouganvilla'),
    ('EL', 'Eldoraigne'),
    ('HE', 'Hennops'),
    ('PO', 'Pretoria-Oos'),
    ('RS', 'Ruimtesig'),
    ('TR', 'Twee Riviere'),
    ('VG', 'Vergelegen'),
    ('WK', 'Waterkloof Marina'),
]

SALON_USERS = [
    ('reception@BB', 'BBBB', 'Bronberg',        'BB'),
    ('reception@BV', 'BVBV', 'Bouganvilla',     'BV'),
    ('reception@EL', 'ELEL', 'Eldoraigne',      'EL'),
    ('reception@HE', 'HEHE', 'Hennops',         'HE'),
    ('reception@PO', 'POPO', 'Pretoria-Oos',    'PO'),
    ('reception@RS', 'RSRS', 'Ruimtesig',       'RS'),
    ('reception@TR', 'TRTR', 'Twee Riviere',    'TR'),
    ('reception@VG', 'VGVG', 'Vergelegen',      'VG'),
    ('reception@WK', 'WKWK', 'Waterkloof Marina','WK'),
]

HO_USERS = [
    ('Gilbert@HO', '1111', 'Gilbert'),
    ('Sarie@HO',   '2222', 'Sarie'),
    ('Marius@HO',  '3333', 'Marius'),
]

SALON_PRODUCTS = [
    'Conditioning Blue Bleach', '10 Vol Peroxide', '20 Vol Peroxide', '30 Vol Peroxide',
    'Neutraliser 1Ltr', 'Blow Wave Styling Lotion', 'Protector', 'Volumising Spray',
    'Super Hold Glaze', 'Placenta Treatment', 'Anti-Dandruff Treatment', 'Salon Mousse',
    'Scalp Massagers', 'Black Rubber Gloves', 'Shower Caps (10)',
    'Shampoo 1L', 'Conditioner 1L', 'Haarspray 1L', 'Volumizing Styling Gel',
    'Colour Wipes', 'Wet Wipes', 'Bicarb (Koeksoda)', 'Seeppoeier',
    'Pine Gel', 'Furniture Polish', 'Rubbish Bags',
    'Besigheidskaartjies', 'Rekening Aansoek Vorms', 'Verlof Vorms',
    'Till Rolls', 'Kaart Printing Rolls', 'Plastieksakke',
    'Foils', 'Timer', 'Tint Bakkie',
]

PERM_PRODUCTS = [
    'Perm No 1 (Normal) 1ltr', 'Perm No 2 (Tinted) 1ltr',
    'Magix Perm', 'Osmo Acid Perm', 'Exta Perm Lotion', 'Exta Perm Neutralizer',
    'Normal Perm Lotion (pienk)', 'Acid Perm',
    'Perm Papers Jumbo', 'Perm Papers (box)', 'Perm Rubbers',
]

RETAIL_PRODUCTS = [
    'Placenta Shampoo', 'Placenta Conditioner', 'Placenta Plus Spray',
    'SVS Handsak Hairspray', 'SVS Shampoo', 'SVS Conditioner',
    'SVS Glaze', 'SVS Hairspray 200ml', 'SVS Silver Conditioner',
    'SVS Silver Shampoo', 'SVS Hair Mask', 'SVS Placenta',
    'SVS Body Wash', 'SVS Body Lotion', 'SVS Hand Wash',
    'SVS Hand Lotion', 'SVS Luxury Foam Bath', 'SVS Face Serum',
    'SVS Hair Serum', 'SVS Heat Protector', 'SVS Liquid Styling Gel',
    'SVS Tissue Oil', 'SVS Hand Sanitizer', 'SVS Shower Caps',
    'Argan Shampoo', 'Argan Conditioner', 'Argan 2 in 1',
    'Argan Leave in Treatment', 'Argan Mask',
    'HEDZ Booster Tabs', 'HEDZ Gel Spray', 'HEDZ Keratin Spray',
    'HEDZ Silver Mousse', 'HEDZ Normal Mousse',
    'HEDZ Pitch Black Shampoo', 'HEDZ Pitch Black Conditioner',
    'HEDZ Premium Shampoo', 'HEDZ Premium Conditioner',
    'HEDZ Firm Hold Hairspray', 'HEDZ Firm Xtra-Hold Hairspray',
    'HEDZ Styling Volumizer Gel', 'HEDZ Remoulding Gum',
    'Icon Frosted Grey Shampoo', 'Icon Frosted Grey Conditioner',
    'Icon Living Proof SPA',
    'Agiva Styling Wax', 'Worx Hair Polish',
]

def main():
    print(f"Databasis: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)

    # Salons
    for code, name in SALONS:
        conn.execute("INSERT OR IGNORE INTO salons (code, name) VALUES (?,?)", (code, name))
    conn.commit()

    # Salon users
    for username, pw, name, salon_code in SALON_USERS:
        salon = conn.execute("SELECT id FROM salons WHERE code=?", (salon_code,)).fetchone()
        if salon:
            conn.execute("INSERT OR REPLACE INTO users (username, password_hash, name, role, salon_id) VALUES (?,?,?,?,?)",
                        (username, hash_pw(pw), name, 'salon', salon[0]))

    # HO users
    for username, pw, name in HO_USERS:
        conn.execute("INSERT OR REPLACE INTO users (username, password_hash, name, role, salon_id) VALUES (?,?,?,?,?)",
                    (username, hash_pw(pw), name, 'ho_admin', None))
    conn.commit()

    # Products — gebruik WHERE NOT EXISTS om te verhoed dat duplikate geskep word
    # as hierdie skrip meer as een keer loop (naam-tjek is onafhanklik van kategorie)
    def insert_product_safe(conn, name, category):
        conn.execute("""
            INSERT INTO products (name, category)
            SELECT ?, ?
            WHERE NOT EXISTS (
                SELECT 1 FROM products WHERE LOWER(TRIM(name)) = LOWER(TRIM(?))
            )
        """, (name, category, name))

    for name in SALON_PRODUCTS:
        insert_product_safe(conn, name, 'Salon')
    for name in PERM_PRODUCTS:
        insert_product_safe(conn, name, 'Perms')
    for name in RETAIL_PRODUCTS:
        insert_product_safe(conn, name, 'Retail')
    conn.commit()
    conn.close()

    print("✓ Databasis gereed!")
    print("\nAanmeld besonderhede:")
    print("  HO:     Gilbert@HO / 1111")
    print("          Sarie@HO   / 2222")
    print("          Marius@HO  / 3333")
    print("  Salons: reception@BB / BBBB  (en so aan vir elke salon)")

if __name__ == '__main__':
    main()
