

def convert_currency(currency_type, balance):
    usd_rate = 45
    gold_rate = 5000
    if currency_type == "USD":
        return round(balance / usd_rate, 2)
    elif currency_type == "Gold":
        return round(balance / gold_rate, 4)
    else:
        return round(balance, 2)