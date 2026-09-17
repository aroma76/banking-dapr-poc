package com.banking.accounting.model;

import jakarta.persistence.*;
import lombok.*;

import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * Records every withdrawal attempt — both successful and failed.
 *
 * Idempotency: request_id has a UNIQUE constraint. If the same requestId is
 * submitted twice, the second INSERT will fail at the DB level, guaranteeing
 * that the balance is never deducted twice for the same logical request.
 */
@Entity
@Table(name = "withdrawal_transactions")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class WithdrawalTransaction {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "transaction_id", nullable = false, unique = true)
    private String transactionId;

    @Column(name = "request_id", nullable = false, unique = true)
    private String requestId;

    @Column(name = "account_id", nullable = false)
    private String accountId;

    @Column(name = "amount", nullable = false, precision = 15, scale = 2)
    private BigDecimal amount;

    @Column(name = "currency", length = 3)
    private String currency;

    @Column(name = "status", nullable = false, length = 20)
    private String status; // SUCCESS or FAILED

    @Column(name = "reason", length = 100)
    private String reason; // null on SUCCESS; e.g. INSUFFICIENT_BALANCE, ACCOUNT_NOT_FOUND

    @Column(name = "remaining_balance", precision = 15, scale = 2)
    private BigDecimal remainingBalance; // null on FAILED

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }
}
