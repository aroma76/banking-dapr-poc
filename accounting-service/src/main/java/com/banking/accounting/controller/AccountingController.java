package com.banking.accounting.controller;

import com.banking.accounting.dto.WithdrawalRequest;
import com.banking.accounting.dto.WithdrawalResponse;
import com.banking.accounting.service.AccountingService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

/**
 * AccountingController — internal endpoint invoked via Dapr service invocation.
 *
 * This endpoint is NOT intended to be called directly by external clients.
 * In production, network policies would restrict access to the Dapr sidecar only.
 *
 * Dapr invocation path:
 *   Transaction Service → Dapr sidecar (localhost:3500)
 *     → POST /v1.0/invoke/accounting-service/method/api/v1/accounting/withdraw
 *       → AccountingController → POST /api/v1/accounting/withdraw
 */
@Slf4j
@RestController
@RequestMapping("/api/v1/accounting")
@RequiredArgsConstructor
public class AccountingController {

    private final AccountingService accountingService;

    @PostMapping("/withdraw")
    public ResponseEntity<WithdrawalResponse> withdraw(@Valid @RequestBody WithdrawalRequest request) {
        log.info("[AccountingController] Received withdrawal via Dapr - requestId={}, accountId={}",
                request.getRequestId(), request.getAccountId());
        WithdrawalResponse response = accountingService.processWithdrawal(request);
        return ResponseEntity.ok(response);
    }
}
