package com.banking.transaction.controller;

import com.banking.transaction.dto.WithdrawalRequest;
import com.banking.transaction.dto.WithdrawalResponse;
import com.banking.transaction.service.TransactionService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@Slf4j
@RestController
@RequestMapping("/api/v1/transactions")
@RequiredArgsConstructor
public class TransactionController {

    private final TransactionService transactionService;

    /**
     * POST /api/v1/transactions/withdraw
     *
     * Client-facing withdrawal endpoint.
     * Validates the request, then forwards to Accounting Service via Dapr.
     */
    @PostMapping("/withdraw")
    public ResponseEntity<WithdrawalResponse> withdraw(@Valid @RequestBody WithdrawalRequest request) {
        log.info("[TransactionController] Received withdrawal request - requestId={}, accountId={}",
                request.getRequestId(), request.getAccountId());
        WithdrawalResponse response = transactionService.processWithdrawal(request);
        return ResponseEntity.ok(response);
    }
}
