import streamlit as st
import pandas as pd
import numpy as np

# ----------------- CONFIG -----------------
st.set_page_config(page_title="Stock & Purchase Insights", layout="wide")
st.title("📊 SAFA OUD MEHTA Stock & Purchase Insights")
st.markdown("""
This dashboard highlights risky stock and purchasing behavior:
- **Dead Stock Risk** → Zero sales before July, purchased after July, still zero sales
- **Over Purchased Risk** → Purchased quantity > avg sales, sales still low after July
""")

# ----------------- LOAD FILES -----------------
df1 = pd.read_excel("safa purchase 1.xlsx")
df2 = pd.read_excel("safa purchase 2.xlsx")
df = pd.concat([df1, df2], ignore_index=True)
df.columns = df.columns.str.strip()

# ----------------- SALES & STOCK CALC -----------------
months = ["Apr, 2025","May, 2025","Jun, 2025","Jul, 2025","Aug, 2025","Sep, 2025"]

df["Stock Value"] = df["Stock"] * df["Cost"]
df["Sales Value"] = df["Total Sales"] * df["Selling"]
df["Avg Sales Before July"] = df[["Apr, 2025","May, 2025","Jun, 2025"]].mean(axis=1)
df["Sales After July"] = df[["Jul, 2025","Aug, 2025","Sep, 2025"]].sum(axis=1)
df["LP Date"] = pd.to_datetime(df["LP Date"], errors="coerce")
df["LP Month"] = df["LP Date"].dt.month

# ----------------- RISK LOGIC -----------------
# Dead Stock: Zero sales before July, purchased after July, still zero sales
df["Dead Stock Risk"] = (
    (df[["Apr, 2025","May, 2025","Jun, 2025"]].sum(axis=1) == 0) &
    (df["LP Month"] >= 7) &
    (df["Sales After July"] == 0)
)

# Over Purchased: Purchased after July, bought > avg sales, sales still low
df["Over Purchased Risk"] = (
    (df["LP Month"] >= 7) &
    (df["LP Qty"] > df["Avg Sales Before July"]) &
    (df["Sales After July"] < df["Avg Sales Before July"])
)

# ----------------- CATEGORY FILTER -----------------
st.sidebar.header("Filter by Category")
categories = st.sidebar.multiselect("Select Category", options=df["Category"].unique(), default=df["Category"].unique())
filtered_df = df[df["Category"].isin(categories)]

# ----------------- FINAL COLUMNS -----------------
final_cols = [
    "Item Bar Code","Item Name","Item No","Category",
    "Stock","Stock Value","Total Sales","Sales Value",
    "Avg Sales Before July","Sales After July",
    "LP Qty","LP Date","LP Supplier","Margin%","Markup%"
] + months + ["Dead Stock Risk","Over Purchased Risk"]

# ----------------- DEAD STOCK -----------------
dead_s_items = filtered_df[filtered_df["Dead Stock Risk"]]
st.subheader("⚠️ Dead Stock Risk Items")
if not dead_s_items.empty:
    st.dataframe(dead_s_items[final_cols], use_container_width=True)
    st.markdown("**Dead Stock Insights**")
    st.markdown(f"- Total Items: **{len(dead_s_items)}**")
    st.markdown(f"- Total Stock Value: **{dead_s_items['Stock Value'].sum():,.0f}**")
    st.markdown(f"- Total Sales Value: **{dead_s_items['Sales Value'].sum():,.0f}**")
else:
    st.info("No items in Dead Stock Risk.")

# ----------------- OVER PURCHASED -----------------
over_p_items = filtered_df[filtered_df["Over Purchased Risk"]]
st.subheader("🚨 Over Purchased Risk Items")
if not over_p_items.empty:
    st.dataframe(over_p_items[final_cols], use_container_width=True)
    st.markdown("**Over Purchased Insights**")
    st.markdown(f"- Total Items: **{len(over_p_items)}**")
    st.markdown(f"- Total Stock Value: **{over_p_items['Stock Value'].sum():,.0f}**")
    st.markdown(f"- Total Sales Value: **{over_p_items['Sales Value'].sum():,.0f}**")
else:
    st.info("No items in Over Purchased Risk.")
