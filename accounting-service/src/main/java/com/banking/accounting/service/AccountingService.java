package com.banking.accounting.service;

import com.banking.accounting.dto.WithdrawalRequest;
import com.banking.accounting.dto.WithdrawalResponse;
import com.banking.accounting.model.Account;
import com.banking.accounting.model.WithdrawalTransaction;
import com.banking.accounting.repository.AccountRepository;
import com.banking.accounting.repository.WithdrawalTransactionRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Optional;
import java.util.UUID;

/**
 * AccountingService — core business logic for withdrawal processing.
 *
 * === Idempotency ===
 * Each request carries a client-provided requestId. Before processing:
 *   1. Check if requestId already exists in withdrawal_transactions.
 *   2. If yes → return the stored result (no double deduction).
 *   3. If no  → process the withdrawal and store the result.
 * The DB UNIQUE constraint on request_id is the final race-condition guard
 * for concurrent duplicate requests.
 *
 * === Concurrency (different requests, same account) ===
 * Balance deduction uses a single atomic UPDATE:
 *   UPDATE accounts SET balance = balance - :amount WHERE account_id = :accountId AND balance >= :amount
 * PostgreSQL serializes concurrent UPDATEs on the same row.
 * The WHERE guard prevents a negative balance without any Java-level locking.
 * If rowsAffected == 0 → account had insufficient balance.
 *
 * === Transaction Boundary ===
 * The entire withdraw() method runs in a single DB transaction:
 *   BEGIN → check account → atomic UPDATE → INSERT transaction record → COMMIT
 * A failure at any step causes a ROLLBACK, leaving the DB consistent.
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class AccountingService {

    private final AccountRepository accountRepository;
    private final WithdrawalTransactionRepository transactionRepository;

    @Transactional
    public WithdrawalResponse processWithdrawal(WithdrawalRequest request) {
        log.info("[AccountingService] Processing withdrawal - requestId={}, accountId={}, amount={}",
                request.getRequestId(), request.getAccountId(), request.getAmount());

        // --- Idempotency check ---
        Optional<WithdrawalTransaction> existing = transactionRepository.findByRequestId(request.getRequestId());
        if (existing.isPresent()) {
            log.info("[AccountingService] Duplicate request detected - requestId={}, returning stored result",
                    request.getRequestId());
            return toResponse(existing.get());
        }

        // --- Validate account exists ---
        Optional<Account> accountOpt = accountRepository.findByAccountId(request.getAccountId());
        if (accountOpt.isEmpty()) {
            log.warn("[AccountingService] Account not found - accountId={}", request.getAccountId());
            return saveAndReturn(buildFailedTransaction(request, "ACCOUNT_NOT_FOUND"));
        }

        // --- Atomic balance deduction ---
        // Returns 1 if deduction succeeded (balance was sufficient), 0 if not.
        int rowsUpdated = accountRepository.deductBalance(request.getAccountId(), request.getAmount());

        if (rowsUpdated == 0) {
            log.warn("[AccountingService] Insufficient balance - accountId={}, requested={}",
                    request.getAccountId(), request.getAmount());
            return saveAndReturn(buildFailedTransaction(request, "INSUFFICIENT_BALANCE"));
        }

        // --- Fetch updated balance for response ---
        Account updated = accountRepository.findByAccountId(request.getAccountId()).orElseThrow();
        String transactionId = UUID.randomUUID().toString();

        WithdrawalTransaction txn = WithdrawalTransaction.builder()
                .transactionId(transactionId)
                .requestId(request.getRequestId())
                .accountId(request.getAccountId())
                .amount(request.getAmount())
                .currency(request.getCurrency())
                .status("SUCCESS")
                .remainingBalance(updated.getBalance())
                .build();

        try {
            transactionRepository.save(txn);
        } catch (DataIntegrityViolationException e) {
            // Concurrent duplicate request raced past the idempotency check.
            // The unique constraint on request_id prevented a double insert.
            // Return the stored result.
            log.warn("[AccountingService] Concurrent duplicate detected for requestId={}, rolling back and returning stored result",
                    request.getRequestId());
            throw e; // Let @Transactional roll back, then caller can retry
        }

        log.info("[AccountingService] Withdrawal SUCCESS - transactionId={}, accountId={}, amount={}, remainingBalance={}",
                transactionId, request.getAccountId(), request.getAmount(), updated.getBalance());

        return WithdrawalResponse.builder()
                .transactionId(transactionId)
                .accountId(request.getAccountId())
                .amount(request.getAmount())
                .currency(request.getCurrency())
                .status("SUCCESS")
                .remainingBalance(updated.getBalance())
                .build();
    }

    private WithdrawalResponse saveAndReturn(WithdrawalTransaction txn) {
        transactionRepository.save(txn);
        return toResponse(txn);
    }

    private WithdrawalTransaction buildFailedTransaction(WithdrawalRequest request, String reason) {
        return WithdrawalTransaction.builder()
                .transactionId(UUID.randomUUID().toString())
                .requestId(request.getRequestId())
                .accountId(request.getAccountId())
                .amount(request.getAmount())
                .currency(request.getCurrency())
                .status("FAILED")
                .reason(reason)
                .build();
    }

    private WithdrawalResponse toResponse(WithdrawalTransaction txn) {
        return WithdrawalResponse.builder()
                .transactionId(txn.getTransactionId())
                .accountId(txn.getAccountId())
                .amount(txn.getAmount())
                .currency(txn.getCurrency())
                .status(txn.getStatus())
                .remainingBalance(txn.getRemainingBalance())
                .reason(txn.getReason())
                .build();
    }
}
