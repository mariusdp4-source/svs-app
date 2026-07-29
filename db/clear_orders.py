#!/usr/bin/env python3
"""
Vee ALLE bestellings, items, handdoek-logs en verskaffer-bestellings uit.
Produkte en salonne bly ongeskonde.
Gebruik dit om van voor af te begin met regte data.
"""
import sqlite3, os

DB_PATH = os.path.join(os.path.expanduser('~'), 'svs_stock.db')

def main():
    print(f"Databasis: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)

    tables = [
        ('supplier_orders', "DELETE FROM supplier_orders"),
        ('towel_logs',      "DELETE FROM towel_logs"),
        ('order_items',     "DELETE FROM order_items"),
        ('stock_orders',    "DELETE FROM stock_orders"),
    ]

    for name, sql in tables:
        try:
            n = conn.execute(sql).rowcount
            conn.commit()
            print(f"  ✓ {name}: {n} rekord(s) verwyder")
        except Exception as e:
            print(f"  ! {name}: {e}")

    # Reset auto-increment tellers
    conn.execute("DELETE FROM sqlite_sequence WHERE name IN ('stock_orders','order_items','towel_logs','supplier_orders')")
    conn.commit()
    conn.close()

    print("\n✅ Gedoen! Databasis is skoon — jy kan van voor begin.")

if __name__ == '__main__':
    main()
