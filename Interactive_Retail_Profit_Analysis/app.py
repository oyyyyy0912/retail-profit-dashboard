import streamlit as st
import pandas as pd
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

This dashboard is designed not only to present charts, but to generate <span style='color:red; font-weight:bold;'>decision-relevant insights</span>.  
Its primary purpose is to help retail managers and business analysts identify where sales performance is strongest, where profitability is under pressure, and how discount strategy affects business sustainability.  

In this product, the competitive value does not come from visualisation alone; it comes from the ability to convert filtered data into <span style='color:red; font-weight:bold;'>clear, actionable managerial insights</span>.
""", unsafe_allow_html=True)

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

    if profit_margin < 5:
        profitability_signal = "Profitability is currently <span style='color:red; font-weight:bold;'>weak</span> and may require immediate managerial attention."
    elif profit_margin < 10:
        profitability_signal = "Profitability is <span style='color:red; font-weight:bold;'>moderate</span> but remains vulnerable to discount pressure."
    else:
        profitability_signal = "Profitability remains <span style='color:red; font-weight:bold;'>relatively healthy</span> under the current selection."

    if avg_discount > 0.2:
        discount_signal = "The current average discount is <span style='color:red; font-weight:bold;'>high</span>, suggesting that margin pressure may be partly discount-driven."
    else:
        discount_signal = "The current average discount remains <span style='color:red; font-weight:bold;'>relatively controlled</span>, reducing immediate pricing risk."

    st.markdown(f"""
**Current Insight Summary:**  
The strongest sales category is <span style='color:red; font-weight:bold;'>{top_category}</span>, while the leading regional contributor is <span style='color:red; font-weight:bold;'>{top_region}</span>.  
The best-selling product under the current filters is <span style='color:red; font-weight:bold;'>{top_product}</span>.  

The current profit margin is <span style='color:red; font-weight:bold;'>{profit_margin:.2f}%</span>. {profitability_signal}  
The average discount level is <span style='color:red; font-weight:bold;'>{avg_discount:.2%}</span>. {discount_signal}
""", unsafe_allow_html=True)
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
**Insight:** The sales series shows a broadly upward trajectory, indicating that the business has achieved <span style='color:red; font-weight:bold;'>overall revenue growth</span> over time.  
However, the visible fluctuations suggest that performance is not fully stable across periods, implying that sales expansion may still be sensitive to seasonal effects, campaign intensity, or operational variation.
""", unsafe_allow_html=True)
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
**Insight:** <span style='color:red; font-weight:bold;'>{top_cat}</span> is the strongest-performing category in the current selection, indicating that category-level revenue is concentrated in this segment.  
From a managerial perspective, this suggests that <span style='color:red; font-weight:bold;'>{top_cat}</span> is likely to be a major driver of sales performance and may warrant priority in inventory planning, promotional allocation, and customer targeting.
""", unsafe_allow_html=True)

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
**Insight:** <span style='color:red; font-weight:bold;'>{top_region}</span> generates the highest sales in the current selection, indicating that regional performance is uneven rather than uniformly distributed.  
This suggests that <span style='color:red; font-weight:bold;'>{top_region}</span> is currently a key contributor to revenue and may reflect stronger demand conditions, more effective market penetration, or better commercial execution than other regions.
""", unsafe_allow_html=True)
    else:
        st.write("No data available for the selected filters.")

# =========================================================
# TAB 3: DISCOUNT ANALYSIS
# =========================================================
with tab3:
    st.markdown("## Discount Analysis")

    if not filtered_df.empty:
        order_count = (
            filtered_df.groupby("Discount")
            .size()
            .reset_index(name="Order Count")
            .sort_values("Discount")
        )

        avg_profit = (
            filtered_df.groupby("Discount")["Profit"]
            .mean()
            .reset_index(name="Average Profit")
            .sort_values("Discount")
        )

        discount_summary = order_count.merge(avg_profit, on="Discount")

        bar_colors = [
            "#2E7D32" if x <= 0.2 else "#F57C00"
            for x in discount_summary["Discount"]
        ]

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=discount_summary["Discount"],
                y=discount_summary["Order Count"],
                name="Order Volume",
                marker=dict(color=bar_colors),
                text=discount_summary["Order Count"],
                textposition="outside",
                yaxis="y1"
            )
        )

        fig.add_trace(
            go.Scatter(
                x=discount_summary["Discount"],
                y=discount_summary["Average Profit"],
                mode="lines",
                fill="tozeroy",
                fillcolor="rgba(102, 187, 106, 0.15)",
                line=dict(color="rgba(0,0,0,0)"),
                showlegend=False,
                yaxis="y2"
            )
        )

        fig.add_trace(
            go.Scatter(
                x=discount_summary["Discount"],
                y=discount_summary["Average Profit"],
                mode="lines+markers+text",
                name="Average Profit",
                line=dict(color="#1B5E20", width=3),
                marker=dict(size=8, color="white", line=dict(color="#1B5E20", width=2)),
                text=[f"{y:.0f}" for y in discount_summary["Average Profit"]],
                textposition=[
                    "top center" if y >= 0 else "bottom center"
                    for y in discount_summary["Average Profit"]
                ],
                yaxis="y2"
            )
        )

        fig.add_hline(y=0, line_dash="dash", line_color="#D84315", yref="y2")

        fig.update_layout(
            title="Discount Level vs Order Volume and Average Profit",
            xaxis=dict(title="Discount Level"),
            yaxis=dict(
                title=dict(text="Number of Orders", font=dict(color="#1B5E20")),
                tickfont=dict(color="#1B5E20")
            ),
            yaxis2=dict(
                title=dict(text="Average Profit"),
                overlaying="y",
                side="right"
            ),
            plot_bgcolor="white",
            paper_bgcolor="white"
        )

        st.plotly_chart(fig, use_container_width=True)

        best_profit_row = discount_summary.loc[discount_summary["Average Profit"].idxmax()]
        max_order_row = discount_summary.loc[discount_summary["Order Count"].idxmax()]

        best_discount = best_profit_row["Discount"]
        best_profit = best_profit_row["Average Profit"]
        max_order_discount = max_order_row["Discount"]
        max_order_count = max_order_row["Order Count"]

        if max_order_discount != best_discount:
            tradeoff_message = (
                f"The highest order volume occurs at <span style='color:red; font-weight:bold;'>{max_order_discount:.1f}</span>, "
                f"whereas the highest profitability occurs at <span style='color:red; font-weight:bold;'>{best_discount:.1f}</span>, "
                "indicating a measurable trade-off between demand expansion and margin preservation."
            )
        else:
            tradeoff_message = (
                f"The same discount level of <span style='color:red; font-weight:bold;'>{best_discount:.1f}</span> supports both the strongest profitability and the highest transaction volume."
            )

        negative = discount_summary[discount_summary["Average Profit"] < 0]["Discount"].tolist()

        if negative:
            negative_text = ", ".join([f"{x:.1f}" for x in negative])
            risk_message = (
                f"Average profit turns negative at discount levels such as <span style='color:red; font-weight:bold;'>{negative_text}</span>, "
                "suggesting that deeper discounting may become financially unsustainable."
            )
        else:
            risk_message = (
                "Average profit remains <span style='color:red; font-weight:bold;'>positive</span> across all visible discount levels."
            )

        st.markdown(f"""
**Managerial Insight:**  
Under the current filters, the most profitable discount level is <span style='color:red; font-weight:bold;'>{best_discount:.1f}</span>, where average profit reaches <span style='color:red; font-weight:bold;'>{best_profit:.1f}</span>.  
By contrast, the highest order volume occurs at <span style='color:red; font-weight:bold;'>{max_order_discount:.1f}</span>, with <span style='color:red; font-weight:bold;'>{int(max_order_count)}</span> orders.  

{tradeoff_message}  
{risk_message}  

Overall, the evidence indicates that discount policy should be managed as a <span style='color:red; font-weight:bold;'>trade-off between demand generation and margin preservation</span>, rather than as a simple sales stimulation mechanism.
""", unsafe_allow_html=True)
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

        fig_products.update_yaxes(automargin=True)

        st.plotly_chart(fig_products, use_container_width=True)

        st.markdown("""
**Insight:** Sales are concentrated among a relatively small number of products, indicating dependence on <span style='color:red; font-weight:bold;'>a limited set of key revenue drivers</span>.  
This concentration can improve managerial focus and resource allocation efficiency, but it also introduces <span style='color:red; font-weight:bold;'>product dependency risk</span> if demand for these leading items weakens.
""", unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("""
### Key Insights

- Revenue performance is concentrated in <span style='color:red; font-weight:bold;'>a limited number of categories, regions, and products</span>, rather than being evenly distributed.
- Sales show an overall growth tendency, but this growth remains <span style='color:red; font-weight:bold;'>structurally unstable</span> across periods.
- Discount strategy involves a clear <span style='color:red; font-weight:bold;'>trade-off</span>: it may support transaction volume, but it can also substantially weaken average profitability.
- Sustainable business performance should therefore be evaluated not only through sales expansion, but through <span style='color:red; font-weight:bold;'>the quality and durability of profit generation</span>.
""", unsafe_allow_html=True)

    st.markdown("""
### Business Recommendations

- Prioritise resource allocation toward <span style='color:red; font-weight:bold;'>high-performing categories and products</span>, while monitoring overdependence risk.
- Reinforce commercially successful regional strategies and investigate the structural causes of underperformance elsewhere.
- Apply discounts <span style='color:red; font-weight:bold;'>selectively rather than aggressively</span>, especially where deeper discounting pushes average profit into negative territory.
- Evaluate commercial performance through both <span style='color:red; font-weight:bold;'>sales growth and margin sustainability</span>, rather than relying on volume measures alone.
""", unsafe_allow_html=True)

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