#!/usr/bin/env python3
import sqlite3
import os
from datetime import datetime

# Configuration
OLD_DB_PATH = 'pcs.db'
NEW_DB_PATH = 'pcs_new.db'
SCHEMA_PATH = 'schema.sql'
MIGRATION_DATE = '2025-06-05 00:00:00'  # Format: YYYY-MM-DD HH:MM:SS

def read_schema():
    with open(SCHEMA_PATH, 'r') as f:
        return f.read()

def migrate_data():
    # Connect to both databases
    old_conn = sqlite3.connect(OLD_DB_PATH)
    new_conn = sqlite3.connect(NEW_DB_PATH)
    
    old_cur = old_conn.cursor()
    new_cur = new_conn.cursor()

    try:
        # Create new schema
        schema_sql = read_schema()
        new_cur.executescript(schema_sql)

        # Migrate PC data
        old_cur.execute('SELECT id, host, serial, cpu, mainboard, ram_total_gb, ram_slots, resolution, notes FROM pc')
        for row in old_cur.fetchall():
            new_cur.execute('''
                INSERT INTO pc (id, host, serial, cpu, mainboard, ram_total_gb, ram_slots, resolution, notes, submitted_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (*row, MIGRATION_DATE))

        # Migrate GPU data
        old_cur.execute('SELECT id, pc_id, name FROM gpu')
        for row in old_cur.fetchall():
            new_cur.execute('INSERT INTO gpu (id, pc_id, name) VALUES (?, ?, ?)', row)

        # Migrate RAM data
        old_cur.execute('SELECT id, pc_id, size_gb, type, model FROM ram_stick')
        for row in old_cur.fetchall():
            new_cur.execute('INSERT INTO ram_stick (id, pc_id, size_gb, type, model) VALUES (?, ?, ?, ?, ?)', row)

        # Migrate disk data
        old_cur.execute('SELECT id, pc_id, size_gb, model, serial, path FROM disk')
        for row in old_cur.fetchall():
            new_cur.execute('INSERT INTO disk (id, pc_id, size_gb, model, serial, path) VALUES (?, ?, ?, ?, ?, ?)', row)

        # Commit the changes
        new_conn.commit()
        print(f"Migration completed successfully. New database created at {NEW_DB_PATH}")

    except Exception as e:
        print(f"Error during migration: {e}")
        new_conn.rollback()
        raise
    finally:
        old_conn.close()
        new_conn.close()

def main():
    if not os.path.exists(OLD_DB_PATH):
        print(f"Error: Old database {OLD_DB_PATH} not found")
        return

    if os.path.exists(NEW_DB_PATH):
        print(f"Warning: {NEW_DB_PATH} already exists. Please remove it first.")
        return

    migrate_data()

if __name__ == '__main__':
    main()