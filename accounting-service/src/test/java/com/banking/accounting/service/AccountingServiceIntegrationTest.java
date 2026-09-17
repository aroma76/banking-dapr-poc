package com.banking.accounting.service;

import com.banking.accounting.dto.WithdrawalRequest;
import com.banking.accounting.dto.WithdrawalResponse;
import com.banking.accounting.model.Account;
import com.banking.accounting.repository.AccountRepository;
import com.banking.accounting.repository.WithdrawalTransactionRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.annotation.DirtiesContext;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * Integration tests for AccountingService using H2 in-memory database.
 *
 * Tests cover:
 *  1. Successful withdrawal
 *  2. Account not found
 *  3. Insufficient balance
 *  4. Duplicate requestId (idempotency)
 *  5. Concurrent withdrawals — only one succeeds when funds are insufficient for both
 *  6. No negative balance under concurrent load
 */
@SpringBootTest
@DirtiesContext(classMode = DirtiesContext.ClassMode.BEFORE_EACH_TEST_METHOD)
class AccountingServiceIntegrationTest {

    @Autowired
    private AccountingService accountingService;

    @Autowired
    private AccountRepository accountRepository;

    @Autowired
    private WithdrawalTransactionRepository transactionRepository;

    private static final String ACCOUNT_ID = "ACC001";

    @BeforeEach
    void setUp() {
        transactionRepository.deleteAll();
        accountRepository.deleteAll();

        Account account = Account.builder()
                .accountId(ACCOUNT_ID)
                .balance(new BigDecimal("5000.00"))
                .currency("INR")
                .version(0L)
                .build();
        accountRepository.save(account);
    }

    // -----------------------------------------------------------------------
    // Test 1: Successful withdrawal
    // -----------------------------------------------------------------------
    @Test
    @DisplayName("Successful withdrawal - deducts balance and records transaction")
    void successfulWithdrawal() {
        WithdrawalRequest request = request("REQ-001", ACCOUNT_ID, "1000");

        WithdrawalResponse response = accountingService.processWithdrawal(request);

        assertThat(response.getStatus()).isEqualTo("SUCCESS");
        assertThat(response.getRemainingBalance()).isEqualByComparingTo("4000.00");
        assertThat(response.getAccountId()).isEqualTo(ACCOUNT_ID);
        assertThat(response.getTransactionId()).isNotBlank();

        // Verify balance in DB
        Account updated = accountRepository.findByAccountId(ACCOUNT_ID).orElseThrow();
        assertThat(updated.getBalance()).isEqualByComparingTo("4000.00");

        // Verify transaction record
        assertThat(transactionRepository.findByRequestId("REQ-001")).isPresent();
    }

    // -----------------------------------------------------------------------
    // Test 2: Account not found
    // -----------------------------------------------------------------------
    @Test
    @DisplayName("Account not found - returns FAILED with ACCOUNT_NOT_FOUND reason")
    void accountNotFound() {
        WithdrawalRequest request = request("REQ-002", "ACC999", "1000");

        WithdrawalResponse response = accountingService.processWithdrawal(request);

        assertThat(response.getStatus()).isEqualTo("FAILED");
        assertThat(response.getReason()).isEqualTo("ACCOUNT_NOT_FOUND");

        // No balance change on any account
        Account original = accountRepository.findByAccountId(ACCOUNT_ID).orElseThrow();
        assertThat(original.getBalance()).isEqualByComparingTo("5000.00");
    }

    // -----------------------------------------------------------------------
    // Test 3: Insufficient balance
    // -----------------------------------------------------------------------
    @Test
    @DisplayName("Insufficient balance - returns FAILED with INSUFFICIENT_BALANCE reason")
    void insufficientBalance() {
        WithdrawalRequest request = request("REQ-003", ACCOUNT_ID, "9999");

        WithdrawalResponse response = accountingService.processWithdrawal(request);

        assertThat(response.getStatus()).isEqualTo("FAILED");
        assertThat(response.getReason()).isEqualTo("INSUFFICIENT_BALANCE");

        // Balance must be unchanged
        Account unchanged = accountRepository.findByAccountId(ACCOUNT_ID).orElseThrow();
        assertThat(unchanged.getBalance()).isEqualByComparingTo("5000.00");
    }

    // -----------------------------------------------------------------------
    // Test 4: Duplicate requestId — idempotency
    // -----------------------------------------------------------------------
    @Test
    @DisplayName("Duplicate requestId - returns same result without deducting balance twice")
    void duplicateRequestId_idempotent() {
        WithdrawalRequest request = request("REQ-004", ACCOUNT_ID, "1000");

        WithdrawalResponse first = accountingService.processWithdrawal(request);
        WithdrawalResponse second = accountingService.processWithdrawal(request);

        assertThat(first.getStatus()).isEqualTo("SUCCESS");
        assertThat(second.getStatus()).isEqualTo("SUCCESS");
        assertThat(second.getTransactionId()).isEqualTo(first.getTransactionId());

        // Balance deducted only ONCE
        Account account = accountRepository.findByAccountId(ACCOUNT_ID).orElseThrow();
        assertThat(account.getBalance()).isEqualByComparingTo("4000.00");

        // Only one transaction record
        assertThat(transactionRepository.findAll()).hasSize(1);
    }

    // -----------------------------------------------------------------------
    // Test 5 & 6: Concurrent withdrawals — no negative balance
    //
    // Scenario: Balance = 5000
    //   Thread A: withdraw 3000
    //   Thread B: withdraw 3000
    // Expected: exactly ONE succeeds, ONE fails with INSUFFICIENT_BALANCE
    //           final balance = 2000, never negative
    // -----------------------------------------------------------------------
    @Test
    @DisplayName("Concurrent withdrawals - only one succeeds when funds are insufficient for both")
    void concurrentWithdrawals_onlyOneSucceeds() throws InterruptedException {
        int threads = 2;
        BigDecimal withdrawAmount = new BigDecimal("3000");
        ExecutorService executor = Executors.newFixedThreadPool(threads);
        CountDownLatch startLatch = new CountDownLatch(1);
        CountDownLatch doneLatch = new CountDownLatch(threads);

        AtomicInteger successCount = new AtomicInteger(0);
        AtomicInteger failCount = new AtomicInteger(0);
        List<WithdrawalResponse> responses = new CopyOnWriteArrayList<>();

        for (int i = 0; i < threads; i++) {
            final String reqId = "REQ-CONCURRENT-" + i;
            executor.submit(() -> {
                try {
                    startLatch.await(); // all threads start simultaneously
                    WithdrawalRequest req = request(reqId, ACCOUNT_ID, withdrawAmount.toPlainString());
                    WithdrawalResponse resp = accountingService.processWithdrawal(req);
                    responses.add(resp);
                    if ("SUCCESS".equals(resp.getStatus())) successCount.incrementAndGet();
                    else failCount.incrementAndGet();
                } catch (Exception e) {
                    failCount.incrementAndGet();
                } finally {
                    doneLatch.countDown();
                }
            });
        }

        startLatch.countDown(); // fire!
        doneLatch.await(10, TimeUnit.SECONDS);
        executor.shutdown();

        // Exactly one success, one failure
        assertThat(successCount.get()).isEqualTo(1);
        assertThat(failCount.get()).isEqualTo(1);

        // Final balance = 5000 - 3000 = 2000 (never negative)
        Account account = accountRepository.findByAccountId(ACCOUNT_ID).orElseThrow();
        assertThat(account.getBalance()).isEqualByComparingTo("2000.00");
        assertThat(account.getBalance()).isGreaterThanOrEqualTo(BigDecimal.ZERO);
    }

    // -----------------------------------------------------------------------
    // Helper
    // -----------------------------------------------------------------------
    private WithdrawalRequest request(String requestId, String accountId, String amount) {
        WithdrawalRequest req = new WithdrawalRequest();
        req.setRequestId(requestId);
        req.setAccountId(accountId);
        req.setAmount(new BigDecimal(amount));
        req.setCurrency("INR");
        return req;
    }
}
