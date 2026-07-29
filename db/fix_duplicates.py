#!/usr/bin/env python3
"""Verwyder duplikaat produkte uit die databasis en herlaai alles korrek."""
import sqlite3, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DB_PATH = os.path.join(os.path.expanduser('~'), 'svs_stock.db')

# ─── Produklys per kategorie ──────────────────────────────────────────────────

SALON_PRODUCTS = [
    'Conditioning Blue Bleach', '10 Vol Peroxide', '20 Vol Peroxide', '30 Vol Peroxide',
    'Neutraliser 1Ltr', 'Blow Wave Styling Lotion', 'Protector', 'Volumising Spray',
    'Super Hold Glaze', 'Placenta Treatment', 'Anti-Dandruff Treatment', 'Salon Mousse',
    'Scalp Massagers', 'Black Rubber Gloves', 'Shower Caps (10)',
    'Shampoo 1L', 'Conditioner 1L', 'Haarspray 1L', 'Volumizing Styling Gel',
    'Colour Wipes', 'Wet Wipes',
    'Besigheidskaartjies', 'Rekening Aansoek Vorms', 'Verlof Vorms',
    'Till Rolls', 'Kaart Printing Rolls', 'Plastieksakke',
    'Foils', 'Timer', 'Tint Bakkie',
]

CLEANING_PRODUCTS = [
    'Bicarb (Koeksoda)', 'Seeppoeier', 'Pine Gel', 'Furniture Polish', 'Rubbish Bags',
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

# ─── Verskaffer-bepaling ──────────────────────────────────────────────────────

def get_supplier(name, category):
    """Bepaal die verskaffer outomaties op grond van kategorie en produk-naam."""
    if category == 'Salon':
        return 'Silver Salon Products'
    if category == 'Perms':
        return 'Silver Salon Products'
    if category == 'Cleaning':
        return ''   # Gebruik admin-bladsy om in te vul
    if category == 'Tints':
        return 'HHB'
    if category == 'Retail':
        for prefix, sup in [
            ('SVS',      'SVS'),
            ('Argan',    'Argan'),
            ('HEDZ',     'HEDZ'),
            ('Icon',     'Icon'),
            ('Agiva',    'Agiva'),
            ('Worx',     'Worx'),
            ('Placenta', 'Silver Salon Products'),
        ]:
            if name.startswith(prefix):
                return sup
        return ''
    return ''


def main():
    print(f"Databasis: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)

    # ─── Kolomme-migrasies (veilig — raak NIE data aan nie) ──────────────────
    # Voeg supplier kolom by sodat INSERT OR IGNORE hieronder werk
    try:
        conn.execute("ALTER TABLE products ADD COLUMN supplier TEXT DEFAULT ''")
        conn.commit()
        print("✓ supplier kolom bygevoeg")
    except Exception:
        pass  # Bestaan reeds

    bestaande = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    print(f"Bestaande produkte in databasis: {bestaande}")

    # ─── Voeg SLEGS ontbrekende produkte by (raak NIE bestaande data aan nie) ─
    # Gebruik WHERE NOT EXISTS op naam alleen — so 'n produk wat reeds bestaan
    # (selfs as dit na 'n ander kategorie geskuif is) word NOOIT heringevoeg nie.
    added = 0
    all_inserts = (
        [(n, 'Salon',    get_supplier(n, 'Salon'))    for n in SALON_PRODUCTS] +
        [(n, 'Cleaning', get_supplier(n, 'Cleaning')) for n in CLEANING_PRODUCTS] +
        [(n, 'Perms',    get_supplier(n, 'Perms'))    for n in PERM_PRODUCTS] +
        [(n, 'Retail',   get_supplier(n, 'Retail'))   for n in RETAIL_PRODUCTS]
    )

    # Verwyder ou (naam+kategorie) indeks wat toegelaat het dat dieselfde naam
    # in twee kategorieë bestaan — dit was die oorsaak van die Neutraliser-probleem
    try:
        conn.execute("DROP INDEX IF EXISTS idx_prod_name_cat")
        conn.commit()
    except Exception:
        pass

    # Skep nuwe unieke indeks op naam alleen sodat dit nie weer kan gebeur nie
    try:
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS uix_products_name ON products(LOWER(TRIM(name)))")
        conn.commit()
    except Exception:
        pass  # Duplikate verhoed die skepping — gebruik eers "Clean Up Duplicates" op die produkte-bladsy

    for name, cat, sup in all_inserts:
        cur = conn.execute("""
            INSERT INTO products (name, category, supplier, active)
            SELECT ?, ?, ?, 1
            WHERE NOT EXISTS (
                SELECT 1 FROM products WHERE LOWER(TRIM(name)) = LOWER(TRIM(?))
            )
        """, (name, cat, sup, name))
        if cur.rowcount:
            added += 1
    conn.commit()

    if added:
        print(f"✓ {added} nuwe produkte bygevoeg")
    else:
        print("✓ Geen nuwe produkte — alles is reeds in die databasis")

    na = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    print(f"Totale produkte na update: {na}")

    # ─── Skep tabelle ────────────────────────────────────────────────────────
    conn.execute("""
        CREATE TABLE IF NOT EXISTS supplier_orders (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            pack_date    TEXT NOT NULL,
            product_name TEXT NOT NULL,
            category     TEXT NOT NULL,
            qty_needed   REAL DEFAULT 0,
            qty_ordered  REAL DEFAULT 0,
            ordered      INTEGER DEFAULT 0,
            ordered_at   TEXT DEFAULT NULL,
            notes        TEXT DEFAULT '',
            created_at   TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS towel_logs (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id   INTEGER,
            salon_id   INTEGER,
            week_date  TEXT,
            towel_type TEXT,
            sent       REAL DEFAULT 0,
            collected  REAL DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS stock_takes (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            taken_at   TEXT NOT NULL,
            taken_by   TEXT DEFAULT '',
            notes      TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS stock_take_items (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            stock_take_id INTEGER NOT NULL,
            product_name  TEXT NOT NULL,
            category      TEXT NOT NULL,
            quantity      REAL DEFAULT 0
        )
    """)
    conn.commit()

    # ─── Kolomme-migrasies ────────────────────────────────────────────────────
    migrations = [
        "ALTER TABLE order_items ADD COLUMN delivered_qty REAL DEFAULT 0",
        "ALTER TABLE order_items ADD COLUMN delivery_note TEXT DEFAULT ''",
        "ALTER TABLE order_items ADD COLUMN packed INTEGER DEFAULT 0",
        "ALTER TABLE order_items ADD COLUMN is_custom INTEGER DEFAULT 0",
        "ALTER TABLE order_items ADD COLUMN note TEXT DEFAULT ''",
        "ALTER TABLE stock_orders ADD COLUMN signed_by TEXT DEFAULT ''",
        "ALTER TABLE stock_orders ADD COLUMN delivered_at TEXT",
        "ALTER TABLE stock_orders ADD COLUMN packed_at TEXT",
        "ALTER TABLE towel_logs ADD COLUMN sent REAL DEFAULT 0",
        "ALTER TABLE towel_logs ADD COLUMN next_qty REAL DEFAULT 0",
    ]
    for stmt in migrations:
        try:
            conn.execute(stmt)
            conn.commit()
        except Exception:
            pass  # Kolom bestaan reeds

    print("✓ Gedoen! Herbegin die app.")
    conn.close()

if __name__ == '__main__':
    main()
