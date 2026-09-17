# Banking Microservices Architecture Documentation

This document provides a comprehensive technical overview and walkthrough of the **Banking Withdrawal POC** architecture, covering both the **High-Level Design (HLD)** and **Low-Level Design (LLD)**.

The editable Draw.io architecture diagram is located at:
* [`architecture.drawio`](file:///c:/Users/Sonux/Desktop/banking-dapr-poc/architecture.drawio)

---

## 1. High-Level Design (HLD) — Container & Network Topology

The system comprises 6 containers operating over an isolated Docker bridge network (`banking-net`). It utilizes the **Dapr Sidecar Pattern** (`network_mode: "service:..."`) to achieve secure, zero-hardcoded-IP communication between microservices.

```
[Client (cURL / Postman)]
       │
       │ [1] POST /api/v1/transactions/withdraw (Port 8081)
       ▼
┌───────────────────────────────────────────────┐
│ Transaction Pod (Localhost Network)           │
│                                               │
│   ┌───────────────────────────────────────┐   │
│   │ transaction-app (Spring Boot :8081)   │   │
│   └───────────────────┬───────────────────┘   │
│                       │                       │
│                       │ [2] localhost:3500    │
│                       ▼                       │
│   ┌───────────────────────────────────────┐   │
│   │ transaction-dapr (Sidecar :3500)      │───┼──────────┐
│   └───────────────────────────────────────┘   │          │
└───────────────────────────────────────────────┘          │
                                                           │ (lookup)
                                                           ▼
                                                ┌─────────────────────┐
                                                │ dapr-placement      │
                                                │ Service Discovery   │
                                                │ Port 50005          │
                                                └─────────────────────┘
                                                           │
                                                           │ [3] Dapr Invocation Mesh
                                                           │     (gRPC over banking-net)
                                                           ▼
┌───────────────────────────────────────────────┐
│ Accounting Pod (Vault / Localhost Network)    │
│                                               │
│   ┌───────────────────────────────────────┐   │
│   │ accounting-dapr (Sidecar :3501)       │◀──┘
│   └───────────────────┬───────────────────┘
│                       │
│                       │ [4] localhost:8082
│                       ▼
│   ┌───────────────────────────────────────┐
│   │ accounting-app (Core Engine :8082)    │
│   └───────────────────┬───────────────────┘
└───────────────────────┼───────────────────────┘
                        │
                        │ [5] SQL UPDATE & Row Lock (Port 5432)
                        ▼
┌───────────────────────────────────────────────┐
│ banking-postgres (PostgreSQL 15 :5432)        │
│ • accounts (balance >= 0)                     │
│ • withdrawal_transactions                     │
└───────────────────────────────────────────────┘
```

### Component Details

| Container | Image / Tech | Port(s) | Network Mode | Purpose |
|---|---|---|---|---|
| `banking-postgres` | `postgres:15-alpine` | `5432` | `banking-net` | Dedicated database. Enforces constraints (`CHECK balance >= 0`) and stores ledger transactions. |
| `dapr-placement` | `daprio/dapr:1.13.0` | `50005` | `banking-net` | Manages actor placement and service discovery directory. |
| `transaction-app` | Spring Boot (Java 17) | `8081` | `banking-net` | Public REST API. Validates requests and delegates to its local sidecar. |
| `transaction-dapr` | `daprio/daprd:1.13.0` | `3500` | `service:transaction-app` | Sidecar co-located with `transaction-app`. Handles mTLS, discovery, and gRPC routing. |
| `accounting-app` | Spring Boot (Java 17) | `8082` | `banking-net` | Core accounting and ledger engine. Executes atomic SQL balance deduction. Not exposed publicly. |
| `accounting-dapr` | `daprio/daprd:1.13.0` | `3501` | `service:accounting-app` | Sidecar co-located with `accounting-app`. Receives service calls and forwards to `:8082`. |

---

## 2. Low-Level Design (LLD) — Execution Pipeline

The execution flow represents the end-to-end lifecycle of a single withdrawal request.

```
[1. REST Ingestion] ──validate──> [2. Service Invocation] ──Dapr gRPC──> [3. Validation & Idempotency]
                                                                                   │
                                                                                proceed
                                                                                   │
                                                                                   ▼
[TABLE: withdrawal_transactions] <──INSERT Audit── [5. Audit Trail] <──1 row── [4. Atomic Balance Deduct]
            │                                                                      │
            └─────────────── FK: account_id ───────────────────────────────────────┴──> [TABLE: accounts]
```

### Step 1: REST Ingestion (`TransactionController`)
- **Endpoint:** `POST /api/v1/transactions/withdraw`
- **Request Body (DTO):**
  ```json
  {
    "accountId": "ACC001",
    "amount": 500.00,
    "currency": "INR",
    "requestId": "req-9901-abcd"
  }
  ```
- **Validations:**
  - `amount > 0`
  - `currency == "INR"`
  - `requestId != null && !requestId.isBlank()`

### Step 2: Dapr Service Invocation (`TransactionService`)
- Invokes the local Dapr sidecar over HTTP:
  ```http
  POST http://localhost:3500/v1.0/invoke/accounting-service/method/accounts/withdraw
  ```
- Dapr resolves `accounting-service` via `dapr-placement` and invokes the remote method over encrypted gRPC.

### Step 3: Validation & Idempotency Gate (`AccountingService`)
Runs within `@Transactional`:
1. **Idempotency Gate:**
   - Calls `txRepo.findByRequestId(req.requestId)`.
   - **If found:** Returns cached receipt immediately (HTTP 200). Balance is **never** deducted twice.
2. **Account Existence Gate:**
   - Calls `accountRepo.findByAccountId(req.accountId)`.
   - **If not found:** Throws `AccountNotFoundException` (HTTP 404).

### Step 4: Atomic Balance Deduction (`AccountRepository`)
- **SQL Atomic Update:**
  ```sql
  UPDATE accounts
  SET balance = balance - :amount
  WHERE account_id = :accountId AND balance >= :amount;
  ```
- **Concurrency Protection:**
  - Row-level lock held by PostgreSQL during update.
  - If balance < amount, 0 rows match $\rightarrow$ throws `InsufficientBalanceException` (HTTP 400).
  - If balance >= amount, 1 row updated $\rightarrow$ proceeds to Step 5.

### Step 5: Audit Trail & Final Response (`TransactionRepository`)
- Saves immutable audit log to `withdrawal_transactions`:
  ```sql
  INSERT INTO withdrawal_transactions (transaction_id, request_id, account_id, amount, currency, status, remaining_balance) ...
  ```
- Returns `WithdrawalResponse` with HTTP 200:
  ```json
  {
    "transactionId": "TX-5501",
    "status": "SUCCESS",
    "remainingBalance": 4500.00
  }
  ```

---

## 3. Database Schemas

```sql
-- Core balances table
CREATE TABLE accounts (
    id BIGSERIAL PRIMARY KEY,
    account_id VARCHAR(50) UNIQUE NOT NULL,
    balance NUMERIC(15, 2) NOT NULL CHECK (balance >= 0),
    currency CHAR(3) NOT NULL DEFAULT 'INR',
    version BIGINT NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Immutable audit ledger
CREATE TABLE withdrawal_transactions (
    id BIGSERIAL PRIMARY KEY,
    transaction_id VARCHAR(100) UNIQUE NOT NULL,
    request_id VARCHAR(100) UNIQUE NOT NULL, -- Enforces idempotency at DB layer
    account_id VARCHAR(50) NOT NULL REFERENCES accounts(account_id),
    amount NUMERIC(15, 2) NOT NULL,
    currency CHAR(3) NOT NULL DEFAULT 'INR',
    status VARCHAR(20) NOT NULL,
    reason VARCHAR(255),
    remaining_balance NUMERIC(15, 2),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

---

## 4. Key Engineering Guarantees

1. **Zero Hardcoded IPs:** Service discovery, connection retries, and network isolation are fully offloaded to Dapr sidecars.
2. **Zero Race Conditions:** The atomic `UPDATE ... WHERE balance >= :amount` SQL clause eliminates negative balance conditions even under massive concurrent spikes.
3. **Strict Idempotency:** Client-supplied `requestId` is checked in application memory and enforced as a `UNIQUE` constraint in the database.
