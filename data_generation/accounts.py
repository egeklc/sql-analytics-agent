import pandas as pd
from faker import Faker
from datetime import date
from dateutil.relativedelta import relativedelta
import random
from pathlib import Path
from config import BASE_DIR, DATA_DIR



def get_acc():
    n_accs = [1, 2, 3]
    w_n_accs = [55, 35, 10]
    return random.choices(n_accs, weights=w_n_accs, k=1)[0]

def get_acc_types(n_accs):
    if n_accs == 1:
        return ["Checking"]
    elif n_accs == 2:
        return ["Checking", random.choice(["Savings", "Investment"])]
    else:
        return ["Checking", "Savings", "Investment"]

def get_currency(acc_type):
    if acc_type == "Checking":
        return "TRY"
    else:
        return random.choice(["TRY", "USD", "Gold"])

def convert_currency(currency_type, balance):
    usd_rate = 45
    gold_rate = 5000
    if currency_type == "USD":
        return round(balance / usd_rate, 2)
    elif currency_type == "Gold":
        return round(balance / gold_rate, 4)
    else:
        return round(balance, 2)

def get_balance(income, acc_type):
    if acc_type == "Checking":
        bracket = random.choices(["low", "medium", "high"], weights=[60, 30, 10])[0]
        if bracket == "low":    
            multiplier = random.uniform(0.1, 0.3)
        elif bracket == "medium": 
            multiplier = random.uniform(0.3, 0.7)
        else:                   
            multiplier = random.uniform(0.7, 1.0)
    elif acc_type == "Savings":
        bracket = random.choices(["zero", "low", "medium", "high"],weights=[10, 50, 30, 10])[0]
        if bracket == "zero":
            return 0
        elif bracket == "low":    
            multiplier = random.uniform(0.3, 2.0)
        elif bracket == "medium": 
            multiplier = random.uniform(2.0, 6.0)
        else:                   
            multiplier = random.uniform(6.0, 12.0)
        
    else:
        bracket = random.choices(["zero", "low", "medium", "high"],weights=[15, 50, 25, 10])[0]
        if bracket == "zero":
            return 0
        elif bracket == "low":    
            multiplier = random.uniform(1.0, 3.0)
        elif bracket == "medium": 
            multiplier = random.uniform(3.0, 12.0)
        else:                   
            multiplier = random.uniform(12.0, 24.0)
    return round(income * multiplier, 2)

def get_status():
    status_type = ["Active", "Dormant", "Closed"]
    status_weights = [80, 15, 5]
    return random.choices(status_type, weights=status_weights)[0]

fake_tr = Faker("tr_TR")
custom_date = date(2026, 6, 12)

customers_path = DATA_DIR / "customers.csv"
customers_df = pd.read_csv(customers_path)

accounts_path = DATA_DIR / "accounts.csv"

def create_accounts_csv(customers_df, accounts_path):
    accounts = []
    count = 0
    
    for customer in customers_df.itertuples():
        
        customer_id = customer.customer_id
        income = customer.income
        n_accounts = get_acc()
        acc_types = get_acc_types(n_accounts)
        signup_date = pd.to_datetime(customer.signup_date)
        
        for acc_type in acc_types:
            count += 1
            account_id = f"ACC{count:08d}"
            opened_date = fake_tr.date_between(start_date = signup_date, end_date=custom_date)
            currency = get_currency(acc_type)
            balance_try = get_balance(income, acc_type)
            final_balance = convert_currency(currency, balance_try)
            status = get_status()
            if status == "Closed":
                final_balance = 0
            accounts_dict = {"account_id": account_id,
                            "customer_id": customer_id,
                            "account_type": acc_type,
                            "opened_date": opened_date,
                            "current_balance": final_balance,
                            "currency": currency,
                            "status": status}
            accounts.append(accounts_dict)
    df = pd.DataFrame(accounts)
    df.to_csv(accounts_path, index=False)

create_accounts_csv(customers_df=customers_df, accounts_path=accounts_path)