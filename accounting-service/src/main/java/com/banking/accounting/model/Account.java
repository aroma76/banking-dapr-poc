package com.banking.accounting.model;

import jakarta.persistence.*;
import lombok.*;

import java.math.BigDecimal;

/**
 * Represents a bank account.
 *
 * Concurrency note: balance is deducted atomically via a single UPDATE statement
 * in AccountRepository that includes a WHERE balance >= :amount guard.
 * This prevents negative balances without requiring Java-level pessimistic locking.
 *
 * The version column is present in the schema for auditability but is not used
 * for optimistic locking in this POC (atomic UPDATE provides the concurrency safety).
 */
@Entity
@Table(name = "accounts")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Account {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "account_id", nullable = false, unique = true)
    private String accountId;

    @Column(name = "balance", nullable = false, precision = 15, scale = 2)
    private BigDecimal balance;

    @Column(name = "currency", nullable = false, length = 3)
    private String currency;

    @Column(name = "version", nullable = false)
    private Long version;
}
