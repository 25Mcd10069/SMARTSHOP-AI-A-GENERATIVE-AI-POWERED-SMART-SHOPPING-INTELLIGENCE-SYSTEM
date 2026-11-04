"""
ShopSmart AI - Data Visualization Module
Generates high-resolution Matplotlib charts as Base64 encoded images
for real-time embedding in the Admin Sales Dashboard.
"""

import io
import base64
import os
from pathlib import Path
from config import Config

# Ensure writable Matplotlib config directory
mpl_dir = Config.DATA_DIR / '.matplotlib'
os.makedirs(mpl_dir, exist_ok=True)
os.environ['MPLCONFIGDIR'] = str(mpl_dir)

import matplotlib
matplotlib.use('Agg') # Headless backend for web server
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from database import get_db_connection

# Modern Color Palette
PRIMARY_BLUE = "#2563eb"
ACCENT_PURPLE = "#7c3aed"
TEAL = "#0d9488"
AMBER = "#f59e0b"
ROSE = "#e11d48"
PALETTE = [PRIMARY_BLUE, ACCENT_PURPLE, TEAL, AMBER, ROSE, "#6366f1", "#059669"]

def fig_to_base64(fig):
    """Convert Matplotlib figure to Base64 data URI string."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=130, facecolor='#ffffff')
    plt.close(fig)
    buf.seek(0)
    img_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{img_b64}"

def generate_monthly_sales_chart():
    """1. Monthly Sales Revenue Trend (Line Chart with Area Fill)"""
    conn = get_db_connection()
    query = """
    SELECT 
        strftime('%Y-%m', created_at) AS month_year,
        ROUND(SUM(total_amount), 2) AS monthly_revenue
    FROM orders
    GROUP BY month_year
    ORDER BY month_year ASC;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    if df.empty:
        df = pd.DataFrame({"month_year": ["2025-06", "2025-07", "2025-08"], "monthly_revenue": [10000, 15000, 20000]})

    fig, ax = plt.subplots(figsize=(7, 3.8))
    
    x = range(len(df))
    y = df['monthly_revenue']
    
    # Line plot with markers
    ax.plot(x, y, color=PRIMARY_BLUE, marker='o', linewidth=2.5, markersize=6, label='Monthly Revenue (₹)')
    ax.fill_between(x, y, color=PRIMARY_BLUE, alpha=0.15)

    # Styling
    ax.set_title("Monthly Sales Trend (₹)", fontsize=13, fontweight='bold', pad=12, color='#1e293b')
    ax.set_xticks(x)
    ax.set_xticklabels(df['month_year'], rotation=35, ha='right', fontsize=9, color='#475569')
    ax.set_ylabel("Revenue (₹)", fontsize=10, color='#475569')
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#cbd5e1')
    ax.spines['bottom'].set_color('#cbd5e1')
    
    # Value annotations on points
    for i, txt in enumerate(y):
        ax.annotate(f"₹{int(txt):,}", (x[i], y[i]), textcoords="offset points", xytext=(0, 7), ha='center', fontsize=8, color='#0f172a', fontweight='semibold')

    return fig_to_base64(fig)

def generate_category_sales_chart():
    """2. Category-wise Sales Distribution (Donut Chart)"""
    conn = get_db_connection()
    query = """
    SELECT 
        p.category,
        ROUND(SUM(od.subtotal), 2) AS category_revenue
    FROM order_details od
    JOIN products p ON od.product_id = p.id
    GROUP BY p.category
    ORDER BY category_revenue DESC;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    if df.empty:
        df = pd.DataFrame({"category": ["Electronics", "Fashion", "Home"], "category_revenue": [5000, 3000, 2000]})

    fig, ax = plt.subplots(figsize=(6, 3.8))
    wedges, texts, autotexts = ax.pie(
        df['category_revenue'],
        labels=df['category'],
        autopct='%1.1f%%',
        startangle=140,
        colors=PALETTE[:len(df)],
        wedgeprops=dict(width=0.45, edgecolor='white', linewidth=2),
        pctdistance=0.75
    )

    for at in autotexts:
        at.set_fontsize(9)
        at.set_fontweight('bold')
        at.set_color('#1e293b')

    for t in texts:
        t.set_fontsize(9)
        t.set_color('#334155')

    ax.set_title("Category-wise Revenue Share", fontsize=13, fontweight='bold', pad=12, color='#1e293b')
    return fig_to_base64(fig)

def generate_top_products_chart():
    """3. Top-selling Products by Units Sold (Horizontal Bar Chart)"""
    conn = get_db_connection()
    query = """
    SELECT 
        od.product_name,
        SUM(od.quantity) AS total_units
    FROM order_details od
    GROUP BY od.product_name
    ORDER BY total_units DESC
    LIMIT 6;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    if df.empty:
        df = pd.DataFrame({"product_name": ["Prod A", "Prod B"], "total_units": [20, 15]})

    # Truncate long names for chart readability
    df['short_name'] = df['product_name'].apply(lambda s: s[:24] + '...' if len(s) > 24 else s)
    df = df.iloc[::-1] # Reverse to display top at the top of horizontal chart

    fig, ax = plt.subplots(figsize=(6.5, 3.8))
    bars = ax.barh(df['short_name'], df['total_units'], color=ACCENT_PURPLE, height=0.55, alpha=0.85)

    ax.set_title("Top 6 Best-Selling Products (Units)", fontsize=13, fontweight='bold', pad=12, color='#1e293b')
    ax.set_xlabel("Units Sold", fontsize=10, color='#475569')
    ax.grid(axis='x', linestyle='--', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#cbd5e1')
    ax.spines['bottom'].set_color('#cbd5e1')

    # Label on end of bars
    for bar in bars:
        w = bar.get_width()
        ax.annotate(f" {int(w)} pcs", xy=(w, bar.get_y() + bar.get_height() / 2),
                    xytext=(3, 0), textcoords="offset points", ha='left', va='center',
                    fontsize=8, fontweight='semibold', color='#334155')

    return fig_to_base64(fig)

def generate_customer_trends_chart():
    """4. Customer Purchase Trends by Payment Method & Volume"""
    conn = get_db_connection()
    query = """
    SELECT 
        payment_method,
        COUNT(id) AS order_count,
        ROUND(SUM(total_amount), 2) AS total_value
    FROM orders
    GROUP BY payment_method
    ORDER BY order_count DESC;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    fig, ax = plt.subplots(figsize=(6.5, 3.8))
    colors = [TEAL, PRIMARY_BLUE, AMBER, ROSE]
    bars = ax.bar(df['payment_method'], df['order_count'], color=colors[:len(df)], width=0.5, alpha=0.9)

    ax.set_title("Customer Payment Preferences", fontsize=13, fontweight='bold', pad=12, color='#1e293b')
    ax.set_ylabel("Order Count", fontsize=10, color='#475569')
    ax.tick_params(axis='x', rotation=15, labelsize=9)
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#cbd5e1')
    ax.spines['bottom'].set_color('#cbd5e1')

    for bar in bars:
        h = bar.get_height()
        ax.annotate(f"{int(h)} orders", xy=(bar.get_x() + bar.get_width() / 2, h),
                    xytext=(0, 4), textcoords="offset points", ha='center', va='bottom',
                    fontsize=8, fontweight='semibold', color='#334155')

    return fig_to_base64(fig)

def generate_product_ratings_chart():
    """5. Product Ratings Distribution (1 to 5 Stars)"""
    conn = get_db_connection()
    query = """
    SELECT 
        rating,
        COUNT(id) AS review_count
    FROM reviews
    GROUP BY rating
    ORDER BY rating ASC;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    # Ensure all ratings 1 to 5 exist
    all_ratings = pd.DataFrame({"rating": [1, 2, 3, 4, 5]})
    df = all_ratings.merge(df, on='rating', how='left').fillna(0)

    fig, ax = plt.subplots(figsize=(6, 3.8))
    rating_labels = [f"{int(r)} ★" for r in df['rating']]
    star_colors = ["#ef4444", "#f97316", "#eab308", "#84cc16", "#22c55e"]
    bars = ax.bar(rating_labels, df['review_count'], color=star_colors, width=0.52)

    ax.set_title("Customer Product Ratings Distribution", fontsize=13, fontweight='bold', pad=12, color='#1e293b')
    ax.set_ylabel("Number of Reviews", fontsize=10, color='#475569')
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#cbd5e1')
    ax.spines['bottom'].set_color('#cbd5e1')

    for bar in bars:
        h = bar.get_height()
        ax.annotate(f"{int(h)}", xy=(bar.get_x() + bar.get_width() / 2, h),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom',
                    fontsize=9, fontweight='semibold', color='#334155')

    return fig_to_base64(fig)

def get_all_dashboard_charts():
    """Generate all 5 visualization charts for the admin dashboard."""
    return {
        "monthly_sales": generate_monthly_sales_chart(),
        "category_sales": generate_category_sales_chart(),
        "top_products": generate_top_products_chart(),
        "customer_trends": generate_customer_trends_chart(),
        "product_ratings": generate_product_ratings_chart()
    }
