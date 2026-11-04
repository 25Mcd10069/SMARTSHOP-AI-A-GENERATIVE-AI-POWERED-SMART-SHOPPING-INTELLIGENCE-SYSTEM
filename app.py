"""
ShopSmart AI - Flask Web Application Backend
Main entry point orchestrating e-commerce workflows, Generative AI modules,
Admin Sales Dashboard, and Data Warehouse interactions.
"""

import os
import random
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config
from database import get_db_connection, init_db
from etl_pipeline import run_etl_pipeline
from data_mining import (
    get_sales_overview,
    get_best_selling_products,
    get_category_sales_breakdown,
    perform_rfm_segmentation,
    predict_product_demand,
    export_cleaned_dataset_to_csv
)
from visualization import get_all_dashboard_charts
from ai_service import (
    generate_shopping_personality,
    analyze_product_reviews,
    battle_products,
    is_gemini_configured
)
from aws_cloud.s3_storage import backup_data_to_s3

app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY

# Ensure database exists upon startup
if not Config.DATABASE_PATH.exists():
    print("[Server Startup] Database not found. Executing ETL pipeline to seed data...")
    run_etl_pipeline()

# Inject cart count & login status into all Jinja templates
@app.context_processor
def inject_global_data():
    cart = session.get('cart', {})
    cart_count = sum(item.get('quantity', 1) for item in cart.values())
    return {
        'cart_count': cart_count,
        'current_user': {
            'id': session.get('user_id'),
            'name': session.get('user_name'),
            'email': session.get('user_email'),
            'role': session.get('user_role', 'guest')
        },
        'gemini_configured': is_gemini_configured()
    }

# ==========================================================
# PAGE 1: Home Page
# ==========================================================
@app.route('/')
def home():
    """Home page displaying hero banner, categories, and featured products."""
    conn = get_db_connection()
    # Featured 6 top-rated products
    featured = conn.execute("""
        SELECT id, name, category, price, rating, review_count, image_url, description 
        FROM products 
        ORDER BY rating DESC, review_count DESC 
        LIMIT 6;
    """).fetchall()

    # Category counts
    categories = conn.execute("""
        SELECT category, COUNT(id) AS count, MIN(image_url) AS sample_img 
        FROM products 
        GROUP BY category;
    """).fetchall()
    conn.close()

    return render_template('index.html', featured_products=featured, categories=categories)

# ==========================================================
# PAGE 2: Authentication (Login, Register, Logout)
# ==========================================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    """User and Admin login with password validation and session creation."""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()

        if not email or not password:
            flash("Please enter both email and password.", "danger")
            return render_template('login.html')

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM customers WHERE email = ?;", (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            session['user_role'] = user['role']
            flash(f"Welcome back, {user['name']}!", "success")
            next_url = request.args.get('next')
            if user['role'] == 'admin':
                return redirect(next_url or url_for('admin_dashboard'))
            return redirect(next_url or url_for('home'))
        else:
            flash("Invalid email or password. Please try again.", "danger")

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration with input validation and database insert."""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        city = request.form.get('city', 'Mumbai').strip()
        state = request.form.get('state', 'Maharashtra').strip()

        # Validation
        if not name or not email or not password:
            flash("All fields (Name, Email, Password) are required.", "danger")
            return render_template('register.html')
        
        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return render_template('register.html')

        conn = get_db_connection()
        existing = conn.execute("SELECT id FROM customers WHERE email = ?;", (email,)).fetchone()
        if existing:
            conn.close()
            flash("An account with this email already exists. Please log in.", "warning")
            return redirect(url_for('login'))

        password_hash = generate_password_hash(password)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO customers (name, email, password_hash, role, city, state)
            VALUES (?, ?, ?, 'customer', ?, ?);
        """, (name, email, password_hash, city, state))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()

        # Auto-login after registration
        session['user_id'] = user_id
        session['user_name'] = name
        session['user_email'] = email
        session['user_role'] = 'customer'
        flash("Registration successful! Welcome to ShopSmart AI.", "success")
        return redirect(url_for('home'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    """Log out user and clear session credentials."""
    session.pop('user_id', None)
    session.pop('user_name', None)
    session.pop('user_email', None)
    session.pop('user_role', None)
    flash("You have been signed out successfully.", "info")
    return redirect(url_for('home'))

# ==========================================================
# PAGE 3: Products Page (Catalog, Search & Filter)
# ==========================================================
@app.route('/products')
def products():
    """Display product catalog with search, category filtering, and sorting."""
    search_query = request.args.get('search', '').strip()
    category_filter = request.args.get('category', '').strip()
    sort_by = request.args.get('sort', 'rating_desc')

    conn = get_db_connection()
    query = "SELECT * FROM products WHERE 1=1"
    params = []

    if search_query:
        query += " AND (name LIKE ? OR description LIKE ? OR features LIKE ?)"
        wildcard = f"%{search_query}%"
        params.extend([wildcard, wildcard, wildcard])

    if category_filter and category_filter != 'All':
        query += " AND category = ?"
        params.append(category_filter)

    # Sorting
    if sort_by == 'price_asc':
        query += " ORDER BY price ASC"
    elif sort_by == 'price_desc':
        query += " ORDER BY price DESC"
    elif sort_by == 'name_asc':
        query += " ORDER BY name ASC"
    else: # rating_desc
        query += " ORDER BY rating DESC, review_count DESC"

    products_list = conn.execute(query, params).fetchall()

    # Get distinct categories for the filter pill bar
    categories = conn.execute("SELECT DISTINCT category FROM products ORDER BY category;").fetchall()
    conn.close()

    return render_template(
        'products.html',
        products=products_list,
        categories=[c['category'] for c in categories],
        selected_category=category_filter or 'All',
        search_query=search_query,
        selected_sort=sort_by
    )

# ==========================================================
# PAGE 4: Shopping Cart & Checkout
# ==========================================================
@app.route('/cart')
def view_cart():
    """Display cart contents, subtotal, taxes/shipping, and grand total."""
    cart = session.get('cart', {})
    cart_items = []
    subtotal = 0.0

    conn = get_db_connection()
    for prod_id_str, item in cart.items():
        prod_id = int(prod_id_str)
        product = conn.execute("SELECT * FROM products WHERE id = ?;", (prod_id,)).fetchone()
        if product:
            qty = item.get('quantity', 1)
            line_total = product['price'] * qty
            subtotal += line_total
            cart_items.append({
                'product': dict(product),
                'quantity': qty,
                'line_total': round(line_total, 2)
            })
    conn.close()

    # Free shipping on orders over ₹999, else ₹99
    shipping = 0.0 if subtotal >= 999.0 or subtotal == 0 else 99.0
    grand_total = subtotal + shipping

    return render_template(
        'cart.html',
        cart_items=cart_items,
        subtotal=round(subtotal, 2),
        shipping=round(shipping, 2),
        grand_total=round(grand_total, 2)
    )

@app.route('/cart/add', methods=['POST'])
def add_to_cart():
    """Add a product to cart (supports both AJAX JSON and form POST)."""
    product_id = request.form.get('product_id') or (request.json and request.json.get('product_id'))
    quantity = int(request.form.get('quantity') or (request.json and request.json.get('quantity')) or 1)

    if not product_id:
        if request.is_json:
            return jsonify({'status': 'error', 'message': 'Missing product_id'}), 400
        flash("Product not found.", "danger")
        return redirect(url_for('products'))

    conn = get_db_connection()
    product = conn.execute("SELECT id, name, price, stock FROM products WHERE id = ?;", (product_id,)).fetchone()
    conn.close()

    if not product:
        if request.is_json:
            return jsonify({'status': 'error', 'message': 'Product does not exist'}), 404
        flash("Product does not exist.", "danger")
        return redirect(url_for('products'))

    cart = session.get('cart', {})
    prod_key = str(product_id)

    if prod_key in cart:
        cart[prod_key]['quantity'] += quantity
    else:
        cart[prod_key] = {'quantity': quantity}

    session['cart'] = cart
    session.modified = True

    total_cart_count = sum(item['quantity'] for item in cart.values())

    if request.is_json:
        return jsonify({
            'status': 'success',
            'message': f"Added '{product['name']}' to cart!",
            'cart_count': total_cart_count
        })

    flash(f"Added '{product['name']}' to your shopping cart.", "success")
    return redirect(request.referrer or url_for('products'))

@app.route('/cart/update', methods=['POST'])
def update_cart():
    """Update item quantity or remove item."""
    data = request.json or request.form
    product_id = str(data.get('product_id'))
    action = data.get('action') # 'increase', 'decrease', 'set', 'remove'

    cart = session.get('cart', {})
    if product_id in cart:
        if action == 'increase':
            cart[product_id]['quantity'] += 1
        elif action == 'decrease':
            cart[product_id]['quantity'] -= 1
            if cart[product_id]['quantity'] <= 0:
                del cart[product_id]
        elif action == 'remove':
            del cart[product_id]
        elif action == 'set':
            new_qty = int(data.get('quantity', 1))
            if new_qty > 0:
                cart[product_id]['quantity'] = new_qty
            else:
                del cart[product_id]

    session['cart'] = cart
    session.modified = True

    if request.is_json:
        total_cart_count = sum(item['quantity'] for item in cart.values())
        return jsonify({'status': 'success', 'cart_count': total_cart_count})

    return redirect(url_for('view_cart'))

@app.route('/cart/clear')
def clear_cart():
    """Clear all items from the shopping cart."""
    session['cart'] = {}
    session.modified = True
    flash("Shopping cart cleared.", "info")
    return redirect(url_for('view_cart'))

@app.route('/checkout', methods=['POST'])
def checkout():
    """Process order placement and generate invoice."""
    cart = session.get('cart', {})
    if not cart:
        flash("Your cart is empty. Add products before placing an order.", "warning")
        return redirect(url_for('products'))

    # Retrieve form data
    full_name = request.form.get('full_name', '').strip() or session.get('user_name', 'Guest Shopper')
    email = request.form.get('email', '').strip().lower() or session.get('user_email', 'guest@example.com')
    shipping_address = request.form.get('address', '101 Cyber Hub, Pune, Maharashtra').strip()
    payment_method = request.form.get('payment_method', 'UPI / GPay')

    conn = get_db_connection()
    cursor = conn.cursor()

    # Calculate final total and assemble order details
    order_items = []
    subtotal = 0.0

    for prod_id_str, item in cart.items():
        prod_id = int(prod_id_str)
        product = cursor.execute("SELECT id, name, price, stock FROM products WHERE id = ?;", (prod_id,)).fetchone()
        if product:
            qty = item['quantity']
            item_subtotal = round(product['price'] * qty, 2)
            subtotal += item_subtotal
            order_items.append({
                'product_id': product['id'],
                'product_name': product['name'],
                'quantity': qty,
                'unit_price': product['price'],
                'subtotal': item_subtotal
            })

    shipping = 0.0 if subtotal >= 999.0 else 99.0
    total_amount = round(subtotal + shipping, 2)

    # Generate unique order number
    now = datetime.now()
    random_suffix = random.randint(1000, 9999)
    order_number = f"ORD-{now.year}{now.month:02d}{now.day:02d}-{random_suffix}"

    customer_id = session.get('user_id')

    # Insert Order Header
    cursor.execute("""
        INSERT INTO orders (order_number, customer_id, customer_name, customer_email, total_amount, shipping_address, payment_method, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'Confirmed', ?);
    """, (order_number, customer_id, full_name, email, total_amount, shipping_address, payment_method, now.strftime("%Y-%m-%d %H:%M:%S")))
    order_id = cursor.lastrowid

    # Insert Order Details
    for item in order_items:
        cursor.execute("""
            INSERT INTO order_details (order_id, product_id, product_name, quantity, unit_price, subtotal)
            VALUES (?, ?, ?, ?, ?, ?);
        """, (order_id, item['product_id'], item['product_name'], item['quantity'], item['unit_price'], item['subtotal']))

        # Deduct stock
        cursor.execute("UPDATE products SET stock = MAX(0, stock - ?) WHERE id = ?;", (item['quantity'], item['product_id']))

    conn.commit()
    conn.close()

    # Empty cart
    session['cart'] = {}
    session.modified = True

    flash("Thank you! Your order has been placed successfully.", "success")
    return redirect(url_for('order_confirmation', order_number=order_number))

@app.route('/order-confirmation/<order_number>')
def order_confirmation(order_number):
    """Display final order confirmation and itemized invoice."""
    conn = get_db_connection()
    order = conn.execute("SELECT * FROM orders WHERE order_number = ?;", (order_number,)).fetchone()
    if not order:
        conn.close()
        flash("Order not found.", "danger")
        return redirect(url_for('home'))

    items = conn.execute("""
        SELECT od.*, p.image_url, p.category 
        FROM order_details od
        LEFT JOIN products p ON od.product_id = p.id
        WHERE od.order_id = ?;
    """, (order['id'],)).fetchall()
    conn.close()

    return render_template('order_confirmation.html', order=order, items=items)

# ==========================================================
# PAGE 5: Admin Sales Dashboard & Data Mining
# ==========================================================
@app.route('/admin')
def admin_dashboard():
    """
    Admin Sales Dashboard showing:
    - Total Sales, Orders, Customers
    - Matplotlib dynamic charts
    - RFM Customer Segmentation
    - Product Demand Forecasting
    - Top Selling Products
    """
    overview = get_sales_overview()
    best_sellers = get_best_selling_products(limit=8)
    category_sales = get_category_sales_breakdown()
    rfm_data = perform_rfm_segmentation()
    demand_predictions = predict_product_demand()[:10]
    charts = get_all_dashboard_charts()

    return render_template(
        'admin_dashboard.html',
        overview=overview,
        best_sellers=best_sellers,
        category_sales=category_sales,
        rfm_data=rfm_data,
        demand_predictions=demand_predictions,
        charts=charts
    )

@app.route('/admin/export-csv')
def export_csv():
    """Export cleaned sales transaction data as CSV for Power BI / Excel."""
    file_path, row_count = export_cleaned_dataset_to_csv()
    flash(f"Successfully generated Power BI ready dataset ({row_count} records).", "success")
    return send_file(file_path, as_attachment=True, download_name="shopsmart_powerbi_sales_data.csv")

@app.route('/admin/cloud-sync', methods=['POST'])
def cloud_sync():
    """Trigger AWS S3 cloud backup sync."""
    result = backup_data_to_s3()
    return jsonify(result)

@app.route('/admin/run-etl', methods=['POST'])
def trigger_etl():
    """Manually re-run the ETL pipeline from the Admin dashboard."""
    result = run_etl_pipeline()
    flash("ETL Pipeline executed: Data Warehouse refreshed successfully!", "success")
    return redirect(url_for('admin_dashboard'))

# ==========================================================
# PAGE 6: Unique Generative AI Module ("ShopSmart AI Intelligence")
# ==========================================================
@app.route('/ai-intelligence')
def ai_intelligence():
    """Main landing page for the three Unique Generative AI modules."""
    conn = get_db_connection()
    products = conn.execute("SELECT id, name, category, price, rating FROM products ORDER BY name ASC;").fetchall()
    conn.close()

    return render_template('ai_intelligence.html', products=products)

# REST API Handlers for the 3 Generative AI Features
@app.route('/api/ai/personality', methods=['POST'])
def api_shopping_personality():
    """Feature 1: Shopping Personality AI API"""
    data = request.json or {}
    persona = data.get('persona', '').strip()
    budget = data.get('budget', 2000.0)

    if not persona:
        return jsonify({'status': 'error', 'message': 'Please describe your shopping requirements or persona.'}), 400

    result = generate_shopping_personality(persona, budget)
    return jsonify(result)

@app.route('/api/ai/review-detective', methods=['POST'])
def api_review_detective():
    """Feature 2: Review Detective AI API"""
    data = request.json or {}
    product_id = data.get('product_id')

    if not product_id:
        return jsonify({'status': 'error', 'message': 'Please select a product to analyze.'}), 400

    result = analyze_product_reviews(int(product_id))
    return jsonify(result)

@app.route('/api/ai/product-battle', methods=['POST'])
def api_product_battle():
    """Feature 3: Smart Product Battle AI API"""
    data = request.json or {}
    prod_id_1 = data.get('product_id_1')
    prod_id_2 = data.get('product_id_2')
    preference = data.get('preference', 'Best Value & Longevity')

    if not prod_id_1 or not prod_id_2:
        return jsonify({'status': 'error', 'message': 'Please select two products to compare.'}), 400

    if str(prod_id_1) == str(prod_id_2):
        return jsonify({'status': 'error', 'message': 'Please select two different products for the battle.'}), 400

    result = battle_products(int(prod_id_1), int(prod_id_2), preference)
    return jsonify(result)

# ==========================================================
# Run Application
# ==========================================================
if __name__ == '__main__':
    print("=" * 65)
    print(" >>> ShopSmart AI – Smart Shopping Intelligence System <<<")
    print(" - Server running locally at: http://127.0.0.1:5000")
    print(" - Admin Sales Dashboard:     http://127.0.0.1:5000/admin")
    print(" - Generative AI Module:      http://127.0.0.1:5000/ai-intelligence")
    print("=" * 65)
    app.run(host='0.0.0.0', port=5000, debug=True)
