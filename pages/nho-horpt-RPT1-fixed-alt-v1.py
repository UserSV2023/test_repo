import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="HORPT1: Unique Session Check-ins", layout="wide")
st.title("📊 HO Number of Unique Check-in Sessions (HORPT1)")

# Check login
if not st.session_state.get("authenticated", False):
    st.warning("Please log in first from the main page.")
    st.stop()

email = st.session_state["user_email"]
role = st.session_state["user_role"]
st.write(f"**You are logged in under {email} as {role}**")

# Load and prep data
df = pd.read_excel("NHO-check-in-chart.xlsx", sheet_name="00-HO-Data-Prime-no-link")

# Convert Timestamp to datetime
df["Timestamp"] = pd.to_datetime(df["Timestamp"])

# Filter by user
if role != "admin":
    df = df[df["User email"] == email]

# Sidebar filters
st.sidebar.header("📅 Filter by Date Range")
start_date = st.sidebar.date_input("Start Date", value=df["Timestamp"].min())
end_date = st.sidebar.date_input("End Date", value=df["Timestamp"].max())

# Apply date filter
mask = (df["Timestamp"] >= pd.to_datetime(start_date)) & (df["Timestamp"] <= pd.to_datetime(end_date))
filtered = df[mask]

st.subheader("Filtered Data")
st.dataframe(filtered)

# Total unique session count
total_unique_sessions = filtered["Session id"].nunique()
st.metric(label="Total Unique Sessions", value=total_unique_sessions)

# ✅ DAILY CHART (Altair version, smaller chart with integer ticks)
st.markdown("### 📆 Unique Sessions by Day (Compact View)")
daily_df = (
    filtered.groupby(filtered["Timestamp"].dt.date)["Session id"]
    .nunique()
    .reset_index()
    .rename(columns={"Timestamp": "Date", "Session id": "Unique Sessions"})
)

daily_chart = alt.Chart(daily_df).mark_bar().encode(
    x=alt.X("Date:T", title="Date"),
    y=alt.Y("Unique Sessions:Q", 
            axis=alt.Axis(
              title="Sessions", 
              tickMinStep=1,  # Ensure ticks are at least 1 unit apart
              format="i" # Format as integers (no decimal places) 
            ))
).properties(
    width=400,
    height=250
)

st.altair_chart(daily_chart, use_container_width=False)

# Weekly chart
st.markdown("### 📆 Unique Sessions by Week")
weekly = filtered.resample("W", on="Timestamp")["Session id"].nunique()
st.bar_chart(
    weekly, 
    width=400,  # Set the width in pixels 
    height=200, # Set the height in pixels
    use_container_width=False # Ensure width and height are respected
)
# repeat sizing for the following chart
# Monthly chart
st.markdown("### 📆 Unique Sessions by Month")
monthly = filtered.resample("ME", on="Timestamp")["Session id"].nunique()
st.bar_chart(
    monthly,
    width=400,  # Set the width in pixels 
    height=200, # Set the height in pixels
    use_container_width=False # Ensure width and height are respected
)

# Yearly chart
st.markdown("### 📆 Unique Sessions by Year")
yearly = filtered.resample("YE", on="Timestamp")["Session id"].nunique()
st.bar_chart(
    yearly,
    width=400,  # Set the width in pixels 
    height=200, # Set the height in pixels
    use_container_width=False # Ensure width and height are respected
)
