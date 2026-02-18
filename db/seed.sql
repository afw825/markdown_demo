-- ==========================================
-- Seed Data for operations schema
-- Source examples: data/sample/*.xlsx
-- ==========================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS operations;

-- Reset data for repeatable test runs
TRUNCATE TABLE
    operations.shipment,
    operations.inspection_event,
    operations.production_run,
    operations.lot,
    operations.inspector,
    operations.defect_type
RESTART IDENTITY CASCADE;

-- Master data
INSERT INTO operations.inspector (inspector_name, shift_preference)
VALUES
    ('A. Nguyen', 'Day Shift'),
    ('M. Patel', 'Night Shift');

INSERT INTO operations.defect_type (defect_id, severity)
VALUES
    ('BURR', 'Major'),
    ('CRACK', 'Major'),
    ('POR', 'Minor'),
    ('WELD', 'Critical'),
    ('SCR', 'Minor'),
    ('DIM', 'Critical');

-- Lot anchor records (normalized lot IDs)
INSERT INTO operations.lot (normalized_lot_id, part_number, production_date)
VALUES
    ('LOT-20251215-001', 'SW-5746-D', '2025-12-15'),
    ('LOT-20251217-002', 'SW-6145-D', '2025-12-17'),
    ('LOT-20251219-003', 'SW-8665-C', '2025-12-19'),
    ('LOT-20251220-002', 'SW-8644-B', '2025-12-20'),
    ('LOT-20251231-002', 'SW-4747-C', '2025-12-31'),
    ('LOT-20260102-001', 'SW-2706-D', '2026-01-02'),
    ('LOT-20260104-003', 'SW-7961-C', '2026-01-04'),
    ('LOT-20260106-001', 'SW-7688-D', '2026-01-06'),
    ('LOT-20260110-003', 'SW-4659-B', '2026-01-10'),
    ('LOT-20260112-001', 'SW-8091-A', '2026-01-12'),
    ('LOT-20260113-002', 'SW-2695-D', '2026-01-13'),
    ('LOT-20260115-001', 'SW-7729-D', '2026-01-15'),
    ('LOT-20260117-001', 'SW-3107-D', '2026-01-17'),
    ('LOT-20260118-001', 'SW-1250-C', '2026-01-18'),
    ('LOT-20260119-002', 'SW-8632-B', '2026-01-19'),
    ('LOT-20260121-002', 'SW-6055-D', '2026-01-21');

-- Production logs
INSERT INTO operations.production_run
    (lot_id, raw_lot_id, line_id, shift, units_planned, units_actual, downtime_minutes, primary_issue)
VALUES
    ((SELECT id FROM operations.lot WHERE normalized_lot_id = 'LOT-20251219-003'), 'Lot-20251219-003', 'Line 1', 'Swing', 500, 487, 13, 'Tool wear'),
    ((SELECT id FROM operations.lot WHERE normalized_lot_id = 'LOT-20251220-002'), 'L0T-20251220-002', 'Line 4', 'Swing', 300, 292, 0, NULL),
    ((SELECT id FROM operations.lot WHERE normalized_lot_id = 'LOT-20260102-001'), 'LOT 20260102 001', 'Line 4', 'Day', 200, 192, 16, NULL),
    ((SELECT id FROM operations.lot WHERE normalized_lot_id = 'LOT-20260104-003'), 'LOT-20260104-003', 'Line 4', 'Day', 400, 379, 13, 'Material shortage'),
    ((SELECT id FROM operations.lot WHERE normalized_lot_id = 'LOT-20260112-001'), 'LOT 20260112 001', 'Line 1', 'Swing', 400, 382, 44, NULL),
    ((SELECT id FROM operations.lot WHERE normalized_lot_id = 'LOT-20260113-002'), 'LOT-20260113-002', 'Line 3', 'Day', 400, 399, 6, NULL),
    ((SELECT id FROM operations.lot WHERE normalized_lot_id = 'LOT-20260115-001'), 'LOT 20260115 001', 'Line 1', 'Night', 200, 198, 48, 'Changeover delay');

-- Inspection logs
INSERT INTO operations.inspection_event
    (lot_id, inspector_id, defect_type_id, inspection_timestamp, qty_checked, qty_defects, disposition, notes)
VALUES
    (
        (SELECT id FROM operations.lot WHERE normalized_lot_id = 'LOT-20251215-001'),
        (SELECT id FROM operations.inspector WHERE inspector_name = 'A. Nguyen'),
        (SELECT id FROM operations.defect_type WHERE defect_id = 'DIM'),
        '2025-12-15 10:20:00',
        20,
        1,
        'Rework',
        'Out of tolerance dimension'
    ),
    (
        (SELECT id FROM operations.lot WHERE normalized_lot_id = 'LOT-20251217-002'),
        (SELECT id FROM operations.inspector WHERE inspector_name = 'M. Patel'),
        (SELECT id FROM operations.defect_type WHERE defect_id = 'CRACK'),
        '2025-12-22 14:00:00',
        20,
        4,
        'Rework',
        'Surface crack'
    ),
    (
        (SELECT id FROM operations.lot WHERE normalized_lot_id = 'LOT-20251220-002'),
        (SELECT id FROM operations.inspector WHERE inspector_name = 'M. Patel'),
        (SELECT id FROM operations.defect_type WHERE defect_id = 'WELD'),
        '2025-12-30 07:10:00',
        30,
        4,
        'Scrap',
        'Weld bead issue'
    ),
    (
        (SELECT id FROM operations.lot WHERE normalized_lot_id = 'LOT-20251231-002'),
        (SELECT id FROM operations.inspector WHERE inspector_name = 'M. Patel'),
        (SELECT id FROM operations.defect_type WHERE defect_id = 'WELD'),
        '2026-01-05 16:40:00',
        30,
        4,
        'Hold for MRB',
        'Weld bead issue'
    ),
    (
        (SELECT id FROM operations.lot WHERE normalized_lot_id = 'LOT-20260106-001'),
        (SELECT id FROM operations.inspector WHERE inspector_name = 'A. Nguyen'),
        NULL,
        '2026-01-15 08:20:00',
        25,
        0,
        NULL,
        NULL
    ),
    (
        (SELECT id FROM operations.lot WHERE normalized_lot_id = 'LOT-20260110-003'),
        (SELECT id FROM operations.inspector WHERE inspector_name = 'M. Patel'),
        (SELECT id FROM operations.defect_type WHERE defect_id = 'BURR'),
        '2026-01-14 14:40:00',
        20,
        1,
        'Rework',
        'Excess burr'
    ),
    (
        (SELECT id FROM operations.lot WHERE normalized_lot_id = 'LOT-20260117-001'),
        (SELECT id FROM operations.inspector WHERE inspector_name = 'A. Nguyen'),
        (SELECT id FROM operations.defect_type WHERE defect_id = 'POR'),
        '2026-01-25 09:10:00',
        10,
        1,
        'Rework',
        'Porosity'
    ),
    (
        (SELECT id FROM operations.lot WHERE normalized_lot_id = 'LOT-20260118-001'),
        (SELECT id FROM operations.inspector WHERE inspector_name = 'M. Patel'),
        (SELECT id FROM operations.defect_type WHERE defect_id = 'BURR'),
        '2026-01-23 07:00:00',
        50,
        2,
        'Use-as-is',
        'Excess burr'
    ),
    (
        (SELECT id FROM operations.lot WHERE normalized_lot_id = 'LOT-20260119-002'),
        (SELECT id FROM operations.inspector WHERE inspector_name = 'A. Nguyen'),
        NULL,
        '2026-01-19 08:20:00',
        25,
        0,
        NULL,
        NULL
    );

-- Shipping logs
INSERT INTO operations.shipment
    (lot_id, sales_order, customer, ship_date, carrier, bol_number, qty_shipped, ship_status)
VALUES
    (
        (SELECT id FROM operations.lot WHERE normalized_lot_id = 'LOT-20251219-003'),
        'SO-52588',
        'Midwest Conveyors',
        '2025-12-20',
        'UPS Freight',
        'BOL-787984',
        80,
        'Shipped'
    ),
    (
        (SELECT id FROM operations.lot WHERE normalized_lot_id = 'LOT-20260112-001'),
        'SO-37512',
        'Prairie Pumps',
        '2026-01-29',
        'XPO',
        'BOL-249382',
        61,
        'Shipped'
    ),
    (
        (SELECT id FROM operations.lot WHERE normalized_lot_id = 'LOT-20260106-001'),
        'SO-60788',
        'Midwest Conveyors',
        '2026-01-23',
        'XPO',
        'BOL-186353',
        100,
        'Shipped'
    ),
    (
        (SELECT id FROM operations.lot WHERE normalized_lot_id = 'LOT-20260121-002'),
        'SO-87464',
        'NorthStar Ag',
        '2026-01-25',
        'XPO',
        'BOL-156825',
        37,
        'On Hold'
    ),
    (
        (SELECT id FROM operations.lot WHERE normalized_lot_id = 'LOT-20260118-001'),
        'SO-90110',
        'NorthStar Ag',
        '2026-01-21',
        'Local Truck',
        'BOL-719513',
        120,
        'Shipped'
    );

COMMIT;
