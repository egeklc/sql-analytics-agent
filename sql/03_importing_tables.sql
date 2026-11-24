
\copy customers (customer_id, first_name, last_name, email, phone_number, city, country, birth_date, occupation, income, signup_date, segment) FROM 'data/customers.csv' WITH (FORMAT CSV, HEADER TRUE, ENCODING 'UTF8')

\copy accounts (account_id, customer_id, account_type, opened_date, opening_balance, current_balance, currency, status, closed_date) FROM 'data/accounts.csv' WITH (FORMAT CSV, HEADER TRUE, ENCODING 'UTF8')

\copy transactions (transaction_id, account_id, transaction_type, amount, transaction_date, channel, balance_before, balance_after) FROM 'data/transactions.csv' WITH (FORMAT CSV, HEADER TRUE, ENCODING 'UTF8')
