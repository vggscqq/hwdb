CREATE TABLE IF NOT EXISTS pc (
    id TEXT PRIMARY KEY, -- sha256(serial)
    host TEXT,
    serial TEXT,
    cpu TEXT,
    mainboard TEXT,
    ram_total_gb INTEGER,
    ram_slots TEXT,
    resolution TEXT,
    notes TEXT,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS gpu (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pc_id TEXT,
    name TEXT,
    FOREIGN KEY(pc_id) REFERENCES pc(id)
);

CREATE TABLE IF NOT EXISTS ram_stick (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pc_id TEXT,
    size_gb INTEGER,
    type TEXT,
    model TEXT,
    FOREIGN KEY(pc_id) REFERENCES pc(id)
);

CREATE TABLE IF NOT EXISTS disk (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pc_id TEXT,
    size_gb INTEGER,
    model TEXT,
    serial TEXT,
    path TEXT,
    FOREIGN KEY(pc_id) REFERENCES pc(id)
);

CREATE TABLE IF NOT EXISTS tag (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    color TEXT DEFAULT '#228BE6'
);

CREATE TABLE IF NOT EXISTS pc_tag (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pc_id TEXT,
    tag_id INTEGER,
    FOREIGN KEY(pc_id) REFERENCES pc(id) ON DELETE CASCADE,
    FOREIGN KEY(tag_id) REFERENCES tag(id) ON DELETE CASCADE,
    UNIQUE(pc_id, tag_id)
);

