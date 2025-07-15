#!/usr/bin/env python3
"""
Migration script to add tag support to existing hwinfo-db database.
This script adds the tag and pc_tag tables if they don't exist.
"""

import sqlite3
import os

DB_PATH = '/data/pcs.db'
# For local development, uncomment the line below
# DB_PATH = './pcs.db'

def migrate_database():
    """Add tag tables to existing database if they don't exist."""
    
    if not os.path.exists(DB_PATH):
        print(f"Database file {DB_PATH} does not exist. Run the main application first.")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    try:
        # Check if tag table exists
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tag'")
        tag_table_exists = cur.fetchone() is not None
        
        if not tag_table_exists:
            print("Creating tag table...")
            cur.execute("""
                CREATE TABLE tag (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE,
                    color TEXT DEFAULT '#228BE6'
                )
            """)
            print("Tag table created successfully.")
        else:
            print("Tag table already exists.")
        
        # Check if pc_tag table exists
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pc_tag'")
        pc_tag_table_exists = cur.fetchone() is not None
        
        if not pc_tag_table_exists:
            print("Creating pc_tag table...")
            cur.execute("""
                CREATE TABLE pc_tag (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pc_id TEXT,
                    tag_id INTEGER,
                    FOREIGN KEY(pc_id) REFERENCES pc(id) ON DELETE CASCADE,
                    FOREIGN KEY(tag_id) REFERENCES tag(id) ON DELETE CASCADE,
                    UNIQUE(pc_id, tag_id)
                )
            """)
            print("PC-tag relationship table created successfully.")
        else:
            print("PC-tag relationship table already exists.")
        
        # Create some default tags if none exist
        cur.execute("SELECT COUNT(*) FROM tag")
        tag_count = cur.fetchone()[0]
        
        if tag_count == 0:
            print("Creating default tags...")
            default_tags = [
                ('Gaming', '#228BE6'),
                ('Office', '#40C057'),
                ('Server', '#FD7E14'),
                ('Development', '#9C88FF'),
                ('Home', '#FA5252'),
            ]
            
            cur.executemany("INSERT INTO tag (name, color) VALUES (?, ?)", default_tags)
            print(f"Created {len(default_tags)} default tags.")
        
        conn.commit()
        print("Migration completed successfully!")
        
    except sqlite3.Error as e:
        print(f"Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
