package com.banking.transaction.dto;

import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;
import lombok.Data;

import java.math.BigDecimal;

@Data
public class WithdrawalRequest {

    @NotBlank(message = "accountId is mandatory")
    private String accountId;

    @NotNull(message = "amount is mandatory")
    @DecimalMin(value = "0.01", message = "amount must be greater than zero")
    private BigDecimal amount;

    @NotBlank(message = "currency is mandatory")
    @Pattern(regexp = "INR", message = "currency must be INR")
    private String currency;

    @NotBlank(message = "requestId is mandatory")
    private String requestId;
}
