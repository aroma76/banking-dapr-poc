package com.banking.transaction.service;

import com.banking.transaction.dto.WithdrawalRequest;
import com.banking.transaction.dto.WithdrawalResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.web.client.RestTemplate;

/**
 * TransactionService forwards withdrawal requests to Accounting Service via Dapr service invocation.
 *
 * Dapr HTTP API format for service invocation:
 *   POST http://<dapr-sidecar-host>:<dapr-http-port>/v1.0/invoke/<app-id>/method/<method-path>
 *
 * Flow:
 *   Client → TransactionService → Dapr sidecar (localhost:3500)
 *          → [Dapr network / mDNS discovery]
 *          → Accounting Dapr sidecar → AccountingService
 *
 * TransactionService does NOT access the database directly.
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class TransactionService {

    private final RestTemplate restTemplate;

    @Value("${dapr.http.endpoint}")
    private String daprEndpoint;

    @Value("${dapr.accounting.app-id}")
    private String accountingAppId;

    public WithdrawalResponse processWithdrawal(WithdrawalRequest request) {
        String daprUrl = String.format(
                "%s/v1.0/invoke/%s/method/api/v1/accounting/withdraw",
                daprEndpoint, accountingAppId
        );

        log.info("[TransactionService] Processing withdrawal - requestId={}, accountId={}, amount={} {}",
                request.getRequestId(), request.getAccountId(), request.getAmount(), request.getCurrency());
        log.info("[TransactionService] Invoking Accounting Service via Dapr: {}", daprUrl);

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        HttpEntity<WithdrawalRequest> entity = new HttpEntity<>(request, headers);

        try {
            ResponseEntity<WithdrawalResponse> response = restTemplate.exchange(
                    daprUrl, HttpMethod.POST, entity, WithdrawalResponse.class
            );

            WithdrawalResponse body = response.getBody();
            log.info("[TransactionService] Accounting Service response - status={}, transactionId={}",
                    body != null ? body.getStatus() : "null",
                    body != null ? body.getTransactionId() : "null");

            return body;

        } catch (HttpClientErrorException e) {
            log.error("[TransactionService] Dapr/Accounting error {} for requestId={}: {}",
                    e.getStatusCode(), request.getRequestId(), e.getMessage());
            throw new RuntimeException("Accounting service error: " + e.getMessage(), e);

        } catch (ResourceAccessException e) {
            log.error("[TransactionService] Cannot reach Dapr sidecar for requestId={}: {}",
                    request.getRequestId(), e.getMessage());
            throw new RuntimeException("Dapr sidecar unreachable. Ensure Dapr is running.", e);
        }
    }
}
