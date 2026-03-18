"""
E-Commerce Customer Behaviour Analysis
Varshitha Malladi | Academic Project | Nov 2025
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (precision_score, recall_score, f1_score,
                             classification_report, silhouette_score,
                             confusion_matrix)
import warnings
warnings.filterwarnings('ignore')

np.random.seed(42)

# ─────────────────────────────────────────────────────────────────────────────
# 1. GENERATE REALISTIC 50,000-ROW DATASET
# ─────────────────────────────────────────────────────────────────────────────
print("=" * 60)
print("  E-COMMERCE CUSTOMER BEHAVIOUR ANALYSIS")
print("=" * 60)
print("\n[1/5] Generating 50,000-row e-commerce dataset...")

N = 50000
customer_ids = np.arange(1, N + 1)

# Simulate realistic customer behaviour distributions
age            = np.random.normal(35, 12, N).clip(18, 70).astype(int)
tenure_months  = np.random.exponential(18, N).clip(1, 60).astype(int)
annual_spend   = np.random.lognormal(7.5, 0.8, N).clip(100, 50000)
num_orders     = np.random.poisson(12, N).clip(1, 80)
avg_order_val  = annual_spend / num_orders
days_since_last= np.random.exponential(30, N).clip(1, 365).astype(int)
num_categories = np.random.randint(1, 9, N)
num_returns    = np.random.poisson(1.5, N).clip(0, 15)
email_opens    = np.random.beta(2, 5, N)          # engagement rate 0-1
discount_usage = np.random.beta(3, 4, N)          # discount affinity 0-1
support_tickets= np.random.poisson(0.8, N).clip(0, 8)
mobile_pct     = np.random.beta(4, 3, N)          # mobile vs desktop

# Simulate churn: higher probability for low spend, low engagement, high recency
churn_prob = (
    0.02
    + 0.30 * (days_since_last / 365)
    + 0.20 * (1 - email_opens)
    + 0.15 * (1 - discount_usage)
    + 0.10 * (num_returns / 15)
    + 0.10 * (support_tickets / 8)
    - 0.10 * (np.log1p(annual_spend) / np.log1p(50000))
    - 0.08 * (tenure_months / 60)
)
churn_prob = churn_prob.clip(0.02, 0.90)
churned = (np.random.rand(N) < churn_prob).astype(int)

categories = ['Electronics', 'Fashion', 'Home & Kitchen', 'Sports',
              'Beauty', 'Books', 'Toys', 'Grocery', 'Automotive']
top_category = np.random.choice(categories, N,
                                p=[0.18,0.20,0.15,0.10,0.12,0.08,0.07,0.07,0.03])
region = np.random.choice(['North', 'South', 'East', 'West', 'Central'], N,
                           p=[0.22, 0.25, 0.20, 0.18, 0.15])

df = pd.DataFrame({
    'customer_id':      customer_ids,
    'age':              age,
    'tenure_months':    tenure_months,
    'annual_spend':     annual_spend.round(2),
    'num_orders':       num_orders,
    'avg_order_value':  avg_order_val.round(2),
    'days_since_last_purchase': days_since_last,
    'num_categories_purchased': num_categories,
    'num_returns':      num_returns,
    'email_open_rate':  email_opens.round(4),
    'discount_usage_rate': discount_usage.round(4),
    'support_tickets':  support_tickets,
    'mobile_purchase_pct': mobile_pct.round(4),
    'top_category':     top_category,
    'region':           region,
    'churned':          churned
})

df.to_csv('/home/claude/ecommerce_project/ecommerce_data.csv', index=False)
print(f"   Dataset shape : {df.shape}")
print(f"   Churn rate    : {churned.mean()*100:.1f}%")
print(f"   Avg spend     : ₹{annual_spend.mean():,.0f}")

# ─────────────────────────────────────────────────────────────────────────────
# 2. EDA — FIGURE 1: PURCHASING PATTERNS
# ─────────────────────────────────────────────────────────────────────────────
print("\n[2/5] Running Exploratory Data Analysis...")

fig1, axes = plt.subplots(2, 3, figsize=(16, 10))
fig1.suptitle('E-Commerce Customer Behaviour — EDA Overview',
              fontsize=16, fontweight='bold', y=1.01)
palette = '#2563EB'

# (a) Annual spend distribution
axes[0,0].hist(df['annual_spend'], bins=60, color=palette, edgecolor='white', alpha=0.85)
axes[0,0].set_title('Annual Spend Distribution', fontweight='bold')
axes[0,0].set_xlabel('Annual Spend (₹)')
axes[0,0].set_ylabel('Count')
axes[0,0].axvline(df['annual_spend'].median(), color='#EF4444', lw=2,
                   linestyle='--', label=f"Median: ₹{df['annual_spend'].median():,.0f}")
axes[0,0].legend(fontsize=9)

# (b) Orders distribution
axes[0,1].hist(df['num_orders'], bins=40, color='#10B981', edgecolor='white', alpha=0.85)
axes[0,1].set_title('Number of Orders per Customer', fontweight='bold')
axes[0,1].set_xlabel('Number of Orders')
axes[0,1].set_ylabel('Count')
axes[0,1].axvline(df['num_orders'].median(), color='#EF4444', lw=2,
                   linestyle='--', label=f"Median: {df['num_orders'].median():.0f}")
axes[0,1].legend(fontsize=9)

# (c) Category popularity
cat_counts = df['top_category'].value_counts()
colors_cat = plt.cm.Blues_r(np.linspace(0.3, 0.85, len(cat_counts)))
axes[0,2].barh(cat_counts.index, cat_counts.values, color=colors_cat, edgecolor='white')
axes[0,2].set_title('Top Category by Customer Count', fontweight='bold')
axes[0,2].set_xlabel('Number of Customers')

# (d) Churn by region
churn_region = df.groupby('region')['churned'].mean() * 100
axes[1,0].bar(churn_region.index, churn_region.values,
              color=['#3B82F6','#60A5FA','#93C5FD','#BFDBFE','#DBEAFE'],
              edgecolor='white')
axes[1,0].set_title('Churn Rate by Region (%)', fontweight='bold')
axes[1,0].set_ylabel('Churn Rate (%)')
axes[1,0].set_ylim(0, 50)
for i, v in enumerate(churn_region.values):
    axes[1,0].text(i, v + 0.5, f'{v:.1f}%', ha='center', fontsize=9, fontweight='bold')

# (e) Spend vs Recency scatter (sampled)
sample = df.sample(2000, random_state=42)
scatter = axes[1,1].scatter(sample['days_since_last_purchase'],
                             sample['annual_spend'],
                             c=sample['churned'], cmap='RdYlGn_r',
                             alpha=0.4, s=8)
axes[1,1].set_title('Spend vs Recency (coloured by churn)', fontweight='bold')
axes[1,1].set_xlabel('Days Since Last Purchase')
axes[1,1].set_ylabel('Annual Spend (₹)')
plt.colorbar(scatter, ax=axes[1,1], label='Churned')

# (f) Correlation heatmap
num_cols = ['annual_spend','num_orders','avg_order_value',
            'days_since_last_purchase','email_open_rate',
            'discount_usage_rate','num_returns','churned']
corr = df[num_cols].corr()
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, ax=axes[1,2], mask=mask, annot=True, fmt='.2f',
            cmap='coolwarm', center=0, linewidths=0.5,
            annot_kws={'size': 7}, cbar_kws={'shrink': 0.8})
axes[1,2].set_title('Feature Correlation Matrix', fontweight='bold')
axes[1,2].tick_params(axis='x', rotation=45, labelsize=7)
axes[1,2].tick_params(axis='y', rotation=0, labelsize=7)

plt.tight_layout()
fig1.savefig('/home/claude/ecommerce_project/fig1_eda.png', dpi=150, bbox_inches='tight')
plt.close()
print("   EDA figure saved.")

# ─────────────────────────────────────────────────────────────────────────────
# 3. K-MEANS CLUSTERING — 5 BEHAVIOURAL COHORTS
# ─────────────────────────────────────────────────────────────────────────────
print("\n[3/5] K-Means Clustering — 5 Behavioural Cohorts...")

cluster_features = ['annual_spend', 'num_orders', 'avg_order_value',
                    'days_since_last_purchase', 'email_open_rate',
                    'discount_usage_rate', 'num_returns', 'tenure_months']

X_cluster = df[cluster_features].copy()
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_cluster)

# Elbow + silhouette to justify K=5
inertias, sil_scores = [], []
K_range = range(2, 9)
for k in K_range:
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(X_scaled)
    inertias.append(km.inertia_)
    sil_scores.append(silhouette_score(X_scaled, labels, sample_size=5000))

# Fit final K=5
kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
df['cluster'] = kmeans.fit_predict(X_scaled)
final_sil = silhouette_score(X_scaled, df['cluster'], sample_size=5000)
print(f"   Silhouette Score (K=5): {final_sil:.4f}")

# PCA for 2D visualisation
pca = PCA(n_components=2, random_state=42)
X_pca = pca.fit_transform(X_scaled)
df['pca1'] = X_pca[:, 0]
df['pca2'] = X_pca[:, 1]
print(f"   PCA variance explained: {pca.explained_variance_ratio_.sum()*100:.1f}%")

# Cluster profiles
cluster_profile = df.groupby('cluster')[cluster_features].mean()
cluster_sizes   = df['cluster'].value_counts().sort_index()

# Assign meaningful names
cluster_names = {
    0: 'Champions',
    1: 'At-Risk',
    2: 'Loyal Regulars',
    3: 'Price Seekers',
    4: 'Dormant'
}

# Re-label based on spend (highest spend = Champions, lowest = Dormant)
spend_order = cluster_profile['annual_spend'].rank(ascending=False).astype(int)
recency_order = cluster_profile['days_since_last_purchase'].rank(ascending=False).astype(int)

# Sort clusters by combined RFM score to assign names intelligently
rfm_score = (cluster_profile['annual_spend'].rank() +
             cluster_profile['num_orders'].rank() +
             (1/cluster_profile['days_since_last_purchase']).rank())
sorted_clusters = rfm_score.sort_values(ascending=False).index.tolist()

name_map = {}
names_ordered = ['Champions', 'Loyal Regulars', 'Price Seekers', 'At-Risk', 'Dormant']
for i, c in enumerate(sorted_clusters):
    name_map[c] = names_ordered[i]

df['segment'] = df['cluster'].map(name_map)

# ── FIGURE 2: Clustering Results ─────────────────────────────────────────────
fig2 = plt.figure(figsize=(18, 12))
gs  = gridspec.GridSpec(2, 3, figure=fig2, hspace=0.40, wspace=0.35)

seg_colors = {
    'Champions':     '#1D4ED8',
    'Loyal Regulars':'#059669',
    'Price Seekers': '#D97706',
    'At-Risk':       '#DC2626',
    'Dormant':       '#6B7280'
}

# (a) Elbow curve
ax_elbow = fig2.add_subplot(gs[0, 0])
ax_elbow.plot(K_range, inertias, 'o-', color='#2563EB', lw=2, markersize=6)
ax_elbow.axvline(5, color='#EF4444', linestyle='--', lw=1.5, label='K=5 chosen')
ax_elbow.set_title('Elbow Curve — Inertia vs K', fontweight='bold')
ax_elbow.set_xlabel('Number of Clusters (K)')
ax_elbow.set_ylabel('Inertia')
ax_elbow.legend(fontsize=9)

# (b) Silhouette scores
ax_sil = fig2.add_subplot(gs[0, 1])
ax_sil.plot(K_range, sil_scores, 's-', color='#10B981', lw=2, markersize=6)
ax_sil.axvline(5, color='#EF4444', linestyle='--', lw=1.5,
               label=f'K=5  (score={final_sil:.3f})')
ax_sil.set_title('Silhouette Score vs K', fontweight='bold')
ax_sil.set_xlabel('Number of Clusters (K)')
ax_sil.set_ylabel('Silhouette Score')
ax_sil.legend(fontsize=9)

# (c) PCA scatter
ax_pca = fig2.add_subplot(gs[0, 2])
sample2 = df.sample(8000, random_state=42)
for seg, grp in sample2.groupby('segment'):
    ax_pca.scatter(grp['pca1'], grp['pca2'],
                   c=seg_colors[seg], label=seg, alpha=0.35, s=6)
ax_pca.set_title(f'Customer Segments — PCA Projection\n(explained var: {pca.explained_variance_ratio_.sum()*100:.1f}%)',
                 fontweight='bold')
ax_pca.set_xlabel('PC1')
ax_pca.set_ylabel('PC2')
ax_pca.legend(fontsize=8, markerscale=3, loc='upper right')

# (d) Segment sizes
ax_size = fig2.add_subplot(gs[1, 0])
seg_counts = df['segment'].value_counts()
bars = ax_size.bar(seg_counts.index, seg_counts.values,
                   color=[seg_colors[s] for s in seg_counts.index],
                   edgecolor='white', linewidth=1.2)
ax_size.set_title('Customers per Segment', fontweight='bold')
ax_size.set_ylabel('Number of Customers')
ax_size.tick_params(axis='x', rotation=20)
for bar, val in zip(bars, seg_counts.values):
    ax_size.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 80,
                 f'{val:,}', ha='center', fontsize=9, fontweight='bold')

# (e) Radar chart — segment profiles
ax_radar = fig2.add_subplot(gs[1, 1], polar=True)
radar_metrics = ['Annual Spend', 'Num Orders', 'Recency\n(inv)', 'Email\nEngagement', 'Loyalty']
radar_cols    = ['annual_spend', 'num_orders', 'days_since_last_purchase',
                 'email_open_rate', 'tenure_months']

seg_means = df.groupby('segment')[radar_cols].mean()
# Normalise 0-1 per column; invert recency
for col in radar_cols:
    seg_means[col] = (seg_means[col] - seg_means[col].min()) / \
                     (seg_means[col].max() - seg_means[col].min() + 1e-9)
seg_means['days_since_last_purchase'] = 1 - seg_means['days_since_last_purchase']

angles = np.linspace(0, 2*np.pi, len(radar_metrics), endpoint=False).tolist()
angles += angles[:1]

for seg in ['Champions', 'Loyal Regulars', 'At-Risk', 'Dormant']:
    vals = seg_means.loc[seg, radar_cols].tolist()
    vals += vals[:1]
    ax_radar.plot(angles, vals, 'o-', lw=2, color=seg_colors[seg], label=seg, markersize=4)
    ax_radar.fill(angles, vals, alpha=0.06, color=seg_colors[seg])

ax_radar.set_xticks(angles[:-1])
ax_radar.set_xticklabels(radar_metrics, size=8)
ax_radar.set_title('Segment Profiles (Radar)', fontweight='bold', pad=18)
ax_radar.legend(fontsize=7, loc='upper right', bbox_to_anchor=(1.35, 1.15))
ax_radar.set_ylim(0, 1)

# (f) Avg spend per segment (horizontal)
ax_spend = fig2.add_subplot(gs[1, 2])
seg_spend = df.groupby('segment')['annual_spend'].mean().sort_values(ascending=True)
colors_sp = [seg_colors[s] for s in seg_spend.index]
bars2 = ax_spend.barh(seg_spend.index, seg_spend.values, color=colors_sp,
                       edgecolor='white', height=0.6)
ax_spend.set_title('Avg Annual Spend by Segment', fontweight='bold')
ax_spend.set_xlabel('Avg Annual Spend (₹)')
for bar, val in zip(bars2, seg_spend.values):
    ax_spend.text(val + 50, bar.get_y() + bar.get_height()/2,
                  f'₹{val:,.0f}', va='center', fontsize=9, fontweight='bold')

fig2.suptitle('K-Means Customer Segmentation Results  |  K=5  |  Silhouette='
              f'{final_sil:.3f}', fontsize=14, fontweight='bold')
fig2.savefig('/home/claude/ecommerce_project/fig2_clustering.png', dpi=150, bbox_inches='tight')
plt.close()
print("   Clustering figure saved.")

# ─────────────────────────────────────────────────────────────────────────────
# 4. CHURN PREDICTION MODEL
# ─────────────────────────────────────────────────────────────────────────────
print("\n[4/5] Training Churn Prediction Models...")

model_features = ['annual_spend', 'num_orders', 'avg_order_value',
                  'days_since_last_purchase', 'email_open_rate',
                  'discount_usage_rate', 'num_returns', 'tenure_months',
                  'num_categories_purchased', 'support_tickets', 'mobile_purchase_pct']

X = df[model_features]
y = df['churned']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)

scaler_m = StandardScaler()
X_train_s = scaler_m.fit_transform(X_train)
X_test_s  = scaler_m.transform(X_test)

# Logistic Regression
lr = LogisticRegression(max_iter=1000, random_state=42, class_weight='balanced')
lr.fit(X_train_s, y_train)
lr_pred = lr.predict(X_test_s)
lr_prec = precision_score(y_test, lr_pred)
lr_rec  = recall_score(y_test, lr_pred)
lr_f1   = f1_score(y_test, lr_pred)

# Random Forest
rf = RandomForestClassifier(n_estimators=200, max_depth=12, random_state=42,
                             class_weight='balanced', n_jobs=-1)
rf.fit(X_train, y_train)
rf_pred = rf.predict(X_test)
rf_prec = precision_score(y_test, rf_pred)
rf_rec  = recall_score(y_test, rf_pred)
rf_f1   = f1_score(y_test, rf_pred)

print(f"\n   Logistic Regression  — Precision: {lr_prec:.4f}  Recall: {lr_rec:.4f}  F1: {lr_f1:.4f}")
print(f"   Random Forest        — Precision: {rf_prec:.4f}  Recall: {rf_rec:.4f}  F1: {rf_f1:.4f}")

# Cross-validation
rf_cv = cross_val_score(rf, X, y, cv=5, scoring='precision', n_jobs=-1)
print(f"   RF 5-Fold CV Precision: {rf_cv.mean():.4f} ± {rf_cv.std():.4f}")

# Feature importance
feat_imp = pd.Series(rf.feature_importances_, index=model_features).sort_values(ascending=False)

# ── FIGURE 3: Model Results ───────────────────────────────────────────────────
fig3, axes3 = plt.subplots(1, 3, figsize=(18, 6))
fig3.suptitle('Churn Prediction Model Results', fontsize=15, fontweight='bold')

# (a) Model comparison bar chart
models     = ['Logistic\nRegression', 'Random\nForest']
precisions = [lr_prec, rf_prec]
recalls    = [lr_rec,  rf_rec]
f1s        = [lr_f1,   rf_f1]

x = np.arange(len(models))
w = 0.25
axes3[0].bar(x - w, precisions, w, label='Precision', color='#2563EB', edgecolor='white')
axes3[0].bar(x,     recalls,    w, label='Recall',    color='#10B981', edgecolor='white')
axes3[0].bar(x + w, f1s,        w, label='F1 Score',  color='#F59E0B', edgecolor='white')
axes3[0].set_xticks(x)
axes3[0].set_xticklabels(models, fontsize=11)
axes3[0].set_ylim(0, 1.05)
axes3[0].set_ylabel('Score')
axes3[0].set_title('Model Performance Comparison', fontweight='bold')
axes3[0].legend(fontsize=10)
for i, (p, r, f) in enumerate(zip(precisions, recalls, f1s)):
    axes3[0].text(i-w, p+0.01, f'{p:.2f}', ha='center', fontsize=8, fontweight='bold')
    axes3[0].text(i,   r+0.01, f'{r:.2f}', ha='center', fontsize=8, fontweight='bold')
    axes3[0].text(i+w, f+0.01, f'{f:.2f}', ha='center', fontsize=8, fontweight='bold')

# (b) Confusion matrix — Random Forest
cm = confusion_matrix(y_test, rf_pred)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes3[1],
            xticklabels=['Retained', 'Churned'],
            yticklabels=['Retained', 'Churned'],
            annot_kws={'size': 14, 'fontweight': 'bold'}, linewidths=1)
axes3[1].set_title(f'Random Forest — Confusion Matrix\n(Precision={rf_prec:.2f}  Recall={rf_rec:.2f})',
                   fontweight='bold')
axes3[1].set_xlabel('Predicted')
axes3[1].set_ylabel('Actual')

# (c) Feature importance
feat_imp_top = feat_imp.head(10)
colors_fi = plt.cm.Blues_r(np.linspace(0.3, 0.85, len(feat_imp_top)))
axes3[2].barh(feat_imp_top.index[::-1], feat_imp_top.values[::-1],
              color=colors_fi[::-1], edgecolor='white')
axes3[2].set_title('Top-10 Feature Importances\n(Random Forest)', fontweight='bold')
axes3[2].set_xlabel('Importance Score')
for i, (val, name) in enumerate(zip(feat_imp_top.values[::-1], feat_imp_top.index[::-1])):
    axes3[2].text(val + 0.001, i, f'{val:.3f}', va='center', fontsize=8)

plt.tight_layout()
fig3.savefig('/home/claude/ecommerce_project/fig3_model.png', dpi=150, bbox_inches='tight')
plt.close()
print("   Model figure saved.")

# ─────────────────────────────────────────────────────────────────────────────
# 5. 3 ACTIONABLE RECOMMENDATIONS REPORT
# ─────────────────────────────────────────────────────────────────────────────
print("\n[5/5] Generating Recommendations Report...")

champ   = df[df['segment']=='Champions']
at_risk = df[df['segment']=='At-Risk']
dormant = df[df['segment']=='Dormant']
seekers = df[df['segment']=='Price Seekers']

rec1_revenue_at_risk = at_risk['annual_spend'].sum()
rec2_dormant_count   = len(dormant)
rec3_champ_spend     = champ['annual_spend'].mean()

report = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║         E-COMMERCE CUSTOMER BEHAVIOUR ANALYSIS — FINDINGS REPORT           ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Dataset  : 50,000 customers  |  Churn Rate: {df['churned'].mean()*100:.1f}%                     ║
║  Segments : 5 cohorts (K-Means)  |  Silhouette Score: {final_sil:.4f}            ║
║  Model    : Random Forest  |  Precision: {rf_prec:.4f}  |  F1: {rf_f1:.4f}          ║
╚══════════════════════════════════════════════════════════════════════════════╝

SEGMENT SUMMARY
───────────────────────────────────────────────────────────────────────────────
"""
for seg in ['Champions','Loyal Regulars','Price Seekers','At-Risk','Dormant']:
    g = df[df['segment']==seg]
    report += (f"  {seg:<18} | n={len(g):>5,} | "
               f"Avg Spend=₹{g['annual_spend'].mean():>8,.0f} | "
               f"Churn={g['churned'].mean()*100:>5.1f}%\n")

report += f"""
───────────────────────────────────────────────────────────────────────────────

RECOMMENDATION 1 — RETAIN AT-RISK CUSTOMERS (High Revenue Impact)
  ● Segment size   : {len(at_risk):,} customers
  ● Revenue at risk: ₹{rec1_revenue_at_risk:,.0f}
  ● Avg days since last purchase: {at_risk['days_since_last_purchase'].mean():.0f} days
  ● Action: Deploy personalised re-engagement emails targeting customers with
    >45 days since last purchase and email_open_rate < 0.25.
    A 15% churn reduction in this segment would recover ≈ ₹{rec1_revenue_at_risk*0.15:,.0f}.

RECOMMENDATION 2 — WIN BACK DORMANT CUSTOMERS VIA DISCOUNT TARGETING
  ● Dormant customers  : {rec2_dormant_count:,}
  ● Avg discount usage : {dormant['discount_usage_rate'].mean():.2%}
  ● Action: Dormant customers have high discount affinity (
    {dormant['discount_usage_rate'].mean():.2%} vs {champ['discount_usage_rate'].mean():.2%} in Champions).
    A time-limited 20% discount campaign with 10% conversion rate would
    generate ≈ ₹{rec2_dormant_count * 0.10 * dormant['annual_spend'].mean():,.0f} in recovered revenue.

RECOMMENDATION 3 — INCREASE SHARE-OF-WALLET AMONG CHAMPIONS
  ● Champions count    : {len(champ):,} customers
  ● Avg annual spend   : ₹{rec3_champ_spend:,.0f}
  ● Avg categories     : {champ['num_categories_purchased'].mean():.1f} / 9
  ● Action: Champions purchase across only {champ['num_categories_purchased'].mean():.1f} categories on average.
    Cross-category recommendation campaigns could expand wallet share.
    A 5% spend increase yields ≈ ₹{len(champ) * rec3_champ_spend * 0.05:,.0f} additional revenue.

MODEL LIMITATIONS
  ● Dataset is synthetic; real-world churn drivers may differ.
  ● Logistic Regression assumes linear decision boundary — may underfit.
  ● Random Forest precision of {rf_prec:.2f} may degrade on new customer cohorts.
  ● Class imbalance ({df['churned'].mean()*100:.1f}% churn) managed via class_weight='balanced'.
  ● Recommend retraining quarterly as seasonal spending patterns shift.

───────────────────────────────────────────────────────────────────────────────
Generated by: Varshitha Malladi  |  Academic Project  |  Nov 2025
"""

with open('/home/claude/ecommerce_project/report.txt', 'w') as f:
    f.write(report)
print(report)

print("\n✅ ALL DONE — Project files saved:")
print("   • ecommerce_data.csv     (50,000 rows)")
print("   • ecommerce_analysis.py  (full source code)")
print("   • fig1_eda.png           (EDA visualisations)")
print("   • fig2_clustering.png    (segmentation results)")
print("   • fig3_model.png         (model performance)")
print("   • report.txt             (findings + recommendations)")
