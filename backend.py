from flask import Flask, request, jsonify
import sqlite3
import hashlib
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
DB_PATH = 'pcs.db'


def init_db():
    with open('schema.sql') as f:
        schema = f.read()
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(schema)
    conn.commit()
    conn.close()


def hash_serial(serial: str) -> str:
    return hashlib.sha256(serial.encode('utf-8')).hexdigest()


@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()
    serial = data.get("serial", "")
    if not serial:
        return jsonify({"error": "Missing serial"}), 400

    pc_id = hash_serial(serial)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Check if PC already exists and get existing data if any
    cur.execute("SELECT * FROM pc WHERE id = ?", (pc_id,))
    existing_pc = cur.fetchone()
    
    if existing_pc:
        # Convert existing_pc tuple to a dictionary using column names
        columns = [column[0] for column in cur.description]
        existing_pc_dict = dict(zip(columns, existing_pc))
        
        # Use existing values for fields not provided in the update
        host = data.get("host", existing_pc_dict.get("host"))
        cpu = data.get("cpu", existing_pc_dict.get("cpu"))
        mainboard = data.get("mainboard", existing_pc_dict.get("mainboard"))
        resolution = data.get("resolution", existing_pc_dict.get("resolution"))
        notes = data.get("notes", existing_pc_dict.get("notes"))
        
        # Handle RAM data carefully
        ram_total_gb = existing_pc_dict.get("ram_total_gb")
        ram_slots = existing_pc_dict.get("ram_slots")
        
        # Only update RAM if explicitly provided in the request
        if "ram" in data and isinstance(data["ram"], dict):
            ram_data = data["ram"]
            ram_total_gb = ram_data.get("total_size_gb", ram_total_gb)
            ram_slots = ram_data.get("slots", ram_slots)
    else:
        # New PC entry
        host = data.get("host")
        cpu = data.get("cpu")
        mainboard = data.get("mainboard")
        resolution = data.get("resolution")
        notes = data.get("notes")
        
        # Handle the case when 'ram' key is missing
        ram_data = data.get("ram", {})
        ram_total_gb = ram_data.get("total_size_gb") if isinstance(ram_data, dict) else None
        ram_slots = ram_data.get("slots") if isinstance(ram_data, dict) else None
    
    # Update or insert the PC record
    cur.execute("""
        INSERT OR REPLACE INTO pc (id, host, serial, cpu, mainboard, ram_total_gb, ram_slots, resolution, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        pc_id,
        host,
        serial,
        cpu,
        mainboard,
        ram_total_gb,
        ram_slots,
        resolution,
        notes
    ))

    # Only update related tables if the data is provided in the request
    if "gpus" in data:
        cur.execute("DELETE FROM gpu WHERE pc_id = ?", (pc_id,))
        for gpu in data.get("gpus", []):
            cur.execute("INSERT INTO gpu (pc_id, name) VALUES (?, ?)", (pc_id, gpu))

    # Only update RAM sticks if explicitly provided
    if "ram" in data and isinstance(data["ram"], dict) and "sticks" in data["ram"]:
        cur.execute("DELETE FROM ram_stick WHERE pc_id = ?", (pc_id,))
        for stick in data["ram"]["sticks"]:
            cur.execute("""
                INSERT INTO ram_stick (pc_id, size_gb, type, model)
                VALUES (?, ?, ?, ?)
            """, (
                pc_id,
                stick.get("size_gb"),
                stick.get("type"),
                stick.get("model")
            ))

    # Only update disks if explicitly provided
    if "disks" in data:
        cur.execute("DELETE FROM disk WHERE pc_id = ?", (pc_id,))
        for disk in data.get("disks", []):
            size_str = disk.get("size", "0G").upper().rstrip("G")
            size_gb = int(float(size_str)) if size_str.replace('.', '', 1).isdigit() else 0
            cur.execute("""
                INSERT INTO disk (pc_id, size_gb, model, serial, path)
                VALUES (?, ?, ?, ?, ?)
            """, (
                pc_id,
                size_gb,
                disk.get("model"),
                disk.get("serial"),
                disk.get("path")
            ))

    conn.commit()
    conn.close()

    return jsonify({"status": "success", "pc_id": pc_id})

@app.route('/pcs', methods=['GET'])
def get_all_pcs():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id FROM pc")
    pcs = [dict(zip([column[0] for column in cur.description], row)) for row in cur.fetchall()]
    conn.close()
    return jsonify(pcs)


@app.route('/pc/<pc_id>', methods=['GET'])
def get_pc_details(pc_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Main PC data
    cur.execute("SELECT * FROM pc WHERE id = ?", (pc_id,))
    row = cur.fetchone()
    if not row:
        return jsonify({"error": "PC not found"}), 404
    pc = dict(zip([column[0] for column in cur.description], row))

    # Related data
    cur.execute("SELECT name FROM gpu WHERE pc_id = ?", (pc_id,))
    pc["gpus"] = [r[0] for r in cur.fetchall()]

    cur.execute("SELECT size_gb, type, model FROM ram_stick WHERE pc_id = ?", (pc_id,))
    pc["ram_sticks"] = [dict(zip(["size_gb", "type", "model"], r)) for r in cur.fetchall()]

    cur.execute("SELECT size_gb, model, serial, path FROM disk WHERE pc_id = ?", (pc_id,))
    pc["disks"] = [dict(zip(["size_gb", "model", "serial", "path"], r)) for r in cur.fetchall()]

    conn.close()
    return jsonify(pc)


if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        init_db()
    app.run(host="0.0.0.0", port=5000)

