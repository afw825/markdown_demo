-- Sample Query 1

-- Seed Inspectors
INSERT INTO operations.inspector (inspector_name, shift_preference) VALUES
('A. Nguyen', 'Day Shift'), 
('M. Patel', 'Night Shift')
ON CONFLICT (inspector_name) DO NOTHING;

-- Seed Defect Types (using defect_id, no description)
INSERT INTO operations.defect_type (defect_id, severity) VALUES
('BURR', 'Major'),
('CRACK', 'Major'),
('POR',  'Minor'),
('WELD', 'Critical'),
('SCR',  'Minor')
ON CONFLICT (defect_id) DO NOTHING;

-- Sample Query 2:

-- Step A: Create a Lot (The Anchor)
INSERT INTO operations.lot (normalized_lot_id, part_number, production_date)
VALUES ('LOT-20260101-001', 'SW-9925-C', '2026-01-01');

-- Step B: Create a Production Run for that Lot
-- We subquery the lot.id to link them dynamically
INSERT INTO operations.production_run 
(lot_id, raw_lot_id, line_id, shift, units_planned, units_actual, primary_issue)
VALUES (
    (SELECT id FROM operations.lot WHERE normalized_lot_id = 'LOT-20260101-001'), 
    'L0T-20260101-001', -- Raw typo version
    'Line 1', 
    'Day', 
    500, 
    480, 
    'None'
);

-- Step C: Create an Inspection Event (Links Lot + Inspector + Defect)
INSERT INTO operations.inspection_event 
(lot_id, inspector_id, defect_type_id, inspection_timestamp, qty_checked, qty_defects, disposition)
VALUES (
    (SELECT id FROM operations.lot WHERE normalized_lot_id = 'LOT-20260101-001'),
    (SELECT id FROM operations.inspector WHERE inspector_name = 'A. Nguyen'),
    (SELECT id FROM operations.defect_type WHERE defect_id = 'BURR'),
    '2026-01-02 10:00:00',
    50, 
    2, 
    'Rework'
);

-- Step D: Create a Shipment
INSERT INTO operations.shipment 
(lot_id, sales_order, customer, ship_date, qty_shipped, ship_status)
VALUES (
    (SELECT id FROM operations.lot WHERE normalized_lot_id = 'LOT-20260101-001'),
    'SO-1001', 
    'Acme Corp', 
    '2026-01-05', 
    478, 
    'Shipped'
);
