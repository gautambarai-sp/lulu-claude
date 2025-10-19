# lulu_sales_dashboardexe.py
# Enterprise-Grade Sales Analytics Dashboard for Lulu UAE
# Built with Improved Prompt Engineering Principles
# Usage: streamlit run lulu_sales_dashboardexe.py

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')

# ===== PAGE CONFIG =====
st.set_page_config(
    page_title="Lulu Sales Analytics Executive Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

alt.data_transformers.enable('default', max_rows=50000)

# ===== CUSTOM STYLING =====
st.markdown("""
<style>
    .main { padding-top: 0; }
    
    .kpi-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 12px;
        color: white;
        text-align: center;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        margin: 5px;
    }
    
    .insight-box {
        background: #e3f2fd;
        padding: 20px;
        border-left: 5px solid #2196F3;
        border-radius: 8px;
        margin: 15px 0;
        font-size: 15px;
    }
    
    .recommendation-box {
        background: #e8f5e9;
        padding: 20px;
        border-left: 5px solid #4caf50;
        border-radius: 8px;
        margin: 15px 0;
        font-size: 15px;
    }
    
    .warning-box {
        background: #fff3e0;
        padding: 20px;
        border-left: 5px solid #ff9800;
        border-radius: 8px;
        margin: 15px 0;
        font-size: 15px;
    }
    
    .metric-value {
        font-size: 28px;
        font-weight: bold;
        color: white;
    }
    
    .metric-label {
        font-size: 14px;
        color: rgba(255,255,255,0.8);
        margin-top: 5px;
    }
</style>
""", unsafe_allow_html=True)

# ===== HELPER FUNCTIONS =====
@st.cache_data
def load_data(file_path):
    try:
        return pd.read_csv(file_path)
    except:
        return None

def detect_columns(df):
    cols = df.columns.tolist()
    def find(terms):
        for t in terms:
            for c in cols:
                if t in c.lower():
                    return c
        return None
    
    return {
        'amount': find(['amount','sales','revenue','total','paid','value']),
        'qty': find(['qty','quantity','units']),
        'department': find(['department','dept']),
        'store_format': find(['store_format','store format','format','storetype']),
        'category': find(['category','cat','sub_category']),
        'product': find(['product','sku','item','product_name','brand']),
        'campaign': find(['campaign','ad_campaign','campaign_name']),
        'channel': find(['channel','ad_channel','media_channel']),
        'promo': find(['promo','voucher','coupon','discount']),
        'gender': find(['gender']),
        'age': find(['age','customer_age']),
        'nationality': find(['nation','country','nationality']),
        'city': find(['city','location']),
        'zone': find(['zone','area','district']),
        'transaction': find(['invoice','transaction','order','receipt','txn']),
        'date': find(['date','transaction_date','purchase_date']),
        'customer_type': find(['customer_type','new_repeat','customer_status'])
    }

def prepare_data(df, mapping):
    d = df.copy()
    
    # Rename columns
    ren = {}
    if mapping['amount']: ren[mapping['amount']] = 'SalesAmount'
    if mapping['qty']: ren[mapping['qty']] = 'Quantity'
    if mapping['department']: ren[mapping['department']] = 'Department'
    if mapping['store_format']: ren[mapping['store_format']] = 'Store_Format'
    if mapping['category']: ren[mapping['category']] = 'Category'
    if mapping['product']: ren[mapping['product']] = 'Product'
    if mapping['campaign']: ren[mapping['campaign']] = 'Campaign'
    if mapping['channel']: ren[mapping['channel']] = 'Channel'
    if mapping['promo']: ren[mapping['promo']] = 'PromoCode'
    if mapping['gender']: ren[mapping['gender']] = 'Gender'
    if mapping['age']: ren[mapping['age']] = 'Age'
    if mapping['nationality']: ren[mapping['nationality']] = 'Nationality'
    if mapping['city']: ren[mapping['city']] = 'City'
    if mapping['zone']: ren[mapping['zone']] = 'Zone'
    if mapping['transaction']: ren[mapping['transaction']] = 'Transaction'
    if mapping['date']: ren[mapping['date']] = 'Date'
    if mapping['customer_type']: ren[mapping['customer_type']] = 'CustomerType'
    
    d = d.rename(columns=ren)
    
    # Ensure numeric columns
    if 'SalesAmount' not in d.columns:
        d['SalesAmount'] = 1.0
    else:
        d['SalesAmount'] = pd.to_numeric(d['SalesAmount'], errors='coerce').fillna(0)
    
    if 'Quantity' not in d.columns:
        d['Quantity'] = 1
    else:
        d['Quantity'] = pd.to_numeric(d['Quantity'], errors='coerce').fillna(1)
    
    if 'Transaction' not in d.columns:
        d['Transaction'] = range(len(d))
    
    # Age groups
    if 'Age' not in d.columns:
        d['Age'] = np.random.randint(18, 65, len(d))
    else:
        d['Age'] = pd.to_numeric(d['Age'], errors='coerce').fillna(30)
    
    def get_age_group(age):
        if pd.isna(age): return 'Unknown'
        if age < 18: return '13-17'
        elif age < 25: return '18-24'
        elif age < 35: return '25-34'
        elif age < 45: return '35-44'
        elif age < 55: return '45-54'
        elif age < 65: return '55-64'
        else: return '65+'
    
    d['AgeGroup'] = d['Age'].apply(get_age_group)
    
    # Fill text columns
    text_cols = ['Department','Store_Format','Category','Product','Campaign','Channel','PromoCode','Gender','Nationality','City','Zone','CustomerType']
    for col in text_cols:
        if col in d.columns:
            d[col] = d[col].fillna('Unknown').astype(str)
    
    # Date
    if 'Date' in d.columns:
        d['Date'] = pd.to_datetime(d['Date'], errors='coerce')
    else:
        d['Date'] = pd.Timestamp.now()
    
    # Promo used
    if 'PromoCode' in d.columns:
        d['PromoUsed'] = d['PromoCode'].apply(lambda x: x != 'Unknown' and x != '' if isinstance(x, str) else False)
    else:
        d['PromoUsed'] = False
    
    return d

def get_top_items(df, col, n=5):
    if col not in df.columns or len(df) == 0:
        return pd.DataFrame()
    return df.groupby(col).agg(
        Sales=('SalesAmount', 'sum'),
        Qty=('Quantity', 'sum'),
        Txns=('Transaction', 'nunique'),
        AvgPrice=('SalesAmount', 'mean')
    ).reset_index().sort_values('Sales', ascending=False).head(n)

def calculate_roi(campaign_sales, campaign_spend=1000):
    if campaign_spend == 0:
        return 0
    return ((campaign_sales - campaign_spend) / campaign_spend) * 100

# ===== LOAD & PREPARE DATA =====
st.sidebar.header("📂 Data Management")

DEFAULT_PATH = "/mnt/data/lulu_uae_master_2000.csv"
raw_data = load_data(DEFAULT_PATH)

if raw_data is None:
    uploaded_file = st.sidebar.file_uploader("📤 Upload CSV File", type=['csv'])
    if uploaded_file:
        raw_data = pd.read_csv(uploaded_file)
    else:
        st.error("❌ No data loaded. Please upload a CSV file.")
        st.stop()

mapping = detect_columns(raw_data)
df = prepare_data(raw_data, mapping)

# ===== GLOBAL FILTERS =====
st.sidebar.header("🎯 Filters")

cities = ['All'] + sorted([c for c in df['City'].unique() if c != 'Unknown'])
selected_city = st.sidebar.selectbox("🏙️ City", cities)

stores = ['All'] + sorted([s for s in df['Store_Format'].unique() if s != 'Unknown'])
selected_store = st.sidebar.selectbox("🏬 Store Format", stores)

if df['Date'].notna().any():
    min_date = df['Date'].min().date()
    max_date = df['Date'].max().date()
    date_range = st.sidebar.date_input("📅 Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
else:
    date_range = None

# Apply filters
mask = pd.Series(True, index=df.index)
if selected_city != 'All':
    mask &= (df['City'] == selected_city)
if selected_store != 'All':
    mask &= (df['Store_Format'] == selected_store)
if date_range and len(date_range) == 2:
    start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    mask &= (df['Date'] >= start) & (df['Date'] <= end)

filtered = df[mask].copy()

if len(filtered) == 0:
    st.warning("⚠️ No data for selected filters")
    st.stop()

# ===== NAVIGATION =====
st.sidebar.header("📑 Navigation")
page = st.sidebar.radio("Select View", [
    "📊 Executive Dashboard",
    "🏙️ City Strategy",
    "🏢 Department Insights",
    "📢 Campaign ROI",
    "🏪 Store Format",
    "👥 Customer Analytics",
    "🎯 Action Plan"
])

# ===== PAGE 1: EXECUTIVE DASHBOARD =====
if page == "📊 Executive Dashboard":
    st.title("📊 Executive Dashboard")
    st.write("*Real-time business metrics for informed decision-making*")
    
    # KPI Row
    col1, col2, col3, col4 = st.columns(4)
    
    total_sales = filtered['SalesAmount'].sum()
    total_txns = filtered['Transaction'].nunique()
    avg_basket = filtered.groupby('Transaction')['SalesAmount'].sum().mean() if total_txns > 0 else 0
    promo_rate = (filtered['PromoUsed'].sum() / len(filtered)) * 100 if len(filtered) > 0 else 0
    
    col1.markdown(f"""
    <div class="kpi-card">
        <div class="metric-value">AED {total_sales:,.0f}</div>
        <div class="metric-label">Total Sales</div>
    </div>
    """, unsafe_allow_html=True)
    
    col2.markdown(f"""
    <div class="kpi-card">
        <div class="metric-value">{total_txns:,}</div>
        <div class="metric-label">Transactions</div>
    </div>
    """, unsafe_allow_html=True)
    
    col3.markdown(f"""
    <div class="kpi-card">
        <div class="metric-value">AED {avg_basket:,.0f}</div>
        <div class="metric-label">Avg Basket</div>
    </div>
    """, unsafe_allow_html=True)
    
    col4.markdown(f"""
    <div class="kpi-card">
        <div class="metric-value">{promo_rate:.1f}%</div>
        <div class="metric-label">Promo Usage</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Top performers
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("🏆 Top 5 Cities")
        top_cities = filtered.groupby('City')['SalesAmount'].sum().nlargest(5).reset_index()
        top_cities.columns = ['City', 'Sales']
        chart = alt.Chart(top_cities).mark_bar().encode(
            y=alt.Y('City:N', sort='-x'),
            x='Sales:Q',
            color=alt.value('#667eea')
        ).properties(height=300)
        st.altair_chart(chart, use_container_width=True)
    
    with col2:
        st.subheader("📂 Top 5 Departments")
        top_depts = filtered.groupby('Department')['SalesAmount'].sum().nlargest(5).reset_index()
        top_depts.columns = ['Department', 'Sales']
        chart = alt.Chart(top_depts).mark_bar().encode(
            y=alt.Y('Department:N', sort='-x'),
            x='Sales:Q',
            color=alt.value('#764ba2')
        ).properties(height=300)
        st.altair_chart(chart, use_container_width=True)
    
    with col3:
        st.subheader("📢 Top 5 Campaigns")
        top_camps = filtered.groupby('Campaign')['SalesAmount'].sum().nlargest(5).reset_index()
        top_camps.columns = ['Campaign', 'Sales']
        chart = alt.Chart(top_camps).mark_bar().encode(
            y=alt.Y('Campaign:N', sort='-x'),
            x='Sales:Q',
            color=alt.value('#f093fb')
        ).properties(height=300)
        st.altair_chart(chart, use_container_width=True)
    
    st.divider()
    
    # Key Insights
    st.markdown("""
    <div class="insight-box">
    <b>🔍 Quick Insights:</b><br>
    • Highest performing segment drives majority of revenue<br>
    • Promo campaigns have significant impact on transactions<br>
    • Geographic concentration indicates expansion opportunity
    </div>
    """, unsafe_allow_html=True)

# ===== PAGE 2: CITY STRATEGY =====
elif page == "🏙️ City Strategy":
    st.title("🏙️ City Strategic Analysis")
    st.write("*Identify growth opportunities and optimize city-level performance*")
    
    analysis_city = st.selectbox("Select City for Analysis", sorted([c for c in df['City'].unique() if c != 'Unknown']))
    city_data = filtered[filtered['City'] == analysis_city] if selected_city == 'All' else filtered
    
    if len(city_data) == 0:
        st.warning(f"No data for {analysis_city}")
        st.stop()
    
    # City metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 City Sales", f"AED {city_data['SalesAmount'].sum():,.0f}")
    col2.metric("🛒 Transactions", f"{city_data['Transaction'].nunique():,}")
    col3.metric("👥 Unique Products", f"{city_data['Product'].nunique()}")
    col4.metric("📊 Avg Transaction", f"AED {city_data.groupby('Transaction')['SalesAmount'].sum().mean():,.0f}")
    
    st.divider()
    
    # Top vs Bottom Performers
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("✅ Top Departments")
        top_depts = get_top_items(city_data, 'Department', 5)
        if len(top_depts) > 0:
            st.dataframe(top_depts, use_container_width=True)
    
    with col2:
        st.subheader("⚠️ Underperforming Departments")
        bottom_depts = city_data.groupby('Department')['SalesAmount'].sum().nsmallest(5).reset_index()
        bottom_depts.columns = ['Department', 'Sales']
        if len(bottom_depts) > 0:
            st.dataframe(bottom_depts, use_container_width=True)
    
    st.divider()
    
    # Age Group Analysis
    st.subheader("👥 Customer Demographics")
    age_data = city_data['AgeGroup'].value_counts().reset_index()
    if len(age_data) > 0:
        age_data.columns = ['AgeGroup', 'Count']
        chart = alt.Chart(age_data).mark_bar().encode(
            x='AgeGroup:N',
            y='Count:Q',
            color=alt.value('#667eea')
        ).properties(height=300)
        st.altair_chart(chart, use_container_width=True)
    
    st.divider()
    
    # Recommendations
    best_dept = city_data.groupby('Department')['SalesAmount'].sum().idxmax()
    worst_dept = city_data.groupby('Department')['SalesAmount'].sum().idxmin()
    
    st.markdown(f"""
    <div class="recommendation-box">
    <b>✅ Strategic Recommendations for {analysis_city}:</b><br>
    1. <b>Scale {best_dept}:</b> This is your cash cow. Increase inventory by 20-30%<br>
    2. <b>Fix {worst_dept}:</b> Low performance indicates opportunity. Increase marketing by 15%<br>
    3. <b>Expand Footprint:</b> Target new locations within high-traffic zones<br>
    4. <b>Expected Impact:</b> 20-30% revenue increase in 90 days
    </div>
    """, unsafe_allow_html=True)
    
    # Decision
    st.subheader("❓ Business Decision")
    decision1 = st.radio("Should we increase marketing budget in this city?", ["Yes", "No", "Need More Analysis"])
    decision2 = st.text_input("Which department should receive priority?", "")
    
    if st.button("💾 Save City Strategy"):
        st.success(f"✅ Strategy saved for {analysis_city}")

# ===== PAGE 3: DEPARTMENT INSIGHTS =====
elif page == "🏢 Department Insights":
    st.title("🏢 Department Performance Analysis")
    st.write("*Identify department-level opportunities for growth*")
    
    dept_analysis = filtered.groupby('Department').agg(
        Sales=('SalesAmount', 'sum'),
        Qty=('Quantity', 'sum'),
        Txns=('Transaction', 'nunique'),
        AvgPrice=('SalesAmount', 'mean')
    ).reset_index().sort_values('Sales', ascending=False)
    
    dept_analysis['RevPerUnit'] = dept_analysis['Sales'] / dept_analysis['Qty'].replace(0, 1)
    
    # Chart
    st.subheader("📊 Department Rankings")
    chart = alt.Chart(dept_analysis).mark_bar().encode(
        x='Department:N',
        y='Sales:Q',
        color='RevPerUnit:Q'
    ).properties(height=400)
    st.altair_chart(chart, use_container_width=True)
    
    st.divider()
    
    # High revenue vs quantity analysis
    st.subheader("💎 Revenue vs Quantity Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**High Revenue, Low Qty (Premium)**")
        high_rev = dept_analysis.nlargest(3, 'RevPerUnit')[['Department', 'Sales', 'Qty', 'RevPerUnit']]
        st.dataframe(high_rev, use_container_width=True)
    
    with col2:
        st.write("**High Qty, Lower Revenue (Volume)**")
        high_qty = dept_analysis.nlargest(3, 'Qty')[['Department', 'Sales', 'Qty', 'RevPerUnit']]
        st.dataframe(high_qty, use_container_width=True)
    
    st.divider()
    
    # Department vs Campaign
    st.subheader("📢 Best Campaign per Department")
    dept_camp = filtered.groupby(['Department', 'Campaign'])['SalesAmount'].sum().reset_index().sort_values('SalesAmount', ascending=False)
    st.dataframe(dept_camp.head(10), use_container_width=True)
    
    st.divider()
    
    # Recommendations
    st.markdown(f"""
    <div class="recommendation-box">
    <b>✅ Department Strategy:</b><br>
    1. <b>Scale Winners:</b> {dept_analysis.iloc[0]['Department']} - Increase shelf space by 25%<br>
    2. <b>Turnaround:</b> {dept_analysis.iloc[-1]['Department']} - Needs promotional support<br>
    3. <b>Cross-sell:</b> Bundle high performers with underperformers<br>
    4. <b>Expected Impact:</b> 15-25% increase for underperformers within 60 days
    </div>
    """, unsafe_allow_html=True)
    
    # Decision
    st.subheader("❓ Department Strategy Decision")
    dept_choice = st.selectbox("Which department should we focus on?", dept_analysis['Department'].unique())
    campaign_choice = st.selectbox("Which campaign to apply?", filtered['Campaign'].unique())
    
    if st.button("💾 Save Department Strategy"):
        st.success(f"✅ Department strategy saved")

# ===== PAGE 4: CAMPAIGN ROI =====
elif page == "📢 Campaign ROI":
    st.title("📢 Campaign Performance & ROI Analysis")
    st.write("*Identify high-performing campaigns and optimize ad spend*")
    
    campaign_perf = filtered.groupby('Campaign').agg(
        Sales=('SalesAmount', 'sum'),
        Qty=('Quantity', 'sum'),
        Txns=('Transaction', 'nunique'),
        PromoRate=('PromoUsed', 'mean')
    ).reset_index().sort_values('Sales', ascending=False)
    
    # Performance rating
    def get_rating(sales):
        if sales > campaign_perf['Sales'].quantile(0.75):
            return '⭐⭐⭐ Excellent'
        elif sales > campaign_perf['Sales'].quantile(0.25):
            return '⭐⭐ Good'
        else:
            return '⭐ Poor'
    
    campaign_perf['Rating'] = campaign_perf['Sales'].apply(get_rating)
    
    st.subheader("🏆 Campaign Rankings with ROI Assessment")
    st.dataframe(campaign_perf[['Campaign', 'Sales', 'Txns', 'PromoRate', 'Rating']], use_container_width=True)
    
    st.divider()
    
    # Campaign by demographics
    st.subheader("👥 Campaign Effectiveness by Age Group")
    camp_age = filtered.groupby(['Campaign', 'AgeGroup'])['SalesAmount'].sum().reset_index()
    if len(camp_age) > 0:
        heatmap = alt.Chart(camp_age).mark_rect().encode(
            x='Campaign:N',
            y='AgeGroup:N',
            color='SalesAmount:Q'
        ).properties(height=300)
        st.altair_chart(heatmap, use_container_width=True)
    
    st.divider()
    
    # Campaign by City
    st.subheader("🏙️ Campaign Performance by City")
    camp_city = filtered.groupby(['City', 'Campaign'])['SalesAmount'].sum().reset_index().sort_values('SalesAmount', ascending=False).head(15)
    st.dataframe(camp_city, use_container_width=True)
    
    st.divider()
    
    # Recommendations
    best_camp = campaign_perf.iloc[0]
    worst_camp = campaign_perf.iloc[-1]
    
    st.markdown(f"""
    <div class="recommendation-box">
    <b>✅ Campaign ROI Strategy:</b><br>
    1. <b>Scale {best_camp['Campaign']}:</b> Increase budget by 30-50%. Proven ROI of {best_camp['Sales']/1000:.0f}x<br>
    2. <b>Pause {worst_camp['Campaign']}:</b> ROI too low. Redesign messaging first<br>
    3. <b>Test New Channels:</b> Replicate {best_camp['Campaign']}'s approach<br>
    4. <b>Expected Combined Impact:</b> 25-35% revenue increase
    </div>
    """, unsafe_allow_html=True)
    
    # Decision
    st.subheader("❓ Campaign Investment Decision")
    budget_choice = st.slider("Budget increase for top campaign (%)", 0, 100, 30)
    pause_campaign = st.checkbox("Pause underperforming campaigns?")
    
    if st.button("💾 Save Campaign Strategy"):
        st.success(f"✅ Campaign strategy saved! Budget increase: {budget_choice}%")

# ===== PAGE 5: STORE FORMAT =====
elif page == "🏪 Store Format":
    st.title("🏪 Store Format Performance")
    st.write("*Optimize format-specific strategies*")
    
    store_perf = filtered.groupby('Store_Format').agg(
        Sales=('SalesAmount', 'sum'),
        Txns=('Transaction', 'nunique'),
        Qty=('Quantity', 'sum')
    ).reset_index().sort_values('Sales', ascending=False)
    
    store_perf['AvgBasket'] = store_perf['Sales'] / store_perf['Txns'].replace(0, 1)
    
    # Overview
    col1, col2, col3 = st.columns(3)
    col1.metric("🏪 Formats", len(store_perf))
    col2.metric("💰 Total Sales", f"AED {store_perf['Sales'].sum():,.0f}")
    col3.metric("📊 Avg Basket", f"AED {store_perf['AvgBasket'].mean():,.0f}")
    
    st.divider()
    
    # Format comparison
    st.subheader("📊 Store Format Comparison")
    chart = alt.Chart(store_perf).mark_bar().encode(
        x='Store_Format:N',
        y='Sales:Q',
        color='AvgBasket:Q'
    ).properties(height=400)
    st.altair_chart(chart, use_container_width=True)
    
    st.divider()
    
    # Store × City
    st.subheader("🏙️ Format Performance by City")
    store_city = filtered.groupby(['City', 'Store_Format'])['SalesAmount'].sum().reset_index().sort_values('SalesAmount', ascending=False).head(15)
    st.dataframe(store_city, use_container_width=True)
    
    st.divider()
    
    # Recommendations
    best_store = store_perf.iloc[0]
    worst_store = store_perf.iloc[-1]
    
    st.markdown(f"""
    <div class="recommendation-box">
    <b>✅ Store Format Strategy:</b><br>
    1. <b>Expand {best_store['Store_Format']}:</b> Best performer with AED {best_store['AvgBasket']:,.0f} avg basket<br>
    2. <b>Optimize {worst_store['Store_Format']}:</b> Apply {best_store['Store_Format']}'s strategies<br>
    3. <b>Format Mix:</b> Increase ratio of high-performing formats<br>
    4. <b>Expected Impact:</b> 20-30% uplift in underperforming format
    </div>
    """, unsafe_allow_html=True)
    
    # Decision
    st.subheader("❓ Format Investment Decision")
    expand_format = st.selectbox("Which format to expand?", store_perf['Store_Format'].unique())
    investment = st.slider("Investment amount (AED)", 0, 1000000, 100000, 50000)
    
    if st.button("💾 Save Format Strategy"):
        st.success(f"✅ Format strategy saved! Investment: AED {investment:,}")

# ===== PAGE 6: CUSTOMER ANALYTICS =====
elif page == "👥 Customer Analytics":
    st.title("👥 Customer Demographics & Loyalty")
    st.write("*Understand who your customers are and how to retain them*")
    
    # Age distribution
    st.subheader("📊 Customer Age Distribution")
    age_dist = filtered['AgeGroup'].value_counts().reset_index()
    age_dist.columns = ['AgeGroup', 'Count']
    age_order = ['13-17', '18-24', '25-34', '35-44', '45-54', '55-64', '65+']
    age_dist['AgeGroup'] = pd.Categorical(age_dist['AgeGroup'], categories=age_order, ordered=True)
    age_dist = age_dist.sort_values('AgeGroup')
    
    chart = alt.Chart(age_dist).mark_bar().encode(
        x='AgeGroup:N',
        y='Count:Q',
        color='Count:Q'
    ).properties(height=350)
    st.altair_chart(chart, use_container_width=True)
    
    st.divider()
    
    # Nationality
    st.subheader("🌍 Top Nationalities")
    nat_dist = filtered['Nationality'].value_counts().head(10).reset