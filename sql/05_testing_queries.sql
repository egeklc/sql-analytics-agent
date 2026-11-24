-- SQL queries for testing the banking_analytics db

-- 1. Customer Analytics

-- Total number of customers
SELECT COUNT(*) AS total_customers
FROM customers;


-- Customer distribution by segment
SELECT segment, COUNT(*) AS customer_count
FROM customers
GROUP BY segment
ORDER BY customer_count DESC;


-- Customer distribution by city
SELECT city, COUNT(*) AS customer_count
FROM customers
GROUP BY city
ORDER BY customer_count DESC;


-- Average customer income by segment
SELECT segment, ROUND(AVG(income), 2) AS average_income,
    ROUND(MIN(income),2) AS minimum_income, ROUND(MAX(income),2) AS maximum_income
FROM customers
GROUP BY segment
ORDER BY average_income DESC;


-- 2. Account Analytics

-- Total number of accounts
SELECT COUNT(*) AS total_accounts
FROM accounts;


-- Account distribution by account type
SELECT account_type, COUNT(*) AS account_count
FROM accounts
GROUP BY account_type
ORDER BY account_count DESC;

-- Account distribution by currency
SELECT currency, COUNT(*) AS account_count
FROM accounts
GROUP BY currency
ORDER BY account_count DESC;

-- Account distribution by status
SELECT status, COUNT(*) AS account_count
FROM accounts
GROUP BY status
ORDER BY account_count DESC;


-- Account distribution by type and currency
SELECT account_type, currency, COUNT(*) AS account_count
FROM accounts
GROUP BY account_type, currency
ORDER BY account_type, account_count DESC;


-- 3. Transaction Analytics

-- Total number of transactions
SELECT COUNT(*) AS total_transactions
FROM transactions;

-- Transaction distribution by type
SELECT transaction_type, COUNT(*) transaction_count
FROM transactions
GROUP BY transaction_type
ORDER BY transaction_count DESC;

-- Average transaction amount by type and currency
SELECT txn.transaction_type, acc.currency,
    COUNT(*) AS transaction_count,
    ROUND(AVG(txn.amount),2) AS average_amount,
    ROUND(SUM(txn.amount),2) AS total_amount
FROM transactions txn
JOIN accounts acc ON acc.account_id = txn.account_id
GROUP BY txn.transaction_type, acc.currency
ORDER BY txn.transaction_type, acc.currency;


-- Transaction distribution by channel
SELECT channel, COUNT(*) AS transaction_count
FROM transactions
GROUP BY channel
ORDER BY transaction_count DESC;


-- Transaction volume by channel and currency
SELECT txn.channel, acc.currency,
    COUNT(*) AS transaction_count,
    ROUND(SUM(txn.amount),2) AS total_amount
FROM transactions txn
JOIN accounts acc ON acc.account_id = txn.account_id
GROUP BY txn.channel, acc.currency
ORDER BY txn.channel, acc.currency;


-- CUSTOMER ACTIVITY

-- Customers with the highest transaction activity (Top 50)

SELECT
    c.customer_id,
    c.first_name,
    c.last_name,
    COUNT(t.transaction_id) AS transaction_count
FROM customers c
JOIN accounts a ON c.customer_id = a.customer_id
JOIN transactions t ON a.account_id = t.account_id
GROUP BY c.customer_id, c.first_name, c.last_name
ORDER BY transaction_count DESC
LIMIT 50;


-- Customer transaction amount by currency

SELECT
    c.customer_id,
    c.first_name,
    c.last_name,
    COUNT(t.transaction_id) AS transaction_count,
    ROUND(SUM(t.amount), 2) AS total_transaction_amount
FROM customers c
JOIN accounts a ON a.customer_id = c.customer_id
JOIN transactions t ON t.account_id = a.account_id
GROUP BY c.customer_id, c.first_name, c.last_name, a.currency
ORDER BY transaction_count DESC;


-- Customers with no transactions

SELECT
    c.customer_id,
    c.first_name,
    c.last_name
FROM customers c
WHERE NOT EXISTS (
    SELECT 1
    FROM accounts a
    JOIN transactions t ON t.account_id = a.account_id
    WHERE a.customer_id = c.customer_id
);


-- ACCOUNT ANALYTICS

-- Accounts with the highest current balances
WITH ranked_accounts AS (
    SELECT
        account_id,
        customer_id,
        account_type,
        currency,
        current_balance,
        RANK() OVER (
            PARTITION BY currency
            ORDER BY current_balance DESC
        ) AS balance_rank
    FROM accounts
)
SELECT * FROM ranked_accounts
WHERE balance_rank <= 10
ORDER BY currency, balance_rank;


-- Average current balance by account type and currency

SELECT
    account_type,
    currency,
    COUNT(*) AS account_count,
    ROUND(AVG(current_balance), 2) AS average_balance
FROM accounts
GROUP BY account_type, currency
ORDER BY account_type, currency;


-- Accounts with no transaction
SELECT 
    a.account_id,
    a.customer_id,
    a.account_type,
    a.currency,
    a.opening_balance,
    a.current_balance
FROM accounts a
LEFT JOIN transactions t
    ON a.account_id = t.account_id
WHERE t.transaction_id IS NULL;


-- TIME BASED ANALYTICS

-- Monthly transaction counts
SELECT
    DATE_TRUNC('month', transaction_date)::DATE AS transaction_month,
    COUNT(*) AS transaction_count
FROM transactions
GROUP BY DATE_TRUNC('month', transaction_date)
ORDER BY transaction_month;


-- Monthly transaction amounts by currency

SELECT
    DATE_TRUNC('month', transaction_date)::DATE AS transaction_month,
    a.currency,
    COUNT(*) AS transaction_count,
    ROUND(SUM(t.amount), 2) AS total_transaction_amount
FROM transactions t
JOIN accounts a
    ON a.account_id = t.account_id
GROUP BY DATE_TRUNC('month', transaction_date), a.currency
ORDER BY transaction_month, a.currency


-- Monthly transaction distribution by type

SELECT
    DATE_TRUNC('month', transaction_date)::DATE AS transaction_month,
    COUNT(*) AS transaction_count,
    transaction_type
FROM transactions
GROUP BY DATE_TRUNC('month', transaction_date), transaction_type
ORDER BY transaction_month, transaction_type;


-- RELATIONAL QUERIES

-- Customer, account, transaction details
SELECT
    c.customer_id,
    c.first_name,
    c.last_name,
    a.account_id,
    a.account_type,
    a.currency,
    t.transaction_id,
    t.transaction_type,
    t.amount,
    t.transaction_date,
    t.channel
FROM customers c
JOIN accounts a 
    ON a.customer_id = c.customer_id
JOIN transactions t 
    ON t.account_id = a.account_id
ORDER BY t.transaction_date DESC
LIMIT 100;


-- Customer account summary
SELECT
    c.customer_id,
    c.first_name,
    c.last_name,
    COUNT(DISTINCT a.account_id) AS account_count,
    COUNT(t.transaction_id) AS transaction_count
FROM customers c
LEFT JOIN accounts a 
    ON a.customer_id = c.customer_id
LEFT JOIN transactions t
    ON t.account_id = a.account_id
GROUP BY c.customer_id, c.first_name, c.last_name
ORDER BY transaction_count DESC;

-- Transaction activity by customer, account type and currency
SELECT
    c.customer_id,
    c.first_name,
    c.last_name,
    a.account_type,
    a.currency,
    COUNT(t.transaction_id) AS transaction_count,
    ROUND(SUM(t.amount),2) AS total_transaction_amount
FROM customers c
JOIN accounts a
    ON a.customer_id = c.customer_id
JOIN transactions t
    ON t.account_id = a.account_id
GROUP BY 
    c.customer_id,
    c.first_name,
    c.last_name,
    a.account_type,
    a.currency
ORDER BY transaction_count DESC;