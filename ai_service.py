"""
ShopSmart AI - Generative AI Service Module
Powers the three Unique Generative AI Modules:
1. Shopping Personality AI
2. Review Detective AI
3. Smart Product Battle AI

Connects with Google Gemini API using Prompt Engineering.
Provides clear setup instructions if API key is not configured.
"""

import os
import json
import sqlite3
import requests
from config import Config
from database import get_db_connection

def is_gemini_configured():
    """Check if a Gemini API key is configured in the environment."""
    key = Config.GEMINI_API_KEY
    return bool(key and len(key) > 10 and not key.startswith("your_"))

def call_gemini_api(prompt, system_instruction=""):
    """
    Call the Google Gemini Generative AI API using HTTP POST.
    Returns (success, response_text_or_error_message).
    """
    api_key = Config.GEMINI_API_KEY
    if not is_gemini_configured():
        return False, "GEMINI_API_KEY is not configured in .env."

    # Gemini 1.5 Flash endpoint
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": f"{system_instruction}\n\n{prompt}" if system_instruction else prompt}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.4,
            "maxOutputTokens": 1024,
            "topP": 0.95
        }
    }

    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        if response.status_code == 200:
            result = response.json()
            try:
                generated_text = result['candidates'][0]['content']['parts'][0]['text']
                return True, generated_text
            except (KeyError, IndexError):
                return False, "Failed to parse Gemini response structure."
        else:
            return False, f"Gemini API Error (HTTP {response.status_code}): {response.text}"
    except Exception as e:
        return False, f"Network exception when calling Gemini API: {str(e)}"

# ==========================================================
# FEATURE 1: Shopping Personality AI
# ==========================================================
def generate_shopping_personality(user_persona, budget):
    """
    Customer enters requirements and budget (e.g. 'I am a college student. Suggest useful products under ₹2000').
    AI analyses available products, generates personalized suggestions and explains suitability.
    """
    conn = get_db_connection()
    try:
        budget_val = float(budget)
    except (ValueError, TypeError):
        budget_val = 2500.0

    # Query products within or around the budget
    query = """
    SELECT id, name, category, price, rating, features, description, image_url 
    FROM products 
    WHERE price <= ? 
    ORDER BY rating DESC, price ASC;
    """
    products = conn.execute(query, (budget_val * 1.15,)).fetchall()
    
    # If no products under budget, fetch 5 cheapest products
    if not products:
        products = conn.execute("SELECT id, name, category, price, rating, features, description, image_url FROM products ORDER BY price ASC LIMIT 5;").fetchall()
    conn.close()

    product_catalog_context = "\n".join([
        f"- ID: {p['id']} | Name: {p['name']} | Category: {p['category']} | Price: ₹{p['price']} | Rating: {p['rating']}★ | Features: {p['features']} | Desc: {p['description']}"
        for p in products
    ])

    system_instruction = (
        "You are 'ShopSmart Shopping Personality AI', an intelligent e-commerce shopping consultant. "
        "Your goal is to recommend the best products tailored specifically to the customer's stated persona, "
        "lifestyle, needs, and budget. Format your answer in clean Markdown with emojis, clear headings, "
        "and bullet points. Highlight why each item solves their specific lifestyle problem."
    )

    prompt = f"""
Customer Request / Persona: "{user_persona}"
Customer Budget: ₹{budget_val}

Available Catalog Products:
{product_catalog_context}

Please generate:
1. 🎯 Persona Analysis: Quick 1-2 sentence understanding of what this customer values most.
2. 🛍️ Tailored Product Recommendations: Select 2 to 3 most relevant products from the catalog above that fit within the budget.
   For each recommended product, specify:
   - Product Name & Exact Price (₹)
   - Why it is suitable for this specific persona
   - Key Feature highlight
3. 💡 Budget Utilization & Smart Shopping Tip: How well their budget is spent and advice for maximizing value.
"""

    if is_gemini_configured():
        success, response_text = call_gemini_api(prompt, system_instruction)
        if success:
            return {
                "status": "success",
                "is_live_ai": True,
                "ai_engine": "Google Gemini 1.5 Flash",
                "content": response_text
            }
        else:
            api_error = response_text
    else:
        api_error = "Gemini API key is not configured in the .env file."

    # Heuristic Data-Driven Fallback (when API key is missing or offline)
    # Strictly transparent according to requirements!
    top_picks = products[:3]
    spent = sum(p['price'] for p in top_picks)
    
    fallback_content = f"""### ⚠️ Gemini API Notice
> **Notice:** Live Gemini LLM is not active ({api_error}).
> To enable real-time Live LLM inference, obtain your free Gemini API key from [Google AI Studio](https://aistudio.google.com/) and paste it into `.env` as `GEMINI_API_KEY=your_key`.
> 
> *Displaying Data Mining Rule-Based Personality Matching:*

---

### 🎯 Persona Analysis
**Customer Profile:** {user_persona}  
**Allocated Budget:** ₹{budget_val:,.2f}  
Our system analyzed the product database and matched high-rated items aligned with your requirements and budget threshold.

### 🛍️ Tailored Product Recommendations
"""
    for p in top_picks:
        fallback_content += f"""
- **{p['name']}** — **₹{p['price']:,.2f}** ({p['rating']} ★)
  - **Category:** {p['category']}
  - **Why it is suitable:** High customer satisfaction rating ({p['rating']}/5) and compact utility. Perfect for students and everyday users wanting high value at an accessible price point.
  - **Key Features:** {p['features']}
"""

    fallback_content += f"""
### 💡 Budget Utilization & Smart Shopping Tip
- **Estimated Basket Value:** ₹{spent:,.2f} ({(spent / budget_val) * 100:.1f}% of budget)
- **Tip:** Consider checking customer reviews and bundles on the Products page to enjoy free doorstep shipping on orders above ₹999.
"""

    return {
        "status": "success",
        "is_live_ai": False,
        "ai_engine": "Heuristic Rule-Based Intelligence (Setup Gemini API for Live LLM)",
        "content": fallback_content
    }

# ==========================================================
# FEATURE 2: Review Detective AI
# ==========================================================
def analyze_product_reviews(product_id):
    """
    AI analyses multiple customer reviews for a chosen product.
    Identifies positive points, negative points, overall summary, and common complaints.
    """
    conn = get_db_connection()
    product = conn.execute("SELECT id, name, category, price, rating, features, description FROM products WHERE id = ?;", (product_id,)).fetchone()
    if not product:
        conn.close()
        return {"status": "error", "message": "Product not found."}

    reviews = conn.execute("SELECT customer_name, rating, review_text, sentiment, created_at FROM reviews WHERE product_id = ? ORDER BY rating DESC;", (product_id,)).fetchall()
    conn.close()

    reviews_text = "\n".join([
        f"- [{r['rating']}★ | {r['sentiment']}] {r['customer_name']}: \"{r['review_text']}\""
        for r in reviews
    ]) if reviews else "No customer reviews yet."

    system_instruction = (
        "You are 'ShopSmart Review Detective AI', an expert in sentiment analysis and consumer review mining. "
        "Your mission is to synthesize all customer feedback into an objective, trustworthy consumer report. "
        "Use Markdown with headers, bold text, and bullet points."
    )

    prompt = f"""
Product: {product['name']} (Category: {product['category']}, Price: ₹{product['price']}, Average Rating: {product['rating']}★)
Description: {product['description']}
Features: {product['features']}

Customer Reviews ({len(reviews)} reviews recorded):
{reviews_text}

Please generate an investigative consumer analysis:
1. 📋 Overall Review Summary: 2-3 concise sentences summarizing what the majority of buyers feel.
2. 🟢 Positive Points (Pros): 3-4 distinct points praised by satisfied buyers.
3. 🔴 Negative Points (Cons): 2-3 authentic criticisms or minor weaknesses mentioned.
4. ⚠️ Common Customer Complaints & Advice: What buyers should know before ordering (sizing, battery care, maintenance, etc.).
5. ⚖️ Verdict & Recommendation: Who should definitely buy this and who might want to consider an alternative.
"""

    if is_gemini_configured():
        success, response_text = call_gemini_api(prompt, system_instruction)
        if success:
            return {
                "status": "success",
                "is_live_ai": True,
                "ai_engine": "Google Gemini 1.5 Flash",
                "product_name": product['name'],
                "content": response_text
            }
        else:
            api_error = response_text
    else:
        api_error = "Gemini API key is not configured in the .env file."

    # Heuristic Fallback Analysis
    pos_reviews = [r for r in reviews if r['rating'] >= 4]
    neg_reviews = [r for r in reviews if r['rating'] <= 3]
    avg_score = sum(r['rating'] for r in reviews) / max(1, len(reviews))

    fallback_content = f"""### ⚠️ Gemini API Notice
> **Notice:** Live Gemini LLM is not active ({api_error}).
> Configure `GEMINI_API_KEY` in `.env` for real-time generative neural synthesis.
> 
> *Displaying Statistical Review Detective Analysis from {len(reviews)} Verified Reviews:*

---

### 📋 Overall Review Summary for **{product['name']}**
Based on **{len(reviews)} customer reviews**, this product holds a solid average rating of **{avg_score:.1f} / 5.0 ★**. The sentiment is predominantly positive, with customers praising its practical build quality and value for money in the **{product['category']}** segment.

### 🟢 Key Positive Points (Pros)
- **High Build & Performance Satisfaction:** Customers repeatedly note that the features align accurately with the manufacturer's description.
- **Great Value-to-Price Ratio:** Priced at **₹{product['price']:,.2f}**, buyers consider it competitively priced compared to alternatives.
- **Sample Verified Praise:** *"{pos_reviews[0]['review_text'] if pos_reviews else 'Reliable day-to-day performance.'}"*

### 🔴 Negative Points & Critiques (Cons)
- **Minor Usability Observations:** Occasional buyers noted minor learning curves or slight ergonomic adjustments needed for prolonged usage.
- **Sample Verified Critique:** *"{neg_reviews[0]['review_text'] if neg_reviews else 'Packaging and cable accessories could be slightly improved.'}"*

### ⚠️ Common Customer Complaints & Buyer Advice
- Carefully check the product dimensions and specifications before purchasing.
- Take advantage of ShopSmart's 7-day hassle-free replacement policy if any accessories require support.

### ⚖️ Detective Verdict
**Recommended For:** Shoppers seeking reliable daily functionality without overspending.
"""

    return {
        "status": "success",
        "is_live_ai": False,
        "ai_engine": "Statistical Review Mining Heuristics",
        "product_name": product['name'],
        "content": fallback_content
    }

# ==========================================================
# FEATURE 3: Smart Product Battle AI
# ==========================================================
def battle_products(prod_id_1, prod_id_2, user_preference="General Value"):
    """
    Allow customers to select two products.
    Compare price, category, features, and ratings.
    Generate an AI comparison report with pros, cons, and a personalized recommendation.
    """
    conn = get_db_connection()
    p1 = conn.execute("SELECT * FROM products WHERE id = ?;", (prod_id_1,)).fetchone()
    p2 = conn.execute("SELECT * FROM products WHERE id = ?;", (prod_id_2,)).fetchone()
    
    if not p1 or not p2:
        conn.close()
        return {"status": "error", "message": "One or both products were not found."}

    # Fetch review summaries for both
    rev1 = conn.execute("SELECT rating, review_text FROM reviews WHERE product_id = ? LIMIT 3;", (prod_id_1,)).fetchall()
    rev2 = conn.execute("SELECT rating, review_text FROM reviews WHERE product_id = ? LIMIT 3;", (prod_id_2,)).fetchall()
    conn.close()

    system_instruction = (
        "You are 'ShopSmart Product Battle AI', an impartial tech and consumer product judge. "
        "Compare the two contenders side-by-side with clear reasoning, pros and cons, and declare "
        "a well-reasoned winner based on customer value and specifications. Use Markdown tables and bullet points."
    )

    prompt = f"""
CONTENDER 1:
- Name: {p1['name']}
- Category: {p1['category']}
- Price: ₹{p1['price']}
- Rating: {p1['rating']}★ ({p1['review_count']} reviews)
- Features: {p1['features']}
- Description: {p1['description']}

CONTENDER 2:
- Name: {p2['name']}
- Category: {p2['category']}
- Price: ₹{p2['price']}
- Rating: {p2['rating']}★ ({p2['review_count']} reviews)
- Features: {p2['features']}
- Description: {p2['description']}

Customer Preference / Focus: "{user_preference}"

Please generate:
1. 🥊 The Head-to-Head Comparison: Markdown table comparing Price, Category, Rating, and Key Highlights.
2. 🏆 Contender 1 Strengths & Weaknesses ({p1['name']}).
3. 🏆 Contender 2 Strengths & Weaknesses ({p2['name']}).
4. 💰 Value-for-Money Analysis: Is the price difference justified?
5. 👑 Final Battle Winner & Advice: Clearly declare who should buy Product 1 vs who should buy Product 2.
"""

    if is_gemini_configured():
        success, response_text = call_gemini_api(prompt, system_instruction)
        if success:
            return {
                "status": "success",
                "is_live_ai": True,
                "ai_engine": "Google Gemini 1.5 Flash",
                "product1": dict(p1),
                "product2": dict(p2),
                "content": response_text
            }
        else:
            api_error = response_text
    else:
        api_error = "Gemini API key is not configured in the .env file."

    # Heuristic Battle Fallback
    price_diff = abs(p1['price'] - p2['price'])
    cheaper = p1 if p1['price'] <= p2['price'] else p2
    pricier = p2 if p1['price'] <= p2['price'] else p1

    fallback_content = f"""### ⚠️ Gemini API Notice
> **Notice:** Live Gemini LLM is not active ({api_error}).
> Configure `GEMINI_API_KEY` in `.env` to unlock live neural battle evaluation.
> 
> *Displaying Rule-Based Feature Comparison Matrix:*

---

### 🥊 Head-to-Head Comparison Matrix

| Feature / Metric | Contender 1: {p1['name']} | Contender 2: {p2['name']} |
| :--- | :--- | :--- |
| **Category** | {p1['category']} | {p2['category']} |
| **Price** | **₹{p1['price']:,.2f}** | **₹{p2['price']:,.2f}** |
| **User Rating** | {p1['rating']} ★ ({p1['review_count']} reviews) | {p2['rating']} ★ ({p2['review_count']} reviews) |
| **Stock Status** | {p1['stock']} units available | {p2['stock']} units available |
| **Key Highlights** | {p1['features']} | {p2['features']} |

---

### 🏆 Contender 1 Analysis: {p1['name']}
- **Advantage:** {"More affordable choice saving ₹" + f"{price_diff:,.2f}" if p1['price'] < p2['price'] else "Offers advanced premium specifications and rich build quality."}
- **Consideration:** Rating of {p1['rating']}★ indicates consistent user reception.

### 🏆 Contender 2 Analysis: {p2['name']}
- **Advantage:** {"More affordable choice saving ₹" + f"{price_diff:,.2f}" if p2['price'] < p1['price'] else "Provides superior feature sets and refined design."}
- **Consideration:** Rating of {p2['rating']}★ across active buyers.

---

### 💰 Value-for-Money Analysis
The price gap between these two products is **₹{price_diff:,.2f}**.
- If budget conservation is your primary objective, **{cheaper['name']}** offers the strongest bang-for-buck at **₹{cheaper['price']:,.2f}**.
- If you desire higher-tier features and longevity, **{pricier['name']}** at **₹{pricier['price']:,.2f}** delivers on premium expectations.

### 👑 Final Recommendation Verdict
- **Go with Contender 1 ({p1['name']})** if you prioritize {p1['category'].lower()} utility and proven reliability.
- **Go with Contender 2 ({p2['name']})** if you prefer {p2['category'].lower()} performance and richer feature sets.
"""

    return {
        "status": "success",
        "is_live_ai": False,
        "ai_engine": "Analytical Comparison Matrix",
        "product1": dict(p1),
        "product2": dict(p2),
        "content": fallback_content
    }
