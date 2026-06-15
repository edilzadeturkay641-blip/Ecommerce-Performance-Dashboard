import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px
from datetime import date
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)



st.set_page_config(page_title="Ecommerce Performance Dashboard", layout="wide")

st.title("Ecommerce Performance Dashboard")
st.caption("Sales, product demand and customer behavior analysis")


# FILTERS


st.sidebar.header("Filters")

cities_query = """
SELECT DISTINCT city
FROM customers
ORDER BY city;
"""

cities_df = pd.read_sql(cities_query, engine)

selected_city = st.sidebar.selectbox("City", ["All"] + cities_df["city"].tolist())

st.sidebar.subheader("Date Filter")

start_date = st.sidebar.date_input("Start Date", value=date(2026, 1, 1))

end_date = st.sidebar.date_input("End Date", value=date.today())

filters = []

if selected_city != "All":
    filters.append(f"c.city = '{selected_city}'")

if start_date and end_date:
    filters.append(f"o.order_date BETWEEN '{start_date}' AND '{end_date}'")

where_clause = ""

if filters:
    where_clause = "WHERE " + " AND ".join(filters)


# umumi gostericiler


basis_query = f"""
SELECT
    ROUND(SUM(o.quantity * p.price)::numeric, 2) AS total_sales,
    COUNT(DISTINCT o.order_id) AS total_orders,
    COUNT(DISTINCT o.customer_id) AS total_customers
FROM orders o
JOIN products p
    ON o.product_id = p.product_id
JOIN customers c
    ON o.customer_id = c.customer_id
{where_clause};
"""

basis_df = pd.read_sql(basis_query, engine)

total_sales = basis_df["total_sales"][0] if pd.notna(basis_df["total_sales"][0]) else 0
total_orders = (
    int(basis_df["total_orders"][0]) if pd.notna(basis_df["total_orders"][0]) else 0
)
total_customers = (
    int(basis_df["total_customers"][0])
    if pd.notna(basis_df["total_customers"][0])
    else 0
)

col1, col2, col3 = st.columns(3)

col1.metric("Gross Sales Sum", f"${total_sales:,.0f}")
col2.metric("Orders", f"{total_orders:,}")
col3.metric("Customers", f"{total_customers:,}")

st.divider()

# AYLIQ SATISLAR


st.subheader("Sales  by Customer Segment")

monthly_query = f"""
SELECT
    DATE_TRUNC('month', o.order_date) AS month,
    p.product_name,
    c.membership_type,
    ROUND(SUM(o.quantity * p.price)::numeric, 2) AS total_sales
FROM orders o
JOIN products p
    ON o.product_id = p.product_id
JOIN customers c
    ON o.customer_id = c.customer_id
{where_clause}
GROUP BY
    month,
    p.product_name,
    c.membership_type
ORDER BY month;
"""

monthly_df = pd.read_sql(monthly_query, engine)

if monthly_df.empty:
    st.warning("No data found for the selected filters.")
    st.stop()

monthly_df["month"] = pd.to_datetime(monthly_df["month"])

selected_product = st.selectbox("Product", monthly_df["product_name"].unique())

filtered_monthly_df = monthly_df[monthly_df["product_name"] == selected_product]

fig_monthly = px.line(
    filtered_monthly_df,
    x="month",
    y="total_sales",
    color="membership_type",
    markers=True,
    title=f"{selected_product} - Monthly Sales by Customer Segment",
)

fig_monthly.update_layout(
    height=500,
    xaxis_title="Month",
    yaxis_title="Sales",
    legend_title="Customer Segment",
    margin=dict(l=40, r=40, t=70, b=40),
)

st.plotly_chart(fig_monthly, use_container_width=True)

st.divider()


# TOP 10 PRODUCTS BY SALES


top_products_query = f"""
SELECT
    p.product_name,
    ROUND(SUM(o.quantity * p.price)::numeric, 2) AS total_sales
FROM orders o
JOIN products p
    ON o.product_id = p.product_id
JOIN customers c
    ON o.customer_id = c.customer_id
{where_clause}
GROUP BY p.product_name
ORDER BY total_sales DESC
LIMIT 10;
"""

top_products_df = pd.read_sql(top_products_query, engine)

fig_top_products = px.bar(
    top_products_df,
    x="total_sales",
    y="product_name",
    orientation="h",
    color="total_sales",
    text="total_sales",
    title="Top 10 Products by Revenue",
    # color_continuous_scale="Plasma"
)

fig_top_products.update_traces(texttemplate="$%{x:,.0f}", textposition="outside")

fig_top_products.update_layout(
    height=580,
    yaxis=dict(autorange="reversed"),
    xaxis_title="Sales",
    yaxis_title="Product",
    showlegend=False,
    margin=dict(l=80, r=140, t=70, b=40),
)

fig_top_products.update_xaxes(range=[0, top_products_df["total_sales"].max() * 1.2])

st.subheader("Top Products")
st.plotly_chart(fig_top_products, use_container_width=True)

st.divider()


# HIGHEST VALUE CUSTOMERS


top_customers_query = f"""
SELECT
    c.name || ' - ' || c.membership_type AS name,
    ROUND(SUM(o.quantity * p.price)::numeric, 2) AS total_sales
FROM customers c
JOIN orders o
    ON c.customer_id = o.customer_id
JOIN products p
    ON o.product_id = p.product_id
{where_clause}
GROUP BY
    c.name,
    c.membership_type
ORDER BY total_sales DESC
LIMIT 10;
"""

top_customers_df = pd.read_sql(top_customers_query, engine)

fig_customers = px.bar(
    top_customers_df,
    x="total_sales",
    y="name",
    orientation="h",
    color="total_sales",
    text="total_sales",
    title="Highest Value Customers",
    # color_continuous_scale="Greens"
)

fig_customers.update_traces(texttemplate="$%{x:,.0f}", textposition="outside")

fig_customers.update_layout(
    height=580,
    yaxis=dict(autorange="reversed"),
    xaxis_title="Sales",
    yaxis_title="Customer",
    showlegend=False,
    margin=dict(l=80, r=140, t=70, b=40),
)

fig_customers.update_xaxes(range=[0, top_customers_df["total_sales"].max() * 1.2])

st.subheader("Highest Value Customers")
st.plotly_chart(fig_customers, use_container_width=True)

st.divider()


# =========================
# SALES BY CATEGORY
# =========================

category_query = f"""
SELECT
    p.category,
    ROUND(SUM(o.quantity * p.price)::numeric, 2) AS total_sales
FROM orders o
JOIN products p
    ON o.product_id = p.product_id
JOIN customers c
    ON o.customer_id = c.customer_id
{where_clause}
GROUP BY p.category
ORDER BY total_sales DESC;
"""

category_df = pd.read_sql(category_query, engine)

BLUE_PALETTE = [
    "#083D77",  # tünd
    "#2166B5",  # orta-tünd
    "#4A92E2",  # orta
    "#7BB8F0",  # açıq
    "#C7E3FA",  # çox açıq
]


fig_category = px.pie(
    category_df,
    names="category",
    values="total_sales",
    hole=0.4,
    color_discrete_sequence=BLUE_PALETTE,
)

fig_category.update_layout(
    height=470, legend_title="Category", margin=dict(l=20, r=20, t=70, b=20)
)

# =========================
# SALES BY CITY
# =========================

city_query = f"""
SELECT
    c.city,
    ROUND(SUM(o.quantity * p.price)::numeric, 2) AS total_sales
FROM customers c
JOIN orders o
    ON c.customer_id = o.customer_id
JOIN products p
    ON o.product_id = p.product_id
{where_clause}
GROUP BY c.city
ORDER BY total_sales DESC;
"""

city_df = pd.read_sql(city_query, engine)

fig_city = px.bar(
    city_df,
    x="city",
    y="total_sales",
    text="total_sales",
    title="Sales by City",
    color="total_sales",
    # color_continuous_scale="Viridis"
)

fig_city.update_traces(
    texttemplate="$%{y:,.0f}", textposition="outside", cliponaxis=False
)

fig_city.update_layout(
    height=470,
    xaxis_title="City",
    yaxis_title="Total Sales",
    showlegend=False,
    margin=dict(l=40, r=40, t=70, b=40),
    uniformtext_minsize=10,
    uniformtext_mode="hide",
)

fig_city.update_yaxes(range=[0, city_df["total_sales"].max() * 1.3])

row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.subheader("Sales by Category")
    st.plotly_chart(fig_category, use_container_width=True)

with row2_col2:
    st.subheader("Sales by City")
    st.plotly_chart(fig_city, use_container_width=True)

    fig_city = px.bar(
        city_df,
        x="city",
        y="total_sales",
        text="total_sales",
        title="Sales by City",
        color="total_sales",


    )
st.divider()


# CUSTOMER ACTIVITY SEGMENTATION


st.subheader("Customer Activity Segmentation")

rfm_query = f"""
SELECT
    c.customer_id,
    c.name,
    c.city,
    c.membership_type,
    MAX(o.order_date) AS last_order_date,
    COUNT(DISTINCT o.order_id) AS frequency,
    ROUND(SUM(o.quantity * p.price)::numeric, 2) AS total_sales
FROM customers c
JOIN orders o
    ON c.customer_id = o.customer_id
JOIN products p
    ON o.product_id = p.product_id
{where_clause}
GROUP BY
    c.customer_id,
    c.name,
    c.city,
    c.membership_type;
"""

rfm_df = pd.read_sql(rfm_query, engine)

if not rfm_df.empty:
    rfm_df["last_order_date"] = pd.to_datetime(rfm_df["last_order_date"])

    today = pd.Timestamp.today()

    rfm_df["recency"] = (today - rfm_df["last_order_date"]).dt.days

    def customer_segment(recency):

        if recency <= 30:
            return "Active Customers"

        elif 30 < recency <= 60:
            return "Normal Customers"

        else:
            return "Risk Customers"

    rfm_df["segment"] = rfm_df["recency"].apply(customer_segment)

         

else:
    st.warning("No customer data found for customer activity analysis.")



segment_df = (
    rfm_df.groupby("segment")
    .agg(
        customers=("customer_id", "count"),
        total_revenue=("total_sales", "sum")
    )
    .reset_index()
) 

fig_segment = px.bar(
    segment_df,
    x="customers",
    y="segment",
    orientation="h",
    text="customers",
    title="Customers by Segment"
)

fig_segment.update_traces(
    textposition="outside"
)

fig_segment.update_layout(
    height=420,
    xaxis_title="Customers",
    yaxis_title="Segment",
    showlegend=False
)

st.plotly_chart(fig_segment, use_container_width=True)

st.subheader("Customer Information by Segment")

selected_segment = st.selectbox(
    "Filter by Segment",
    ["All"] + sorted(rfm_df["segment"].unique().tolist())
)

if selected_segment == "All":
    filtered_rfm_df = rfm_df
else:
    filtered_rfm_df = rfm_df[
        rfm_df["segment"] == selected_segment
    ]

st.dataframe(
    filtered_rfm_df[
        [
            "name",
            "city",
            "membership_type",
            "recency",
            "frequency",
            "total_sales",
            "segment"
        ]
    ],
    use_container_width=True
)