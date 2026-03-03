#!/usr/bin/env python3
"""
Migration script: SQLite → PostgreSQL
"""
import sqlite3
import psycopg2
from psycopg2.extras import execute_batch

# SQLite config
SQLITE_DB = "cleaning.db"

# PostgreSQL config
PG_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "cleaning",
    "user": "postgres",
    "password": "postgres"
}


def migrate_cleaners(sqlite_conn, pg_conn):
    """Migrate cleaners table"""
    print("Migrating cleaners...")
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT id, name, phone, status, created_at FROM cleaners")
    rows = cursor.fetchall()
    
    pg_cursor = pg_conn.cursor()
    query = """
        INSERT INTO cleaners (id, name, phone, status, created_at)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING
    """
    execute_batch(pg_cursor, query, rows)
    pg_conn.commit()
    print(f"  Migrated {len(rows)} cleaners")


def migrate_hosts(sqlite_conn, pg_conn):
    """Migrate hosts table"""
    print("Migrating hosts...")
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT id, name, phone, code, created_at FROM hosts")
    rows = cursor.fetchall()
    
    pg_cursor = pg_conn.cursor()
    query = """
        INSERT INTO hosts (id, name, phone, code, created_at)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING
    """
    execute_batch(pg_cursor, query, rows)
    pg_conn.commit()
    print(f"  Migrated {len(rows)} hosts")


def migrate_properties(sqlite_conn, pg_conn):
    """Migrate properties table"""
    print("Migrating properties...")
    cursor = sqlite_conn.cursor()
    cursor.execute("""
        SELECT id, name, address, bedrooms, bathrooms, cleaning_time_minutes,
               host_phone, province, city, street, house_number, postal_code,
               floor, area, status, created_at
        FROM properties
    """)
    rows = cursor.fetchall()
    
    pg_cursor = pg_conn.cursor()
    query = """
        INSERT INTO properties (id, name, address, bedrooms, bathrooms, cleaning_time_minutes,
               host_phone, province, city, street, house_number, postal_code,
               floor, area, status, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING
    """
    execute_batch(pg_cursor, query, rows)
    pg_conn.commit()
    print(f"  Migrated {len(rows)} properties")


def migrate_orders(sqlite_conn, pg_conn):
    """Migrate orders table"""
    print("Migrating orders...")
    cursor = sqlite_conn.cursor()
    cursor.execute("""
        SELECT id, property_id, host_name, host_phone, checkout_time, price, status,
               assigned_cleaner_id, assigned_at, arrived_at, voice_url, text_notes,
               completion_photos, accepted_by_host, host_id, created_at
        FROM orders
    """)
    rows = cursor.fetchall()
    
    pg_cursor = pg_conn.cursor()
    query = """
        INSERT INTO orders (id, property_id, host_name, host_phone, checkout_time, price, status,
               assigned_cleaner_id, assigned_at, arrived_at, voice_url, text_notes,
               completion_photos, accepted_by_host, host_id, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING
    """
    execute_batch(pg_cursor, query, rows)
    pg_conn.commit()
    print(f"  Migrated {len(rows)} orders")


def main():
    print("=== SQLite → PostgreSQL Migration ===\n")
    
    # Connect to SQLite
    sqlite_conn = sqlite3.connect(SQLITE_DB)
    print(f"Connected to SQLite: {SQLITE_DB}")
    
    # Connect to PostgreSQL
    pg_conn = psycopg2.connect(**PG_CONFIG)
    print(f"Connected to PostgreSQL: {PG_CONFIG['host']}/{PG_CONFIG['database']}\n")
    
    # Migrate tables
    migrate_cleaners(sqlite_conn, pg_conn)
    migrate_hosts(sqlite_conn, pg_conn)
    migrate_properties(sqlite_conn, pg_conn)
    migrate_orders(sqlite_conn, pg_conn)
    
    # Close connections
    sqlite_conn.close()
    pg_conn.close()
    
    print("\n=== Migration Complete! ===")


if __name__ == "__main__":
    main()
