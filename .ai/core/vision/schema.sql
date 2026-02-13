-- ═══════════════════════════════════════════════════════════════════════════════
-- Visual Cortex Schema V2.0 — Cognitive Neuro-Vision
-- Production-grade schema with temporal memory, code metrics, and telemetry
-- Optimized for read-heavy access by multiple agents (WAL mode expected)
-- ═══════════════════════════════════════════════════════════════════════════════

-- ┌─────────────────────────────────────────────────────────────────────────────┐
-- │ CORE GRAPH TABLES                                                          │
-- └─────────────────────────────────────────────────────────────────────────────┘

CREATE TABLE IF NOT EXISTS meta (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS nodes (
    id TEXT PRIMARY KEY,              -- e.g. "app/main.py::MyClass::my_method"
    type TEXT NOT NULL,               -- file | class | function | variable | import
    path TEXT NOT NULL,               -- File path relative to project root
    name TEXT NOT NULL,               -- Short name (e.g. "my_method")
    parent_id TEXT,                   -- Parent node (file for class, class for method)
    start_line INTEGER,
    end_line INTEGER,
    content_hash TEXT,                -- SHA256 for change detection
    metadata JSON DEFAULT '{}',       -- Docstrings, args, decorators, bases
    last_scanned TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(parent_id) REFERENCES nodes(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS edges (
    source TEXT NOT NULL,
    target TEXT NOT NULL,
    type TEXT NOT NULL,               -- imports | defines | calls | inherits | reads | writes
    weight REAL DEFAULT 1.0,
    metadata JSON DEFAULT '{}',
    PRIMARY KEY (source, target, type)
    -- No FKs: targets may reference external modules not in nodes table
);

-- ┌─────────────────────────────────────────────────────────────────────────────┐
-- │ CODE QUALITY METRICS                                                       │
-- └─────────────────────────────────────────────────────────────────────────────┘

CREATE TABLE IF NOT EXISTS code_metrics (
    node_id TEXT PRIMARY KEY,
    cyclomatic_complexity INTEGER DEFAULT 0,
    cognitive_complexity INTEGER DEFAULT 0,
    lines_of_code INTEGER DEFAULT 0,
    num_parameters INTEGER DEFAULT 0,
    nesting_depth INTEGER DEFAULT 0,
    coupling_in INTEGER DEFAULT 0,       -- How many nodes depend on this
    coupling_out INTEGER DEFAULT 0,      -- How many nodes this depends on
    risk_score REAL DEFAULT 0.0,         -- 0-100 aggregate risk score
    last_computed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(node_id) REFERENCES nodes(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS code_smells (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id TEXT NOT NULL,
    smell_type TEXT NOT NULL,            -- god_class | long_method | deep_nesting | circular_import | high_coupling
    severity TEXT NOT NULL DEFAULT 'warning',  -- info | warning | critical
    description TEXT,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(node_id) REFERENCES nodes(id) ON DELETE CASCADE
);

-- ┌─────────────────────────────────────────────────────────────────────────────┐
-- │ TEMPORAL MEMORY (Evolution Tracking)                                       │
-- └─────────────────────────────────────────────────────────────────────────────┘

CREATE TABLE IF NOT EXISTS scan_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_root TEXT NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    duration_ms INTEGER,
    total_nodes INTEGER DEFAULT 0,
    total_edges INTEGER DEFAULT 0,
    total_files INTEGER DEFAULT 0,
    total_smells INTEGER DEFAULT 0,
    status TEXT DEFAULT 'running'        -- running | completed | failed
);

CREATE TABLE IF NOT EXISTS node_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_id INTEGER NOT NULL,
    node_id TEXT NOT NULL,
    content_hash TEXT,
    metrics_snapshot JSON DEFAULT '{}',   -- Frozen copy of metrics at scan time
    change_type TEXT,                     -- added | modified | removed | unchanged
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(scan_id) REFERENCES scan_history(id) ON DELETE CASCADE
);

-- ┌─────────────────────────────────────────────────────────────────────────────┐
-- │ REAL-TIME TELEMETRY                                                        │
-- └─────────────────────────────────────────────────────────────────────────────┘

CREATE TABLE IF NOT EXISTS telemetry_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id TEXT NOT NULL,
    event_type TEXT NOT NULL,            -- execution | error | variable_update | warning
    metadata JSON DEFAULT '{}',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_id TEXT                       -- Groups events from same agent session
);

-- ┌─────────────────────────────────────────────────────────────────────────────┐
-- │ PERFORMANCE INDICES                                                        │
-- └─────────────────────────────────────────────────────────────────────────────┘

-- Core graph indices
CREATE INDEX IF NOT EXISTS idx_nodes_type ON nodes(type);
CREATE INDEX IF NOT EXISTS idx_nodes_path ON nodes(path);
CREATE INDEX IF NOT EXISTS idx_nodes_name ON nodes(name);
CREATE INDEX IF NOT EXISTS idx_nodes_parent ON nodes(parent_id);
CREATE INDEX IF NOT EXISTS idx_edges_source ON edges(source);
CREATE INDEX IF NOT EXISTS idx_edges_target ON edges(target);
CREATE INDEX IF NOT EXISTS idx_edges_type ON edges(type);
CREATE INDEX IF NOT EXISTS idx_edges_source_type ON edges(source, type);
CREATE INDEX IF NOT EXISTS idx_edges_target_type ON edges(target, type);

-- Metrics indices
CREATE INDEX IF NOT EXISTS idx_metrics_risk ON code_metrics(risk_score DESC);
CREATE INDEX IF NOT EXISTS idx_smells_type ON code_smells(smell_type);
CREATE INDEX IF NOT EXISTS idx_smells_severity ON code_smells(severity);
CREATE INDEX IF NOT EXISTS idx_smells_node ON code_smells(node_id);

-- Temporal indices
CREATE INDEX IF NOT EXISTS idx_scan_history_status ON scan_history(status);
CREATE INDEX IF NOT EXISTS idx_snapshots_scan ON node_snapshots(scan_id);
CREATE INDEX IF NOT EXISTS idx_snapshots_node ON node_snapshots(node_id);
CREATE INDEX IF NOT EXISTS idx_snapshots_change ON node_snapshots(change_type);

-- Telemetry indices
CREATE INDEX IF NOT EXISTS idx_telemetry_node ON telemetry_events(node_id);
CREATE INDEX IF NOT EXISTS idx_telemetry_type ON telemetry_events(event_type);
CREATE INDEX IF NOT EXISTS idx_telemetry_time ON telemetry_events(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_telemetry_session ON telemetry_events(session_id);
