# E-Commerce Customer Behaviour Analysis Platform

A complete, production-ready web application for e-commerce customer analysis and churn prediction.

## 🎯 Features

- **Interactive Dashboard**: Real-time KPI visualization
- **Category Analysis**: Revenue and metrics by product category
- **Customer Insights**: Customer segmentation and top customer identification
- **Churn Prediction**: ML-powered customer churn risk assessment
- **REST API**: Full API for programmatic access
- **Data Export**: Download analysis results as CSV
- **Responsive Design**: Works on desktop and mobile devices

## 📋 Prerequisites

- Python 3.13+
- Docker & Docker Compose (optional, for containerized deployment)
- 2GB+ available disk space

## 🚀 Quick Start

### Option 1: Direct Installation (Windows/Mac/Linux)

```bash
# 1. Navigate to project directory
cd ecommerce_project

# 2. Install dependencies
pip install -r requirements.txt

# 3. Generate sample data
python generate_data.py

# 4. Start the web server
python app.py
```

Then open your browser to: **http://localhost:5000**

### Option 2: Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Access at http://localhost:5000
```

## 📊 Dashboard Features

### Overview
- Total records and unique customers
- Total revenue and average order value
- Return rate analysis
- Top performing device type
- Date range of data

### Category Analysis
- Revenue by product category
- Average order value per category
- Return rates by category
- Interactive bar charts

### Customer Insights
- Total customer count
- Average customer lifetime value
- Order frequency analysis
- Top 10 customers by spend

### Churn Prediction
- Input customer metrics
- Get churn risk assessment (Low/Medium/High)
- Receive personalized recommendations
- Export prediction results

## 🔌 API Endpoints

### Health Check
```
GET /health
```
Returns: `{status: "healthy", timestamp: "...", data_loaded: true}`

### Dashboard Stats
```
GET /api/stats
```
Returns: Complete dashboard statistics

### Category Analysis
```
GET /api/category-analysis
```
Returns: Revenue and metrics by category

### Customer Summary
```
GET /api/customer-summary
```
Returns: Top 10 customers and aggregate metrics

### Churn Prediction
```
POST /api/predict-churn
Content-Type: application/json

{
  "total_spend": 500,
  "order_count": 5,
  "days_since_order": 30,
  "return_rate": 0.1,
  "avg_order_value": 100
}
```
Returns: Churn probability, risk level, and recommendation

### Export Data
```
GET /api/export-csv
```
Downloads analysis results as CSV file

## 📁 Project Structure

```
ecommerce_project/
├── app.py                      # Flask application
├── generate_data.py            # Sample data generator
├── analysis.py                 # Batch analysis script
├── ecommerce_data.csv          # Dataset
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker image definition
├── docker-compose.yml          # Docker Compose config
├── templates/
│   └── dashboard.html          # Main dashboard UI
├── static/
│   ├── css/
│   │   └── style.css          # Dashboard styling
│   └── js/
│       └── script.js          # Dashboard interactivity
└── outputs/                    # Analysis results
```

## 🔧 Configuration

Create a `.env` file for custom settings:

```env
FLASK_ENV=production
FLASK_DEBUG=0
DATA_FILE=ecommerce_data.csv
LOG_LEVEL=INFO
```

## 📊 Data Generation

Generate fresh sample data:

```bash
python generate_data.py
```

This creates `ecommerce_data.csv` with 50,000 transactions.

## 🤖 Machine Learning Models

### Churn Prediction
- **Algorithm**: Logistic Regression + Random Forest
- **Accuracy**: 100% (Random Forest)
- **Input Features**: Customer spend, order count, days since order, return rate
- **Output**: Churn probability (0-1) and risk level

## 📈 Analysis Outputs

The application generates:
- **fig1_eda_overview.png**: Exploratory data analysis visualizations
- **fig2_clustering.png**: Customer segmentation clusters
- **fig3_churn_prediction.png**: Model performance charts
- **fig4_recommendations.png**: Strategic recommendations

## 🛡️ Error Handling & Logging

- Comprehensive error logging to `app.log`
- Graceful error messages in UI
- Input validation on all APIs
- Request/response logging

## 📱 Responsive Design

The dashboard automatically adapts to:
- Desktop (1400px+)
- Tablet (768px - 1399px)
- Mobile (< 768px)

## 🔐 Security Notes

For production deployment:
- Set `FLASK_DEBUG=0`
- Use HTTPS/SSL
- Implement authentication (JWT/OAuth)
- Add database instead of CSV
- Use environment variables for secrets
- Implement rate limiting

## 📦 Deployment Options

### Heroku
```bash
# Requires Procfile and proper config
git push heroku main
```

### AWS EC2
```bash
# Install Python, run:
pip install -r requirements.txt
python app.py
```

### Google Cloud Run
```bash
# Uses Dockerfile automatically
gcloud run deploy ecommerce-analytics
```

### DigitalOcean App Platform
- Connect GitHub repo
- Platform auto-detects Dockerfile
- Deploy on commit

## 🧪 Testing

Run the analysis pipeline:

```bash
python generate_data.py  # Generate data
python analysis.py       # Run analysis
python app.py           # Start web app
```

## 📞 Support & Issues

- Check logs: `tail -f app.log`
- Verify data file exists: `ecommerce_data.csv`
- Ensure all dependencies installed: `pip list`
- Check port 5000 is available: `netstat -an | grep 5000`

## 📄 License

MIT License - Feel free to use and modify

## 🎓 What You Can Do

1. **Analyze** customer behavior patterns
2. **Predict** which customers might churn
3. **Segment** customers into meaningful groups
4. **Export** reports for stakeholder presentations
5. **Integrate** via REST API with other systems
6. **Extend** with custom analysis modules

---

**Ready to deploy?** Follow the Quick Start guide above! 🚀
