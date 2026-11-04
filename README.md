# ShopSmart AI – Smart Shopping Intelligence System
*An End-to-End E-Commerce, Data Warehouse, Data Mining, and Generative AI Platform*
*Designed for MCA Data Science Mini Project*

---

## 📌 Project Overview
**ShopSmart AI** is a modern, beginner-friendly e-commerce web application that bridges online retail with data science and artificial intelligence. The platform combines a full shopping experience with an automated **ETL Data Warehouse**, **Pandas Data Mining (RFM Customer Segmentation & Demand Forecasting)**, **Matplotlib Data Visualizations**, **AWS Cloud Readiness (S3 & EC2)**, and a **Generative AI Intelligence Suite (Google Gemini)**.

---

## 🛠️ Technology Stack
*Built strictly with standard, clean, and reliable technologies — no heavy frontend frameworks or unnecessary libraries:*
- **Frontend:** HTML5, CSS3, Vanilla JavaScript (Modern responsive design, white background with royal blue `#2563eb` & purple `#7c3aed` accents).
- **Backend:** Python 3, Flask.
- **Database / Data Warehouse:** SQLite3 (`data/shopsmart.db`).
- **Data Science & Mining:** Pandas, NumPy.
- **Data Visualization:** Matplotlib (embedded dynamic Base64 charts + Power BI CSV export).
- **Generative AI:** Google Gemini 1.5 Flash API (with prompt engineering and heuristic fallback).
- **Cloud Computing:** AWS S3 dataset backup sync (`boto3`) and AWS EC2 deployment automation.

---

## 📂 Project Folder Structure
```text
SMART SYSTEM GEN AI/
├── app.py                     # Main Flask web application & API controllers
├── config.py                  # Environment configuration & paths
├── database.py                # SQLite schema creation & connection manager
├── etl_pipeline.py            # Extract, Transform, Load pipeline (>950 records)
├── data_mining.py             # RFM Customer Segmentation & Product Demand Forecasting
├── visualization.py           # Matplotlib high-resolution charts generator
├── ai_service.py              # Generative AI module (Gemini API + Prompt Engineering)
├── test_app.py                # End-to-end integration test suite
├── requirements.txt           # Python dependencies
├── .env.example               # Environment variables template
├── .env                       # Local environment configuration
├── README.md                  # Comprehensive project documentation
├── Dockerfile                 # Container image specification
├── docker-compose.yml         # Multi-service container launcher
├── data/
│   ├── raw/                   # Raw operational CSVs (customers, products, orders, reviews)
│   ├── shopsmart.db           # SQLite Data Warehouse
│   └── shopsmart_cleaned_powerbi_dataset.csv # Cleaned export for Power BI
├── static/
│   ├── css/
│   │   └── style.css          # Master responsive stylesheet (white, blue, purple)
│   └── js/
│       └── main.js            # Frontend AJAX controller, toasts, and AI tab manager
├── templates/
│   ├── base.html              # Shared layout & responsive navbar
│   ├── index.html             # Page 1: Home page with hero & categories
│   ├── login.html             # Page 2: User / Admin Login
│   ├── register.html          # Page 2: Customer Registration
│   ├── products.html          # Page 3: Product Catalog with search & filter
│   ├── cart.html              # Page 4: Shopping Cart & Checkout
│   ├── order_confirmation.html# Page 4: Order Confirmation & Invoice receipt
│   ├── admin_dashboard.html   # Page 5: Sales Analytics, Charts & Data Mining
│   └── ai_intelligence.html   # Section 3: Unique Generative AI Suite
└── aws_cloud/
    ├── s3_storage.py          # AWS S3 cloud backup script (live/simulated)
    └── ec2_setup.sh           # AWS EC2 Ubuntu production deployment script
```

---

## 🚀 How to Run the Project in VS Code (Step-by-Step)

### Prerequisites
- Python 3.10+ installed on your system.
- Visual Studio Code.

### Step 1: Open the Project in VS Code
1. Launch **VS Code**.
2. Go to **File → Open Folder...** and select `SMART SYSTEM GEN AI`.
3. Open a new Terminal in VS Code (**Terminal → New Terminal** or press ``Ctrl + ` ``).

### Step 2: Create and Activate a Python Virtual Environment
In the VS Code terminal (PowerShell or Bash):
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# (If using Command Prompt)
# .\venv\Scripts\activate.bat

# (If using macOS / Linux)
# source venv/bin/activate
```

### Step 3: Install Required Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables (Optional for Gemini AI)
1. Copy `.env.example` to `.env`:
```powershell
cp .env.example .env
```
2. Open `.env` and add your free Google Gemini API key:
```ini
GEMINI_API_KEY=your_gemini_api_key_here
```
> *Note:* If you do not have a Gemini API key yet, the application will automatically run in **Heuristic Intelligence Mode**, showing a clear setup notice while still providing data-driven recommendations without crashing!

### Step 5: Initialize the Data Warehouse (Run ETL)
```powershell
python etl_pipeline.py
```
*This extracts raw datasets, cleans the data with Pandas, and seeds 954 records into SQLite.*

### Step 6: Start the Flask Web Server
```powershell
python app.py
```

### Step 7: Open the Application in your Browser
Navigate to:
- **Home Page:** [http://127.0.0.1:5000/](http://127.0.0.1:5000/)
- **Product Catalog:** [http://127.0.0.1:5000/products](http://127.0.0.1:5000/products)
- **AI Intelligence Suite:** [http://127.0.0.1:5000/ai-intelligence](http://127.0.0.1:5000/ai-intelligence)
- **Admin Dashboard:** [http://127.0.0.1:5000/admin](http://127.0.0.1:5000/admin)

---

## 🔑 Demo Login Credentials
For quick evaluation during project demonstration or grading:
| Role | Email | Password | Access Privileges |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin@shopsmart.ai` | `admin123` | Full access to Admin Dashboard, ETL & Cloud sync |
| **Customer** | `student@shopsmart.ai` | `student123` | Shopping cart, checkout & AI tools |

*(Both login and register pages include 1-click **Fast Demo Sign-In** buttons).*

---

## 🌟 Core Features & Modules Walkthrough

### 1. E-Commerce Storefront
- **Home Page:** Hero banner, quick product search, category navigation (Electronics, Fashion, Home & Kitchen, Books, Fitness & Sports), featured products grid.
- **Products Catalog:** Search by keyword, filter by category pills, sort by Price (Low to High / High to Low), Rating, or Name.
- **Shopping Cart:** AJAX add-to-cart toast notifications, real-time cart badge counter, increment/decrement controls, free delivery calculator (threshold ₹999).
- **Checkout & Invoice:** Generates unique order tracking numbers (`ORD-YYYYMMDD-XXXX`), deducts stock from inventory, and outputs a printable receipt.

### 2. Unique Generative AI Module ("ShopSmart AI Intelligence")
Accessed via `/ai-intelligence` with three dedicated tools:
1. **Feature 1: Shopping Personality AI**
   - User inputs persona and budget (e.g., *"I am a college student. Suggest useful products under ₹2000"*).
   - Prompt-engineered LLM scans eligible catalog items, generates custom recommendations, and explains suitability.
   - Includes 1-click quick persona presets (College Student, Remote Worker, Home Fitness, Reader).
2. **Feature 2: Review Detective AI**
   - User selects any product from the catalog.
   - AI mines all customer reviews from the database, extracts **Positive Points (Pros)**, **Negative Points (Cons)**, an **Overall Summary**, and flags **Common Customer Complaints**.
3. **Feature 3: Smart Product Battle AI**
   - Select two products for a head-to-head comparison.
   - Generates an objective comparison matrix (Price, Specs, Ratings), evaluates trade-offs, and provides a clear purchase verdict.

### 3. Data Warehouse & ETL Pipeline
- **Extract:** Ingests raw data from CSV files.
- **Transform:** Cleans data using Pandas:
  - Trims whitespace and normalizes email formats to lowercase.
  - Fills missing demographic fields.
  - Recalculates average product ratings and verified review counts.
  - Reconciles order totals against itemized subtotal sums.
- **Load:** Ingests cleaned DataFrames into SQLite tables: `customers`, `products`, `orders`, `order_details`, `reviews`.
- **Dataset Size:** Contains **954 records** (exceeding the 500 records requirement).

### 4. Data Mining Techniques
1. **RFM Customer Segmentation:**
   - Evaluates **Recency** (days since last purchase), **Frequency** (order volume), and **Monetary Value** (total spend).
   - Segments buyers into: *Champion Shoppers*, *Loyal Customers*, *Potential Growth*, and *At-Risk / Inactive*.
   - Suggests actionable marketing strategies for each segment.
2. **Product Demand Forecasting:**
   - Computes monthly sales velocity and moving averages per SKU.
   - Projects 30-day forecasted demand with inventory reorder triggers.

### 5. Data Visualization (Matplotlib Dynamic Charts)
All charts are dynamically generated in backend Python and embedded as crisp Base64 PNGs in `/admin`:
1. **Monthly Sales Revenue Trend:** Line chart with area fill and point labels.
2. **Category-wise Sales Breakdown:** Donut chart showing revenue share percentage.
3. **Top Best-Selling Products:** Horizontal bar chart by units sold.
4. **Customer Payment Preferences:** Bar chart of UPI, Card, Net Banking, and COD volume.
5. **Customer Product Ratings Distribution:** Star-rating histogram (1 to 5 stars).
6. **Power BI Export:** 1-click download of `shopsmart_powerbi_sales_data.csv`.

### 6. Cloud Computing Readiness (AWS)
- **Amazon S3 Storage:** `aws_cloud/s3_storage.py` backs up the SQLite database and Power BI datasets to an S3 bucket (supports both live AWS credentials and safe local simulation).
- **AWS EC2 Deployment Script:** `aws_cloud/ec2_setup.sh` automates OS packages, Python virtual environment, Gunicorn WSGI server, Systemd service, and Nginx reverse proxy.
- **Docker Support:** Ready for AWS ECS / EC2 container deployment via `Dockerfile` and `docker-compose.yml`.

---

## 🧪 Running Automated Tests
To run the automated test suite verifying all 8 core workflows:
```powershell
python test_app.py
```
**Expected Output:**
```text
Ran 8 tests in 2.2s
OK
[Test] Total Database Records: 954 (Customers: 62, Products: 24, Orders: 180, Details: 558, Reviews: 130)
```

---

## 🎓 Academic Viva / Presentation Highlights
1. **Generative AI Integration:** Uses prompt engineering and dynamic context injection to pass database records to Google Gemini.
2. **Data Science Core:** Real ETL pipeline and RFM customer segmentation implemented using Pandas rather than static mock templates.
3. **No Heavy Framework Overhead:** Built strictly with HTML, CSS, JavaScript, Flask, SQLite, Pandas, and Matplotlib.
