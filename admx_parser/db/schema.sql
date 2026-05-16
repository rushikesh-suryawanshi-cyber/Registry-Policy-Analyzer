CREATE TABLE IF NOT EXISTS policies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    class_type TEXT,
    key TEXT,
    value_name TEXT,
    display_name TEXT,
    explain_text TEXT,
    gpo_path TEXT,
    enabled_value INTEGER,
    disabled_value INTEGER,
    min_value INTEGER,
    max_value INTEGER
);

CREATE INDEX IF NOT EXISTS idx_policies_name ON policies(name);
CREATE INDEX IF NOT EXISTS idx_policies_class_type ON policies(class_type);
CREATE INDEX IF NOT EXISTS idx_policies_key ON policies(key);

CREATE TABLE IF NOT EXISTS registry_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    policy_id INTEGER NOT NULL,
    key TEXT NOT NULL,
    value_name TEXT,
    FOREIGN KEY (policy_id) REFERENCES policies (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_registry_entries_policy_id ON registry_entries(policy_id);
CREATE INDEX IF NOT EXISTS idx_registry_entries_key ON registry_entries(key);

CREATE TABLE IF NOT EXISTS policy_values (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    policy_id INTEGER NOT NULL,
    type TEXT NOT NULL, -- e.g., 'enum', 'enabled_list', 'disabled_list', 'element'
    display_name TEXT,
    value_name TEXT,
    value INTEGER,
    element_id TEXT,
    required TEXT,
    min_value TEXT,
    max_value TEXT,
    FOREIGN KEY (policy_id) REFERENCES policies (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_policy_values_policy_id ON policy_values(policy_id);

CREATE TABLE IF NOT EXISTS policy_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    policy_id INTEGER NOT NULL,
    tag TEXT NOT NULL,
    FOREIGN KEY (policy_id) REFERENCES policies (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_policy_tags_policy_id ON policy_tags(policy_id);
CREATE INDEX IF NOT EXISTS idx_policy_tags_tag ON policy_tags(tag);

-- FTS5 Virtual Table for searching
CREATE VIRTUAL TABLE IF NOT EXISTS policies_fts USING fts5(
    name,
    display_name,
    explain_text,
    gpo_path,
    content='policies',
    content_rowid='id'
);

-- Triggers to keep FTS table in sync with policies table
CREATE TRIGGER IF NOT EXISTS policies_ai AFTER INSERT ON policies BEGIN
  INSERT INTO policies_fts(rowid, name, display_name, explain_text, gpo_path) 
  VALUES (new.id, new.name, new.display_name, new.explain_text, new.gpo_path);
END;

CREATE TRIGGER IF NOT EXISTS policies_ad AFTER DELETE ON policies BEGIN
  INSERT INTO policies_fts(policies_fts, rowid, name, display_name, explain_text, gpo_path) 
  VALUES('delete', old.id, old.name, old.display_name, old.explain_text, old.gpo_path);
END;

CREATE TRIGGER IF NOT EXISTS policies_au AFTER UPDATE ON policies BEGIN
  INSERT INTO policies_fts(policies_fts, rowid, name, display_name, explain_text, gpo_path) 
  VALUES('delete', old.id, old.name, old.display_name, old.explain_text, old.gpo_path);
  INSERT INTO policies_fts(rowid, name, display_name, explain_text, gpo_path) 
  VALUES (new.id, new.name, new.display_name, new.explain_text, new.gpo_path);
END;
