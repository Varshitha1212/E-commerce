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
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# Disable caching
@app.after_request
def no_cache(response):
    response.cache_control.no_cache = True
    response.cache_control.no_store = True
    response.cache_control.must_revalidate = True
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Config
PORT = int(os.environ.get('PORT', 5000))
DATA_FILE = 'ecommerce_data.csv'
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}

# Create uploads folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max

# Load data once
df = None
current_data_file = DATA_FILE

def load_data():
    global df, current_data_file
    if df is None:
        try:
            df = pd.read_csv(current_data_file, parse_dates=['order_date'])
            logger.info(f"✅ Loaded {len(df):,} records from {current_data_file}")
        except Exception as e:
            logger.error(f"❌ Error loading data: {e}")
            df = pd.DataFrame()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

@app.route('/api/upload', methods=['POST'])
def api_upload():
    global df, current_data_file
    
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if not allowed_file(file.filename):
        return jsonify({"error": "Only CSV files are allowed"}), 400
    
    try:
        filename = secure_filename(f"upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Validate CSV has required columns
        test_df = pd.read_csv(filepath, nrows=1)
        required_cols = ['customer_id', 'order_date', 'order_value', 'product_category']
        if not all(col in test_df.columns for col in required_cols):
            os.remove(filepath)
            return jsonify({"error": f"CSV must contain columns: {', '.join(required_cols)}"}), 400
        
        # Load the new data
        df = pd.read_csv(filepath, parse_dates=['order_date'])
        current_data_file = filepath
        logger.info(f"✅ Uploaded data: {len(df):,} records")
        
        return jsonify({
            "success": True,
            "message": f"Uploaded {len(df):,} records",
            "records": len(df),
            "file": filename
        }), 200
    
    except Exception as e:
        logger.error(f"❌ Upload error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health')
def health():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    logger.info(f"🚀 Starting on port {PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=False)
