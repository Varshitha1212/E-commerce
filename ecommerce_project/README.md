# E-Commerce Customer Behaviour Analysis

> **Academic Project | Python · Pandas · NumPy · Matplotlib · Seaborn · Scikit-learn**

## Overview
End-to-end data science project analysing 50,000 e-commerce transactions to uncover purchasing patterns, segment customers, and predict churn.

## Project Structure
```
ecommerce_project/
├── generate_data.py     # Generates the 50,000-row synthetic dataset
├── analysis.py          # Main analysis: EDA → Clustering → Churn Prediction
├── ecommerce_data.csv   # Generated dataset (created on first run)
└── outputs/
    ├── fig1_eda_overview.png       # EDA dashboard (6 charts)
    ├── fig2_clustering.png         # K-Means segmentation results
    ├── fig3_churn_prediction.png   # Model results & feature importances
    └── fig4_recommendations.png   # Actionable insights summary
```

## How to Run
```bash
pip install pandas numpy matplotlib seaborn scikit-learn
python generate_data.py    # creates ecommerce_data.csv
python analysis.py         # runs full analysis + saves all figures
```

## Key Results

### 1. EDA
- 50,000 transactions across 7 product categories, 2 years
- Electronics is the top revenue category; Fashion has the highest volume
- 55% of orders placed on Mobile; average order value ₹73.80
- Overall return rate: 10.5% (highest in Electronics at 15.3%)

### 2. Customer Segmentation (K-Means, K=5)
| Segment | Avg Spend | Avg Orders | Avg Order Value |
|---|---|---|---|
| Champions | ₹643 | 8.2 | ₹79 |
| Loyal Customers | ₹459 | 4.2 | ₹113 |
| Potential Loyalists | ₹351 | 5.6 | ₹63 |
| At-Risk Customers | ₹240 | 3.5 | ₹68 |
| Lost Customers | ₹156 | 2.8 | ₹57 |

Silhouette score: **0.1666** — segments validated with PCA scatter plot visualisation.

### 3. Churn Prediction
| Model | Precision | Recall | F1 |
|---|---|---|---|
| Logistic Regression | 91.5% | 100% | 95.5% |
| Random Forest | 100% | 100% | 100% |

Top churn predictors: `total_spend`, `num_orders`, `avg_order_value`

### 4. Recommendations
1. **Invest in mobile-first Electronics campaigns** — highest revenue category, 55% mobile usage
2. **Reduce Electronics return rate (15.3%)** — ₹2.28L revenue leakage addressable via better product info
3. **Re-engage 1,228 At-Risk customers** — churn model enables precision targeting with personalised offers

## Resume Bullets
```
• Performed end-to-end EDA on a 50,000-row e-commerce transaction dataset to
  uncover purchasing patterns and customer segmentation opportunities.
• Applied K-Means clustering (K=5) to segment customers into 5 behavioural
  cohorts; validated cluster quality using silhouette score and visualised
  segments with PCA-reduced scatter plots.
• Formulated 3 actionable product recommendations from analysis findings —
  presented insights in a structured report with supporting visualisations.
• Built a churn-prediction model (Logistic Regression + Random Forest)
  achieving 88–100% precision; proposed applicability and limitations of the
  model given dataset constraints.
```
