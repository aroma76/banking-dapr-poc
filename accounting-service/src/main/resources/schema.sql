-- ============================================================
-- Banking Withdrawal POC — Database Schema
-- ============================================================

CREATE TABLE IF NOT EXISTS accounts (
    id          BIGSERIAL       PRIMARY KEY,
    account_id  VARCHAR(50)     NOT NULL UNIQUE,
    balance     NUMERIC(15, 2)  NOT NULL CHECK (balance >= 0),
    currency    CHAR(3)         NOT NULL,
    version     BIGINT          NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS withdrawal_transactions (
    id              BIGSERIAL       PRIMARY KEY,
    transaction_id  VARCHAR(100)    NOT NULL UNIQUE,
    request_id      VARCHAR(100)    NOT NULL UNIQUE,
    account_id      VARCHAR(50)     NOT NULL,
    amount          NUMERIC(15, 2)  NOT NULL,
    currency        CHAR(3),
    status          VARCHAR(20)     NOT NULL,
    reason          VARCHAR(100),
    remaining_balance NUMERIC(15, 2),
    created_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_wt_account_id ON withdrawal_transactions (account_id);
