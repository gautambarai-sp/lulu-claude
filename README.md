# 🏪 Lulu UAE Sales Dashboard Executive

**Professional-grade Business Intelligence Dashboard for Data-Driven Decision Making**

A comprehensive Streamlit-based analytics platform designed for retail executives, store managers, and marketing teams to analyze sales performance, customer behavior, and campaign effectiveness across multiple dimensions.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Installation](#installation)
4. [CSV Format Requirements](#csv-format-requirements)
5. [How to Use](#how-to-use)
6. [Page Descriptions](#page-descriptions)
7. [Deployment](#deployment)
8. [Troubleshooting](#troubleshooting)
9. [FAQ](#faq)

---

## 🎯 Overview

This dashboard provides 360-degree insights into:

- **Geographic Performance**: City-wise sales, campaigns, and demographics
- **Department Analytics**: Revenue, quantity, and ROI analysis
- **Campaign ROI**: Multi-channel performance tracking
- **Store Format Optimization**: Format-specific performance metrics
- **Customer Demographics**: Age, nationality, gender purchasing patterns
- **Strategic Insights**: AI-powered recommendations with actionable items

**Perfect for:**
- Retail Executives making strategic decisions
- Store Managers optimizing local performance
- Marketing Teams planning campaigns
- Finance Teams tracking ROI
- Business Analysts identifying opportunities

---

## ✨ Key Features

### 📊 **Executive Summary**
- Real-time KPI dashboard (Total Sales, Transactions, Avg Basket, Qty)
- Top 5 performers: Cities, Store Formats, Departments, Campaigns
- Quick performance overview for daily monitoring

### 🏙️ **City Analysis**
**Top Performers:**
- Top departments, categories, campaigns, store formats
- Successful campaigns and age group analysis
- Nationality and store format preferences

**Underperformers:**
- Minimum sales departments and categories
- Underperforming campaigns and zones

**Insights & Recommendations:**
- Age group ordering patterns
- Least popular departments and zones
- Cross-city comparative analysis
- Business decision recommendations

**Decision Questionnaire:**
- Marketing budget allocation
- Campaign prioritization
- Implementation strategy

### 🏢 **Department Analysis**
**Performance Overview:**
- Sales ranking across all departments
- Quantity sold vs. revenue correlation

**High Revenue Per Unit:**
- Departments with low quantity but high revenue
- Departments with high quantity but low revenue
- Highlighted middle performers for optimization

**Comparative Analysis:**
- Department performance by city
- Department performance by campaign
- Which campaigns work best for each department

**Recommendations:**
- Expected ROI from applying successful campaigns
- Department-specific growth strategies
- Cross-department learning opportunities

### 📢 **Campaign & Channels**
**Performance Ranking:**
- Campaign success ratings (⭐⭐⭐ Excellent, ⭐⭐ Good, ⭐ Poor)
- High vs. low performance comparison
- Channel effectiveness analysis

**Multi-Dimensional Analysis:**
- Campaign effectiveness by department
- Campaign performance by city
- Campaign success across age groups
- Heatmap visualization of campaign-demographic match

**Strategic Insights:**
- Which campaigns acquire new users
- Which campaigns maintain loyal customers
- Campaign-specific ROI metrics
- Recommendation for budget allocation

### 🏪 **Store Format Analysis**
**Performance Metrics:**
- Sales, quantity, transactions by format
- Average basket size by format

**Geographic Spread:**
- Store format performance by city
- Format-specific city rankings

**Department Distribution:**
- High and low selling departments by format
- Format-specific inventory recommendations

**Customer Persona Match:**
- Age group preferences by format
- Nationality preferences by format
- Campaign success by format

**Optimization Recommendations:**
- Format-specific promotional strategies
- Cross-format learning opportunities
- Expected sales uplift from optimizations

### 👥 **People Demographics**
**Age Group Analysis:**
- Customer distribution by age group
- Department preferences by age
- Heatmap of age × department relationships

**Nationality Analysis:**
- Top 10 nationalities by volume
- Department preferences by nationality
- Top spending nationalities

**Gender Analysis:**
- Gender distribution
- Gender-based purchasing patterns
- Sales breakdown by gender

**Loyalty Profiles:**
- Most loyal customer segments
- High-value customer personas
- Repeat purchase patterns

**Demographic Targeting:**
- Primary customer persona identification
- Secondary persona insights
- Loyalty program recommendations

### 🎯 **Strategic Recommendations**
**Executive Summary:**
- All-in-one strategic overview
- Top 3 major recommendations
- Expected impact percentages

**Comprehensive Analysis:**
- Best vs. worst performer gaps
- Geographic expansion opportunities
- Department turnaround strategies
- Demographic targeting focus

**Action Items:**
- Quick decision questions
- Implementation timeline options
- Budget allocation recommendations

---

## 🚀 Installation

### Prerequisites
- Python 3.7+
- pip package manager
- 100MB free disk space

### Step 1: Clone or Download
```bash
git clone <repository-url>
cd lulu-sales-dashboard
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

Or manually:
```bash
pip install streamlit pandas numpy altair
```

### Step 3: Run Dashboard
```bash
streamlit run lulu_sales_dashboardexe.py
```

Dashboard opens at: `http://localhost:8501`

---

## 📁 CSV Format Requirements

### Required Columns

Your CSV must include these columns (auto-detected):

| Column | Alternatives | Type | Example |
|--------|---|------|---|
| Amount | sales, revenue, total, paid, value | Numeric | 1250.50 |
| Quantity | qty, units | Numeric | 3 |
| Department | dept | Text | Groceries |
| Store Format | store_type, format | Text | Hypermarket |
| Category | cat, sub_category | Text | Dairy |
| Product | sku, item, product_name, brand | Text | Milk-1L |
| Campaign | ad_campaign, campaign_name | Text | Summer Sale |
| Channel | ad_channel, media_channel | Text | Facebook |
| Promo Code | voucher, coupon, promo_code, discount | Text | PROMO20 |
| Gender | gender | Text | M or F |
| Age | customer_age, age_group | Numeric | 35 |
| Nationality | country, nationality | Text | Indian |
| City | location | Text | Dubai |
| Zone | area, district | Text | Marina |
| Transaction | invoice, order, receipt, bill, txn | Text | TXN001 |
| Date | transaction_date, purchase_date | Date | 2024-01-15 |
| Customer Type | new_repeat, customer_status | Text | New/Repeat |

### Sample CSV Structure
```csv
Amount,Quantity,Department,Store_Format,Category,Product,Campaign,Channel,Promo_Code,Gender,Age,Nationality,City,Zone,Transaction,Date,Customer_Type
1250.50,3,Groceries,Hypermarket,Dairy,Milk-1L,Summer Sale,Facebook,PROMO20,M,35,UAE,Dubai,Marina,TXN001,2024-01-15,Repeat
850.00,2,Electronics,Express,Mobile,Phone X,Tech Week,Instagram,DISC10,F,28,Indian,Abu Dhabi,Downtown,TXN002,2024-01-16,New
650.75,1,Fashion,Web,Apparel,Shirt-XL,New Year,Email,,M,42,Filipino,Sharjah,Central,TXN003,2024-01-17,Repeat
```

### Data Quality Guidelines
- ✅ No special characters in text fields
- ✅ Consistent date format (YYYY-MM-DD)
- ✅ No empty required columns
- ✅ Age values between 13-100
- ✅ Sales amounts > 0

---

## 📖 How to Use

### 1. **Starting the Dashboard**
```bash
streamlit run lulu_sales_dashboardexe.py
```

### 2. **Global Filters (Apply to All Pages)**
Located in left sidebar:
- **🏙️ City**: Filter by specific city
- **🏬 Store Format**: Filter by format (Hypermarket, Express, Web, etc.)
- **📅 Date Range**: Select analysis period

### 3. **Navigation**
Use the radio button menu to jump between sections:
- 📊 Executive Summary
- 🏙️ City Analysis
- 🏢 Department Analysis
- 📢 Campaign & Channels
- 🏪 Store Format Analysis
- 👥 People Demographics
- 🎯 Strategic Recommendations

### 4. **Interacting with Visualizations**
- **Hover**: See detailed information in tooltips
- **Zoom**: Drag on chart to zoom into area
- **Pan**: Hold Shift + Drag to move around
- **Legend**: Click items to toggle visibility

### 5. **Using Questionnaires**
Each section ends with decision questions:
- Select dropdown options based on your strategy
- Answer questions to define actions
- Click "Save" buttons to record decisions

### 6. **Exporting Data**
- Use sidebar button to download filtered CSV
- Export includes all current filters applied
- Perfect for Excel analysis or sharing

---

## 📑 Page Descriptions

### 📊 Executive Summary
**Purpose:** Quick overview of overall business health

**Key Metrics:**
- Total sales in analysis period
- Number of transactions
- Average basket size
- Total quantity sold

**Charts:**
- Bar charts for top cities, store formats, departments
- Sortable, comparable across dimensions
- Quick identification of leaders and laggards

**Use Case:** Morning briefing, stakeholder updates

---

### 🏙️ City Analysis
**Purpose:** Deep dive into city-specific performance

**Sections:**

1. **Top Performers**
   - Best departments, categories, campaigns
   - Successful strategies to replicate

2. **Underperformers**
   - Minimum sales categories
   - Improvement opportunities

3. **Demographics**
   - Age groups ordering most/least
   - Nationality preferences
   - Store format popularity

4. **Insights & Recommendations**
   - Actionable strategies
   - Cross-city comparisons
   - Expected impact

5. **Questionnaire**
   - Marketing budget decisions
   - Campaign prioritization
   - Implementation strategy

**Use Case:** City manager planning, local optimization

---

### 🏢 Department Analysis
**Purpose:** Understand department-level performance and opportunities

**Sections:**

1. **Performance Overview**
   - Ranking by sales
   - Quantity vs. revenue analysis

2. **High Revenue Per Unit Analysis**
   - Premium departments (high revenue, low qty)
   - Budget departments (high qty, low revenue)
   - Middle departments for optimization

3. **Comparative Analysis**
   - Department by city performance
   - Department by campaign effectiveness
   - Best campaigns for each department

4. **ROI Projections**
   - Expected increase from applying successful campaigns
   - Department-specific growth potential

5. **Questionnaire**
   - Department focus selection
   - Campaign strategy
   - Expected uplift targets

**Use Case:** Buying decisions, inventory planning, promotional strategy

---

### 📢 Campaign & Channels
**Purpose:** Evaluate campaign ROI and effectiveness

**Sections:**

1. **Performance Ranking**
   - Star ratings for each campaign
   - High vs. low performers
   - ROI scores

2. **Multi-Dimensional Analysis**
   - Campaign by department
   - Campaign by city
   - Campaign by age group
   - Heatmap visualization

3. **Customer Type Analysis**
   - New vs. repeat customer acquisition
   - Loyalty campaign effectiveness
   - Seasonal campaign performance

4. **Budget Recommendations**
   - Scale up high performers
   - Optimize medium performers
   - Discontinue low performers

5. **Questionnaire**
   - Campaign priority selection
   - Budget allocation %
   - Target demographics

**Use Case:** Marketing planning, campaign ROI tracking, channel optimization

---

### 🏪 Store Format Analysis
**Purpose:** Optimize performance by store format

**Sections:**

1. **Format Overview**
   - Ranking by sales
   - Transaction volume
   - Average basket size

2. **Geographic Distribution**
   - Format performance by city
   - City-specific format success

3. **Department Distribution**
   - Top departments by format
   - Low performers by format
   - Format-specific recommendations

4. **Customer Preferences**
   - Age group format preferences
   - Nationality format preferences
   - Campaign effectiveness by format

5. **Optimization Strategy**
   - Cross-format learning
   - Expected uplift from changes
   - Implementation roadmap

**Use Case:** Store operations, format-specific strategies, expansion planning

---

### 👥 People Demographics
**Purpose:** Understand customer profiles and targeting

**Sections:**

1. **Age Group Analysis**
