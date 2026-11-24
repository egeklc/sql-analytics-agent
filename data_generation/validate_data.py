import sys
import pandas as pd
from pathlib import Path
from config import  BASE_DIR, DATA_DIR, VALIDATION_DIR



# --------------------------------------------------
# PATHS AND VALIDATION RESULTS
# --------------------------------------------------

VALIDATION_DIR = BASE_DIR / "validation_outputs"

validation_errors = []
validation_results = {}


def check_result(name, error_count):
    """Register and print a validation result."""

    error_count = int(error_count)
    validation_results[name] = error_count

    status = "PASSED" if error_count == 0 else "FAILED"

    print(f"{name}: {error_count} [{status}]")

    if error_count > 0:
        validation_errors.append(name)


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

try:
    customers = pd.read_csv(DATA_DIR / "customers.csv")
    accounts = pd.read_csv(DATA_DIR / "accounts.csv")
    transactions = pd.read_csv(DATA_DIR / "transactions.csv")

    # Parse dates
    accounts["opened_date"] = pd.to_datetime(
        accounts["opened_date"], errors="coerce"
    )

    accounts["closed_date"] = pd.to_datetime(
        accounts["closed_date"], errors="coerce"
    )

    transactions["transaction_date"] = pd.to_datetime(
        transactions["transaction_date"], errors="coerce"
    )

    # Normalize text fields
    accounts["status"] = (
        accounts["status"].astype("string").str.strip().str.lower()
    )

    transactions["transaction_type"] = (
        transactions["transaction_type"].astype("string").str.strip().str.lower()
    )

except Exception as e:
    print(f"\nERROR: Could not load or prepare CSV files: {e}")
    sys.exit(1)


try:

    # --------------------------------------------------
    # UNIQUE IDs
    # --------------------------------------------------

    print("\n--- UNIQUE ID CHECKS ---")

    check_result(
        "Duplicate customer IDs",
        customers["customer_id"].duplicated().sum()
    )

    check_result(
        "Duplicate account IDs",
        accounts["account_id"].duplicated().sum()
    )

    check_result(
        "Duplicate transaction IDs",
        transactions["transaction_id"].duplicated().sum()
    )

    # --------------------------------------------------
    # FOREIGN KEYS
    # --------------------------------------------------

    print("\n--- FOREIGN KEY CHECKS ---")

    check_result(
        "Accounts with missing customers",
        (~accounts["customer_id"].isin(customers["customer_id"])).sum()
    )

    check_result(
        "Transactions with missing accounts",
        (~transactions["account_id"].isin(accounts["account_id"])).sum()
    )

    # --------------------------------------------------
    # REQUIRED FIELDS
    # --------------------------------------------------

    print("\n--- REQUIRED FIELD CHECKS ---")

    required_fields = [
        (
            "customers",
            customers,
            ["customer_id"]
        ),
        (
            "accounts",
            accounts,
            [
                "account_id",
                "customer_id",
                "account_type",
                "opened_date",
                "opening_balance",
                "current_balance",
                "currency",
                "status"
            ]
        ),
        (
            "transactions",
            transactions,
            [
                "transaction_id",
                "account_id",
                "transaction_type",
                "amount",
                "transaction_date",
                "balance_before",
                "balance_after"
            ]
        )
    ]

    for name, df, cols in required_fields:

        missing_count = df[cols].isna().sum().sum()

        print(f"{name} missing required values:")
        print(df[cols].isna().sum()[lambda s: s > 0])

        check_result(
            f"Missing required values in {name}",
            missing_count
        )

    # --------------------------------------------------
    # VALID VALUES
    # --------------------------------------------------

    print("\n--- VALID VALUE CHECKS ---")

    valid_currencies = {"TRY", "USD", "Gold"}

    check_result(
        "Invalid account currencies",
        (~accounts["currency"].isin(valid_currencies)).sum()
    )

    valid_txn_types = {
        "deposit",
        "withdrawal",
        "transfer_in",
        "transfer_out"
    }

    check_result(
        "Invalid transaction types",
        (~transactions["transaction_type"].isin(valid_txn_types)).sum()
    )

    valid_statuses = {"active", "dormant", "closed"}

    check_result(
        "Invalid account statuses",
        (~accounts["status"].isin(valid_statuses)).sum()
    )

    # --------------------------------------------------
    # NUMERIC CHECKS
    # --------------------------------------------------

    print("\n--- NUMERIC CHECKS ---")

    check_result(
        "Negative opening balances",
        (accounts["opening_balance"] < 0).sum()
    )

    check_result(
        "Negative current balances",
        (accounts["current_balance"] < 0).sum()
    )

    check_result(
        "Negative transaction amounts",
        (transactions["amount"] < 0).sum()
    )

    check_result(
        "Negative transaction balances",
        (
            (transactions["balance_before"] < 0) |
            (transactions["balance_after"] < 0)
        ).sum()
    )

    # --------------------------------------------------
    # TRANSACTION BALANCE ARITHMETIC
    # --------------------------------------------------

    print("\n--- TRANSACTION ARITHMETIC ---")

    signed_amount = transactions["transaction_type"].map({
        "deposit": 1,
        "transfer_in": 1,
        "withdrawal": -1,
        "transfer_out": -1
    })

    transactions["expected_after"] = (
        transactions["balance_before"] +
        signed_amount * transactions["amount"]
    )

    transactions["arithmetic_error"] = (
        (
            transactions["balance_after"] -
            transactions["expected_after"]
        ).abs() > 0.011
    )

    check_result(
        "Incorrect transaction balance arithmetic",
        transactions["arithmetic_error"].sum()
    )

    # --------------------------------------------------
    # CHRONOLOGY AND BALANCE CONTINUITY
    # --------------------------------------------------

    print("\n--- CHRONOLOGY CHECKS ---")

    tx = transactions.merge(
        accounts[["account_id", "opened_date", "closed_date"]],
        on="account_id",
        how="left",
        validate="many_to_one"
    )

    check_result(
        "Transactions before account opening",
        (tx["transaction_date"] < tx["opened_date"]).sum()
    )

    check_result(
        "Transactions after account closure",
        (
            tx["closed_date"].notna() &
            (tx["transaction_date"] > tx["closed_date"])
        ).sum()
    )

    tx = tx.sort_values(
        ["account_id", "transaction_date", "transaction_id"]
    ).copy()

    tx["previous_after"] = (
        tx.groupby("account_id")["balance_after"].shift()
    )

    tx["continuity_error"] = (
        tx["previous_after"].notna() &
        (
            (
                tx["balance_before"] -
                tx["previous_after"]
            ).abs() > 0.011
        )
    )

    check_result(
        "Broken transaction balance continuity",
        tx["continuity_error"].sum()
    )

    # --------------------------------------------------
    # CURRENT BALANCE RECONCILIATION
    # --------------------------------------------------

    print("\n--- CURRENT BALANCE CHECK ---")

    last_tx = (
        tx.dropna(subset=["transaction_date"])
        .sort_values(["account_id", "transaction_date", "transaction_id"])
        .groupby("account_id")
        .tail(1)[["account_id", "balance_after"]]
        .rename(columns={
            "balance_after": "last_transaction_balance"
        })
    )

    check = accounts.merge(
        last_tx,
        on="account_id",
        how="left"
    )

    check["expected_current_balance"] = (
        check["last_transaction_balance"].fillna(
            check["opening_balance"]
        )
    )

    check["current_balance_error"] = (
        (
            check["current_balance"] -
            check["expected_current_balance"]
        ).abs() > 0.011
    )

    check_result(
        "Current balance mismatches",
        check["current_balance_error"].sum()
    )

    # --------------------------------------------------
    # ACCOUNT STATUS AND CLOSURE DATES
    # --------------------------------------------------

    print("\n--- ACCOUNT STATUS CHECKS ---")

    check_result(
        "Closed accounts without a closure date",
        (
            (accounts["status"] == "closed") &
            accounts["closed_date"].isna()
        ).sum()
    )

    check_result(
        "Non-closed accounts with a closure date",
        (
            (accounts["status"] != "closed") &
            accounts["closed_date"].notna()
        ).sum()
    )

    # --------------------------------------------------
    # EXPORT VALIDATION REPORTS
    # --------------------------------------------------


    tx[tx["arithmetic_error"]].to_csv(
        VALIDATION_DIR / "transaction_arithmetic_errors.csv",
        index=False
    )

    tx[tx["continuity_error"]].to_csv(
        VALIDATION_DIR / "transaction_continuity_errors.csv",
        index=False
    )

    check[check["current_balance_error"]].to_csv(
        VALIDATION_DIR / "current_balance_errors.csv",
        index=False
    )

    # Export validation summary
    summary = pd.DataFrame(
        validation_results.items(),
        columns=["validation_check", "error_count"]
    )

    summary.to_csv(
        VALIDATION_DIR / "validation_summary.csv",
        index=False
    )

    # --------------------------------------------------
    # FINAL VALIDATION RESULT
    # --------------------------------------------------

    print("\n" + "=" * 55)

    if validation_errors:

        print("VALIDATION FAILED")
        print("\nFailed checks:")

        for error in validation_errors:
            print(f"- {error}")

        print(f"\nTotal failed checks: {len(validation_errors)}")
        print(f"Reports saved to: {VALIDATION_DIR}")
        sys.exit(1)

    else:
        print("ALL VALIDATION CHECKS PASSED")
        sys.exit(0)


except Exception as e:

    print("\n" + "=" * 55)
    print("VALIDATION SCRIPT ERROR")
    print(f"Error: {e}")
    print("=" * 55)

    sys.exit(1)
