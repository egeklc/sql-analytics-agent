import pandas as pd
from datetime import date
from dateutil.relativedelta import relativedelta
import random
from unidecode import unidecode
from pathlib import Path
from config import DATA_DIR, FAKE_TR, CUSTOM_DATE


min_birth_date = CUSTOM_DATE - relativedelta(years=80)
max_birth_date = CUSTOM_DATE - relativedelta(years=18)



city_list = [
    "Balıkesir",
    "Bilecik",
    "Bursa",
    "Çanakkale",
    "Edirne",
    "İstanbul",
    "Kırklareli",
    "Kocaeli",
    "Sakarya",
    "Tekirdağ",
    "Yalova"
]

job_list = [
    "Teacher",
    "Doctor",
    "Engineer",
    "Lawyer",
    "Accountant",
    "Nurse",
    "Sales Representative",
    "Business Owner",
    "Student",
    "Retired"
]

def get_job(age):
    if age <= 25:
        weights = [4, 2, 4, 4, 4, 4, 4, 3, 80, 0]
    elif age <= 60:
        weights = [10, 8, 12, 10, 10, 8, 10, 12, 0, 2]
    else:
        weights = [5, 7, 8, 7, 7, 6, 5, 10, 0, 60]
    return random.choices(job_list, weights=weights, k=1)[0]

def get_segment(annual_income):
    if annual_income < 50000:
        return "Standard"
    elif annual_income < 100000 :
        return "Gold"
    else:
        return "Premium"

income_ranges = {
    "Teacher" : (30000, 80000),
    "Doctor" : (80000, 300000),
    "Engineer" : (50000, 150000),
    "Lawyer" : (60000, 250000),
    "Accountant" : (40000, 120000),
    "Nurse" : (35000, 80000),
    "Sales Representative" : (25000, 100000),
    "Business Owner" : (30000, 500000),
    "Student" : (3000, 25000),
    "Retired" : (15000, 60000)
}


def create_customers_csv(n_customers, csv_path):
    customers = []
    
    for n in range(1, n_customers + 1):
        customer_id = f"CUST{n:08d}"
        
        first_name = FAKE_TR.first_name()
        last_name = FAKE_TR.last_name()
        
        email = f"{first_name.lower()}.{last_name.lower()}{random.randint(0,999)}@{FAKE_TR.free_email_domain()}"
        email = unidecode(email)
        
        birth_date = FAKE_TR.date_between(start_date=min_birth_date, end_date=max_birth_date)
        age = relativedelta(CUSTOM_DATE, birth_date).years
        # phone_number = f"05{fake_tr.msisdn()[4:]}" # format 05XX XXX XX XX
        phone_number = FAKE_TR.numerify(text="05#########")
        
        city = random.choice(city_list)
        country = "Turkey"
        
        job = get_job(age)
        min_income, max_income = income_ranges[job]
        income = random.randrange(min_income, max_income+1 , 1000)
        segment = get_segment(income)
        
        eligible_date = birth_date + relativedelta(years=18)
        signup_date = FAKE_TR.date_between(start_date=eligible_date, end_date=CUSTOM_DATE)
        
        customers_dict = {"customer_id": customer_id, 
                            "first_name": first_name,
                            "last_name": last_name,
                            "email": email,
                            "phone_number": phone_number,
                            "city": city,
                            "country": country,
                            "birth_date": birth_date,
                            "occupation": job,
                            "income": income,
                            "signup_date": signup_date,
                            "segment": segment
                            }
        customers.append(customers_dict)
    df = pd.DataFrame(customers)
    df.to_csv(csv_path, index=False)

n_customers = 1000
customers_path = DATA_DIR / "customers.csv"
create_customers_csv(n_customers=n_customers, csv_path=customers_path)

