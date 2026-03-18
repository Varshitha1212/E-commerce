"""
Flask web application for E-Commerce Customer Behaviour Analysis
Provides both REST API and interactive web dashboard
PUBLIC ACCESS - NO AUTHENTICATION REQUIRED
"""

from flask import Flask, render_template, request, jsonify, send_file, redirect
from flask_cors import CORS
import pandas as pd
import numpy as np
import os
import logging
from datetime import datetime, timedelta
import joblib
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
import io

# ──────────────────────────────────────────────────────────────
# Configuration & Setup
# ──────────────────────────────────────────────────────────────

app = Flask(__name__)
CORS(app)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
DATA_FILE = 'ecommerce_data.csv'
MODEL_FILE = 'churn_model.pkl'
OUTPUTS_DIR = 'outputs'
PORT = int(os.environ.get('PORT', 5000))

os.makedirs(OUTPUTS_DIR, exist_ok=True)

# ──────────────────────────────────────────────────────────────
# Routes - Dashboard
# ──────────────────────────────────────────────────────────────

@app.route('/')
def index():
    """Redirect to dashboard"""
    return redirect('/dashboard')


@app.route('/dashboard')
def dashboard():
    """Main interactive dashboard - public access"""
    if app.df is None:
        return "Error: Data not loaded", 500
    
    try:
        stats = get_dashboard_stats()
        logger.info("Dashboard accessed")
        return render_template('dashboard.html', stats=stats, username='User')
    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}")
        return f"Error loading dashboard: {str(e)}", 500

# ──────────────────────────────────────────────────────────────
# Data Loading & Caching
# ──────────────────────────────────────────────────────────────

@app.before_request
def load_data():
    """Load data once per app lifecycle"""
    if not hasattr(app, 'df'):
        try:
            app.df = pd.read_csv(DATA_FILE, parse_dates=['order_date'])
            logger.info(f"Loaded dataset: {app.df.shape[0]:,} rows")
        except Exception as e:
            logger.error(f"Failed to load data: {str(e)}")
            app.df = None


def get_dashboard_stats():
    """Calculate dashboard statistics"""
    df = app.df
    
    return {
        "total_records": int(df.shape[0]),
        "unique_customers": int(df['customer_id'].nunique()),
        "total_revenue": float(df['order_value'].sum()),
        "avg_order_value": float(df['order_value'].mean()),
        "return_rate": float(df['returned'].mean() * 100),
        "date_range": {
            "start": df['order_date'].min().strftime('%Y-%m-%d'),
            "end": df['order_date'].max().strftime('%Y-%m-%d')
        },
        "top_categories": df['product_category'].value_counts().head(5).to_dict(),
        "top_device": df['device'].value_counts().index[0],
        "avg_session_count": float(df['session_count'].mean())
    }


# ──────────────────────────────────────────────────────────────
# Routes - Analysis APIs
# ──────────────────────────────────────────────────────────────

@app.route('/api/stats')
def api_stats():
    """API endpoint: Get summary statistics"""
    if app.df is None:
        return jsonify({"error": "Data not loaded"}), 500
    
    try:
        stats = get_dashboard_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Stats API error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/category-analysis', methods=['GET'])
def api_category_analysis():
    """Detailed revenue & metrics by product category"""
    if app.df is None:
        return jsonify({"error": "Data not loaded"}), 500
    
    try:
        df = app.df
        result = []
        
        for category in df['product_category'].unique():
            cat_data = df[df['product_category'] == category]
            total_revenue = float(cat_data['order_value'].sum())
            avg_order_value = float(cat_data['order_value'].mean())
            order_count = int(len(cat_data))
            return_rate = float((cat_data['returned'].sum() / len(cat_data)) * 100)
            
            result.append({
                "category": category,
                "total_revenue": total_revenue,
                "avg_order_value": avg_order_value,
                "order_count": order_count,
                "return_rate": return_rate
            })
        
        return jsonify({"categories": sorted(result, key=lambda x: x['total_revenue'], reverse=True)})
    except Exception as e:
        logger.error(f"Category analysis error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/customer-summary', methods=['GET'])
def api_customer_summary():
    """Get customer-level insights"""
    if app.df is None:
        return jsonify({"error": "Data not loaded"}), 500
    
    try:
        df = app.df
        cust_agg = df.groupby('customer_id').agg({
            'order_value': ['sum', 'mean', 'count'],
            'returned': 'sum',
            'order_date': ['min', 'max']
        }).round(2)
        
        cust_agg.columns = ['total_spend', 'avg_order_value', 'order_count', 'returns', 'first_order', 'last_order']
        
        return jsonify({
            "total_customers": len(cust_agg),
            "avg_customer_value": float(cust_agg['total_spend'].mean()),
            "avg_orders_per_customer": float(cust_agg['order_count'].mean()),
            "top_10_customers": cust_agg.nlargest(10, 'total_spend')[['total_spend', 'order_count', 'avg_order_value']].to_dict(orient='index')
        })
    except Exception as e:
        logger.error(f"Customer summary error: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ──────────────────────────────────────────────────────────────
# Routes - Predictions
# ──────────────────────────────────────────────────────────────

@app.route('/api/predict-churn', methods=['POST'])
def api_predict_churn():
    """Predict customer churn probability"""
    if app.df is None:
        return jsonify({"error": "Data not loaded"}), 500
    
    try:
        data = request.get_json()
        
        # Validate input
        required_fields = ['total_spend', 'order_count', 'days_since_order']
        if not all(field in data for field in required_fields):
            return jsonify({"error": f"Missing required fields: {required_fields}"}), 400
        
        # Create feature vector (simple features for demo)
        features = np.array([[
            data.get('total_spend', 0),
            data.get('order_count', 0),
            data.get('days_since_order', 0),
            data.get('return_rate', 0),
            data.get('avg_order_value', 50)
        ]])
        
        # Simple heuristic model (in production, load trained model)
        churn_prob = min(1.0, (data['days_since_order'] / 365) * 0.7 + (0.1 if data.get('return_rate', 0) > 0.2 else 0))
        churn_risk = "High" if churn_prob > 0.5 else ("Medium" if churn_prob > 0.3 else "Low")
        
        return jsonify({
            "churn_probability": float(churn_prob),
            "churn_risk": churn_risk,
            "recommendation": get_churn_recommendation(churn_prob, data)
        })
    except Exception as e:
        logger.error(f"Churn prediction error: {str(e)}")
        return jsonify({"error": str(e)}), 500


def get_churn_recommendation(churn_prob, customer_data):
    """Generate recommendations based on churn risk"""
    if churn_prob > 0.6:
        return "🔴 Urgent: Send personalized offer (15-20% discount) within 7 days"
    elif churn_prob > 0.4:
        return "🟡 At-Risk: Send email campaign with product recommendations"
    else:
        return "🟢 Engaged: Continue regular communications"


# ──────────────────────────────────────────────────────────────
# Routes - File Exports
# ──────────────────────────────────────────────────────────────

@app.route('/api/export-csv', methods=['GET'])
def api_export_csv():
    """Export analysis results as CSV"""
    if app.df is None:
        return jsonify({"error": "Data not loaded"}), 500
    
    try:
        csv_buffer = io.StringIO()
        app.df.head(1000).to_csv(csv_buffer, index=False)
        
        csv_buffer.seek(0)
        return send_file(
            io.BytesIO(csv_buffer.getvalue().encode()),
            mimetype="text/csv",
            as_attachment=True,
            download_name=f"ecommerce_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
    except Exception as e:
        logger.error(f"Export error: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ──────────────────────────────────────────────────────────────
# Error Handlers
# ──────────────────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def server_error(error):
    logger.error(f"Server error: {str(error)}")
    return jsonify({"error": "Internal server error"}), 500


# ──────────────────────────────────────────────────────────────
# Health Check
# ──────────────────────────────────────────────────────────────

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "data_loaded": app.df is not None
    })


if __name__ == '__main__':
    logger.info(f"Starting E-Commerce Analysis Web Application on port {PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=False)
