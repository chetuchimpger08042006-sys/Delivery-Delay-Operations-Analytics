import os

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

st.set_page_config(
    page_title="Delivery Delay Operations Dashboard",
    page_icon="📦",
    layout="wide"
)

st.title("Delivery Delay & Operations Analytics")
st.write("Dashboard for analysing delivery performance and operational bottlenecks (Olist dataset).")

FILE_NAMES = {
    "orders": "olist_orders_dataset.csv",
    "items": "olist_order_items_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "customers": "olist_customers_dataset.csv",
}


# -----------------------------
# Helper functions
# -----------------------------
@st.cache_data
def read_csv_file(file_or_path):
    """Read one CSV file (uploaded file or local path)."""
    return pd.read_csv(file_or_path)


@st.cache_data
def prepare_data(orders, order_items, products, sellers, customers):
    """Clean, combine, and create delivery-delay features."""
    orders = orders.copy()  # do not change the cached input

    date_columns = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]
    for column in date_columns:
        orders[column] = pd.to_datetime(orders[column], errors="coerce")

    # Keep delivered orders that have both an actual and an estimated delivery date.
    delivered_orders = orders[
        (orders["order_status"] == "delivered")
        & orders["order_delivered_customer_date"].notna()
        & orders["order_estimated_delivery_date"].notna()
    ].copy()

    # Summarise item-level information at order level.
    items_by_order = order_items.groupby("order_id").agg(
        number_of_items=("order_item_id", "count"),
        total_price=("price", "sum"),
        total_freight=("freight_value", "sum"),
        seller_id=("seller_id", "first"),
        product_id=("product_id", "first"),
    ).reset_index()

    analysis = delivered_orders.merge(items_by_order, on="order_id", how="left")
    analysis = analysis.merge(
        customers[["customer_id", "customer_state", "customer_city"]],
        on="customer_id", how="left",
    )
    analysis = analysis.merge(
        sellers[["seller_id", "seller_state", "seller_city"]],
        on="seller_id", how="left",
    )
    analysis = analysis.merge(
        products[["product_id", "product_category_name"]],
        on="product_id", how="left",
    )

    # Main project features.
    analysis["delay_days"] = (
        analysis["order_delivered_customer_date"]
        - analysis["order_estimated_delivery_date"]
    ).dt.days
    analysis["is_late"] = (analysis["delay_days"] > 0).astype(int)
    analysis["is_on_time"] = (analysis["delay_days"] <= 0).astype(int)
    analysis["delivery_days_from_purchase"] = (
        analysis["order_delivered_customer_date"]
        - analysis["order_purchase_timestamp"]
    ).dt.days

    analysis["purchase_weekday"] = analysis["order_purchase_timestamp"].dt.day_name()
    analysis["purchase_month"] = analysis["order_purchase_timestamp"].dt.month
    analysis["purchase_year"] = analysis["order_purchase_timestamp"].dt.year

    def get_season(month):
        # Brazil is in the southern hemisphere, so the seasons are reversed.
        if month in [12, 1, 2]:
            return "Summer"
        if month in [3, 4, 5]:
            return "Autumn"
        if month in [6, 7, 8]:
            return "Winter"
        return "Spring"

    analysis["season"] = analysis["purchase_month"].apply(get_season)
    analysis["product_category_name"] = analysis["product_category_name"].fillna("Unknown")
    analysis["seller_state"] = analysis["seller_state"].fillna("Unknown")
    analysis["customer_state"] = analysis["customer_state"].fillna("Unknown")
    analysis["route"] = analysis["seller_state"] + " to " + analysis["customer_state"]
    analysis["same_state_route"] = (
        analysis["seller_state"] == analysis["customer_state"]
    ).astype(int)

    return analysis


def group_summary(data, group_column):
    """Return order count, late percentage, and average delay by group."""
    result = data.groupby(group_column).agg(
        orders=("order_id", "count"),
        late_orders=("is_late", "sum"),
        average_delay_days=("delay_days", "mean"),
    ).reset_index()
    result["late_percentage"] = result["late_orders"] / result["orders"] * 100
    result["on_time_percentage"] = 100 - result["late_percentage"]
    return result


# -----------------------------
# Sidebar: data upload
# -----------------------------
st.sidebar.header("1. Data")
st.sidebar.info(
    "Upload the five Olist CSV files, or place them in the same folder as app.py."
)

uploads = {
    key: st.sidebar.file_uploader(f"Upload {name}", type="csv")
    for key, name in FILE_NAMES.items()
}

if all(uploads.values()):
    sources = uploads
else:
    local_files = {key: name for key, name in FILE_NAMES.items() if os.path.exists(name)}
    if len(local_files) == len(FILE_NAMES):
        sources = local_files
        st.sidebar.success("Using the CSV files found in the app folder.")
    else:
        st.warning("Please upload all five required CSV files in the sidebar to start the dashboard.")
        st.markdown("""
        ### Required dataset
        [Brazilian E-Commerce Public Dataset by Olist on Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)

        **Dataset limitation:** Olist does not contain real carrier names, warehouse IDs, or detailed
        delivery-event history. This dashboard uses seller state as the warehouse proxy,
        `seller_id` as a fulfilment proxy and seller state to customer state as the route.
        """)
        st.stop()

try:
    analysis = prepare_data(
        read_csv_file(sources["orders"]),
        read_csv_file(sources["items"]),
        read_csv_file(sources["products"]),
        read_csv_file(sources["sellers"]),
        read_csv_file(sources["customers"]),
    )
except Exception as error:
    st.error("The files could not be processed. Check that you uploaded the correct Olist CSV files.")
    st.exception(error)
    st.stop()

# -----------------------------
# Sidebar: filters
# -----------------------------
st.sidebar.header("2. Filters")

year_options = sorted(analysis["purchase_year"].dropna().unique().tolist())
selected_years = st.sidebar.multiselect("Purchase year", options=year_options, default=year_options)

season_options = sorted(analysis["season"].dropna().unique().tolist())
selected_seasons = st.sidebar.multiselect("Season", options=season_options, default=season_options)

state_options = sorted(analysis["customer_state"].dropna().unique().tolist())
selected_customer_states = st.sidebar.multiselect(
    "Customer state", options=state_options, default=state_options
)

filtered_data = analysis[
    analysis["purchase_year"].isin(selected_years)
    & analysis["season"].isin(selected_seasons)
    & analysis["customer_state"].isin(selected_customer_states)
].copy()

if filtered_data.empty:
    st.error("No rows match the selected filters. Please select more values.")
    st.stop()

st.sidebar.success(f"Showing {len(filtered_data):,} delivered orders")

# -----------------------------
# KPI cards
# -----------------------------
st.header("Delivery Performance Overview")

late_orders_only = filtered_data[filtered_data["is_late"] == 1]
average_late_delay = late_orders_only["delay_days"].mean() if len(late_orders_only) > 0 else 0

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
kpi1.metric("Delivered orders", f"{len(filtered_data):,}")
kpi2.metric("On-time %", f"{filtered_data['is_on_time'].mean() * 100:.2f}%")
kpi3.metric("Late %", f"{filtered_data['is_late'].mean() * 100:.2f}%")
kpi4.metric("Avg delay of late orders", f"{average_late_delay:.1f} days")
kpi5.metric("Avg delivery time", f"{filtered_data['delivery_days_from_purchase'].mean():.1f} days")

st.caption(
    "A delivery is late when it arrives after the estimated date. "
    "On average, orders arrive "
    f"{abs(filtered_data['delay_days'].mean()):.1f} days "
    f"{'before' if filtered_data['delay_days'].mean() < 0 else 'after'} the estimated date."
)

# -----------------------------
# Delay distribution
# -----------------------------
st.header("Delay Distribution")

fig, ax = plt.subplots(figsize=(12, 4))
sns.histplot(data=filtered_data, x="delay_days", bins=40, kde=True, ax=ax)
ax.axvline(0, color="red", linestyle="--", label="Estimated delivery date")
ax.set_title("Delivery Delay Distribution")
ax.set_xlabel("Delay days: positive = late, negative = early")
ax.set_ylabel("Number of orders")
ax.legend()
st.pyplot(fig)
plt.close(fig)

# -----------------------------
# Trend chart and spikes
# -----------------------------
st.header("Monthly Delivery Trend and Spikes")

monthly_summary = filtered_data.groupby(["purchase_year", "purchase_month"]).agg(
    orders=("order_id", "count"),
    late_percentage=("is_late", "mean"),
    average_delay_days=("delay_days", "mean"),
).reset_index()
monthly_summary["late_percentage"] = monthly_summary["late_percentage"] * 100
monthly_summary["month"] = (
    monthly_summary["purchase_year"].astype(str)
    + "-"
    + monthly_summary["purchase_month"].astype(str).str.zfill(2)
)

# Months with very few orders create fake spikes, so they are excluded.
reliable_months = monthly_summary[monthly_summary["orders"] >= 100]

if reliable_months.empty:
    st.info("Not enough orders per month to show a trend. Select more data.")
else:
    st.line_chart(
        reliable_months.set_index("month")["late_percentage"],
        y_label="Late percentage",
        x_label="Purchase month",
    )

    if len(reliable_months) >= 3:
        spike_limit = (
            reliable_months["late_percentage"].mean()
            + 1.5 * reliable_months["late_percentage"].std()
        )
        spikes = reliable_months[reliable_months["late_percentage"] > spike_limit]
        st.caption(
            f"Unusual months = late % above mean + 1.5 standard deviations ({spike_limit:.1f}%). "
            "Months with fewer than 100 orders are excluded."
        )
        if spikes.empty:
            st.info("No unusual spike months in the selected data.")
        else:
            st.dataframe(
                spikes[["month", "orders", "late_percentage", "average_delay_days"]],
                hide_index=True,
                column_config={
                    "late_percentage": st.column_config.NumberColumn("Late %", format="%.2f"),
                    "average_delay_days": st.column_config.NumberColumn("Avg delay days", format="%.2f"),
                },
            )

# -----------------------------
# Hotspot analysis
# -----------------------------
st.header("Operational Hotspots")

column_map = {
    "Route": "route",
    "Warehouse proxy (seller state)": "seller_state",
    "Seller (fulfilment proxy)": "seller_id",
    "Product category": "product_category_name",
    "Customer state": "customer_state",
    "Purchase weekday": "purchase_weekday",
    "Season": "season",
}

hotspot_type = st.selectbox("Choose a dimension to investigate", options=list(column_map.keys()))
selected_column = column_map[hotspot_type]

minimum_orders = st.slider(
    "Minimum orders required for a group to be shown",
    min_value=1, max_value=500, value=50, step=1,
)

hotspot_table = group_summary(filtered_data, selected_column)
hotspot_table = hotspot_table[hotspot_table["orders"] >= minimum_orders]
hotspot_table = hotspot_table.sort_values("late_percentage", ascending=False)

if hotspot_table.empty:
    st.info("No groups meet the selected minimum order count.")
else:
    left, right = st.columns([1, 1])
    with left:
        st.dataframe(
            hotspot_table.head(15),
            hide_index=True,
            column_config={
                "late_percentage": st.column_config.NumberColumn("Late %", format="%.2f"),
                "on_time_percentage": st.column_config.NumberColumn("On-time %", format="%.2f"),
                "average_delay_days": st.column_config.NumberColumn("Avg delay days", format="%.2f"),
            },
        )
    with right:
        chart_data = hotspot_table.head(10).sort_values("late_percentage")
        st.bar_chart(
            chart_data.set_index(selected_column)["late_percentage"],
            y_label="Late percentage",
            x_label=hotspot_type,
        )

# -----------------------------
# High-delay combinations (heatmap)
# -----------------------------
st.subheader("High-Delay Combinations: Warehouse State x Customer State")

combo_min = st.slider("Minimum orders per combination", 10, 300, 50, step=10, key="combo_min")
combo = filtered_data.groupby(["seller_state", "customer_state"]).agg(
    orders=("order_id", "count"),
    late_percentage=("is_late", "mean"),
).reset_index()
combo["late_percentage"] = combo["late_percentage"] * 100
combo = combo[combo["orders"] >= combo_min]

if combo.empty:
    st.info("No combinations meet the minimum order count.")
else:
    heatmap_data = combo.pivot(index="seller_state", columns="customer_state", values="late_percentage")
    fig, ax = plt.subplots(figsize=(12, 5))
    sns.heatmap(heatmap_data, cmap="Reds", annot=True, fmt=".0f", linewidths=0.5, ax=ax,
                cbar_kws={"label": "Late %"})
    ax.set_xlabel("Customer state")
    ax.set_ylabel("Seller state (warehouse proxy)")
    st.pyplot(fig)
    plt.close(fig)

# -----------------------------
# Recommendations
# -----------------------------
st.header("Prioritized Recommendations")

route_summary = group_summary(filtered_data, "route")
route_summary = route_summary[route_summary["orders"] >= 100]
route_summary = route_summary.sort_values("late_percentage", ascending=False).head(10)

if route_summary.empty:
    st.info("Select more data to produce reliable route recommendations (routes need 100+ orders).")
else:
    recommendations = route_summary[["route", "orders", "late_percentage", "average_delay_days"]].copy()

    def assign_priority(late_percentage):
        if late_percentage >= 20:
            return "High"
        if late_percentage >= 15:
            return "Medium"
        return "Low"

    recommendations["priority"] = recommendations["late_percentage"].apply(assign_priority)
    recommendations["recommended_action"] = recommendations["priority"].map({
        "High": "Add a delivery-date buffer and review seller handoff and transport plan",
        "Medium": "Monitor weekly and investigate recurring delays",
        "Low": "Keep monitoring as a comparison group",
    })

    st.dataframe(
        recommendations,
        hide_index=True,
        column_config={
            "late_percentage": st.column_config.NumberColumn("Late %", format="%.2f"),
            "average_delay_days": st.column_config.NumberColumn("Avg delay days", format="%.2f"),
        },
    )

# -----------------------------
# Delay-risk model
# -----------------------------
st.header("Delay-Risk Model")
st.write(
    "A simple decision tree using only information available before delivery. "
    "Classes are balanced because late orders are rare, so overall accuracy is misleading: "
    "check recall and precision for late orders (class 1)."
)

run_model = st.checkbox("Run decision-tree model")

if run_model:
    try:
        from sklearn.model_selection import train_test_split
        from sklearn.tree import DecisionTreeClassifier
        from sklearn.metrics import classification_report, confusion_matrix

        model_data = filtered_data[[
            "is_late", "seller_state", "customer_state", "product_category_name",
            "purchase_weekday", "purchase_month", "number_of_items",
            "total_price", "total_freight", "same_state_route",
        ]].copy()

        for column in ["number_of_items", "total_price", "total_freight"]:
            model_data[column] = model_data[column].fillna(model_data[column].median())

        text_columns = ["seller_state", "customer_state", "product_category_name", "purchase_weekday"]
        for column in text_columns:
            model_data[column] = model_data[column].fillna("Unknown")

        model_data = pd.get_dummies(model_data, columns=text_columns, drop_first=True)

        X = model_data.drop("is_late", axis=1)
        y = model_data["is_late"]

        if y.value_counts().min() < 10:
            st.warning("Too few late (or on-time) orders in the selected data to train a model. Select more data.")
        else:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )

            model = DecisionTreeClassifier(
                max_depth=5, class_weight="balanced", min_samples_leaf=50, random_state=42
            )
            model.fit(X_train, y_train)
            predictions = model.predict(X_test)

            report = classification_report(y_test, predictions, output_dict=True, zero_division=0)
            m1, m2, m3 = st.columns(3)
            m1.metric("Recall (late orders)", f"{report['1']['recall']:.2f}")
            m2.metric("Precision (late orders)", f"{report['1']['precision']:.2f}")
            m3.metric("Overall accuracy", f"{report['accuracy']:.2f}")

            st.text("Classification report")
            st.text(classification_report(y_test, predictions, zero_division=0))
            st.text("Confusion matrix (rows = actual, columns = predicted)")
            st.text(str(confusion_matrix(y_test, predictions)))

            feature_importance = pd.DataFrame({
                "feature": X.columns,
                "importance": model.feature_importances_,
            }).sort_values("importance", ascending=False).head(10)

            st.subheader("Most important model features")
            st.dataframe(feature_importance, hide_index=True)

    except Exception as error:
        st.error("The model could not run. Try selecting more data or check the uploaded files.")
        st.exception(error)

# -----------------------------
# Download filtered data
# -----------------------------
st.header("Download Filtered Data")

st.download_button(
    label="Download filtered analytical data as CSV",
    data=filtered_data.to_csv(index=False).encode("utf-8"),
    file_name="filtered_delivery_delay_analysis.csv",
    mime="text/csv",
)

st.divider()
st.caption("Olist dataset limitation: no true carrier, warehouse ID or delivery-event data; seller and route fields are proxies.")
