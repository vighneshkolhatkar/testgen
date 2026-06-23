package com.example.payment;

import com.example.payment.exception.PaymentException;
import com.example.payment.model.Transaction;
import com.example.payment.model.CardDetails;
import com.example.payment.repository.TransactionRepository;
import com.example.payment.gateway.PaymentGatewayClient;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.Optional;
import java.util.UUID;

@Service
public class PaymentService {

    private final TransactionRepository transactionRepository;
    private final PaymentGatewayClient gatewayClient;

    @Autowired
    public PaymentService(
        TransactionRepository transactionRepository,
        PaymentGatewayClient gatewayClient
    ) {
        this.transactionRepository = transactionRepository;
        this.gatewayClient = gatewayClient;
    }

    public Transaction processPayment(CardDetails card, double amount, String currency)
        throws PaymentException {
        if (amount <= 0) {
            throw new PaymentException("Amount must be positive");
        }
        validateCard(card);
        String gatewayRef = gatewayClient.charge(card.getToken(), amount, currency);
        Transaction txn = new Transaction(UUID.randomUUID().toString(), amount, currency, "COMPLETED", gatewayRef);
        return transactionRepository.save(txn);
    }

    public Transaction refund(String transactionId, double amount) throws PaymentException {
        Transaction txn = transactionRepository.findById(transactionId)
            .orElseThrow(() -> new PaymentException("Transaction not found: " + transactionId));
        if (amount > txn.getAmount()) {
            throw new PaymentException("Refund exceeds original amount");
        }
        gatewayClient.refund(txn.getGatewayRef(), amount);
        txn.setStatus("REFUNDED");
        return transactionRepository.save(txn);
    }

    public Optional<Transaction> getTransaction(String transactionId) {
        return transactionRepository.findById(transactionId);
    }

    public boolean validateCard(CardDetails card) throws PaymentException {
        if (card == null || card.getToken() == null || card.getToken().isBlank()) {
            throw new PaymentException("Invalid card token");
        }
        return true;
    }
}
