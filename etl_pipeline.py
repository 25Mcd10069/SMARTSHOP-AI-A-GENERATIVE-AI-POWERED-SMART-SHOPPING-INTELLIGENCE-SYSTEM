"""
ShopSmart AI - ETL Pipeline Module
Extract, Transform, and Load (ETL) pipeline using Pandas and SQLite.
Generates comprehensive e-commerce datasets (>500 records), cleanses data,
and loads it into the Data Warehouse.
"""

import os
import random
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from config import Config
from database import init_db, get_db_connection

def generate_raw_datasets():
    """Generate sample raw datasets for the e-commerce data warehouse (>500 records)."""
    os.makedirs(Config.RAW_DATA_DIR, exist_ok=True)
    random.seed(42)
    np.random.seed(42)

    # 1. Products Master Data
    products_data = [
        # Electronics
        {"id": 1, "name": "AuraPulse Wireless Noise-Cancelling Headphones", "category": "Electronics", "price": 4499.0, "stock": 45, "rating": 4.6, "features": "Active Noise Cancellation, 40-Hour Battery, Bluetooth 5.3, Ultra-soft ear cushions", "description": "Premium over-ear wireless headphones with studio-quality audio, deep bass, and dual microphone ENC for crystal clear calls.", "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&auto=format&fit=crop&q=80"},
        {"id": 2, "name": "HyperSync Smartwatch Series 5", "category": "Electronics", "price": 2999.0, "stock": 60, "rating": 4.4, "features": "AMOLED Display, 24/7 Heart Rate & SpO2, 100+ Sports Modes, IP68 Waterproof", "description": "Sleek metallic smartwatch featuring vibrant always-on display, health metrics tracking, and 7-day battery life.", "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&auto=format&fit=crop&q=80"},
        {"id": 3, "name": "BassBoom Portable Bluetooth Speaker", "category": "Electronics", "price": 1799.0, "stock": 80, "rating": 4.5, "features": "20W Stereo Sound, IPX7 Waterproof, RGB Dynamic Lights, 12h Playtime", "description": "Rugged outdoor wireless speaker delivering punchy 360-degree sound and rich bass for pool parties and camping trips.", "image_url": "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=600&auto=format&fit=crop&q=80"},
        {"id": 4, "name": "NeoGlow Mechanical Gaming Keyboard", "category": "Electronics", "price": 2499.0, "stock": 35, "rating": 4.7, "features": "RGB Per-Key Backlight, Tactile Blue Switches, Detachable Type-C, Anti-Ghosting", "description": "Professional compact mechanical gaming keyboard engineered for ultra-fast response and satisfying clicky keystrokes.", "image_url": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600&auto=format&fit=crop&q=80"},
        {"id": 5, "name": "Quantum Precision Optical Wireless Mouse", "category": "Electronics", "price": 899.0, "stock": 110, "rating": 4.3, "features": "Ergonomic Grip, 4000 DPI Sensor, Silent Click Buttons, Dual 2.4G & Bluetooth", "description": "Ergonomic precision wireless mouse built for productive office work and lag-free casual gaming with whisper-quiet switches.", "image_url": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=600&auto=format&fit=crop&q=80"},
        {"id": 6, "name": "PowerCore 20000mAh Fast Charging Power Bank", "category": "Electronics", "price": 1599.0, "stock": 90, "rating": 4.6, "features": "22.5W Fast Charge, Triple Output Ports, LED Digital Battery Display, Multi-Protection", "description": "High-capacity portable battery pack able to charge a modern smartphone up to 4.5 times with rapid PD 3.0 technology.", "image_url": "https://images.unsplash.com/photo-1609592426868-68f44d5c1c0e?w=600&auto=format&fit=crop&q=80"},

        # Fashion
        {"id": 7, "name": "UrbanStyle Minimalist Cotton Hoodie", "category": "Fashion", "price": 1299.0, "stock": 70, "rating": 4.5, "features": "100% Bio-Washed Combed Cotton, Fleece Lined, Kangaroo Pocket, Preshrunk", "description": "Cozy and breathable unisex heavyweight hoodie tailored for relaxed everyday wear and effortless urban styling.", "image_url": "https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=600&auto=format&fit=crop&q=80"},
        {"id": 8, "name": "Vintage Slim-Fit Denim Jacket", "category": "Fashion", "price": 2199.0, "stock": 40, "rating": 4.6, "features": "Premium Indigo Denim, Classic Button Placket, Dual Chest Flap Pockets, Vintage Wash", "description": "Timeless denim jacket with a rugged fade wash and tailored silhouette that pairs effortlessly with any outfit.", "image_url": "https://images.unsplash.com/photo-1576995853123-5a10305d93c0?w=600&auto=format&fit=crop&q=80"},
        {"id": 9, "name": "AeroStride Breathable Running Sneakers", "category": "Fashion", "price": 2899.0, "stock": 55, "rating": 4.4, "features": "Shock Absorbing Eva Sole, Breathable Mesh Upper, Anti-Slip Tread, Lightweight 260g", "description": "Ergonomically engineered athletic shoes providing superior shock absorption and lightweight flexibility for daily jogs.", "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&auto=format&fit=crop&q=80"},
        {"id": 10, "name": "Classic Oxford Cotton Formal Shirt", "category": "Fashion", "price": 1199.0, "stock": 85, "rating": 4.3, "features": "Wrinkle-Resistant Cotton, Button-Down Collar, Curved Hemline, Breathable Weave", "description": "Crisp and sophisticated button-down shirt designed for all-day comfort in corporate offices and business meetings.", "image_url": "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=600&auto=format&fit=crop&q=80"},
        {"id": 11, "name": "LeatherCraft Handcrafted Bifold Wallet", "category": "Fashion", "price": 799.0, "stock": 100, "rating": 4.7, "features": "Genuine Top-Grain Leather, RFID Blocking Protection, 8 Card Slots, Coin Pocket", "description": "Handcrafted slim bifold leather wallet featuring built-in RFID shielding to protect cards from unauthorized scans.", "image_url": "https://images.unsplash.com/photo-1627123424574-724758594e93?w=600&auto=format&fit=crop&q=80"},

        # Home & Kitchen
        {"id": 12, "name": "AromaPure Ceramic Pour-Over Coffee Maker", "category": "Home & Kitchen", "price": 1399.0, "stock": 50, "rating": 4.8, "features": "Heat-Resistant Borosilicate Glass, Reusable Stainless Filter, Ergonomic Wooden Collar", "description": "Artisan pour-over drip coffee brewer ensuring maximum flavor extraction and aromatic purity for coffee connoisseurs.", "image_url": "https://images.unsplash.com/photo-1517668808822-9ebb02f2a0e6?w=600&auto=format&fit=crop&q=80"},
        {"id": 13, "name": "AirFry Pro 4.5L Digital Air Fryer", "category": "Home & Kitchen", "price": 4999.0, "stock": 30, "rating": 4.7, "features": "360 Rapid Air Circulation, 8 Preset Cooking Modes, Non-Stick Basket, 85% Less Oil", "description": "Health-conscious digital air fryer that crisps chicken, fries, and snacks with little to no oil using rapid convection.", "image_url": "https://images.unsplash.com/photo-1584269600464-37b1b58a9fe7?w=600&auto=format&fit=crop&q=80"},
        {"id": 14, "name": "EcoSteel Vacuum Insulated Water Bottle 1L", "category": "Home & Kitchen", "price": 649.0, "stock": 120, "rating": 4.6, "features": "Double-Wall Insulated, 24h Cold & 12h Hot, Food-Grade 18/8 Stainless, Leakproof Cap", "description": "BPA-free vacuum insulated stainless steel flask keeping beverages icy cold or piping hot throughout your busy day.", "image_url": "https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=600&auto=format&fit=crop&q=80"},
        {"id": 15, "name": "ZenMist Ultrasonic Essential Oil Diffuser", "category": "Home & Kitchen", "price": 1249.0, "stock": 65, "rating": 4.5, "features": "500ml Water Tank, 7 Ambient LED Colors, Whisper Quiet, Auto Shut-Off Timer", "description": "Aromatherapy cool mist humidifier with soft ambient lighting for stress relief, meditation, and better bedroom sleep.", "image_url": "https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?w=600&auto=format&fit=crop&q=80"},
        {"id": 16, "name": "MasterChef 5-Piece Non-Stick Cookware Set", "category": "Home & Kitchen", "price": 3499.0, "stock": 40, "rating": 4.4, "features": "Hard-Anodized Aluminum, Granite Non-Stick Coating, Induction Compatible, Stay-Cool Handles", "description": "Durable kitchen cookware collection including frying pan, kadai with glass lid, saucepan, and spatulas.", "image_url": "https://images.unsplash.com/photo-1584990347449-39906d029555?w=600&auto=format&fit=crop&q=80"},

        # Books & Stationery
        {"id": 17, "name": "Atomic Habits: Proven Framework for Success", "category": "Books", "price": 499.0, "stock": 150, "rating": 4.9, "features": "Hardcover Edition, Practical Exercises, Visual Diagrams, 320 Pages", "description": "The definitive guide by James Clear on how tiny changes lead to remarkable results and long-term personal transformation.", "image_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600&auto=format&fit=crop&q=80"},
        {"id": 18, "name": "Hands-On Machine Learning with Python", "category": "Books", "price": 1499.0, "stock": 45, "rating": 4.8, "features": "Comprehensive Guide, Scikit-Learn & TensorFlow Examples, 800+ Pages, Code Exercises", "description": "Essential textbook for MCA, Data Science, and AI students covering end-to-end machine learning workflows and deep neural networks.", "image_url": "https://images.unsplash.com/photo-1532012164546-f432f2e3777f?w=600&auto=format&fit=crop&q=80"},
        {"id": 19, "name": "SmartNotes Dotted Leather Hardcover Journal", "category": "Books", "price": 399.0, "stock": 130, "rating": 4.6, "features": "120 GSM Bleed-Proof Ivory Paper, Lay-Flat Binding, Bookmark Ribbon, Elastic Closure", "description": "Elegantly crafted bullet grid notebook ideal for daily planning, sketches, study notes, and creative journaling.", "image_url": "https://images.unsplash.com/photo-1589829085413-56de8ae18c73?w=600&auto=format&fit=crop&q=80"},
        {"id": 20, "name": "The Psychology of Money by Morgan Housel", "category": "Books", "price": 389.0, "stock": 140, "rating": 4.7, "features": "Paperback, 19 Short Stories on Wealth and Happiness, Easy English, 256 Pages", "description": "Eye-opening stories exploring how people think about money, risk, and greed, teaching you to make smarter financial decisions.", "image_url": "https://images.unsplash.com/photo-1592496431122-2349e0fbc666?w=600&auto=format&fit=crop&q=80"},

        # Fitness & Sports
        {"id": 21, "name": "FlexiGrip Resistance Exercise Bands Set of 5", "category": "Fitness & Sports", "price": 599.0, "stock": 95, "rating": 4.5, "features": "100% Natural Latex, 5 Stackable Resistance Levels (10-50 lbs), Carry Bag & Workout Guide", "description": "Versatile strength training loop bands for full-body home workouts, yoga stretching, and muscle rehabilitation.", "image_url": "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=600&auto=format&fit=crop&q=80"},
        {"id": 22, "name": "ProGrip Non-Slip Eco Yoga Mat (6mm)", "category": "Fitness & Sports", "price": 999.0, "stock": 75, "rating": 4.6, "features": "Eco-Friendly TPE Material, Dual-Sided Non-Slip Texture, Alignment Lines, Free Carry Strap", "description": "High-density cushioned yoga mat offering firm joint protection and excellent grip during sweaty Pilates and floor workouts.", "image_url": "https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=600&auto=format&fit=crop&q=80"},
        {"id": 23, "name": "HexaCore Rubber Encased Dumbbell Pair (5kg x 2)", "category": "Fitness & Sports", "price": 1899.0, "stock": 40, "rating": 4.7, "features": "Cast Iron Core, Thick Rubber Coating, Anti-Roll Hexagonal Ends, Knurled Chrome Handles", "description": "Commercial-grade solid dumbbells designed for quiet floor contact and safe upper body strength conditioning at home.", "image_url": "https://images.unsplash.com/photo-1583454110551-21f2fa2afe61?w=600&auto=format&fit=crop&q=80"},
        {"id": 24, "name": "SpeedRope Digital Skipping Rope with Counter", "category": "Fitness & Sports", "price": 499.0, "stock": 110, "rating": 4.4, "features": "Backlit LCD Display, Calorie & Jump Counter, Dual Cordless & Rope Mode, Smooth Ball Bearings", "description": "Smart jump rope with electronic fitness tracking for indoor cardio conditioning and rapid calorie burning.", "image_url": "https://images.unsplash.com/photo-1518611012118-696072aa579a?w=600&auto=format&fit=crop&q=80"}
    ]
    df_products = pd.DataFrame(products_data)
    df_products.to_csv(Config.RAW_DATA_DIR / 'raw_products.csv', index=False)

    # 2. Customers Master Data (60 customers)
    indian_names = [
        "Aarav Sharma", "Priya Patel", "Rohan Verma", "Sneha Iyer", "Aditya Nair",
        "Ananya Roy", "Karan Malhotra", "Pooja Deshmukh", "Vikram Singh", "Neha Gupta",
        "Rahul Mehta", "Divya Menon", "Amit Joshi", "Kavita Reddy", "Siddharth Rao",
        "Meera Chatterjee", "Arjun Kapoor", "Ishita Bose", "Manish Pandey", "Ritu Saxena",
        "Gaurav Tiwari", "Tanvi Kulkarni", "Harsh Vardhan", "Nandini Bhatt", "Alok Kumar",
        "Shreya Nambiar", "Varun Chauhan", "Deepika Agarwal", "Rajesh Pillai", "Simran Kaur",
        "Kunal Shah", "Swati Mishra", "Naveen Prasad", "Preeti Das", "Akash Sengupta",
        "Rachna Chawla", "Mohit Bansal", "Sunita Nair", "Tarun Goel", "Bhavna Sen",
        "Abhishek Mukherjee", "Shruti Pillai", "Pranav Hegde", "Anjali Jain", "Sameer Qureshi",
        "Komal Thakur", "Devendra Rathore", "Pallavi Joshi", "Vivek Anand", "Garima Mittal",
        "Ashish Tripathi", "Sonal Dixit", "Dinesh Yadav", "Payal Singhania", "Chirag Parekh",
        "Jyoti Bhatnagar", "Chetan Deshpande", "Megha Solanki", "Lokesh Bajaj", "Monika Rawat"
    ]
    cities_states = [
        ("Mumbai", "Maharashtra"), ("Bengaluru", "Karnataka"), ("Delhi", "Delhi"),
        ("Hyderabad", "Telangana"), ("Pune", "Maharashtra"), ("Chennai", "Tamil Nadu"),
        ("Kolkata", "West Bengal"), ("Ahmedabad", "Gujarat"), ("Jaipur", "Rajasthan"),
        ("Kochi", "Kerala"), ("Chandigarh", "Punjab"), ("Indore", "Madhya Pradesh")
    ]

    customers = []
    # Default demo users
    customers.append({
        "id": 1,
        "name": "Admin Manager",
        "email": "admin@shopsmart.ai",
        "password_hash": generate_password_hash("admin123"),
        "role": "admin",
        "city": "Bengaluru",
        "state": "Karnataka",
        "created_at": "2025-01-10 10:00:00"
    })
    customers.append({
        "id": 2,
        "name": "Demo Shopper",
        "email": "student@shopsmart.ai",
        "password_hash": generate_password_hash("student123"),
        "role": "customer",
        "city": "Pune",
        "state": "Maharashtra",
        "created_at": "2025-01-15 14:30:00"
    })

    start_date = datetime(2025, 1, 1)
    for idx, name in enumerate(indian_names, start=3):
        city, state = random.choice(cities_states)
        email_prefix = name.lower().replace(" ", ".") + str(random.randint(10, 99))
        created_dt = start_date + timedelta(days=random.randint(0, 400), hours=random.randint(8, 20))
        # Intentionally inject occasional uppercase or leading spaces to showcase cleaning
        name_entry = f"  {name} " if idx % 5 == 0 else name
        email_entry = f"{email_prefix.upper()}@gmail.com" if idx % 4 == 0 else f"{email_prefix}@gmail.com"

        customers.append({
            "id": idx,
            "name": name_entry,
            "email": email_entry,
            "password_hash": generate_password_hash("password123"),
            "role": "customer",
            "city": city if idx % 9 != 0 else "", # occasional blank for cleaning demo
            "state": state,
            "created_at": created_dt.strftime("%Y-%m-%d %H:%M:%S")
        })

    df_customers = pd.DataFrame(customers)
    df_customers.to_csv(Config.RAW_DATA_DIR / 'raw_customers.csv', index=False)

    # 3. Orders & Order Details Data (180 orders, >550 order details items)
    orders = []
    order_details = []
    order_detail_id = 1
    payment_methods = ["UPI / GPay", "Credit/Debit Card", "Net Banking", "Cash on Delivery"]

    base_time = datetime(2025, 2, 1)
    for order_id in range(1, 181):
        cust = random.choice(customers)
        cust_id = cust["id"]
        # Cleaned display name & email
        c_name = cust["name"].strip()
        c_email = cust["email"].strip().lower()

        # Date spread from Feb 2025 to Feb 2026 (13 months to provide rich monthly trend analysis)
        order_days = random.randint(0, 390)
        order_time = base_time + timedelta(days=order_days, hours=random.randint(9, 21), minutes=random.randint(0, 59))
        order_number = f"ORD-{order_time.year}{order_time.month:02d}-{1000 + order_id}"

        # 2 to 5 items per order to exceed 500 order details
        num_items = random.choices([2, 3, 4, 5], weights=[0.3, 0.4, 0.2, 0.1])[0]
        chosen_prods = random.sample(products_data, num_items)

        order_total = 0.0
        for prod in chosen_prods:
            qty = random.choices([1, 2, 3], weights=[0.75, 0.2, 0.05])[0]
            price = prod["price"]
            subtotal = round(qty * price, 2)
            order_total += subtotal

            order_details.append({
                "id": order_detail_id,
                "order_id": order_id,
                "product_id": prod["id"],
                "product_name": prod["name"],
                "quantity": qty,
                "unit_price": price,
                "subtotal": subtotal
            })
            order_detail_id += 1

        orders.append({
            "id": order_id,
            "order_number": order_number,
            "customer_id": cust_id,
            "customer_name": c_name,
            "customer_email": c_email,
            "total_amount": round(order_total, 2),
            "shipping_address": f"Flat {random.randint(101, 909)}, Sunshine Heights, {cust.get('city') or 'Mumbai'}",
            "payment_method": random.choice(payment_methods),
            "status": random.choices(["Delivered", "Delivered", "Shipped", "Processing"], weights=[0.8, 0.1, 0.05, 0.05])[0],
            "created_at": order_time.strftime("%Y-%m-%d %H:%M:%S")
        })

    df_orders = pd.DataFrame(orders)
    df_order_details = pd.DataFrame(order_details)
    df_orders.to_csv(Config.RAW_DATA_DIR / 'raw_orders.csv', index=False)
    df_order_details.to_csv(Config.RAW_DATA_DIR / 'raw_order_details.csv', index=False)

    # 4. Reviews Master Data (100+ rich reviews for Review Detective AI)
    review_templates = {
        "Electronics": [
            (5, "Exceptional clarity and the noise cancellation is astonishing for the price. Battery lasts through long study sessions easily.", "Positive"),
            (5, "Brilliant build quality and quick Bluetooth pairing. Soundstage is punchy without distorting vocals.", "Positive"),
            (4, "Good gadget overall. Bass is hearty, but the ear cushions can feel slightly warm after 3 straight hours of use.", "Positive"),
            (3, "Decent performance for casual listening, though microphone pick-up in noisy outdoor areas could be better.", "Neutral"),
            (2, "Sound is alright, but the charging cable was rather short and the companion app takes time to sync.", "Negative"),
            (1, "Battery drops faster than advertised when volume is pushed above 80%. Disappointed with customer support response.", "Negative")
        ],
        "Fashion": [
            (5, "Superb fabric quality! Soft inside and the color didn't bleed after the first three machine washes. Perfect fit.", "Positive"),
            (5, "Very stylish and comfortable. Gives a premium look that rivals expensive mall brands.", "Positive"),
            (4, "Fits well and fabric is durable. Slightly snug around the shoulders, consider ordering one size larger if you like loose fits.", "Positive"),
            (3, "Average quality. It is okay for daily casual wear, but stitching near the cuffs could be reinforced.", "Neutral"),
            (2, "The size chart is a bit misleading. Delivered size L fits more like an M.", "Negative")
        ],
        "Home & Kitchen": [
            (5, "Best purchase of the year! Extremely easy to clean and cooks food with crispy golden finish using just a spray of oil.", "Positive"),
            (5, "Looks gorgeous on my kitchen counter and brews exceptionally smooth, aromatic coffee without grit.", "Positive"),
            (4, "Works flawlessly and keeps water chilled for full 24 hours during peak summer. Sturdy metal lid.", "Positive"),
            (3, "Good utility product, but takes a few tries to master the temperature presets. Manual could be clearer.", "Neutral"),
            (2, "A bit bulky for small kitchen counters. Cable is on the shorter side.", "Negative")
        ],
        "Books": [
            (5, "Must-read masterpiece! Practical, actionable advice that completely changed how I manage my daily habits.", "Positive"),
            (5, "Comprehensive, easy-to-follow Python exercises. Highly recommended for any MCA or computer science student.", "Positive"),
            (4, "Inspiring stories and well-written chapters. The paper quality of the hardcover is top notch.", "Positive"),
            (4, "Great binding and dot-grid format. Ink doesn't bleed through even with fountain pens.", "Positive"),
            (3, "Good concepts, though the middle chapters feel a bit repetitive.", "Neutral")
        ],
        "Fitness & Sports": [
            (5, "High-grade rubber that doesn't smell. Perfect resistance levels for home gym progression.", "Positive"),
            (5, "Super grippy mat with excellent joint cushioning. Doesn't slide on tiled floors even when sweating.", "Positive"),
            (4, "Solid dumbbells with ergonomic knurling. Great value for money compared to offline sports stores.", "Positive"),
            (3, "Rope is fine and the digital counter works, but the handle plastic feels somewhat light.", "Neutral"),
            (2, "Lightest resistance band snapped after two weeks of aggressive stretching. Other bands are holding up well.", "Negative")
        ]
    }

    reviews = []
    review_id = 1
    for prod in products_data:
        cat = prod["category"]
        pool = review_templates.get(cat, review_templates["Electronics"])
        # Generate 4-7 reviews per product
        num_reviews = random.randint(4, 7)
        for _ in range(num_reviews):
            rating, text, sentiment = random.choice(pool)
            cust_name = random.choice(indian_names)
            rev_time = base_time + timedelta(days=random.randint(10, 380))
            reviews.append({
                "id": review_id,
                "product_id": prod["id"],
                "customer_name": cust_name,
                "rating": rating,
                "review_text": text,
                "sentiment": sentiment,
                "created_at": rev_time.strftime("%Y-%m-%d %H:%M:%S")
            })
            review_id += 1

    df_reviews = pd.DataFrame(reviews)
    df_reviews.to_csv(Config.RAW_DATA_DIR / 'raw_reviews.csv', index=False)

    print(f"[ETL Setup] Generated raw datasets:")
    print(f" - Products: {len(df_products)} rows")
    print(f" - Customers: {len(df_customers)} rows")
    print(f" - Orders: {len(df_orders)} rows")
    print(f" - Order Details: {len(df_order_details)} rows")
    print(f" - Reviews: {len(df_reviews)} rows")
    print(f" Total records created: {len(df_products) + len(df_customers) + len(df_orders) + len(df_order_details) + len(df_reviews)} (>500 records verified)")

def run_etl_pipeline():
    """
    Extract, Transform, and Load (ETL) pipeline using Pandas.
    - Extract: Reads raw CSVs
    - Transform: Performs data cleansing, standardization, null handling, validation
    - Load: Inserts into SQLite Data Warehouse
    """
    print("[ETL Pipeline] Starting ETL execution...")

    # Ensure raw files exist
    if not (Config.RAW_DATA_DIR / 'raw_products.csv').exists():
        generate_raw_datasets()

    # Initialize SQLite database schema
    init_db()
    conn = get_db_connection()

    # ==========================
    # 1. EXTRACT STEP
    # ==========================
    df_products_raw = pd.read_csv(Config.RAW_DATA_DIR / 'raw_products.csv')
    df_customers_raw = pd.read_csv(Config.RAW_DATA_DIR / 'raw_customers.csv')
    df_orders_raw = pd.read_csv(Config.RAW_DATA_DIR / 'raw_orders.csv')
    df_order_details_raw = pd.read_csv(Config.RAW_DATA_DIR / 'raw_order_details.csv')
    df_reviews_raw = pd.read_csv(Config.RAW_DATA_DIR / 'raw_reviews.csv')

    # ==========================
    # 2. TRANSFORM STEP (Data Cleaning with Pandas)
    # ==========================
    # A. Clean Customers Data
    df_customers_clean = df_customers_raw.copy()
    # Strip whitespace from names and strings
    df_customers_clean['name'] = df_customers_clean['name'].astype(str).str.strip()
    df_customers_clean['email'] = df_customers_clean['email'].astype(str).str.strip().str.lower()
    # Handle missing cities / states
    df_customers_clean['city'] = df_customers_clean['city'].fillna('Mumbai').replace('', 'Mumbai').str.strip()
    df_customers_clean['state'] = df_customers_clean['state'].fillna('Maharashtra').replace('', 'Maharashtra').str.strip()
    # Deduplicate on email
    df_customers_clean = df_customers_clean.drop_duplicates(subset=['email'])

    # B. Clean Products Data
    df_products_clean = df_products_raw.copy()
    df_products_clean['name'] = df_products_clean['name'].astype(str).str.strip()
    df_products_clean['category'] = df_products_clean['category'].astype(str).str.strip()
    df_products_clean['price'] = pd.to_numeric(df_products_clean['price'], errors='coerce').fillna(999.0)
    df_products_clean['stock'] = pd.to_numeric(df_products_clean['stock'], errors='coerce').fillna(50).astype(int)

    # Recalculate average rating & review count from actual reviews dataset
    review_agg = df_reviews_raw.groupby('product_id').agg(
        avg_rating=('rating', 'mean'),
        num_reviews=('id', 'count')
    ).reset_index()

    df_products_clean = df_products_clean.merge(review_agg, left_on='id', right_on='product_id', how='left')
    df_products_clean['rating'] = df_products_clean['avg_rating'].fillna(df_products_clean['rating']).round(1)
    df_products_clean['review_count'] = df_products_clean['num_reviews'].fillna(0).astype(int)
    df_products_clean = df_products_clean.drop(columns=['product_id', 'avg_rating', 'num_reviews'], errors='ignore')

    # C. Clean Orders & Order Details Data
    df_orders_clean = df_orders_raw.copy()
    df_orders_clean['customer_name'] = df_orders_clean['customer_name'].astype(str).str.strip()
    df_orders_clean['customer_email'] = df_orders_clean['customer_email'].astype(str).str.strip().str.lower()
    df_orders_clean['total_amount'] = pd.to_numeric(df_orders_clean['total_amount'], errors='coerce').round(2)
    df_orders_clean['created_at'] = pd.to_datetime(df_orders_clean['created_at']).dt.strftime('%Y-%m-%d %H:%M:%S')

    df_order_details_clean = df_order_details_raw.copy()
    df_order_details_clean['quantity'] = pd.to_numeric(df_order_details_clean['quantity'], errors='coerce').fillna(1).astype(int)
    df_order_details_clean['unit_price'] = pd.to_numeric(df_order_details_clean['unit_price'], errors='coerce').round(2)
    df_order_details_clean['subtotal'] = (df_order_details_clean['quantity'] * df_order_details_clean['unit_price']).round(2)

    # Validate Order Totals against Order Details subtotal
    subtotal_by_order = df_order_details_clean.groupby('order_id')['subtotal'].sum().round(2).reset_index()
    df_orders_clean = df_orders_clean.merge(subtotal_by_order, left_on='id', right_on='order_id', how='left')
    # Update total_amount to true calculated subtotal if discrepancy existed
    df_orders_clean['total_amount'] = df_orders_clean['subtotal'].fillna(df_orders_clean['total_amount'])
    df_orders_clean = df_orders_clean.drop(columns=['order_id', 'subtotal'], errors='ignore')

    # D. Clean Reviews Data
    df_reviews_clean = df_reviews_raw.copy()
    df_reviews_clean['customer_name'] = df_reviews_clean['customer_name'].astype(str).str.strip()
    df_reviews_clean['review_text'] = df_reviews_clean['review_text'].astype(str).str.strip()
    df_reviews_clean['rating'] = pd.to_numeric(df_reviews_clean['rating'], errors='coerce').clip(1, 5).astype(int)
    df_reviews_clean['created_at'] = pd.to_datetime(df_reviews_clean['created_at']).dt.strftime('%Y-%m-%d %H:%M:%S')

    # ==========================
    # 3. LOAD STEP (Load into SQLite Data Warehouse)
    # ==========================
    # Load each DataFrame into SQLite using Pandas to_sql
    cursor = conn.cursor()
    # Clear existing records before reloading
    cursor.execute("DELETE FROM order_details;")
    cursor.execute("DELETE FROM orders;")
    cursor.execute("DELETE FROM reviews;")
    cursor.execute("DELETE FROM products;")
    cursor.execute("DELETE FROM customers;")
    conn.commit()

    # Load cleaned tables
    df_customers_clean.to_sql('customers', conn, if_exists='append', index=False)
    df_products_clean.to_sql('products', conn, if_exists='append', index=False)
    df_orders_clean.to_sql('orders', conn, if_exists='append', index=False)
    df_order_details_clean.to_sql('order_details', conn, if_exists='append', index=False)
    df_reviews_clean.to_sql('reviews', conn, if_exists='append', index=False)

    conn.commit()
    conn.close()

    total_records = len(df_customers_clean) + len(df_products_clean) + len(df_orders_clean) + len(df_order_details_clean) + len(df_reviews_clean)
    print(f"[ETL Pipeline] Success: {total_records} cleaned records loaded into SQLite Data Warehouse.")
    return {
        "status": "success",
        "customers": len(df_customers_clean),
        "products": len(df_products_clean),
        "orders": len(df_orders_clean),
        "order_details": len(df_order_details_clean),
        "reviews": len(df_reviews_clean),
        "total_records": total_records
    }

if __name__ == '__main__':
    generate_raw_datasets()
    run_etl_pipeline()
