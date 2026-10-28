# Online Shopping Transaction Analysis System

Flask + SQLite web app that imports online-store order data (CSV) and analyses it:
revenue, orders, customers, average order value, repeat-customer rate, return and cancel rates,
monthly sales trend, revenue by category, payment-method split, top products and top customers,
with date-range filtering and interactive charts.

## Run (Windows PowerShell)
    py -m venv venv
    .\venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    python generate_sample_data.py
    python app.py

Open http://127.0.0.1:5000, go to **Upload data**, and import `data/sample_transactions.csv`.

## CSV format
order_id, order_date (YYYY-MM-DD), customer_id, product, category, quantity, unit_price, payment_method, status
