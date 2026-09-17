package com.banking.transaction.controller;

import com.banking.transaction.dto.WithdrawalResponse;
import com.banking.transaction.service.TransactionService;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.math.BigDecimal;
import java.util.Map;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(TransactionController.class)
class TransactionControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @MockBean
    private TransactionService transactionService;

    private static final String URL = "/api/v1/transactions/withdraw";

    // -----------------------------------------------------------------------
    // Test 1: Valid withdrawal request → forwards to service, returns response
    // -----------------------------------------------------------------------
    @Test
    @DisplayName("Valid withdrawal request - returns 200 with SUCCESS response")
    void validWithdrawal_returns200() throws Exception {
        WithdrawalResponse mockResponse = WithdrawalResponse.builder()
                .transactionId("TXN-001")
                .accountId("ACC001")
                .amount(new BigDecimal("1000"))
                .currency("INR")
                .status("SUCCESS")
                .remainingBalance(new BigDecimal("4000"))
                .build();

        when(transactionService.processWithdrawal(any())).thenReturn(mockResponse);

        String body = """
                {
                  "accountId": "ACC001",
                  "amount": 1000,
                  "currency": "INR",
                  "requestId": "REQ-001"
                }
                """;

        mockMvc.perform(post(URL)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(body))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("SUCCESS"))
                .andExpect(jsonPath("$.transactionId").value("TXN-001"))
                .andExpect(jsonPath("$.remainingBalance").value(4000));

        verify(transactionService, times(1)).processWithdrawal(any());
    }

    // -----------------------------------------------------------------------
    // Test 2: Zero amount → 400 validation error
    // -----------------------------------------------------------------------
    @Test
    @DisplayName("Zero amount - returns 400 validation error")
    void zeroAmount_returns400() throws Exception {
        String body = """
                {
                  "accountId": "ACC001",
                  "amount": 0,
                  "currency": "INR",
                  "requestId": "REQ-002"
                }
                """;

        mockMvc.perform(post(URL)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(body))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.reason").value("VALIDATION_ERROR"));

        verifyNoInteractions(transactionService);
    }

    // -----------------------------------------------------------------------
    // Test 3: Negative amount → 400 validation error
    // -----------------------------------------------------------------------
    @Test
    @DisplayName("Negative amount - returns 400 validation error")
    void negativeAmount_returns400() throws Exception {
        String body = """
                {
                  "accountId": "ACC001",
                  "amount": -500,
                  "currency": "INR",
                  "requestId": "REQ-003"
                }
                """;

        mockMvc.perform(post(URL)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(body))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.reason").value("VALIDATION_ERROR"));

        verifyNoInteractions(transactionService);
    }

    // -----------------------------------------------------------------------
    // Test 4: Missing accountId → 400 validation error
    // -----------------------------------------------------------------------
    @Test
    @DisplayName("Missing accountId - returns 400 validation error")
    void missingAccountId_returns400() throws Exception {
        String body = """
                {
                  "amount": 1000,
                  "currency": "INR",
                  "requestId": "REQ-004"
                }
                """;

        mockMvc.perform(post(URL)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(body))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.reason").value("VALIDATION_ERROR"));

        verifyNoInteractions(transactionService);
    }

    // -----------------------------------------------------------------------
    // Test 5: Invalid currency (not INR) → 400 validation error
    // -----------------------------------------------------------------------
    @Test
    @DisplayName("Invalid currency (USD) - returns 400 validation error")
    void invalidCurrency_returns400() throws Exception {
        String body = """
                {
                  "accountId": "ACC001",
                  "amount": 1000,
                  "currency": "USD",
                  "requestId": "REQ-005"
                }
                """;

        mockMvc.perform(post(URL)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(body))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.reason").value("VALIDATION_ERROR"));

        verifyNoInteractions(transactionService);
    }

    // -----------------------------------------------------------------------
    // Test 6: Missing requestId → 400 validation error
    // -----------------------------------------------------------------------
    @Test
    @DisplayName("Missing requestId - returns 400 validation error")
    void missingRequestId_returns400() throws Exception {
        String body = """
                {
                  "accountId": "ACC001",
                  "amount": 1000,
                  "currency": "INR"
                }
                """;

        mockMvc.perform(post(URL)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(body))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.reason").value("VALIDATION_ERROR"));

        verifyNoInteractions(transactionService);
    }

    // -----------------------------------------------------------------------
    // Test 7: Accounting Service (Dapr) failure → returns 503
    // -----------------------------------------------------------------------
    @Test
    @DisplayName("Accounting Service unavailable - returns 503")
    void accountingServiceFailure_returns503() throws Exception {
        when(transactionService.processWithdrawal(any()))
                .thenThrow(new RuntimeException("Dapr sidecar unreachable. Ensure Dapr is running."));

        String body = """
                {
                  "accountId": "ACC001",
                  "amount": 1000,
                  "currency": "INR",
                  "requestId": "REQ-007"
                }
                """;

        mockMvc.perform(post(URL)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(body))
                .andExpect(status().isServiceUnavailable())
                .andExpect(jsonPath("$.reason").value("SERVICE_ERROR"));
    }
}
