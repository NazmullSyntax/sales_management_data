import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Executive Business Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling cards and layout
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #1f77b4;
    }
    .metric-label {
        font-size: 14px;
        color: #6c757d;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# STEP 1: Generate Synthetic Business Data
# ==========================================
@st.cache_data
def load_data():
    np.random.seed(42)
    num_records = 1500

    dates = pd.date_range(start="2025-01-01", end="2025-12-31", periods=num_records)
    categories = ["Electronics", "Clothing", "Home & Kitchen", "Books"]
    products = {
        "Electronics": ["Laptop", "Smartphone", "Headphones"],
        "Clothing": ["T-Shirt", "Jeans", "Jacket"],
        "Home & Kitchen": ["Blender", "Coffee Maker", "Cookware"],
        "Books": ["Fiction", "Tech Guide", "Cookbook"]
    }
    regions = ["North", "South", "East", "West"]

    records = []
    for i in range(num_records):
        cat = np.random.choice(categories)
        prod = np.random.choice(products[cat])
        reg = np.random.choice(regions)
        price = round(np.random.uniform(15, 600), 2)
        qty = np.random.randint(1, 8)
        discount = np.random.choice([0.0, 0.05, 0.10, 0.15, 0.20])
        
        records.append({
            "Order_ID": 1000 + i,
            "Date": np.random.choice(dates),
            "Category": cat,
            "Product": prod,
            "Region": reg,
            "Unit_Price": price,
            "Quantity": qty,
            "Discount": discount
        })

    df = pd.DataFrame(records)
    df["Gross_Sales"] = df["Unit_Price"] * df["Quantity"]
    df["Net_Sales"] = df["Gross_Sales"] * (1 - df["Discount"])
    df["Month_Year"] = df["Date"].dt.to_period("M").astype(str)
    return df

df = load_data()

# ==========================================
# STEP 2: Sidebar Dynamic Filters
# ==========================================
st.sidebar.header("🔍 Filter Dashboard")

# Region Filter
selected_region = st.sidebar.multiselect(
    "Select Region(s):",
    options=df["Region"].unique(),
    default=df["Region"].unique()
)

# Category Filter
selected_category = st.sidebar.multiselect(
    "Select Category:",
    options=df["Category"].unique(),
    default=df["Category"].unique()
)

# Date Range Filter
min_date = df["Date"].min().date()
max_date = df["Date"].max().date()

start_date, end_date = st.sidebar.date_input(
    "Select Date Range:",
    value=[min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# Apply Filters
filtered_df = df[
    (df["Region"].isin(selected_region)) &
    (df["Category"].isin(selected_category)) &
    (df["Date"].dt.date >= start_date) &
    (df["Date"].dt.date <= end_date)
]

# ==========================================
# STEP 3: Dashboard Header & KPI Metrics
# ==========================================
st.title("📊 Executive Sales & Operations Dashboard")
st.markdown("Real-time dynamic overview of operational sales metrics.")

# Calculate Key Business KPIs
total_revenue = filtered_df["Net_Sales"].sum()
total_orders = filtered_df["Order_ID"].nunique()
avg_order_value = filtered_df["Net_Sales"].mean() if not filtered_df.empty else 0
total_units = filtered_df["Quantity"].sum()

# Display KPIs in 4 Columns
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric("Total Revenue", f"${total_revenue:,.2f}")

with kpi2:
    st.metric("Total Orders", f"{total_orders:,}")

with kpi3:
    st.metric("Avg Order Value", f"${avg_order_value:,.2f}")

with kpi4:
    st.metric("Units Sold", f"{total_units:,}")

st.markdown("---")

# ==========================================
# STEP 4: Visualizations Grid
# ==========================================
if filtered_df.empty:
    st.warning("No data available for the selected filters.")
else:
    col1, col2 = st.columns(2)

    with col1:
        # Monthly Revenue Line Chart
        monthly_sales = filtered_df.groupby("Month_Year")["Net_Sales"].sum().reset_index()
        fig_line = px.line(
            monthly_sales, 
            x="Month_Year", 
            y="Net_Sales", 
            title="📈 Monthly Revenue Performance",
            markers=True,
            line_shape="spline"
        )
        fig_line.update_layout(xaxis_title="Month", yaxis_title="Net Sales ($)")
        st.plotly_chart(fig_line, use_container_width=True)

    with col2:
        # Revenue by Category Bar Chart
        cat_sales = filtered_df.groupby("Category")["Net_Sales"].sum().reset_index().sort_values(by="Net_Sales", ascending=False)
        fig_bar = px.bar(
            cat_sales, 
            x="Category", 
            y="Net_Sales", 
            color="Category",
            title="🏷️ Revenue Share by Category",
            text_auto=".2s"
        )
        fig_bar.update_layout(yaxis_title="Net Sales ($)")
        st.plotly_chart(fig_bar, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        # Regional Distribution Donut Chart
        reg_sales = filtered_df.groupby("Region")["Net_Sales"].sum().reset_index()
        fig_donut = px.pie(
            reg_sales, 
            values="Net_Sales", 
            names="Region", 
            title="🌍 Regional Revenue Breakdown",
            hole=0.4
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with col4:
        # Top 5 Best-Selling Products Horizontal Bar Chart
        top_prods = filtered_df.groupby("Product")["Quantity"].sum().reset_index().sort_values(by="Quantity", ascending=True).tail(5)
        fig_top = px.bar(
            top_prods, 
            x="Quantity", 
            y="Product", 
            orientation="h",
            title="⭐ Top 5 Best-Selling Products (Volume)",
            color="Quantity",
            color_continuous_scale="Purples"
        )
        st.plotly_chart(fig_top, use_container_width=True)

# ==========================================
# STEP 5: Detailed Data Table & Export
# ==========================================
st.markdown("---")
st.subheader("📋 Raw Order Data")

with st.expander("Expand to view detailed order table"):
    st.dataframe(filtered_df, use_container_width=True)
    
    # Download CSV Button
    csv_data = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Filtered Data as CSV",
        data=csv_data,
        file_name="filtered_sales_data.csv",
        mime="text/csv"
    )