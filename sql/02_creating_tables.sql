CREATE TABLE customers (
    customer_id VARCHAR(12) PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone_number VARCHAR(11) NOT NULL,
    city VARCHAR(50) NOT NULL,
    country VARCHAR(50) NOT NULL,
    birth_date DATE NOT NULL,
    occupation VARCHAR(100) NOT NULL,
    income NUMERIC(20, 4) NOT NULL,
    signup_date DATE NOT NULL,
    segment VARCHAR(30) NOT NULL
    );



CREATE TABLE accounts (
    account_id VARCHAR(12) PRIMARY KEY,
    customer_id VARCHAR(12) NOT NULL,
    account_type VARCHAR(30) NOT NULL,
    opened_date DATE NOT NULL,
    opening_balance NUMERIC(20, 4) NOT NULL,
    current_balance NUMERIC(20, 4) NOT NULL,
    currency VARCHAR(10) NOT NULL,
    status VARCHAR(20) NOT NULL,
    closed_date DATE,

    CONSTRAINT fk_accounts_customer
        FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id),

    CONSTRAINT chk_account_type
        CHECK (account_type IN ('Checking', 'Savings', 'Investment')),
    
    CONSTRAINT chk_account_currency
        CHECK (currency IN ('TRY', 'USD', 'Gold')),

    CONSTRAINT chk_account_status
        CHECK (status IN ('Active', 'Dormant', 'Closed')),

    CONSTRAINT chk_opening_balance
        CHECK (opening_balance >= 0),

    CONSTRAINT chk_current_balance
        CHECK (current_balance >= 0),

    CONSTRAINT chk_account_dates
        CHECK (closed_date IS NULL OR closed_date >= opened_date)
);



CREATE TABLE transactions(
    transaction_id VARCHAR(12) PRIMARY KEY,
    account_id VARCHAR(12) NOT NULL,
    transaction_type VARCHAR(50) NOT NULL,
    amount NUMERIC(20, 4) NOT NULL,
    transaction_date TIMESTAMP NOT NULL,
    channel VARCHAR(50) NOT NULL,
    balance_before NUMERIC(20, 4) NOT NULL,
    balance_after NUMERIC(20, 4) NOT NULL,
    
    CONSTRAINT fk_transactions_account
        FOREIGN KEY (account_id)
        REFERENCES accounts(account_id),
    
    CONSTRAINT chk_transaction_type
        CHECK (transaction_type IN ('transfer_out',
                                    'deposit',
                                    'transfer_in',
                                    'withdrawal')
                                    ),
    CONSTRAINT chk_channel
        CHECK (channel IN ('ATM',
                            'Mobile App',
                            'Web',
                            'Branch',
                            'POS')
                            ),


    CONSTRAINT chk_transaction_amount
        CHECK (amount > 0),
    
    CONSTRAINT chk_transaction_balances
        CHECK (balance_before >= 0 AND balance_after >= 0)
);