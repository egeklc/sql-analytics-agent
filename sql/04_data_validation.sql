
-- Checking row numbers
SELECT 'customers' AS table_name, COUNT(*) AS row_count
FROM customers
UNION ALL

SELECT 'accounts', COUNT(*)
FROM accounts
UNION ALL

SELECT 'transactions', COUNT(*)
FROM transactions;


-- Checking primary key duplicates

SELECT customer_id, COUNT(*) as duplicate_count
FROM customers
GROUP BY customer_id
HAVING COUNT(*) > 1;

SELECT account_id, COUNT(*) as duplicate_count
FROM accounts
GROUP BY account_id
HAVING COUNT(*) > 1;

SELECT transaction_id, COUNT(*) as duplicate_count
FROM transactions
GROUP BY transaction_id
HAVING COUNT(*) > 1;


-- Checking foreign key
SELECT COUNT(*) AS invalid_accounts
FROM accounts acc
LEFT JOIN customers cust ON cust.customer_id = acc.customer_id
WHERE cust.customer_id IS NULL;

SELECT COUNT(*) AS invalid_transactions
FROM transactions txn
LEFT JOIN accounts acc ON acc.account_id = txn.account_id
WHERE acc.account_id IS NULL;

-- Checking NULL values for all columns
SELECT
    COUNT(*) FILTER (WHERE customer_id IS NULL) AS missing_customer_id,
    COUNT(*) FILTER (WHERE first_name IS NULL) AS missing_first_name,
    COUNT(*) FILTER (WHERE last_name IS NULL) AS missing_last_name,
    COUNT(*) FILTER (WHERE email IS NULL) AS missing_email,
    COUNT(*) FILTER (WHERE phone_number IS NULL) AS missing_phone_number,
    COUNT(*) FILTER (WHERE city IS NULL) AS missing_city,
    COUNT(*) FILTER (WHERE country IS NULL) AS missing_country,
    COUNT(*) FILTER (WHERE birth_date IS NULL) AS missing_birth_date,
    COUNT(*) FILTER (WHERE occupation IS NULL) AS missing_occupation,
    COUNT(*) FILTER (WHERE income IS NULL) AS missing_income,
    COUNT(*) FILTER (WHERE signup_date IS NULL) AS missing_signup_date,
    COUNT(*) FILTER (WHERE segment IS NULL) AS missing_segment
FROM customers;


SELECT
    COUNT(*) FILTER (WHERE account_id IS NULL) AS missing_account_id,
    COUNT(*) FILTER (WHERE customer_id IS NULL) AS missing_customer_id,
    COUNT(*) FILTER (WHERE account_type IS NULL) AS missing_account_type,
    COUNT(*) FILTER (WHERE opened_date IS NULL) AS missing_opened_date,
    COUNT(*) FILTER (WHERE opening_balance IS NULL) AS missing_opening_balance,
    COUNT(*) FILTER (WHERE current_balance IS NULL) AS missing_current_balance,
    COUNT(*) FILTER (WHERE currency IS NULL) AS missing_currency,
    COUNT(*) FILTER (WHERE status IS NULL) AS missing_status
FROM accounts;


SELECT
    COUNT(*) FILTER (WHERE transaction_id IS NULL) AS missing_transaction_id,
    COUNT(*) FILTER (WHERE account_id IS NULL) AS missing_account_id,
    COUNT(*) FILTER (WHERE transaction_type IS NULL) AS missing_transaction_type,
    COUNT(*) FILTER (WHERE amount IS NULL) AS missing_amount,
    COUNT(*) FILTER (WHERE transaction_date IS NULL) AS missing_transaction_date,
    COUNT(*) FILTER (WHERE channel IS NULL) AS missing_channel,
    COUNT(*) FILTER (WHERE balance_before IS NULL) AS missing_balance_before,
    COUNT(*) FILTER (WHERE balance_after IS NULL) AS missing_balance_after
FROM transactions;


-- Checking for invalid values
SELECT *
FROM accounts
WHERE account_type NOT IN ('Checking', 'Savings', 'Investment')
    OR currency NOT IN ('TRY', 'USD', 'Gold')
    OR status NOT IN ('Active', 'Dormant', 'Closed');


SELECT *
FROM transactions
WHERE transaction_type NOT IN (
    'transfer_out',
    'deposit',
    'transfer_in',
    'withdrawal'
)
OR channel NOT IN ('ATM', 'Mobile App', 'Web', 'Branch', 'POS');


-- Checking negative values
SELECT *
FROM accounts
WHERE opening_balance < 0
    OR current_balance < 0;

SELECT *
FROM transactions
WHERE amount <= 0
    OR balance_before < 0
    OR balance_after < 0;


-- Checking date consistency for accounts and transactions
SELECT *
FROM accounts
WHERE closed_date < opened_date;

SELECT *
FROM accounts
WHERE (status = 'Closed' AND closed_date IS NULL)
    OR (status <> 'Closed' AND closed_date IS NOT NULL);

-- Transactions cannot precede account opening date
SELECT txn.*
FROM transactions txn
JOIN accounts acc
    ON txn.account_id = acc.account_id
WHERE txn.transaction_date < acc.opened_date;

-- Transactions cannot occur after account is closed
SELECT txn.*
FROM transactions txn
JOIN accounts acc
    ON txn.account_id = acc.account_id
WHERE acc.closed_date IS NOT NULL
    AND txn.transaction_date > acc.closed_date;


WITH ordered_transactions AS (
    SELECT
        transaction_id,
        account_id,
        transaction_date,
        balance_before,
        balance_after,
        LAG(balance_after) OVER (
            PARTITION BY account_id
            ORDER BY transaction_date, transaction_id
        ) AS previous_balance
    FROM transactions
)
SELECT *
FROM ordered_transactions
WHERE previous_balance IS NOT NULL
    AND balance_before <> previous_balance;


-- Checking balance consistency
WITH latest_transactions AS (
    SELECT DISTINCT ON (account_id)
        account_id,
        balance_after
    FROM transactions
    ORDER BY account_id, transaction_date DESC, transaction_id DESC
)
SELECT
    a.account_id,
    a.current_balance,
    lt.balance_after AS latest_transaction_balance
FROM accounts a
JOIN latest_transactions lt
    ON a.account_id = lt.account_id
WHERE a.current_balance <> lt.balance_after;