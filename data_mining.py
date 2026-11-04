"""
ShopSmart AI - Data Mining Module
Implements advanced analytics, RFM Customer Segmentation, Sales Analysis,
and Product Demand Forecasting using Pandas.
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
from config import Config
from database import get_db_connection

def get_sales_overview():
    """Calculate overall high-level e-commerce performance metrics."""
    conn = get_db_connection()
    
    # Total revenue and orders
    orders_df = pd.read_sql_query("SELECT id, total_amount, created_at, status FROM orders;", conn)
    customers_df = pd.read_sql_query("SELECT id FROM customers WHERE role = 'customer';", conn)
    products_df = pd.read_sql_query("SELECT id, stock FROM products;", conn)
    
    conn.close()

    total_sales = float(orders_df['total_amount'].sum()) if not orders_df.empty else 0.0
    total_orders = int(len(orders_df))
    total_customers = int(len(customers_df))
    avg_order_value = float(orders_df['total_amount'].mean()) if total_orders > 0 else 0.0
    total_inventory = int(products_df['stock'].sum()) if not products_df.empty else 0

    return {
        "total_sales": round(total_sales, 2),
        "total_orders": total_orders,
        "total_customers": total_customers,
        "avg_order_value": round(avg_order_value, 2),
        "total_inventory": total_inventory
    }

def get_best_selling_products(limit=5):
    """Retrieve top selling products by units sold and generated revenue."""
    conn = get_db_connection()
    query = """
    SELECT 
        od.product_id,
        od.product_name,
        p.category,
        p.price,
        p.stock,
        p.rating,
        SUM(od.quantity) AS total_units_sold,
        ROUND(SUM(od.subtotal), 2) AS total_revenue
    FROM order_details od
    JOIN products p ON od.product_id = p.id
    GROUP BY od.product_id, od.product_name, p.category, p.price, p.stock, p.rating
    ORDER BY total_units_sold DESC
    LIMIT ?;
    """
    df = pd.read_sql_query(query, conn, params=(limit,))
    conn.close()
    return df.to_dict(orient='records')

def get_category_sales_breakdown():
    """Calculate sales revenue and quantity breakdown by product category."""
    conn = get_db_connection()
    query = """
    SELECT 
        p.category,
        COUNT(DISTINCT od.order_id) AS order_count,
        SUM(od.quantity) AS total_units,
        ROUND(SUM(od.subtotal), 2) AS category_revenue
    FROM order_details od
    JOIN products p ON od.product_id = p.id
    GROUP BY p.category
    ORDER BY category_revenue DESC;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df.to_dict(orient='records')

def perform_rfm_segmentation():
    """
    Perform RFM (Recency, Frequency, Monetary) Customer Segmentation.
    Data Mining technique to group customers based on purchasing behavior.
    """
    conn = get_db_connection()
    query = """
    SELECT 
        c.id AS customer_id,
        c.name AS customer_name,
        c.email,
        c.city,
        o.id AS order_id,
        o.total_amount,
        o.created_at AS order_date
    FROM customers c
    LEFT JOIN orders o ON c.id = o.customer_id
    WHERE c.role = 'customer';
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    if df.empty or df['order_id'].dropna().empty:
        return {"segments": [], "summary": {}}

    # Reference date is max order date in dataset
    df['order_date'] = pd.to_datetime(df['order_date'])
    reference_date = df['order_date'].max() + pd.Timedelta(days=1)

    # Compute Recency, Frequency, Monetary
    rfm = df.groupby(['customer_id', 'customer_name', 'email', 'city']).agg(
        recency=('order_date', lambda dates: (reference_date - dates.max()).days if pd.notnull(dates.max()) else 365),
        frequency=('order_id', lambda x: x.dropna().nunique()),
        monetary=('total_amount', lambda x: round(x.dropna().sum(), 2))
    ).reset_index()

    # Rule-based clustering for clear MCA interpretation
    def assign_segment(row):
        f = row['frequency']
        m = row['monetary']
        r = row['recency']
        
        if f >= 4 and m >= 8000:
            return "Champion Shoppers", "VIP Perks & Personalized AI Bundles", "badge-primary"
        elif f >= 3 and r <= 60:
            return "Loyal Customers", "Loyalty Rewards & Cross-Sell Discounts", "badge-success"
        elif f >= 1 and r <= 45:
            return "Potential Growth", "Targeted Welcome Offers & New Arrivals", "badge-info"
        elif f >= 2 and r > 90:
            return "At-Risk / Inactive", "Re-engagement Push & Winback Coupons", "badge-warning"
        else:
            return "Occasional Shoppers", "Nudge with Trending Products", "badge-secondary"

    results = rfm.apply(assign_segment, axis=1)
    rfm['segment'] = [res[0] for res in results]
    rfm['recommended_action'] = [res[1] for res in results]
    rfm['badge_class'] = [res[2] for res in results]

    # Segment summary breakdown
    segment_summary = rfm.groupby('segment').agg(
        customer_count=('customer_id', 'count'),
        total_revenue=('monetary', 'sum'),
        avg_spend=('monetary', 'mean')
    ).round(2).reset_index().to_dict(orient='records')

    top_customers = rfm.sort_values(by='monetary', ascending=False).head(15).to_dict(orient='records')

    return {
        "top_customers": top_customers,
        "segment_summary": segment_summary,
        "total_segmented": len(rfm)
    }

def predict_product_demand():
    """
    Data Mining Module: Product Demand Prediction.
    Calculates historical monthly sales velocity, moving average,
    and estimates forecasted demand for the upcoming 30 days.
    """
    conn = get_db_connection()
    query = """
    SELECT 
        p.id AS product_id,
        p.name AS product_name,
        p.category,
        p.price,
        p.stock AS current_stock,
        od.quantity,
        o.created_at AS order_date
    FROM products p
    LEFT JOIN order_details od ON p.id = od.product_id
    LEFT JOIN orders o ON od.order_id = o.id;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    if df.empty:
        return []

    df['order_date'] = pd.to_datetime(df['order_date'])
    
    forecasts = []
    for (prod_id, prod_name, cat, price, stock), group in df.groupby(['product_id', 'product_name', 'category', 'price', 'current_stock']):
        units_sold = group['quantity'].dropna().sum()
        
        # Calculate monthly average velocity
        if not group['order_date'].dropna().empty:
            date_range_days = max(1, (group['order_date'].max() - group['order_date'].min()).days)
            monthly_velocity = (units_sold / (date_range_days / 30.0))
        else:
            monthly_velocity = 5.0
            
        # Predict next 30-day demand applying a seasonal growth factor (8-15%)
        predicted_demand = int(np.ceil(monthly_velocity * 1.12))
        
        # Determine inventory recommendation
        if stock < predicted_demand:
            stock_status = "Reorder Urgently"
            status_badge = "badge-danger"
            recommended_procurement = predicted_demand * 2 - stock
        elif stock < predicted_demand * 1.5:
            stock_status = "Moderate Stock"
            status_badge = "badge-warning"
            recommended_procurement = predicted_demand
        else:
            stock_status = "Optimal Stock"
            status_badge = "badge-success"
            recommended_procurement = 0

        forecasts.append({
            "product_id": prod_id,
            "product_name": prod_name,
            "category": cat,
            "price": price,
            "current_stock": stock,
            "total_sold": int(units_sold),
            "monthly_velocity": round(monthly_velocity, 1),
            "predicted_demand_next_month": predicted_demand,
            "stock_status": stock_status,
            "status_badge": status_badge,
            "recommended_procurement": max(0, recommended_procurement)
        })

    # Sort by predicted demand
    forecasts.sort(key=lambda x: x['predicted_demand_next_month'], reverse=True)
    return forecasts

def export_cleaned_dataset_to_csv():
    """Export complete joined transaction dataset for Power BI visualization."""
    conn = get_db_connection()
    query = """
    SELECT 
        o.order_number,
        o.created_at AS order_date,
        c.name AS customer_name,
        c.city AS customer_city,
        c.state AS customer_state,
        p.name AS product_name,
        p.category AS product_category,
        od.quantity,
        od.unit_price,
        od.subtotal,
        o.payment_method,
        o.status AS order_status
    FROM orders o
    JOIN customers c ON o.customer_id = c.id
    JOIN order_details od ON o.id = od.order_id
    JOIN products p ON od.product_id = p.id
    ORDER BY o.created_at DESC;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    export_path = Config.DATA_DIR / 'shopsmart_cleaned_powerbi_dataset.csv'
    df.to_csv(export_path, index=False)
    return str(export_path), len(df)
