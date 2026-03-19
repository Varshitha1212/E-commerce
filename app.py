"""
E-Commerce Analytics Platform - SIMPLIFIED FOR DEPLOYMENT
No ML dependencies, minimal imports, guaranteed to work
"""

from flask import Flask, render_template, request, jsonify, send_file, redirect
from flask_cors import CORS
import pandas as pd
import os
import logging
from datetime import datetime
import io

app = Flask(__name__)
CORS(app)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Config
PORT = int(os.environ.get('PORT', 5000))
DATA_FILE = 'ecommerce_data.csv'

# Load data once
df = None

def load_data():
    global df
    if df is None:
        try:
            df = pd.read_csv(DATA_FILE, parse_dates=['order_date'])
            logger.info(f"✅ Loaded {len(df):,} records")
        except Exception as e:
            logger.error(f"❌ Error loading data: {e}")
            df = pd.DataFrame()

# Routes
@app.route('/')
def home():
    return redirect('/dashboard')

@app.route('/dashboard')
def dashboard():
    load_data()
    if df.empty:
        return "Error: No data", 500
    
    stats = {
        "total_records": len(df),
        "total_revenue": float(df['order_value'].sum()),
        "avg_order_value": float(df['order_value'].mean()),
        "unique_customers": df['customer_id'].nunique(),
        "return_rate": float(df['returned'].mean() * 100),
        "top_categories": df['product_category'].value_counts().head(5).to_dict()
    }
    return render_template('dashboard.html', stats=stats)

@app.route('/api/stats')
def api_stats():
    load_data()
    if df.empty:
        return jsonify({"error": "No data"}), 500
    
    return jsonify({
        "total_records": len(df),
        "total_revenue": float(df['order_value'].sum()),
        "avg_order_value": float(df['order_value'].mean()),
        "unique_customers": df['customer_id'].nunique(),
        "return_rate": float(df['returned'].mean() * 100),
        "date_range": {
            "start": str(df['order_date'].min().date()),
            "end": str(df['order_date'].max().date())
        }
    })

@app.route('/api/categories')
def api_categories():
    load_data()
    if df.empty:
        return jsonify({"error": "No data"}), 500
    
    categories = []
    for cat in df['product_category'].unique():
        cat_df = df[df['product_category'] == cat]
        categories.append({
            "category": cat,
            "revenue": float(cat_df['order_value'].sum()),
            "orders": len(cat_df),
            "avg_value": float(cat_df['order_value'].mean())
        })
    return jsonify({"categories": sorted(categories, key=lambda x: x['revenue'], reverse=True)})

@app.route('/api/export')
def api_export():
    load_data()
    if df.empty:
        return jsonify({"error": "No data"}), 500
    
    csv = df.head(1000).to_csv(index=False)
    return send_file(
        io.BytesIO(csv.encode()),
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"export_{datetime.now().strftime('%Y%m%d')}.csv"
    )

@app.route('/health')
def health():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    logger.info(f"🚀 Starting on port {PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=False)
