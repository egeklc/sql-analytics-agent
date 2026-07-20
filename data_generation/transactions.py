import pandas as pd
from datetime import date
from dateutil.relativedelta import relativedelta
import random
from pathlib import Path
from config import  DATA_DIR, FAKE_TR, CUSTOM_DATE
from utils import convert_currency

def get_n_transactions():
    return random.randint(3,10)

def get_transaction_type():
    txn_type = ["deposit", "withdrawal", "transfer_in", "transfer_out"]
    txn_weights = [30, 40, 15, 15]
    return random.choices(txn_type, txn_weights, k=1)[0]

def get_transaction_amount(transaction_type, opening_balance, currency):
    if transaction_type in ("deposit", "withdrawal"):
        multiplier = random.uniform(0.05, 0.3)
        amount = opening_balance * multiplier
        return convert_currency(currency, amount)
    else:
        multiplier= random.uniform(0.1, 0.6)
        amount = opening_balance * multiplier
        return convert_currency(currency, amount)

def get_transaction_date(opened_date, closed_date):
    opened_date = pd.to_datetime(opened_date)
    if pd.notna(closed_date):
        return pd.to_datetime(FAKE_TR.date_time_between(start_date=opened_date, end_date=pd.to_datetime(closed_date)))
    else:
        return pd.to_datetime(FAKE_TR.date_time_between(start_date=opened_date, end_date=CUSTOM_DATE))

def get_balance(opening_balance, txn_list):
    balance = opening_balance
    for txn in txn_list:
        txn["balance_before"] = balance
        
        if (balance <= 0 and txn["txn_type"] in ("withdrawal", "transfer_out")):
            txn["txn_type"] = random.choice(["deposit", "transfer_in"])
            
        if txn["txn_type"] in ("deposit", "transfer_in"):
            balance += txn["amount"]
        else:
            if txn["amount"] > balance:
                txn["amount"] = balance
            balance -= txn["amount"]
        txn["balance_after"] = balance
    return balance

def get_channel():
    channels = ["ATM", "Mobile App", "POS", "Web", "Branch"]
    channel_weights = [25, 30, 20, 10, 15]
    return random.choices(channels,weights=channel_weights, k=1)[0]

def create_transactions_csv(acc_df, transactions_path, accounts_path):
    transactions = []
    count = 0
    
    for account in acc_df.itertuples():
        opening_balance = account.opening_balance
        currency = account.currency
        opened_date = account.opened_date
        closed_date = account.closed_date
        n_txn = get_n_transactions()
        txn_list = []
        for _ in range(0,n_txn):
            count += 1
            txn_id = f"TXN{count:08d}"
            txn_type = get_transaction_type()
            amount = get_transaction_amount(txn_type, opening_balance, currency)
            txn_date =  get_transaction_date(opened_date=opened_date, closed_date=closed_date)
            channel = get_channel()
            txn_dict = {"txn_id" : txn_id,
                        "account_id": account.account_id,
                        "txn_type": txn_type,
                        "amount": amount,
                        "txn_date": txn_date,
                        "channel": channel}
            txn_list.append(txn_dict)
        sorted_txn_list = sorted(txn_list, key=lambda txn: txn["txn_date"])
        final_balance = get_balance(opening_balance=opening_balance, txn_list=sorted_txn_list)
        transactions.extend(sorted_txn_list)
        acc_df.loc[acc_df["account_id"] == account.account_id, "current_balance"] = final_balance
        
    df = pd.DataFrame(transactions)
    df.to_csv(transactions_path, index=False)
    acc_df.to_csv(accounts_path, index=False)

accounts_path = DATA_DIR / "accounts.csv"
transactions_path = DATA_DIR / "transactions.csv"

acc_df = pd.read_csv(accounts_path)

create_transactions_csv(acc_df=acc_df, transactions_path=transactions_path, accounts_path=accounts_path)