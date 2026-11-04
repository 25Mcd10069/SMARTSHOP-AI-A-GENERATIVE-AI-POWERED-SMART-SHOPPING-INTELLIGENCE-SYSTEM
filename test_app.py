"""
ShopSmart AI - End-to-End System Integration Tests
Validates all routes, database transactions, cart logic,
Generative AI endpoints, Matplotlib charts, and Data Mining outputs.
"""

import unittest
from app import app
from database import get_db_connection

class ShopSmartTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

    def test_01_database_records(self):
        """Verify the e-commerce data warehouse contains >500 records."""
        conn = get_db_connection()
        c_count = conn.execute("SELECT COUNT(*) FROM customers;").fetchone()[0]
        p_count = conn.execute("SELECT COUNT(*) FROM products;").fetchone()[0]
        o_count = conn.execute("SELECT COUNT(*) FROM orders;").fetchone()[0]
        od_count = conn.execute("SELECT COUNT(*) FROM order_details;").fetchone()[0]
        r_count = conn.execute("SELECT COUNT(*) FROM reviews;").fetchone()[0]
        conn.close()

        total = c_count + p_count + o_count + od_count + r_count
        print(f"\n[Test] Total Database Records: {total} (Customers: {c_count}, Products: {p_count}, Orders: {o_count}, Details: {od_count}, Reviews: {r_count})")
        self.assertGreaterEqual(total, 500, "Dataset must have at least 500 records.")

    def test_02_home_page(self):
        """Test home page rendering and HTTP 200."""
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'ShopSmart', res.data)
        self.assertIn(b'Shopping Personality AI', res.data)

    def test_03_products_catalog(self):
        """Test product browsing, search, and category filtering."""
        res = self.client.get('/products')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Product Catalog', res.data)

        # Search test
        search_res = self.client.get('/products?search=Headphones')
        self.assertEqual(search_res.status_code, 200)
        self.assertIn(b'Headphones', search_res.data)

        # Category test
        cat_res = self.client.get('/products?category=Electronics')
        self.assertEqual(cat_res.status_code, 200)

    def test_04_shopping_cart_workflow(self):
        """Test adding item to cart, viewing cart, and updating quantity."""
        # Add product 1 to cart
        add_res = self.client.post('/cart/add', json={'product_id': 1, 'quantity': 2})
        self.assertEqual(add_res.status_code, 200)
        data = add_res.get_json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['cart_count'], 2)

        # View cart
        cart_view = self.client.get('/cart')
        self.assertEqual(cart_view.status_code, 200)
        self.assertIn(b'AuraPulse Wireless Noise-Cancelling Headphones', cart_view.data)

        # Checkout test
        order_res = self.client.post('/checkout', data={
            'full_name': 'Test Shopper',
            'email': 'shopper@test.com',
            'address': '123 Test Street, Bengaluru',
            'payment_method': 'UPI / GPay'
        }, follow_redirects=True)
        self.assertEqual(order_res.status_code, 200)
        self.assertIn(b'Order Confirmed!', order_res.data)

    def test_05_admin_dashboard_and_visualizations(self):
        """Test admin dashboard rendering, data mining metrics, and charts."""
        res = self.client.get('/admin')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Admin Sales', res.data)
        self.assertIn(b'RFM Customer Segmentation', res.data)
        self.assertIn(b'Product Demand Prediction', res.data)
        self.assertIn(b'data:image/png;base64', res.data) # Base64 chart verified

    def test_06_ai_feature_1_personality(self):
        """Test Feature 1: Shopping Personality AI API endpoint."""
        res = self.client.post('/api/ai/personality', json={
            'persona': 'I am a college student. Suggest useful products under 2000.',
            'budget': 2000.0
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('content', data)

    def test_07_ai_feature_2_review_detective(self):
        """Test Feature 2: Review Detective AI API endpoint."""
        res = self.client.post('/api/ai/review-detective', json={'product_id': 1})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('content', data)

    def test_08_ai_feature_3_product_battle(self):
        """Test Feature 3: Smart Product Battle AI API endpoint."""
        res = self.client.post('/api/ai/product-battle', json={
            'product_id_1': 1,
            'product_id_2': 3,
            'preference': 'Best Audio Quality'
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('content', data)

if __name__ == '__main__':
    unittest.main()
