import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(
    page_title="Retail Profit Intelligence Dashboard",
    layout="wide"
)

# ----------------------------
# Load data
# ----------------------------
@st.cache_data
def load_data():
    base_dir = Path(__file__).resolve().parent
    csv_path = base_dir / "samplesuperstore.csv"

    df = pd.read_csv(csv_path)
    df = df.dropna()
    df["Order Date"] = pd.to_datetime(df["Order Date"])
    return df

df = load_data()

# ----------------------------
# Sidebar filters
# ----------------------------
st.sidebar.header("Filters")

region_options = ["All"] + sorted(df["Region"].unique().tolist())
category_options = ["All"] + sorted(df["Category"].unique().tolist())
segment_options = ["All"] + sorted(df["Segment"].unique().tolist())
subcat_options = ["All"] + sorted(df["Sub-Category"].unique().tolist())

selected_region = st.sidebar.selectbox("Select Region", region_options)
selected_category = st.sidebar.selectbox("Select Category", category_options)
selected_segment = st.sidebar.selectbox("Select Segment", segment_options)
selected_subcat = st.sidebar.selectbox("Select Sub-Category", subcat_options)

min_date = df["Order Date"].min().date()
max_date = df["Order Date"].max().date()

date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

top_n = st.sidebar.slider("Top N Products", min_value=5, max_value=20, value=10, step=1)
high_discount_only = st.sidebar.checkbox("Show only discount > 0.2", value=False)

# ----------------------------
# Apply filters
# ----------------------------
filtered_df = df.copy()

if selected_region != "All":
    filtered_df = filtered_df[filtered_df["Region"] == selected_region]

if selected_category != "All":
    filtered_df = filtered_df[filtered_df["Category"] == selected_category]

if selected_segment != "All":
    filtered_df = filtered_df[filtered_df["Segment"] == selected_segment]

if selected_subcat != "All":
    filtered_df = filtered_df[filtered_df["Sub-Category"] == selected_subcat]

if high_discount_only:
    filtered_df = filtered_df[filtered_df["Discount"] > 0.2]

if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = filtered_df[
        (filtered_df["Order Date"].dt.date >= start_date) &
        (filtered_df["Order Date"].dt.date <= end_date)
    ]

# ----------------------------
# Title and intro
# ----------------------------
st.title("📊 Retail Profit Intelligence Dashboard")

st.markdown("""
### Business Decision Support Tool

Retail businesses often use discount strategies to increase sales, but excessive discounting can reduce profitability.  
This dashboard is designed for **retail managers** and **business analysts** who want to evaluate business performance and make more informed pricing and promotion decisions.
""")

st.markdown("""
**Core Analytical Question:**  
How can discount strategies be managed to improve sales performance without damaging profitability?
""")

st.markdown("---")

# ----------------------------
# KPIs
# ----------------------------
total_sales = filtered_df["Sales"].sum()
total_profit = filtered_df["Profit"].sum()
avg_discount = filtered_df["Discount"].mean()
profit_margin = (total_profit / total_sales * 100) if total_sales != 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Sales", f"{total_sales:,.0f}")
col2.metric("Total Profit", f"{total_profit:,.0f}")
col3.metric("Avg Discount", f"{avg_discount:.2%}")
col4.metric("Profit Margin", f"{profit_margin:.2f}%")

st.markdown("---")

# ----------------------------
# Dynamic insights
# ----------------------------
st.markdown("## 🔎 Dynamic Insights")

if not filtered_df.empty:
    top_category = filtered_df.groupby("Category")["Sales"].sum().idxmax()
    top_region = filtered_df.groupby("Region")["Sales"].sum().idxmax()
    top_product = filtered_df.groupby("Product Name")["Sales"].sum().idxmax()

    insight_lines = [
        f"- **Top category:** {top_category}",
        f"- **Top region:** {top_region}",
        f"- **Top product:** {top_product}",
        f"- **Profit margin:** {profit_margin:.2f}%"
    ]

    if profit_margin < 5:
        insight_lines.append("- **Signal:** Profitability is weak under the current selection.")
    elif profit_margin < 10:
        insight_lines.append("- **Signal:** Profitability is moderate and should be monitored carefully.")
    else:
        insight_lines.append("- **Signal:** Profitability remains relatively healthy in the current view.")

    if avg_discount > 0.2:
        insight_lines.append("- **Discount risk:** The average discount is relatively high and may create margin pressure.")
    else:
        insight_lines.append("- **Discount risk:** The average discount remains at a relatively controlled level.")

    st.markdown("\n".join(insight_lines))
else:
    st.write("No data available for the selected filters.")

st.markdown("---")

# ----------------------------
# Tabs
# ----------------------------
tab1, tab2, tab3, tab4 = st.tabs(
    ["Overview", "Sales Analysis", "Discount Analysis", "Products & Notes"]
)

# =========================================================
# TAB 1: OVERVIEW
# =========================================================
with tab1:
    st.markdown("## Overview")

    if not filtered_df.empty:
        monthly_sales = (
            filtered_df
            .set_index("Order Date")
            .resample("ME")["Sales"]
            .sum()
            .reset_index()
        )

        fig_trend = px.line(
            monthly_sales,
            x="Order Date",
            y="Sales",
            title="Monthly Sales Trend",
            markers=True
        )
        fig_trend.update_traces(line_color="darkgreen")
        fig_trend.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            title_font_size=18
        )
        st.plotly_chart(fig_trend, use_container_width=True)

        st.markdown("""
**Insight:** Sales generally show an upward trend over time, although short-term fluctuations remain visible.  
This suggests business growth, but also indicates that performance is not equally stable across all periods.
""")
    else:
        st.write("No data available for the selected filters.")

# =========================================================
# TAB 2: SALES ANALYSIS
# =========================================================
with tab2:
    st.markdown("## Sales Analysis")

    if not filtered_df.empty:
        col_left, col_right = st.columns(2)

        with col_left:
            category_sales = (
                filtered_df.groupby("Category")["Sales"]
                .sum()
                .reset_index()
                .sort_values("Sales", ascending=False)
            )
            category_sales["Highlight"] = category_sales["Sales"].apply(
                lambda x: "Top Category" if x == category_sales["Sales"].max() else "Other Categories"
            )

            fig_cat = px.bar(
                category_sales,
                x="Category",
                y="Sales",
                color="Highlight",
                text="Sales",
                title="Sales Performance by Category",
                color_discrete_map={
                    "Top Category": "orange",
                    "Other Categories": "darkgreen"
                }
            )
            fig_cat.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
            fig_cat.update_layout(
                showlegend=False,
                plot_bgcolor="white",
                paper_bgcolor="white"
            )
            st.plotly_chart(fig_cat, use_container_width=True)

            top_cat = category_sales.iloc[0]["Category"]
            st.markdown(f"""
**Insight:** {top_cat} is the strongest-performing category in the current selection.  
This suggests that revenue is concentrated in this segment and that it plays a major role in driving sales performance.
""")

        with col_right:
            region_sales = (
                filtered_df.groupby("Region")["Sales"]
                .sum()
                .reset_index()
                .sort_values("Sales", ascending=False)
            )
            region_sales["Highlight"] = region_sales["Sales"].apply(
                lambda x: "Top Region" if x == region_sales["Sales"].max() else "Other Regions"
            )

            fig_region = px.bar(
                region_sales,
                x="Region",
                y="Sales",
                color="Highlight",
                text="Sales",
                title="Regional Sales Analysis",
                color_discrete_map={
                    "Top Region": "orange",
                    "Other Regions": "darkgreen"
                }
            )
            fig_region.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
            fig_region.update_layout(
                showlegend=False,
                plot_bgcolor="white",
                paper_bgcolor="white"
            )
            st.plotly_chart(fig_region, use_container_width=True)

            top_region = region_sales.iloc[0]["Region"]
            st.markdown(f"""
**Insight:** {top_region} generates the highest sales in the current selection.  
This indicates stronger market performance and suggests that this region is a key contributor to overall revenue.
""")
    else:
        st.write("No data available for the selected filters.")

# =========================================================
# TAB 3: DISCOUNT ANALYSIS
# =========================================================
with tab3:
    st.markdown("## Discount Analysis")

    if not filtered_df.empty:
        # 1. Average Profit by Discount Level (Bar Chart)
        discount_profit = (
            filtered_df.groupby("Discount")["Profit"]
            .mean()
            .reset_index()
            .sort_values("Discount")
        )

        # 为了使用黄绿配色，增加一个同名分类列
        discount_profit["Discount Label"] = discount_profit["Discount"].astype(str)

        fig_bar = px.bar(
            discount_profit,
            x="Discount",
            y="Profit",
            color="Discount Label",
            text="Profit",
            title="1. Average Profit by Discount Level",
            color_discrete_sequence=px.colors.sequential.YlGn
        )

        fig_bar.update_traces(
            texttemplate="%{text:.1f}",
            textposition="outside"
        )

        fig_bar.add_hline(y=0, line_dash="dash", line_color="darkgreen")

        fig_bar.update_layout(
            showlegend=False,
            plot_bgcolor="white",
            paper_bgcolor="white",
            xaxis_title="Discount Level",
            yaxis_title="Average Profit"
        )

        st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("""
**Insight:** Average profit declines as discount levels increase. Moderate discount levels maintain relatively stable profitability, while higher discount levels significantly reduce profit, indicating increased financial risk. This suggests that excessive discounting may weaken margins rather than improve overall business performance.
""")

        st.markdown("---")

        # 2. Average Profit by Discount Level (Line Chart)
        fig_line = px.line(
            discount_profit,
            x="Discount",
            y="Profit",
            title="2. Average Profit by Discount Level (Trend View)",
            markers=True
        )
        fig_line.update_traces(line_color="darkgreen")
        fig_line.add_hline(y=0, line_dash="dash", line_color="red")
        fig_line.update_layout(plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig_line, use_container_width=True)

        st.markdown("""
**Insight:** The trend view confirms that profitability weakens as discounts become deeper. Although modest discounts may still be sustainable, higher discount levels place substantial pressure on average profit.
""")

        st.markdown("---")

        # 3. Average Profit by Discount Group
        discount_group = filtered_df.copy()
        discount_group["Discount Group"] = pd.cut(
            discount_group["Discount"],
            bins=[-0.01, 0, 0.2, 0.4, 1.0],
            labels=["No Discount", "Low Discount", "Medium Discount", "High Discount"]
        )

        group_profit = (
            discount_group.groupby("Discount Group", observed=False)["Profit"]
            .mean()
            .reset_index()
        )

        group_profit["Highlight"] = group_profit["Discount Group"].apply(
            lambda x: "High Risk" if x in ["Medium Discount", "High Discount"] else "Lower Risk"
        )

        fig_group = px.bar(
            group_profit,
            x="Discount Group",
            y="Profit",
            color="Highlight",
            text="Profit",
            title="3. Average Profit by Discount Group",
            color_discrete_map={
                "High Risk": "orange",
                "Lower Risk": "darkgreen"
            }
        )
        fig_group.update_traces(texttemplate="%{text:.1f}", textposition="outside")
        fig_group.add_hline(y=0, line_dash="dash", line_color="red")
        fig_group.update_layout(
            showlegend=False,
            plot_bgcolor="white",
            paper_bgcolor="white"
        )
        st.plotly_chart(fig_group, use_container_width=True)

        st.markdown("""
**Insight:** Orders with no or low discount tend to maintain stronger profitability, while medium and high discount groups show weaker results. This highlights the trade-off between promotional pricing and margin protection.
""")
    else:
        st.write("No data available for the selected filters.")

# =========================================================
# TAB 4: PRODUCTS & NOTES
# =========================================================
with tab4:
    st.markdown("## Products & Notes")

    if not filtered_df.empty:
        top_products = (
            filtered_df.groupby("Product Name")["Sales"]
            .sum()
            .reset_index()
            .sort_values("Sales", ascending=False)
            .head(top_n)
            .sort_values("Sales")
        )

        top_products["Short Name"] = top_products["Product Name"].apply(
            lambda x: x[:38] + "..." if len(x) > 38 else x
        )

        top_products["Highlight"] = top_products["Sales"].apply(
            lambda x: "Top Product" if x == top_products["Sales"].max() else "Other Products"
        )

        fig_products = px.bar(
            top_products,
            x="Sales",
            y="Short Name",
            orientation="h",
            color="Highlight",
            text="Sales",
            title=f"Top {top_n} Products by Sales",
            hover_data={"Product Name": True, "Short Name": False, "Sales": ":,.0f"},
            color_discrete_map={
                "Top Product": "orange",
                "Other Products": "darkgreen"
            }
        )

        fig_products.update_traces(
            texttemplate="%{text:,.0f}",
            textposition="outside"
        )

        fig_products.update_layout(
            showlegend=False,
            plot_bgcolor="white",
            paper_bgcolor="white",
            xaxis_title="Sales",
            yaxis_title="Product",
            height=max(500, top_n * 45),
            margin=dict(l=320, r=80, t=60, b=60)
        )

        fig_products.update_yaxes(
            automargin=True
        )

        st.plotly_chart(fig_products, use_container_width=True)

        st.markdown("""
**Insight:** Sales are highly concentrated among a small number of products, indicating reliance on key revenue drivers. Strategic focus on these products could improve performance, but overdependence may also create concentration risk.
""")

    st.markdown("---")

    st.markdown("## Summary")

    st.markdown("""
### Key Insights

- Strong sales performance is concentrated in a limited number of categories and products.
- Some regions contribute significantly more revenue than others, highlighting uneven market performance.
- Sales generally increase over time, despite visible short-term volatility.
- Higher discount levels are associated with lower profit margins.
- Business performance depends not only on sales growth, but also on careful discount control.
""")

    st.markdown("""
### Business Recommendations

- Maintain stronger investment in high-performing categories and products.
- Reinforce successful regional strategies while reviewing weaker regional performance.
- Use discount strategies selectively rather than aggressively.
- Monitor margin erosion when discount levels become too high.
- Treat this dashboard as a decision-support tool for pricing, promotion, and product focus.
""")

    st.markdown("---")

    st.markdown("## Limitations")

    st.markdown("""
- This dataset is a sample retail dataset and may not fully reflect real-world business complexity.
- The dashboard mainly supports descriptive analysis and simple trend interpretation rather than advanced predictive modelling.
- Some relationships shown in the charts may be influenced by other factors such as customer type, product mix, or seasonality, which are not fully controlled here.
- Results may change when filters are applied, so insights should be interpreted within the selected context rather than as universal conclusions.
""")

    st.markdown("---")

    st.markdown("## Data Source and Notes")

    st.markdown("""
- **Dataset:** Sample Superstore dataset (Kaggle)  
- **Date accessed:** April 2026  
- **Purpose:** Educational retail profit analysis  
- **Note:** This dashboard is intended as a decision-support tool rather than a predictive model.
""")