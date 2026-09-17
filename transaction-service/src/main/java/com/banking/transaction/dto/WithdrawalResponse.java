package com.banking.transaction.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@JsonInclude(JsonInclude.Include.NON_NULL)
public class WithdrawalResponse {

    private String transactionId;
    private String accountId;
    private BigDecimal amount;
    private String currency;
    private String status;           // SUCCESS or FAILED
    private BigDecimal remainingBalance; // present on SUCCESS
    private String reason;           // present on FAILED (e.g. INSUFFICIENT_BALANCE)
    private String message;          // optional human-readable message
}
