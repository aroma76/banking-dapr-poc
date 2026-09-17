-- ============================================================
-- Banking Withdrawal POC — Seed Data
-- ============================================================

INSERT INTO accounts (account_id, balance, currency)
VALUES
    ('ACC001', 5000.00, 'INR'),
    ('ACC002', 10000.00, 'INR')
ON CONFLICT (account_id) DO NOTHING;
