"""
generate_data.py
Generates a realistic 50,000-row e-commerce transaction dataset.
"""
import numpy as np
import pandas as pd

np.random.seed(42)
N = 50000

# Customer IDs (some repeat — simulating returning customers)
customer_ids = np.random.choice(range(1000, 11000), size=N)

# Product categories
categories = ['Electronics', 'Fashion', 'Home & Kitchen', 'Books', 'Beauty', 'Sports', 'Toys']
cat_weights = [0.20, 0.25, 0.15, 0.10, 0.12, 0.10, 0.08]
product_category = np.random.choice(categories, size=N, p=cat_weights)

# Order values based on category
base_price = {'Electronics': 150, 'Fashion': 60, 'Home & Kitchen': 80,
              'Books': 20, 'Beauty': 40, 'Sports': 70, 'Toys': 35}
order_value = np.array([
    max(5, np.random.normal(base_price[c], base_price[c] * 0.4))
    for c in product_category
]).round(2)

# Dates over 2 years
start = pd.Timestamp('2023-01-01')
end   = pd.Timestamp('2024-12-31')
days  = (end - start).days
order_date = [start + pd.Timedelta(days=int(np.random.randint(0, days))) for _ in range(N)]

# Sessions per month (proxy for engagement)
session_count = np.random.poisson(lam=4, size=N) + 1

# Pages viewed per session
pages_viewed = np.random.poisson(lam=6, size=N) + 1

# Device type
device = np.random.choice(['Mobile', 'Desktop', 'Tablet'], size=N, p=[0.55, 0.35, 0.10])

# Payment method
payment = np.random.choice(['Credit Card', 'UPI', 'Debit Card', 'Wallet', 'COD'],
                            size=N, p=[0.30, 0.28, 0.20, 0.12, 0.10])

# Returns (10% chance, higher for Fashion & Electronics)
return_prob = np.where(np.isin(product_category, ['Fashion', 'Electronics']), 0.15, 0.07)
returned = np.array([np.random.binomial(1, p) for p in return_prob])

# Discount applied
discount_pct = np.random.choice([0, 5, 10, 15, 20, 25], size=N, p=[0.40, 0.15, 0.20, 0.12, 0.08, 0.05])

# Customer age group
age_group = np.random.choice(['18-24', '25-34', '35-44', '45-54', '55+'],
                               size=N, p=[0.20, 0.35, 0.25, 0.12, 0.08])

# Region
region = np.random.choice(['North', 'South', 'East', 'West', 'Central'],
                            size=N, p=[0.22, 0.28, 0.18, 0.20, 0.12])

df = pd.DataFrame({
    'customer_id':       customer_ids,
    'order_date':        order_date,
    'product_category':  product_category,
    'order_value':       order_value,
    'session_count':     session_count,
    'pages_viewed':      pages_viewed,
    'device':            device,
    'payment_method':    payment,
    'returned':          returned,
    'discount_pct':      discount_pct,
    'age_group':         age_group,
    'region':            region
})

df.to_csv('ecommerce_data.csv', index=False)
print(f"Dataset saved: {len(df):,} rows, {df.shape[1]} columns")
print(df.head())
