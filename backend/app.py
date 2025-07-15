from flask import Flask, request, jsonify, render_template_string
import sqlite3
import hashlib
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
DB_PATH = '/data/pcs.db'
#DB_PATH = './pcs.db'

# HTML template for the dashboard
DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PC Hardware Dashboard</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .pc-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .pc-tile {
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            padding: 15px;
            transition: all 0.3s ease;
        }
        .pc-tile:hover {
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }
        .pc-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            cursor: pointer;
        }
        .pc-title {
            font-weight: bold;
            font-size: 1.2em;
            color: #444;
        }
        .header-buttons {
            display: flex;
            gap: 5px;
            align-items: center;
        }
        .delete-btn {
            background: none;
            border: none;
            font-size: 1.2em;
            cursor: pointer;
            color: #d9534f;
            padding: 5px;
            border-radius: 4px;
        }
        .delete-btn:hover {
            background-color: #f8d7da;
        }
        .toggle-btn {
            background: none;
            border: none;
            font-size: 1.5em;
            cursor: pointer;
            color: #666;
        }
        .pc-short-info {
            margin-bottom: 10px;
        }
        .pc-extended-info {
            border-top: 1px solid #eee;
            padding-top: 10px;
            display: none;
        }
        .info-row {
            display: flex;
            margin-bottom: 5px;
        }
        .info-label {
            font-weight: bold;
            width: 120px;
            color: #666;
        }
        .info-value {
            flex: 1;
        }
        .section-title {
            font-weight: bold;
            margin: 10px 0 5px;
            color: #555;
        }
        .component-item {
            background-color: #f9f9f9;
            padding: 8px;
            margin-bottom: 5px;
            border-radius: 4px;
        }
        .loading {
            text-align: center;
            padding: 50px;
            font-size: 1.2em;
            color: #666;
        }
        .error {
            color: #d9534f;
            text-align: center;
            padding: 20px;
        }
        .notes-input {
            width: 100%;
            min-height: 60px;
            margin-top: 5px;
            padding: 5px;
            border: 1px solid #ddd;
            border-radius: 4px;
            resize: vertical;
        }
        .save-notes-btn {
            margin-top: 5px;
            padding: 5px 10px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        .save-notes-btn:hover {
            background-color: #45a049;
        }
        .notes-edit-container {
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>PC Hardware Dashboard</h1>
        
        <div id="pc-grid" class="pc-grid">
            <div class="loading">Loading PC data...</div>
        </div>
    </div>

    <script>
        // Function to fetch all PCs
        async function fetchPCs() {
            try {
                const response = await fetch('/pcs');
                if (!response.ok) {
                    throw new Error('Failed to fetch PC list');
                }
                const data = await response.json();
                return data;
            } catch (error) {
                console.error('Error fetching PCs:', error);
                document.getElementById('pc-grid').innerHTML = 
                    `<div class="error">Error loading PC data: ${error.message}</div>`;
                return [];
            }
        }

        // Function to fetch details for a specific PC
        async function fetchPCDetails(pcId) {
            try {
                const response = await fetch(`/pc/${pcId}`);
                if (!response.ok) {
                    throw new Error('Failed to fetch PC details');
                }
                return await response.json();
            } catch (error) {
                console.error(`Error fetching details for PC ${pcId}:`, error);
                return null;
            }
        }

        // Function to toggle the extended info display
        function toggleExtendedInfo(pcId) {
            const extendedInfo = document.getElementById(`extended-info-${pcId}`);
            const toggleBtn = document.getElementById(`toggle-btn-${pcId}`);
            
            if (extendedInfo.style.display === 'block') {
                extendedInfo.style.display = 'none';
                toggleBtn.textContent = '+';
            } else {
                extendedInfo.style.display = 'block';
                toggleBtn.textContent = '-';
            }
        }

        // Function to create a PC tile with short and extended info
        function createPCTile(pc) {
            const tile = document.createElement('div');
            tile.className = 'pc-tile';
            
            // Short info section (always visible)
            const shortInfo = `
                <div class="pc-header">
                    <div class="pc-title" onclick="toggleExtendedInfo('${pc.id}')">${pc.host || 'Unknown Host'}</div>
                    <div class="header-buttons">
                        <button onclick="deletePC('${pc.id}')" class="delete-btn">🗑️</button>
                        <button id="toggle-btn-${pc.id}" class="toggle-btn" onclick="toggleExtendedInfo('${pc.id}')">+</button>
                    </div>
                </div>
                <div class="pc-short-info">
                    <div class="info-row">
                        <div class="info-label">CPU:</div>
                        <div class="info-value">${pc.cpu || 'N/A'}</div>
                    </div>
                    <div class="info-row">
                        <div class="info-label">RAM:</div>
                        <div class="info-value">${pc.ram_total_gb || 0} GB</div>
                    </div>
                    <div class="info-row">
                        <div class="info-label">Notes:</div>
                        <div id="notes-display-${pc.id}">${pc.notes || ''}</div>
                    </div>
                </div>
            `;
            
            // Extended info section (hidden by default)
            let extendedInfo = `
                <div id="extended-info-${pc.id}" class="pc-extended-info">
                    <div class="info-row">
                        <div class="info-label">Mainboard:</div>
                        <div class="info-value">${pc.mainboard || 'N/A'}</div>
                    </div>
                    <div class="info-row">
                        <div class="info-label">RAM Slots:</div>
                        <div class="info-value">${pc.ram_slots || 'N/A'}</div>
                    </div>
                    <div class="info-row">
                        <div class="info-label">Resolution:</div>
                        <div class="info-value">${pc.resolution || 'N/A'}</div>
                    </div>
                    <div class="info-row">
                        <div class="info-label">Serial:</div>
                        <div class="info-value">${pc.serial || 'N/A'}</div>
                    </div>
                    <div class="info-row">
                        <div class="info-label">Submitted:</div>
                        <div class="info-value">${pc.submitted_at || 'N/A'}</div>
                    </div>
                    <div class="info-row">
                        <div class="info-label">Notes:</div>
                        <div class="info-value">
                            <div class="notes-edit-container">
                                <textarea id="notes-input-${pc.id}" class="notes-input" placeholder="Add notes about this PC">${pc.notes || ''}</textarea>
                                <button onclick="saveNotes('${pc.id}')" class="save-notes-btn">Save Notes</button>
                            </div>
                        </div>
                    </div>
            `;
            
            // GPUs section
            if (pc.gpus && pc.gpus.length > 0) {
                extendedInfo += `
                    <div class="section-title">GPUs:</div>
                    ${pc.gpus.map(gpu => `
                        <div class="component-item">${gpu}</div>
                    `).join('')}
                `;
            }
            
            // RAM sticks section
            if (pc.ram_sticks && pc.ram_sticks.length > 0) {
                extendedInfo += `
                    <div class="section-title">RAM Sticks:</div>
                    ${pc.ram_sticks.map(stick => `
                        <div class="component-item">
                            ${stick.size_gb || 0} GB ${stick.type || ''} - ${stick.model || 'Unknown'}
                        </div>
                    `).join('')}
                `;
            }
            
            // Disks section
            if (pc.disks && pc.disks.length > 0) {
                extendedInfo += `
                    <div class="section-title">Disks:</div>
                    ${pc.disks.map(disk => `
                        <div class="component-item">
                            ${disk.size_gb || 0} GB - ${disk.model || 'Unknown'} (${disk.path || 'N/A'})
                        </div>
                    `).join('')}
                `;
            }
            
            extendedInfo += '</div>'; // Close extended info div
            
            tile.innerHTML = shortInfo + extendedInfo;
            return tile;
        }

        // Function to save notes for a PC
        async function saveNotes(pcId) {
            const notesInput = document.getElementById(`notes-input-${pcId}`);
            const notesDisplay = document.getElementById(`notes-display-${pcId}`);
            const notes = notesInput.value;
            
            try {
                // Submit the notes update using the new endpoint
                const response = await fetch('/update_notes', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        pc_id: pcId,
                        notes: notes
                    })
                });
                
                if (!response.ok) {
                    throw new Error('Failed to save notes');
                }
                
                // Update the display
                notesDisplay.textContent = notes;
                alert('Notes saved successfully!');
            } catch (error) {
                console.error('Error saving notes:', error);
                alert(`Error saving notes: ${error.message}`);
            }
        }

        // Function to delete a PC
        async function deletePC(pcId) {
            if (!confirm('Are you sure you want to delete this PC? This action cannot be undone.')) {
                return;
            }
            
            try {
                const response = await fetch(`/pc/${pcId}/delete`, {
                    method: 'DELETE'
                });
                
                if (!response.ok) {
                    throw new Error('Failed to delete PC');
                }
                
                // Reload the dashboard to reflect the changes
                loadPCDashboard();
                alert('PC deleted successfully!');
            } catch (error) {
                console.error('Error deleting PC:', error);
                alert(`Error deleting PC: ${error.message}`);
            }
        }

        // Main function to load all PCs and their details
        async function loadPCDashboard() {
            const pcGrid = document.getElementById('pc-grid');
            pcGrid.innerHTML = '<div class="loading">Loading PC data...</div>';
            
            try {
                // Fetch the list of all PCs
                const pcs = await fetchPCs();
                
                if (pcs.length === 0) {
                    pcGrid.innerHTML = '<div class="error">No PCs found in the database</div>';
                    return;
                }
                
                // Clear the loading message
                pcGrid.innerHTML = '';
                
                // For each PC, fetch its details and create a tile
                for (const pc of pcs) {
                    const pcDetails = await fetchPCDetails(pc.id);
                    if (pcDetails) {
                        const pcTile = createPCTile(pcDetails);
                        pcGrid.appendChild(pcTile);
                    }
                }
            } catch (error) {
                console.error('Error loading dashboard:', error);
                pcGrid.innerHTML = `<div class="error">Error loading dashboard: ${error.message}</div>`;
            }
        }

        // Load the dashboard when the page loads
        window.onload = loadPCDashboard;
    </script>
</body>
</html>
'''

def init_db():
    with open('schema.sql') as f:
        schema = f.read()
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(schema)
    conn.commit()
    conn.close()


def hash_serial(serial: str) -> str:
    return hashlib.sha256(serial.encode('utf-8')).hexdigest()


@app.route('/update_notes', methods=['POST'])
def update_notes():
    data = request.get_json()
    pc_id = data.get("pc_id", "")
    notes = data.get("notes", "")
    
    if not pc_id:
        return jsonify({"error": "Missing pc_id"}), 400

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Check if PC exists
    cur.execute("SELECT id FROM pc WHERE id = ?", (pc_id,))
    if not cur.fetchone():
        conn.close()
        return jsonify({"error": "PC not found"}), 404

    # Update only the notes field
    cur.execute("UPDATE pc SET notes = ? WHERE id = ?", (notes, pc_id))
    conn.commit()
    conn.close()

    return jsonify({"status": "success", "pc_id": pc_id})

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
        INSERT OR REPLACE INTO pc (id, host, serial, cpu, mainboard, ram_total_gb, ram_slots, resolution, notes, submitted_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
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
    
    # Get sorting and filtering parameters
    sort_by = request.args.get('sort_by', 'submitted_at')  # Default sort by date
    sort_order = request.args.get('sort_order', 'desc')  # Default newest first
    tag_filter = request.args.get('tag')  # Optional tag filter
    
    # Build query with optional tag filtering
    base_query = """
        SELECT DISTINCT p.id, p.host, p.cpu, p.ram_total_gb, p.submitted_at,
               GROUP_CONCAT(t.name) as tags,
               GROUP_CONCAT(t.color) as tag_colors
        FROM pc p
        LEFT JOIN pc_tag pt ON p.id = pt.pc_id
        LEFT JOIN tag t ON pt.tag_id = t.id
    """
    
    params = []
    if tag_filter:
        base_query += " WHERE t.name = ?"
        params.append(tag_filter)
    
    base_query += " GROUP BY p.id"
    
    # Add sorting
    if sort_by in ['submitted_at', 'host', 'cpu']:
        order_clause = f" ORDER BY p.{sort_by}"
        if sort_order.lower() == 'desc':
            order_clause += " DESC"
        else:
            order_clause += " ASC"
        base_query += order_clause
    
    cur.execute(base_query, params)
    rows = cur.fetchall()
    
    pcs = []
    for row in rows:
        pc_dict = dict(zip([column[0] for column in cur.description], row))
        # Parse tags
        if pc_dict['tags']:
            tag_names = pc_dict['tags'].split(',')
            tag_colors = pc_dict['tag_colors'].split(',')
            pc_dict['tags'] = [{'name': name, 'color': color} for name, color in zip(tag_names, tag_colors)]
        else:
            pc_dict['tags'] = []
        del pc_dict['tag_colors']
        pcs.append(pc_dict)
    
    conn.close()
    return jsonify(pcs)


@app.route('/pc/<pc_id>', methods=['GET'])
def get_pc_details(pc_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Main PC data
    cur.execute("SELECT id, host, serial, cpu, mainboard, ram_total_gb, ram_slots, resolution, notes, datetime(submitted_at, 'localtime') as submitted_at FROM pc WHERE id = ?", (pc_id,))
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

    # Tags data
    cur.execute("""
        SELECT t.id, t.name, t.color
        FROM tag t
        JOIN pc_tag pt ON t.id = pt.tag_id
        WHERE pt.pc_id = ?
        ORDER BY t.name
    """, (pc_id,))
    pc["tags"] = [dict(zip(["id", "name", "color"], r)) for r in cur.fetchall()]

    conn.close()
    return jsonify(pc)


@app.route('/pc/<pc_id>/delete', methods=['DELETE'])
def delete_pc(pc_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    try:
        # Check if PC exists
        cur.execute("SELECT id FROM pc WHERE id = ?", (pc_id,))
        if not cur.fetchone():
            conn.close()
            return jsonify({"error": "PC not found"}), 404

        # Delete related records first due to foreign key constraints
        cur.execute("DELETE FROM gpu WHERE pc_id = ?", (pc_id,))
        cur.execute("DELETE FROM ram_stick WHERE pc_id = ?", (pc_id,))
        cur.execute("DELETE FROM disk WHERE pc_id = ?", (pc_id,))
        
        # Delete the PC record
        cur.execute("DELETE FROM pc WHERE id = ?", (pc_id,))
        
        conn.commit()
        return jsonify({"status": "success", "message": "PC and all related data deleted successfully"})
    
    except sqlite3.Error as e:
        conn.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        conn.close()

# Tag management endpoints
@app.route('/tags', methods=['GET'])
def get_all_tags():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, name, color FROM tag ORDER BY name")
    tags = [dict(zip([column[0] for column in cur.description], row)) for row in cur.fetchall()]
    conn.close()
    return jsonify(tags)

@app.route('/tags', methods=['POST'])
def create_tag():
    data = request.get_json()
    name = data.get('name', '').strip()
    color = data.get('color', '#228BE6')
    
    if not name:
        return jsonify({"error": "Tag name is required"}), 400
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    try:
        cur.execute("INSERT INTO tag (name, color) VALUES (?, ?)", (name, color))
        tag_id = cur.lastrowid
        conn.commit()
        conn.close()
        return jsonify({"id": tag_id, "name": name, "color": color}), 201
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": "Tag name already exists"}), 409

@app.route('/tags/<int:tag_id>', methods=['DELETE'])
def delete_tag(tag_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Check if tag exists
    cur.execute("SELECT id FROM tag WHERE id = ?", (tag_id,))
    if not cur.fetchone():
        conn.close()
        return jsonify({"error": "Tag not found"}), 404
    
    # Delete tag (cascade will handle pc_tag relationships)
    cur.execute("DELETE FROM tag WHERE id = ?", (tag_id,))
    conn.commit()
    conn.close()
    
    return jsonify({"status": "success", "message": "Tag deleted successfully"})

@app.route('/pc/<pc_id>/tags', methods=['POST'])
def add_tag_to_pc(pc_id):
    data = request.get_json()
    tag_id = data.get('tag_id')
    
    if not tag_id:
        return jsonify({"error": "tag_id is required"}), 400
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Check if PC exists
    cur.execute("SELECT id FROM pc WHERE id = ?", (pc_id,))
    if not cur.fetchone():
        conn.close()
        return jsonify({"error": "PC not found"}), 404
    
    # Check if tag exists
    cur.execute("SELECT id FROM tag WHERE id = ?", (tag_id,))
    if not cur.fetchone():
        conn.close()
        return jsonify({"error": "Tag not found"}), 404
    
    try:
        cur.execute("INSERT INTO pc_tag (pc_id, tag_id) VALUES (?, ?)", (pc_id, tag_id))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Tag added to PC"})
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": "Tag already assigned to this PC"}), 409

@app.route('/pc/<pc_id>/tags/<int:tag_id>', methods=['DELETE'])
def remove_tag_from_pc(pc_id, tag_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Remove tag from PC
    cur.execute("DELETE FROM pc_tag WHERE pc_id = ? AND tag_id = ?", (pc_id, tag_id))
    
    if cur.rowcount == 0:
        conn.close()
        return jsonify({"error": "Tag not found on this PC"}), 404
    
    conn.commit()
    conn.close()
    
    return jsonify({"status": "success", "message": "Tag removed from PC"})

@app.route('/pc/<pc_id>/tags', methods=['GET'])
def get_pc_tags(pc_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    cur.execute("""
        SELECT t.id, t.name, t.color
        FROM tag t
        JOIN pc_tag pt ON t.id = pt.tag_id
        WHERE pt.pc_id = ?
        ORDER BY t.name
    """, (pc_id,))
    
    tags = [dict(zip([column[0] for column in cur.description], row)) for row in cur.fetchall()]
    conn.close()
    return jsonify(tags)

@app.route('/')
def dashboard():
    return render_template_string(DASHBOARD_TEMPLATE)


if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        init_db()
    app.run(host="0.0.0.0", port=5000)
