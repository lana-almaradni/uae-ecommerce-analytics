# ============================================================
# UAE E-Commerce Analytics — SQL + AI Insights
# Built in Hex using Python, DuckDB, and OpenAI API
# Author: Lana Al Maradni
# GitHub: https://github.com/lana-almaradni
# ============================================================


# ======================
# CELL 2 — DATA CREATION
# ======================

import pandas as pd
import numpy as np

np.random.seed(42)

# Customers table
customers = pd.DataFrame({
    'customer_id': range(1, 101),
    'customer_name': [f'Customer_{i}' for i in range(1, 101)],
    'city': np.random.choice(['Dubai', 'Abu Dhabi', 'Sharjah', 'Ajman'], 100),
    'segment': np.random.choice(['Retail', 'Wholesale', 'VIP'], 100)
})

# Products table
products = pd.DataFrame({
    'product_id': range(1, 21),
    'product_name': [f'Product_{i}' for i in range(1, 21)],
    'category': np.random.choice(['Electronics', 'Fashion', 'Home', 'Beauty', 'Sports'], 20),
    'price': np.round(np.random.uniform(20, 500, 20), 2)
})

# Orders table
orders = pd.DataFrame({
    'order_id': range(1, 301),
    'customer_id': np.random.randint(1, 101, 300),
    'product_id': np.random.randint(1, 21, 300),
    'order_date': pd.date_range(start='2024-01-01', periods=300, freq='D').strftime('%Y-%m-%d'),
    'quantity': np.random.randint(1, 10, 300),
    'status': np.random.choice(['Delivered', 'Returned', 'Pending'], 300, p=[0.7, 0.15, 0.15])
})

orders['total_amount'] = orders['quantity'] * orders['product_id'].map(products.set_index('product_id')['price'])


# ===========================
# CELL 3 — DUCKDB REGISTRATION
# ===========================

import duckdb

duckdb.register('customers', customers)
duckdb.register('products', products)
duckdb.register('orders', orders)

print("✅ Tables registered successfully!")


# ================================
# CELL 4 — QUERY 1: REVENUE BY CATEGORY
# ================================

result1 = duckdb.query("""
    SELECT 
        p.category,
        COUNT(o.order_id) AS total_orders,
        SUM(o.total_amount) AS total_revenue,
        ROUND(AVG(o.total_amount), 2) AS avg_order_value
    FROM orders o
    JOIN products p ON o.product_id = p.product_id
    WHERE o.status = 'Delivered'
    GROUP BY p.category
    ORDER BY total_revenue DESC
""").df()

print(result1)


# ===================================
# CELL 5 — QUERY 2: TOP 10 CUSTOMERS BY SPEND
# ===================================

result2 = duckdb.query("""
    SELECT 
        c.customer_name,
        c.city,
        c.segment,
        COUNT(o.order_id) AS total_orders,
        ROUND(SUM(o.total_amount), 2) AS total_spent
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    WHERE o.status = 'Delivered'
    GROUP BY c.customer_name, c.city, c.segment
    ORDER BY total_spent DESC
    LIMIT 10
""").df()

print(result2)


# ================================
# CELL 6 — QUERY 3: MONTHLY SALES TREND
# ================================

result3 = duckdb.query("""
    SELECT 
        STRFTIME('%Y-%m', CAST(order_date AS DATE)) AS month,
        COUNT(order_id) AS total_orders,
        ROUND(SUM(total_amount), 2) AS monthly_revenue
    FROM orders
    WHERE status = 'Delivered'
    GROUP BY month
    ORDER BY month ASC
""").df()

print(result3)


# ================================
# CELL 7 — QUERY 4: ORDERS BY STATUS
# ================================

result4 = duckdb.query("""
    SELECT 
        status,
        COUNT(order_id) AS total_orders,
        ROUND(SUM(total_amount), 2) AS total_value,
        ROUND(COUNT(order_id) * 100.0 / SUM(COUNT(order_id)) OVER(), 2) AS percentage
    FROM orders
    GROUP BY status
    ORDER BY total_orders DESC
""").df()

print(result4)


# =====================================
# CELL 8 — QUERY 5: CUSTOMER RETENTION
# =====================================

result5 = duckdb.query("""
    SELECT 
        c.city,
        c.segment,
        COUNT(DISTINCT c.customer_id) AS total_customers,
        COUNT(DISTINCT CASE WHEN order_count > 1 THEN c.customer_id END) AS repeat_customers,
        ROUND(COUNT(DISTINCT CASE WHEN order_count > 1 THEN c.customer_id END) * 100.0 / 
              COUNT(DISTINCT c.customer_id), 2) AS retention_rate
    FROM customers c
    LEFT JOIN (
        SELECT 
            customer_id,
            COUNT(order_id) AS order_count
        FROM orders
        WHERE status = 'Delivered'
        GROUP BY customer_id
    ) o ON c.customer_id = o.customer_id
    GROUP BY c.city, c.segment
    ORDER BY retention_rate DESC
""").df()

print(result5)


# ================================
# CELL 9 — QUERY 6: REVENUE BY CITY
# ================================

result6 = duckdb.query("""
    SELECT 
        c.city,
        COUNT(o.order_id) AS total_orders,
        ROUND(SUM(o.total_amount), 2) AS total_revenue,
        ROUND(AVG(o.total_amount), 2) AS avg_order_value,
        ROUND(SUM(o.total_amount) * 100.0 / SUM(SUM(o.total_amount)) OVER(), 2) AS revenue_share_pct
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    WHERE o.status = 'Delivered'
    GROUP BY c.city
    ORDER BY total_revenue DESC
""").df()

print(result6)


# ==============================
# CELL 10 — 4-CHART DASHBOARD
# ==============================

import matplotlib.pyplot as plt
from matplotlib.patches import Patch

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('UAE E-Commerce Analytics Dashboard', fontsize=16, fontweight='bold')

# Chart 1 — Revenue by Category
axes[0, 0].bar(result1['category'], result1['total_revenue'], color=['#2196F3', '#4CAF50', '#FF9800', '#E91E63', '#9C27B0'])
axes[0, 0].set_title('Revenue by Category (AED)')
axes[0, 0].set_xlabel('Category')
axes[0, 0].set_ylabel('Revenue (AED)')
axes[0, 0].tick_params(axis='x', rotation=15)

# Chart 2 — Monthly Revenue Trend
axes[0, 1].plot(result3['month'], result3['monthly_revenue'], marker='o', color='#2196F3', linewidth=2)
axes[0, 1].set_title('Monthly Revenue Trend (AED)')
axes[0, 1].set_xlabel('Month')
axes[0, 1].set_ylabel('Revenue (AED)')
axes[0, 1].tick_params(axis='x', rotation=45)

# Chart 3 — Orders by Status
axes[1, 0].pie(result4['total_orders'], labels=result4['status'], autopct='%1.1f%%', colors=['#4CAF50', '#FF9800', '#F44336'])
axes[1, 0].set_title('Orders by Status')

# Chart 4 — Top 10 Customers by Spend (colored by segment)
segment_colors = {'Wholesale': '#2196F3', 'VIP': '#9C27B0', 'Retail': '#4CAF50'}
bar_colors = result2['segment'].map(segment_colors)

axes[1, 1].barh(result2['customer_name'], result2['total_spent'], color=bar_colors)
axes[1, 1].set_title('Top 10 Customers by Spend (AED)')
axes[1, 1].set_xlabel('Total Spent (AED)')

legend_elements = [Patch(facecolor=v, label=k) for k, v in segment_colors.items()]
axes[1, 1].legend(handles=legend_elements, loc='lower right', fontsize=8)

plt.tight_layout()
plt.show()


# ==============================
# CELL 12 — AI EXECUTIVE SUMMARY
# ==============================

import requests

summary_data = f"""
E-Commerce Analytics Summary:

1. Revenue by Category:
{result1.to_string(index=False)}

2. Top 10 Customers:
{result2.to_string(index=False)}

3. Monthly Revenue Trend:
{result3.to_string(index=False)}

4. Orders by Status:
{result4.to_string(index=False)}

5. Customer Retention by City and Segment:
{result5.to_string(index=False)}

6. Revenue by City:
{result6.to_string(index=False)}
"""

response = requests.post(
    "https://api.openai.com/v1/chat/completions",
    headers={
        "Authorization": "Bearer your-api-key-here",
        "Content-Type": "application/json"
    },
    json={
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": f"""You are a senior business analyst.

Based on this UAE e-commerce data, write a short executive summary with:
1. Top 3 insights
2. Top 2 risks
3. One recommended action

Note: Pay special attention to the city-level revenue breakdown (Query 6)
and how it relates to customer retention patterns.

Keep it concise and business-focused.

{summary_data}"""
            }
        ]
    }
)

result = response.json()
print(result['choices'][0]['message']['content'])
