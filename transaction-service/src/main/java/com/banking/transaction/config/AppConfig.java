package com.banking.transaction.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.client.RestTemplate;

@Configuration
public class AppConfig {

    /**
     * RestTemplate used by TransactionService to call the Dapr sidecar HTTP API.
     * The Dapr sidecar translates the call to the target service via service invocation.
     */
    @Bean
    public RestTemplate restTemplate() {
        return new RestTemplate();
    }
}
