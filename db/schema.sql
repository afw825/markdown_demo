-- ==========================================
-- 1. Schema & Setup
-- ==========================================
CREATE SCHEMA IF NOT EXISTS operations;

-- ==========================================
-- 2. Master Data Entities
-- ==========================================

-- Table: Inspector
CREATE TABLE operations.inspector (
    id SERIAL PRIMARY KEY,
    inspector_name VARCHAR(100) NOT NULL,
    shift_preference VARCHAR(50),
    
    CONSTRAINT uq_inspector_name UNIQUE (inspector_name)
);

-- Table: Defect_Type
-- Updated: 'defect_code' renamed to 'defect_id'
CREATE TABLE operations.defect_type (
    id SERIAL PRIMARY KEY,
    defect_id VARCHAR(20) NOT NULL, -- e.g., 'BURR', 'WELD'
    severity VARCHAR(20) CHECK (severity IN ('Minor', 'Major', 'Critical', 'Cosmetic')),
    
    CONSTRAINT uq_defect_id UNIQUE (defect_id)
);

-- Table: Lot
CREATE TABLE operations.lot (
    id BIGSERIAL PRIMARY KEY,
    normalized_lot_id VARCHAR(50) NOT NULL,
    part_number VARCHAR(50) NOT NULL,
    production_date DATE NOT NULL,
    
    CONSTRAINT uq_lot_normalized_id UNIQUE (normalized_lot_id)
);

-- ==========================================
-- 3. Transactional Entities
-- ==========================================

-- Table: Production_Run
CREATE TABLE operations.production_run (
    id SERIAL PRIMARY KEY,
    lot_id BIGINT NOT NULL,
    raw_lot_id VARCHAR(100),
    line_id VARCHAR(50),
    shift VARCHAR(20) CHECK (shift IN ('Day', 'Swing', 'Night')),
    units_planned INTEGER,
    units_actual INTEGER,
    downtime_minutes INTEGER DEFAULT 0,
    primary_issue TEXT,
    
    CONSTRAINT fk_prod_lot_id FOREIGN KEY (lot_id) 
        REFERENCES operations.lot(id) 
        ON DELETE CASCADE,

    CONSTRAINT uq_prod_lot_id UNIQUE (lot_id) 
);

-- Table: Inspection_Event
CREATE TABLE operations.inspection_event (
    id SERIAL PRIMARY KEY,
    lot_id BIGINT NOT NULL,
    inspector_id INTEGER NOT NULL,
    defect_type_id INTEGER, -- Links to defect_type.id (Surrogate Key)
    inspection_timestamp TIMESTAMP NOT NULL,
    qty_checked INTEGER NOT NULL DEFAULT 0,
    qty_defects INTEGER NOT NULL DEFAULT 0,
    disposition VARCHAR(50), 
    notes TEXT,

    -- Data Integrity Checks
    CONSTRAINT chk_insp_defects_positive CHECK (qty_defects >= 0),
    CONSTRAINT chk_insp_checked_positive CHECK (qty_checked >= 0),
    CONSTRAINT chk_defects_lte_checked CHECK (qty_defects <= qty_checked),

    -- FKs with Cascade
    CONSTRAINT fk_insp_lot_id FOREIGN KEY (lot_id) 
        REFERENCES operations.lot(id) 
        ON DELETE CASCADE,
        
    CONSTRAINT fk_insp_inspector_id FOREIGN KEY (inspector_id) 
        REFERENCES operations.inspector(id) 
        ON DELETE CASCADE,
        
    CONSTRAINT fk_insp_defect_id FOREIGN KEY (defect_type_id) 
        REFERENCES operations.defect_type(id) 
        ON DELETE CASCADE
);

-- Table: Shipment
CREATE TABLE operations.shipment (
    id SERIAL PRIMARY KEY,
    lot_id BIGINT NOT NULL,
    sales_order VARCHAR(50),
    customer VARCHAR(100),
    ship_date DATE,
    carrier VARCHAR(100),
    bol_number VARCHAR(50),
    qty_shipped INTEGER,
    ship_status VARCHAR(50),

    CONSTRAINT fk_ship_lot_id FOREIGN KEY (lot_id) 
        REFERENCES operations.lot(id) 
        ON DELETE CASCADE
);

-- ==========================================
-- 4. Performance Indexes
-- ==========================================
CREATE INDEX idx_prod_lot_id ON operations.production_run(lot_id);
CREATE INDEX idx_insp_lot_id ON operations.inspection_event(lot_id);
CREATE INDEX idx_ship_lot_id ON operations.shipment(lot_id);
CREATE INDEX idx_insp_date ON operations.inspection_event(inspection_timestamp);

-- ==========================================
-- 5. User Story Implementation (View)
-- ==========================================

CREATE OR REPLACE VIEW operations.vw_recurring_defect_analysis AS
WITH DefectStats AS (
    SELECT 
        dt.defect_id, -- Updated from defect_code
        dt.severity,
        COUNT(DISTINCT ie.lot_id) AS impacted_lot_count,
        MIN(ie.inspection_timestamp) AS first_detected,
        MAX(ie.inspection_timestamp) AS last_detected,
        SUM(ie.qty_defects) AS total_defects,
        EXTRACT(DAY FROM (MAX(ie.inspection_timestamp) - MIN(ie.inspection_timestamp))) AS days_span
    FROM 
        operations.inspection_event ie
    JOIN 
        operations.defect_type dt ON ie.defect_type_id = dt.id
    WHERE 
        ie.qty_defects > 0 
    GROUP BY 
        dt.defect_id, dt.severity
)
SELECT 
    *,
    CASE 
        WHEN impacted_lot_count > 1 AND days_span >= 7 THEN 'Recurring - Critical'
        WHEN impacted_lot_count > 1 AND days_span < 7 THEN 'Recurring - High Frequency'
        WHEN impacted_lot_count = 1 THEN 'Isolated Incident'
        ELSE 'Insufficient Data' 
    END AS trend_classification
FROM 
    DefectStats
WHERE
    impacted_lot_count > 1 
ORDER BY 
    impacted_lot_count DESC,
    last_detected DESC;

-- ==========================================
-- 6. Reference Data Initialization
-- ==========================================

-- Seed Defect Types (using defect_id)
INSERT INTO operations.defect_type (defect_id, severity) VALUES
('BURR', 'Major'),
('CRACK', 'Major'),
('POR',  'Minor'),
('WELD', 'Critical'),
('SCR',  'Minor')
ON CONFLICT (defect_id) DO NOTHING;

INSERT INTO operations.inspector (inspector_name, shift_preference) VALUES
('A. Nguyen', 'Day Shift'), 
('M. Patel', 'Night Shift')
ON CONFLICT (inspector_name) DO NOTHING;
