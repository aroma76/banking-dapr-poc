package com.banking.accounting.repository;

import com.banking.accounting.model.WithdrawalTransaction;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface WithdrawalTransactionRepository extends JpaRepository<WithdrawalTransaction, Long> {

    Optional<WithdrawalTransaction> findByRequestId(String requestId);
}
