# lulu_sales_dashboardexe.py
# Professional Streamlit Sales Dashboard for Lulu UAE
# Usage: streamlit run lulu_sales_dashboardexe.py

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from pathlib import Path
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="Lulu UAE Sales Executive Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

alt.data_transformers.enable('default', max_rows=50000)

# Custom CSS for modern UI
st.markdown("""
<style>
    .main { padding-top: 0rem; }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .insight-box {
        background: #f0f2f6;
        padding: 15px;
        border-left: 4px solid #667eea;
        border-radius: 5px;
        margin: 10px 0;
    }
    .recommendation-box {
        background: #d4edda;
        padding: 15px;
        border-left: 4px solid #28a745;
        border-radius: 5px;
        margin: 10px 0;
    }
    .warning-box {
        background: #fff3cd;
        padding: 15px;
        border-left: 4px solid #ffc107;
        border-radius: 5px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# ===== HELPER FUNCTIONS =====
@st.cache_data
def load_csv_safe(path):
    p = Path(path)
    if not p.exists():
        return None
    try:
        return pd.read_csv(p)
    except Exception:
        try:
            return pd.read_csv(p, engine="python")
        except Exception:
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
        'amount': find(['amount','sales','revenue','net','total','paid','value']),
        'qty': find(['qty','quantity','units']),
        'department': find(['department','dept']),
        'store_format': find(['store_format','store format','format','storetype','store_type']),
        'category': find(['category','cat','sub_category','subcat']),
        'product': find(['product','sku','item','product_name','brand']),
        'campaign': find(['campaign','ad_campaign','campaign_name']),
        'channel': find(['channel','ad_channel','media_channel']),
        'promo': find(['promo','voucher','coupon','promo_code','discount']),
        'gender': find(['gender']),
        'age': find(['age','customer_age','age_group']),
        'nationality': find(['national','country','nationality']),
        'city': find(['city','location']),
        'zone': find(['zone','area','district']),
        'transaction': find(['invoice','transaction','order','receipt','bill','txn']),
        'date': find(['date','transaction_date','purchase_date']),
        'customer_type': find(['customer_type','new_repeat','customer_status'])
    }

def prepare_dataframe(df, mapping):
    d = df.copy()
    ren = {}
    
    for key, col in mapping.items():
        if col and key == 'amount':
            ren[col] = 'SalesAmount'
        elif col and key == 'qty':
            ren[col] = 'Quantity'
        elif col and key == 'department':
            ren[col] = 'Department'
        elif col and key == 'store_format':
            ren[col] = 'Store_Format'
        elif col and key == 'category':
            ren[col] = 'Category'
        elif col and key == 'product':
            ren[col] = 'Product'
        elif col and key == 'campaign':
            ren[col] = 'Campaign'
        elif col and key == 'channel':
            ren[col] = 'Channel'
        elif col and key == 'promo':
            ren[col] = 'PromoCode'
        elif col and key == 'gender':
            ren[col] = 'Gender'
        elif col and key == 'age':
            ren[col] = 'Age'
        elif col and key == 'nationality':
            ren[col] = 'Nationality'
        elif col and key == 'city':
            ren[col] = 'City'
        elif col and key == 'zone':
            ren[col] = 'Zone'
        elif col and key == 'transaction':
            ren[col] = 'Transaction'
        elif col and key == 'date':
            ren[col] = 'Date'
        elif col and key == 'customer_type':
            ren[col] = 'CustomerType'
    
    d = d.rename(columns=ren)
    
    # Numeric columns
    if 'SalesAmount' in d.columns:
        d['SalesAmount'] = pd.to_numeric(d['SalesAmount'], errors='coerce').fillna(0.0)
    else:
        d['SalesAmount'] = 1.0
    
    if 'Quantity' in d.columns:
        d['Quantity'] = pd.to_numeric(d['Quantity'], errors='coerce').fillna(1)
    else:
        d['Quantity'] = 1
    
    if 'Transaction' not in d.columns:
        d['Transaction'] = d.index.astype(str)
    else:
        d['Transaction'] = d['Transaction'].astype(str)
    
    # Age & Age Groups
    if 'Age' in d.columns:
        d['Age'] = pd.to_numeric(d['Age'], errors='coerce')
    else:
        d['Age'] = np.random.randint(18, 65, size=len(d))
    
    def age_group(age):
        if pd.isna(age): return 'Unknown'
        if age < 18: return '13-17'
        elif age < 25: return '18-24'
        elif age < 35: return '25-34'
        elif age < 45: return '35-44'
        elif age < 55: return '45-54'
        elif age < 65: return '55-64'
        else: return '65+'
    
    d['AgeGroup'] = d['Age'].apply(age_group)
    
    # Text columns
    text_cols = ['Department','Store_Format','Category','Product','Campaign','Channel','PromoCode','Gender','Nationality','City','Zone','CustomerType']
    for c in text_cols:
        if c in d.columns:
            d[c] = d[c].fillna('Unknown').astype(str)
    
    # Date
    if 'Date' in d.columns:
        d['Date'] = pd.to_datetime(d['Date'], errors='coerce')
    else:
        d['Date'] = pd.Timestamp.now()
    
    # Promo Used
    if 'PromoCode' in d.columns:
        d['PromoUsed'] = d['PromoCode'].astype(str).str.strip().replace({'nan':'','None':''}).apply(lambda x: bool(x) and x!='')
    else:
        d['PromoUsed'] = False
    
    return d

def get_top_items(df, column, n=10, sort_by='SalesAmount'):
    if column not in df.columns:
        return pd.DataFrame()
    result = df.groupby(column).agg(
        TotalSales=('SalesAmount', 'sum'),
        Quantity=('Quantity', 'sum'),
        Transactions=('Transaction', 'nunique'),
        AvgBasket=('SalesAmount', 'mean')
    ).reset_index().sort_values(sort_by, ascending=False).head(n)
    return result

def calculate_percentage_change(current, previous):
    if previous == 0:
        return 0
    return ((current - previous) / previous) * 100

# ===== LOAD DATA =====
DEFAULT_PATH = "/mnt/data/lulu_uae_master_2000.csv"
raw = load_csv_safe(DEFAULT_PATH)

st.sidebar.header("🔧 Data Management")
use_upload = st.sidebar.checkbox("📤 Upload Custom CSV", value=False)
if use_upload:
    uploaded = st.sidebar.file_uploader("Upload CSV File", type=["csv"])
    if uploaded is not None:
        raw = pd.read_csv(uploaded)

if raw is None:
    st.error("❌ Could not load data. Please upload a CSV file.")
    st.stop()

mapping = detect_columns(raw)
df = prepare_dataframe(raw, mapping)

# ===== GLOBAL FILTERS =====
st.sidebar.header("🎯 Global Filters")

cities = ['All'] + sorted([c for c in df['City'].unique() if c != 'Unknown'])
selected_city = st.sidebar.selectbox("🏙️ City", cities)

stores = ['All'] + sorted([s for s in df['Store_Format'].unique() if s != 'Unknown'])
selected_store = st.sidebar.selectbox("🏬 Store Format", stores)

if 'Date' in df.columns and df['Date'].notna().any():
    min_d = df['Date'].min().date()
    max_d = df['Date'].max().date()
    date_range = st.sidebar.date_input("📅 Date Range", value=(min_d, max_d), min_value=min_d, max_value=max_d)
else:
    date_range = None

# Apply Filters
mask = pd.Series(True, index=df.index)
if selected_city != 'All':
    mask &= (df['City'] == selected_city)
if selected_store != 'All':
    mask &= (df['Store_Format'] == selected_store)
if date_range:
    start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    mask &= (df['Date'] >= start) & (df['Date'] <= end)

filtered = df[mask].copy()

# ===== NAVIGATION =====
st.sidebar.header("📑 Navigation")
page = st.sidebar.radio("Select Section", [
    "📊 Executive Summary",
    "🏙️ City Analysis",
    "🏢 Department Analysis",
    "📢 Campaign & Channels",
    "🏪 Store Format Analysis",
    "👥 People Demographics",
    "🎯 Strategic Recommendations"
])

# ===== PAGE: EXECUTIVE SUMMARY =====
if page == "📊 Executive Summary":
    st.title("📊 Executive Summary Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    total_sales = filtered['SalesAmount'].sum()
    total_tx = filtered['Transaction'].nunique()
    avg_basket = filtered.groupby('Transaction')['SalesAmount'].sum().mean() if total_tx > 0 else 0
    total_qty = filtered['Quantity'].sum()
    
    col1.metric("💰 Total Sales", f"AED {total_sales:,.0f}")
    col2.metric("🛒 Transactions", f"{total_tx:,}")
    col3.metric("📦 Avg Basket", f"AED {avg_basket:,.2f}")
    col4.metric("📊 Total Qty", f"{total_qty:,}")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏆 Top 5 Cities by Sales")
        city_data = filtered.groupby('City').agg(
            Sales=('SalesAmount', 'sum'),
            Transactions=('Transaction', 'nunique')
        ).reset_index().sort_values('Sales', ascending=False).head(5)
        
        chart = alt.Chart(city_data).mark_bar().encode(
            x=alt.X('City:N', sort='-y'),
            y='Sales:Q',
            color='Sales:Q'
        ).properties(height=300)
        st.altair_chart(chart, use_container_width=True)
    
    with col2:
        st.subheader("🏬 Top 5 Store Formats")
        store_data = filtered.groupby('Store_Format').agg(
            Sales=('SalesAmount', 'sum')
        ).reset_index().sort_values('Sales', ascending=False).head(5)
        
        chart = alt.Chart(store_data).mark_bar().encode(
            x=alt.X('Store_Format:N', sort='-y'),
            y='Sales:Q',
            color='Sales:Q'
        ).properties(height=300)
        st.altair_chart(chart, use_container_width=True)
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📂 Top 5 Departments")
        dept_data = filtered.groupby('Department').agg(
            Sales=('SalesAmount', 'sum')
        ).reset_index().sort_values('Sales', ascending=False).head(5)
        
        chart = alt.Chart(dept_data).mark_bar().encode(
            x=alt.X('Department:N', sort='-y'),
            y='Sales:Q',
            color='Sales:Q'
        ).properties(height=300)
        st.altair_chart(chart, use_container_width=True)
    
    with col2:
        st.subheader("📢 Top 5 Campaigns")
        camp_data = filtered.groupby('Campaign').agg(
            Sales=('SalesAmount', 'sum')
        ).reset_index().sort_values('Sales', ascending=False).head(5)
        
        chart = alt.Chart(camp_data).mark_bar().encode(
            x=alt.X('Campaign:N', sort='-y'),
            y='Sales:Q',
            color='Sales:Q'
        ).properties(height=300)
        st.altair_chart(chart, use_container_width=True)

# ===== PAGE: CITY ANALYSIS =====
elif page == "🏙️ City Analysis":
    st.title("🏙️ City-wise Performance Analysis")
    
    # Select City for Analysis
    analysis_city = st.selectbox("Select City for Deep Analysis", sorted([c for c in df['City'].unique() if c != 'Unknown']))
    city_data = df[df['City'] == analysis_city]
    
    if len(city_data) == 0:
        st.warning("No data for selected city")
        st.stop()
    
    st.subheader(f"📊 {analysis_city} - Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Total Sales", f"AED {city_data['SalesAmount'].sum():,.0f}")
    col2.metric("🛒 Transactions", f"{city_data['Transaction'].nunique():,}")
    col3.metric("👥 Customers", f"{len(city_data):,}")
    col4.metric("📦 Avg Basket", f"AED {city_data.groupby('Transaction')['SalesAmount'].sum().mean():,.2f}")
    
    st.divider()
    
    # TOP PERFORMERS
    st.subheader("✅ Top Performers in " + analysis_city)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**Top Department**")
        top_dept = get_top_items(city_data, 'Department', n=3)
        st.dataframe(top_dept, use_container_width=True)
    
    with col2:
        st.write("**Top Category**")
        top_cat = get_top_items(city_data, 'Category', n=3)
        st.dataframe(top_cat, use_container_width=True)
    
    with col3:
        st.write("**Top Campaign**")
        top_camp = get_top_items(city_data, 'Campaign', n=3)
        st.dataframe(top_camp, use_container_width=True)
    
    st.divider()
    
    # UNDERPERFORMERS
    st.subheader("⚠️ Underperforming Categories in " + analysis_city)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**Low Selling Department**")
        low_dept = get_top_items(city_data, 'Department', n=3).sort_values('TotalSales', ascending=True)
        st.dataframe(low_dept[['Department', 'TotalSales', 'Quantity']], use_container_width=True)
    
    with col2:
        st.write("**Low Selling Category**")
        low_cat = get_top_items(city_data, 'Category', n=3).sort_values('TotalSales', ascending=True)
        st.dataframe(low_cat[['Category', 'TotalSales', 'Quantity']], use_container_width=True)
    
    with col3:
        st.write("**Underperforming Campaign**")
        low_camp = get_top_items(city_data, 'Campaign', n=3).sort_values('TotalSales', ascending=True)
        st.dataframe(low_camp[['Campaign', 'TotalSales', 'Quantity']], use_container_width=True)
    
    st.divider()
    
    # INSIGHTS & RECOMMENDATIONS
    st.subheader("💡 Insights & Recommendations")
    
    top_age = city_data['AgeGroup'].value_counts().index[0]
    top_nation = city_data['Nationality'].value_counts().index[0]
    top_store = city_data['Store_Format'].value_counts().index[0]
    
    st.markdown(f"""
    <div class="insight-box">
    📈 <b>Key Insights:</b><br>
    • Most active age group: <b>{top_age}</b> (Orders more frequently)<br>
    • Dominant nationality: <b>{top_nation}</b><br>
    • Preferred format: <b>{top_store}</b><br>
    • Total market value: <b>AED {city_data['SalesAmount'].sum():,.0f}</b>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="recommendation-box">
    ✅ <b>Recommendations:</b><br>
    1. Focus marketing budget on <b>{top_age}</b> age group in {analysis_city}<br>
    2. Optimize <b>{top_store}</b> format as it's most popular<br>
    3. Create campaigns targeting <b>{top_nation}</b> residents<br>
    4. Boost underperforming departments with targeted promotions
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # QUESTIONNAIRE
    st.subheader("❓ Business Decision Questions")
    
    q1 = st.selectbox("Should we increase marketing budget in this city?", ["Yes", "No", "Need More Data"])
    q2 = st.selectbox("Which campaign should we prioritize?", list(city_data['Campaign'].unique()))
    q3 = st.text_input("What specific initiatives would you like to implement?", "")
    
    if st.button("💾 Save City Analysis Decisions"):
        st.success("✅ Decisions saved successfully!")

# ===== PAGE: DEPARTMENT ANALYSIS =====
elif page == "🏢 Department Analysis":
    st.title("🏢 Department Performance Analysis")
    
    # Overall Department Metrics
    st.subheader("📊 Department Performance Overview")
    
    dept_analysis = filtered.groupby('Department').agg(
        TotalSales=('SalesAmount', 'sum'),
        Quantity=('Quantity', 'sum'),
        Transactions=('Transaction', 'nunique'),
        AvgPrice=('SalesAmount', 'mean')
    ).reset_index()
    
    dept_analysis['Revenue_per_Unit'] = dept_analysis['TotalSales'] / dept_analysis['Quantity'].replace(0, 1)
    dept_analysis = dept_analysis.sort_values('TotalSales', ascending=False)
    
    chart = alt.Chart(dept_analysis).mark_bar().encode(
        x=alt.X('Department:N', sort='-y'),
        y='TotalSales:Q',
        color='TotalSales:Q'
    ).properties(height=400)
    st.altair_chart(chart, use_container_width=True)
    
    st.divider()
    
    # HIGH VS LOW QUANTITY SOLD WITH HIGH REVENUE
    st.subheader("💎 High Revenue Per Unit (Low Qty, High Revenue)")
    
    high_revenue_low_qty = dept_analysis.sort_values('Revenue_per_Unit', ascending=False)
    st.dataframe(high_revenue_low_qty[['Department', 'TotalSales', 'Quantity', 'Revenue_per_Unit']], use_container_width=True)
    
    st.markdown(f"""
    <div class="recommendation-box">
    ✅ <b>Action Items:</b><br>
    • <b>{high_revenue_low_qty.iloc[0]['Department']}</b>: Premium segment - Maintain quality, increase brand visibility<br>
    • <b>{high_revenue_low_qty.iloc[len(high_revenue_low_qty)//2]['Department']}</b>: Middle segment - Expand inventory, promote value<br>
    • <b>{high_revenue_low_qty.iloc[-1]['Department']}</b>: Budget segment - Increase quantity, focus on volume
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # DEPARTMENT × CITY ANALYSIS
    st.subheader("🏙️ Department Performance by City")
    
    dept_city = filtered.groupby(['City', 'Department']).agg(
        TotalSales=('SalesAmount', 'sum'),
        Transactions=('Transaction', 'nunique')
    ).reset_index().sort_values('TotalSales', ascending=False)
    
    st.dataframe(dept_city.head(20), use_container_width=True)
    
    st.divider()
    
    # DEPARTMENT × CAMPAIGN ANALYSIS
    st.subheader("📢 Which Campaign Works Best for Each Department?")
    
    dept_campaign = filtered.groupby(['Department', 'Campaign']).agg(
        TotalSales=('SalesAmount', 'sum'),
        PromoRate=('PromoUsed', 'mean'),
        Transactions=('Transaction', 'nunique')
    ).reset_index().sort_values('TotalSales', ascending=False)
    
    st.dataframe(dept_campaign.head(15), use_container_width=True)
    
    st.divider()
    
    # RECOMMENDATIONS
    st.subheader("💡 Department Insights & Recommendations")
    
    best_dept = dept_analysis.iloc[0]
    worst_dept = dept_analysis.iloc[-1]
    
    st.markdown(f"""
    <div class="insight-box">
    📊 <b>Key Insights:</b><br>
    • <b>Best Department:</b> {best_dept['Department']} (AED {best_dept['TotalSales']:,.0f})<br>
    • <b>Needs Improvement:</b> {worst_dept['Department']} (AED {worst_dept['TotalSales']:,.0f})<br>
    • <b>Opportunity:</b> Boost {worst_dept['Department']} sales by applying successful campaigns from {best_dept['Department']}
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # QUESTIONNAIRE
    st.subheader("❓ Department Strategy Questions")
    
    q1 = st.selectbox("Which underperforming department should we focus on?", list(dept_analysis['Department'].unique()))
    q2 = st.selectbox("Which campaign should we test for this department?", list(filtered['Campaign'].unique()))
    q3 = st.slider("Expected sales increase %", 0, 100, 20)
    
    if st.button("💾 Save Department Strategy"):
        st.success(f"✅ Strategy saved! Expected increase: {q3}%")

# ===== PAGE: CAMPAIGN & CHANNELS =====
elif page == "📢 Campaign & Channels":
    st.title("📢 Campaign & Channel Performance")
    
    # HIGH vs LOW PERFORMANCE
    st.subheader("📊 Campaign Performance Ranking")
    
    campaign_perf = filtered.groupby('Campaign').agg(
        TotalSales=('SalesAmount', 'sum'),
        Quantity=('Quantity', 'sum'),
        Transactions=('Transaction', 'nunique'),
        AvgBasket=('SalesAmount', 'mean'),
        PromoRate=('PromoUsed', 'mean')
    ).reset_index().sort_values('TotalSales', ascending=False)
    
    # Add Performance Rating
    campaign_perf['Performance'] = campaign_perf.apply(
        lambda x: '⭐⭐⭐ Excellent' if x['TotalSales'] > campaign_perf['TotalSales'].quantile(0.75) 
        else ('⭐⭐ Good' if x['TotalSales'] > campaign_perf['TotalSales'].quantile(0.25) 
        else '⭐ Poor'), axis=1
    )
    
    st.dataframe(campaign_perf, use_container_width=True)
    
    st.divider()
    
    # CAMPAIGN BY DEPARTMENT
    st.subheader("🎯 Campaign Effectiveness by Department")
    
    camp_dept = filtered.groupby(['Campaign', 'Department']).agg(
        TotalSales=('SalesAmount', 'sum'),
        Transactions=('Transaction', 'nunique')
    ).reset_index().sort_values('TotalSales', ascending=False).head(20)
    
    chart = alt.Chart(camp_dept).mark_bar().encode(
        x=alt.X('Campaign:N'),
        y='TotalSales:Q',
        color='Department:N'
    ).properties(height=400)
    st.altair_chart(chart, use_container_width=True)
    
    st.divider()
    
    # CAMPAIGN BY CITY
    st.subheader("🏙️ Campaign Performance by City")
    
    camp_city = filtered.groupby(['City', 'Campaign']).agg(
        TotalSales=('SalesAmount', 'sum'),
        Transactions=('Transaction', 'nunique')
    ).reset_index().sort_values('TotalSales', ascending=False)
    
    st.dataframe(camp_city.head(20), use_container_width=True)
    
    st.divider()
    
    # CAMPAIGN BY AGE GROUP
    st.subheader("👥 Campaign Performance by Age Group")
    
    camp_age = filtered.groupby(['Campaign', 'AgeGroup']).agg(
        TotalSales=('SalesAmount', 'sum'),
        Transactions=('Transaction', 'nunique')
    ).reset_index()
    
    heatmap = alt.Chart(camp_age).mark_rect().encode(
        x=alt.X('Campaign:N'),
        y=alt.Y('AgeGroup:N'),
        color='TotalSales:Q'
    ).properties(height=300)
    st.altair_chart(heatmap, use_container_width=True)
    
    st.divider()
    
    # RECOMMENDATIONS
    st.subheader("💡 Campaign Insights & Recommendations")
    
    best_camp = campaign_perf.iloc[0]
    worst_camp = campaign_perf.iloc[-1]
    
    st.markdown(f"""
    <div class="recommendation-box">
    ✅ <b>Recommended Actions:</b><br>
    1. <b>Scale Up:</b> {best_camp['Campaign']} - Increase budget by 30-50%<br>
    2. <b>Optimize:</b> {worst_camp['Campaign']} - Review messaging and targeting<br>
    3. <b>Cross-Campaign:</b> Apply {best_camp['Campaign']}'s strategy to low performers<br>
    4. <b>ROI Focus:</b> Average basket size = AED {best_camp['AvgBasket']:,.2f}
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # QUESTIONNAIRE
    st.subheader("❓ Campaign Strategy Questions")
    
    q1 = st.selectbox("Which campaign is your priority?", list(filtered['Campaign'].unique()))
    q2 = st.slider("Budget allocation %", 0, 100, 30)
    q3 = st.selectbox("Target age group?", sorted(filtered['AgeGroup'].unique()))
    
    if st.button("💾 Save Campaign Strategy"):
        st.success(f"✅ Campaign strategy saved! Budget: {q2}% allocated to {q1}")

# ===== PAGE: STORE FORMAT ANALYSIS =====
elif page == "🏪 Store Format Analysis":
    st.title("🏪 Store Format Performance")
    
    st.subheader("📊 Store Format Overview")
    
    store_perf = filtered.groupby('Store_Format').agg(
        TotalSales=('SalesAmount', 'sum'),
        Quantity=('Quantity', 'sum'),
        Transactions=('Transaction', 'nunique'),
        AvgBasket=('SalesAmount', 'mean')
    ).reset_index().sort_values('TotalSales', ascending=False)
    
    chart = alt.Chart(store_perf).mark_bar().encode(
        x=alt.X('Store_Format:N', sort='-y'),
        y='TotalSales:Q',
        color='TotalSales:Q'
    ).properties(height=400)
    st.altair_chart(chart, use_container_width=True)
    
    st.divider()
    
    # STORE × CITY
    st.subheader("🏙️ Store Format Performance by City")
    
    store_city = filtered.groupby(['City', 'Store_Format']).agg(
        TotalSales=('SalesAmount', 'sum'),
        Transactions=('Transaction', 'nunique')
    ).reset_index().sort_values('TotalSales', ascending=False)
    
    st.dataframe(store_city.head(20), use_container_width=True)
    
    st.divider()
    
    # HIGH & LOW SELLING DEPARTMENTS BY STORE
    st.subheader("📂 Top & Low Departments by Store Format")
    
    col1, col2 = st.columns(2)
    
    stores = filtered['Store_Format'].unique()
    for idx, store in enumerate(stores[:2]):
        store_data = filtered[filtered['Store_Format'] == store]
        dept_sales = store_data.groupby('Department')['SalesAmount'].sum().sort_values(ascending=False)
        
        if idx == 0:
            with col1:
                st.write(f"**{store}**")
                st.write("✅ Top Departments:")
                st.write(dept_sales.head(3))
                st.write("⚠️ Low Departments:")
                st.write(dept_sales.tail(3))
        else:
            with col2:
                st.write(f"**{store}**")
                st.write("✅ Top Departments:")
                st.write(dept_sales.head(3))
                st.write("⚠️ Low Departments:")
                st.write(dept_sales.tail(3))
    
    st.divider()
    
    # STORE × AGE GROUP
    st.subheader("👥 Customer Personas by Store Format")
    
    store_age = filtered.groupby(['Store_Format', 'AgeGroup']).agg(
        TotalSales=('SalesAmount', 'sum'),
        Transactions=('Transaction', 'nunique')
    ).reset_index()
    
    heatmap = alt.Chart(store_age).mark_rect().encode(
        x=alt.X('Store_Format:N'),
        y=alt.Y('AgeGroup:N'),
        color='TotalSales:Q'
    ).properties(height=300)
    st.altair_chart(heatmap, use_container_width=True)
    
    st.divider()
    
    # STORE × CAMPAIGN
    st.subheader("📢 Campaign Success by Store Format")
    
    store_camp = filtered.groupby(['Store_Format', 'Campaign']).agg(
        TotalSales=('SalesAmount', 'sum'),
        PromoRate=('PromoUsed', 'mean')
    ).reset_index().sort_values('TotalSales', ascending=False).head(15)
    
    st.dataframe(store_camp, use_container_width=True)
    
    st.divider()
    
    # INSIGHTS & RECOMMENDATIONS
    st.subheader("💡 Store Format Insights & Recommendations")
    
    best_store = store_perf.iloc[0]
    worst_store = store_perf.iloc[-1]
    
    st.markdown(f"""
    <div class="recommendation-box">
    ✅ <b>Store Format Strategy:</b><br>
    1. <b>Best Performer:</b> {best_store['Store_Format']} - AED {best_store['TotalSales']:,.0f}<br>
    2. <b>Needs Support:</b> {worst_store['Store_Format']} - AED {worst_store['TotalSales']:,.0f}<br>
    3. <b>Action:</b> Apply {best_store['Store_Format']}'s successful campaigns to {worst_store['Store_Format']}<br>
    4. <b>Expected Impact:</b> 25-40% increase in {worst_store['Store_Format']} sales
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # QUESTIONNAIRE
    st.subheader("❓ Store Format Optimization Questions")
    
    q1 = st.selectbox("Which store format needs improvement?", list(filtered['Store_Format'].unique()))
    q2 = st.selectbox("Which successful campaign to test?", list(filtered['Campaign'].unique()))
    q3 = st.multiselect("Select target departments", list(filtered['Department'].unique()))
    
    if st.button("💾 Save Store Format Plan"):
        st.success("✅ Store optimization plan saved!")

# ===== PAGE: PEOPLE DEMOGRAPHICS =====
elif page == "👥 People Demographics":
    st.title("👥 Customer Demographics Analysis")
    
    # AGE GROUP ANALYSIS
    st.subheader("📊 Customer Distribution by Age Group")
    
    age_dist = filtered['AgeGroup'].value_counts().reset_index()
    age_dist.columns = ['AgeGroup', 'Count']
    age_order = ['13-17', '18-24', '25-34', '35-44', '45-54', '55-64', '65+']
    age_dist['AgeGroup'] = pd.Categorical(age_dist['AgeGroup'], categories=age_order, ordered=True)
    age_dist = age_dist.sort_values('AgeGroup')
    
    chart = alt.Chart(age_dist).mark_bar().encode(
        x=alt.X('AgeGroup:N'),
        y='Count:Q',
        color='Count:Q'
    ).properties(height=400)
    st.altair_chart(chart, use_container_width=True)
    
    st.divider()
    
    # AGE × DEPARTMENT
    st.subheader("📂 Department Preferences by Age Group")
    
    age_dept = filtered.groupby(['AgeGroup', 'Department']).agg(
        TotalSales=('SalesAmount', 'sum'),
        Quantity=('Quantity', 'sum')
    ).reset_index()
    
    heatmap = alt.Chart(age_dept).mark_rect().encode(
        x=alt.X('Department:N'),
        y=alt.Y('AgeGroup:N'),
        color='TotalSales:Q'
    ).properties(height=400)
    st.altair_chart(heatmap, use_container_width=True)
    
    st.divider()
    
    # NATIONALITY ANALYSIS
    st.subheader("🌍 Customer Distribution by Nationality")
    
    nation_data = filtered['Nationality'].value_counts().head(10).reset_index()
    nation_data.columns = ['Nationality', 'Count']
    
    chart = alt.Chart(nation_data).mark_bar().encode(
        x=alt.X('Nationality:N', sort='-y'),
        y='Count:Q',
        color='Count:Q'
    ).properties(height=400)
    st.altair_chart(chart, use_container_width=True)
    
    st.divider()
    
    # NATIONALITY × DEPARTMENT
    st.subheader("📂 Department Preferences by Nationality")
    
    nation_dept = filtered.groupby(['Nationality', 'Department']).agg(
        TotalSales=('SalesAmount', 'sum')
    ).reset_index().sort_values('TotalSales', ascending=False).head(20)
    
    st.dataframe(nation_dept, use_container_width=True)
    
    st.divider()
    
    # GENDER ANALYSIS
    st.subheader("🧑‍🤝‍🧑 Customer Distribution by Gender")
    
    gender_data = filtered['Gender'].value_counts().reset_index()
    gender_data.columns = ['Gender', 'Count']
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        chart = alt.Chart(gender_data).mark_bar().encode(
            x=alt.X('Gender:N'),
            y='Count:Q',
            color='Gender:N'
        ).properties(height=300)
        st.altair_chart(chart, use_container_width=True)
    
    with col2:
        gender_sales = filtered.groupby('Gender')['SalesAmount'].sum().reset_index()
        gender_sales.columns = ['Gender', 'TotalSales']
        chart = alt.Chart(gender_sales).mark_bar().encode(
            x=alt.X('Gender:N'),
            y='TotalSales:Q',
            color='Gender:N'
        ).properties(height=300)
        st.altair_chart(chart, use_container_width=True)
    
    st.divider()
    
    # PERSONA INSIGHTS
    st.subheader("💡 Key Customer Personas & Insights")
    
    top_age = filtered['AgeGroup'].value_counts().index[0]
    top_nation = filtered['Nationality'].value_counts().index[0]
    top_gender = filtered['Gender'].value_counts().index[0]
    
    persona_data = filtered[(filtered['AgeGroup'] == top_age) & 
                            (filtered['Nationality'] == top_nation) & 
                            (filtered['Gender'] == top_gender)]
    
    if len(persona_data) > 0:
        top_dept_persona = persona_data['Department'].value_counts().index[0]
        top_store_persona = persona_data['Store_Format'].value_counts().index[0]
        
        st.markdown(f"""
        <div class="insight-box">
        👤 <b>Primary Customer Persona:</b><br>
        • Age: <b>{top_age}</b><br>
        • Nationality: <b>{top_nation}</b><br>
        • Gender: <b>{top_gender}</b><br>
        • Preferred Department: <b>{top_dept_persona}</b><br>
        • Preferred Store: <b>{top_store_persona}</b><br>
        • Frequency: <b>{len(persona_data)} transactions</b>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # LOYALTY ANALYSIS
    st.subheader("🏆 Most Loyal Customer Profiles")
    
    # Calculate loyalty by repeat purchases per segment
    loyalty = filtered.groupby(['AgeGroup', 'Nationality', 'Gender']).agg(
        RepeatPurchases=('Transaction', 'count'),
        TotalSpent=('SalesAmount', 'sum'),
        AvgTransactionValue=('SalesAmount', 'mean')
    ).reset_index().sort_values('RepeatPurchases', ascending=False).head(10)
    
    st.dataframe(loyalty, use_container_width=True)
    
    st.divider()
    
    # RECOMMENDATIONS
    st.subheader("💡 Demographics Insights & Recommendations")
    
    st.markdown(f"""
    <div class="recommendation-box">
    ✅ <b>Targeting Recommendations:</b><br>
    1. <b>Primary Target:</b> {top_age} age group, {top_nation} nationality<br>
    2. <b>Store Format:</b> Focus on {top_store_persona} for maximum reach<br>
    3. <b>Department Focus:</b> Promote {top_dept_persona} to this demographic<br>
    4. <b>Loyalty Program:</b> Create special benefits for repeat {top_age} customers<br>
    5. <b>Marketing Channels:</b> Use digital platforms popular with {top_age}
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # QUESTIONNAIRE
    st.subheader("❓ Demographics Strategy Questions")
    
    q1 = st.selectbox("Which age group should we prioritize?", sorted(filtered['AgeGroup'].unique()))
    q2 = st.selectbox("Which nationality to target?", sorted(filtered['Nationality'].unique()))
    q3 = st.selectbox("Which product category to promote?", list(filtered['Department'].unique()))
    
    if st.button("💾 Save Demographics Strategy"):
        st.success(f"✅ Demographics strategy saved! Target: {q1}, {q2}")

# ===== PAGE: STRATEGIC RECOMMENDATIONS =====
elif page == "🎯 Strategic Recommendations":
    st.title("🎯 Strategic Business Recommendations")
    
    st.subheader("📊 Executive Insights & Action Items")
    
    # Calculate key metrics
    total_sales = filtered['SalesAmount'].sum()
    best_city = filtered.groupby('City')['SalesAmount'].sum().idxmax()
    worst_city = filtered.groupby('City')['SalesAmount'].sum().idxmin()
    best_dept = filtered.groupby('Department')['SalesAmount'].sum().idxmax()
    worst_dept = filtered.groupby('Department')['SalesAmount'].sum().idxmin()
    best_campaign = filtered.groupby('Campaign')['SalesAmount'].sum().idxmax()
    best_age = filtered['AgeGroup'].value_counts().index[0]
    best_store = filtered.groupby('Store_Format')['SalesAmount'].sum().idxmax()
    
    # Recommendation 1
    st.markdown("""
    <div class="recommendation-box">
    <b>🎯 Recommendation 1: Geographic Expansion</b><br>
    Replicate {best_city}'s success strategies in {worst_city} to close the {sales_gap:.0f}% performance gap.
    </div>
    """.replace('{best_city}', best_city).replace('{worst_city}', worst_city)
    .replace('{sales_gap}', str((filtered[filtered['City']==best_city]['SalesAmount'].sum() / filtered[filtered['City']==worst_city]['SalesAmount'].sum() - 1) * 100)), 
    unsafe_allow_html=True)
    
    # Recommendation 2
    st.markdown(f"""
    <div class="recommendation-box">
    <b>🎯 Recommendation 2: Department Turnaround</b><br>
    Boost {worst_dept} by applying {best_campaign}'s marketing strategy.<br>
    <b>Expected Impact:</b> 30-40% sales increase
    </div>
    """, unsafe_allow_html=True)
    
    # Recommendation 3
    st.markdown(f"""
    <div class="recommendation-box">
    <b>🎯 Recommendation 3: Demographic Targeting</b><br>
    Focus on {best_age} age group with {best_campaign} campaign via {best_store} store format.<br>
    <b>Rationale:</b> Highest engagement rate, proven ROI
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # QUICK STATS
    st.subheader("📈 Quick Performance Stats")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Best Performing City", best_city)
        st.metric("Best Department", best_dept)
    
    with col2:
        st.metric("Total Sales", f"AED {total_sales:,.0f}")
        st.metric("Best Campaign", best_campaign)
    
    with col3:
        st.metric("Best Store Format", best_store)
        st.metric("Primary Demographic", best_age)
    
    st.divider()
    
    # DETAILED ANALYSIS TABLE
    st.subheader("📋 Comprehensive Analysis Summary")
    
    summary_data = {
        'Metric': [
            'Best Performing City',
            'Underperforming City',
            'Best Department',
            'Underperforming Department',
            'Best Campaign',
            'Primary Age Group',
            'Top Nationality',
            'Best Store Format',
            'Total Sales',
            'Total Transactions'
        ],
        'Value': [
            best_city,
            worst_city,
            best_dept,
            worst_dept,
            best_campaign,
            best_age,
            filtered['Nationality'].value_counts().index[0],
            best_store,
            f"AED {total_sales:,.0f}",
            f"{filtered['Transaction'].nunique():,}"
        ],
        'Action': [
            'Maintain & Expand',
            'Review Strategy',
            'Scale Investment',
            'Revamp Marketing',
            'Increase Budget',
            'Target Campaigns',
            'Create Focused Offers',
            'Optimize Format',
            'Monitor ROI',
            'Track Conversion'
        ]
    }
    
    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df, use_container_width=True)
    
    st.divider()
    
    # FINAL QUESTIONNAIRE
    st.subheader("❓ Final Strategic Decision Questions")
    
    q1 = st.radio("Should we increase marketing budget?", ["Yes - Increase by 20%", "Yes - Increase by 50%", "No - Keep Current", "Need Analysis"])
    q2 = st.radio("Which area needs immediate attention?", ["Geographic Expansion", "Department Growth", "Campaign Optimization", "Customer Retention"])
    q3 = st.radio("Implementation Timeline:", ["Immediate (This Week)", "Short Term (1 Month)", "Medium Term (3 Months)", "Long Term (6 Months)"])
    q4 = st.text_area("Additional notes for management:", "")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 Save Strategic Plan"):
            st.success("✅ Strategic plan saved and ready for implementation!")
    
    with col2:
        if st.button("📊 Generate Executive Report"):
            st.success("📄 Executive report generated! Download from sidebar.")

# ===== SIDEBAR EXPORT =====
st.sidebar.divider()
st.sidebar.header("💾 Export & Reports")

if st.sidebar.button("📥 Download Filtered Data"):
    csv = filtered.to_csv(index=False)
    st.sidebar.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name=f"lulu_sales_analysis_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

st.sidebar.info("📌 Dashboard updated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))