import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import plotly.io as pio

# import plotly.graph_objects as go
pio.templates.default = "plotly"

st.set_page_config(page_title="Journal RPT: Journal Reportss", layout="wide")
st.title("📊 Journal Reports (Journal RPT)")

# Check login
if not st.session_state.get("authenticated", False):
    st.warning("Please log in first from the main page.")
    st.stop()

email = st.session_state["user_email"]
role = st.session_state["user_role"]
st.write(f"**You are logged in under {email} as {role}**")

# Load data
df = pd.read_excel("NC-Journal-Data.xlsx", sheet_name="Journal-Data-wo-link", header=1)
df["Timestamp"] = pd.to_datetime(df["Timestamp"])

# Filter by user
if role != "admin":
    df = df[df["User email"] == email]

# Sidebar filters
st.sidebar.header("📅 Filter Options")
start_date = st.sidebar.date_input("Start Date", value=df["Timestamp"].min())
end_date = st.sidebar.date_input("End Date", value=df["Timestamp"].max())
# User input for Top N places
# fil_places = df["n_place"].dropna().unique() # if more than xx, perhaps just ask for input
# top_n = st.sidebar.slider("Select Top N Places", min_value=1, max_value=10, value=5)

# if admin, ask email filtering
if role == "admin":
    fil_emails = df["User email"].dropna().unique() # if more than xx, perhaps just ask for input
    selected_emails = st.sidebar.multiselect("🎯 Select up to 3 emails", fil_emails, max_selections=3)
#   selected_emails = st.text_input("Enter user email to filter:").strip().lower()
else:
    selected_emails = ""

# indicators = df["Indicator"].dropna().unique()
# selected_indicators = st.sidebar.multiselect("🎯 Select up to 3 Indicators", indicators, max_selections=3)

# Apply filters
mask = (df["Timestamp"] >= pd.to_datetime(start_date)) & (df["Timestamp"] <= pd.to_datetime(end_date))
#if selected_indicators:
#    mask &= df["Indicator"].isin(selected_indicators)
if selected_emails:
    mask &= df["User email"].isin(selected_emails)

filtered = df[mask]

if filtered.empty:
    st.warning("No data found for the selected filters.")
    st.stop()

# Altair bar chart for average rating

# filtered_df = df[df['Indicator'].isin(selected_indicators)]

# Group data and create the line chart
if filtered.empty:  # Ensure data is not empty before plotting
     st.warning("No record to show, pls try again.")
     st.stop()

# Total unique session count
total_unique_places = filtered["n_Place"].nunique()
st.metric(label="Total Unique Places: ", value=total_unique_places)

# User input for Top N places
if total_unique_places > 10:
  max_fil_places = 10 # if more than xx, perhaps just ask for input
else:
  max_fil_places = total_unique_places

top_n = st.sidebar.slider("Select Top N Places", min_value=1, max_value=max_fil_places, value=5)
# top_places = grouped_data.groupby('n_Place')['n_Duration'].sum().nlargest(num_top_places).index.tolist()
# top_df = grouped_data[grouped_data['n_Place'].isin(top_places)]

# Total sum of Time spent in Nature
total_minutes = filtered["n_Duration"].sum()
hours = total_minutes // 60
minutes = total_minutes % 60
st.metric("Total Time in Nature: ", f"{hours}h {minutes}m")

# Group by 'Date' and 'Place' and count occurrences
# if admin -- i think we need to group by email, date, n_place
grouped_data = filtered.groupby([filtered['Timestamp'].dt.date, 'n_Place']).agg(
    Count=('n_Place', 'size'),
    Unique_places=('n_Place', 'unique'),
    SumMin=('n_Duration', 'sum'),
    Latitude=('n_Lati', 'mean'),
    Longitude=('n_Long', 'mean')
).reset_index().sort_values('SumMin', ascending=False).rename(columns={'Timestamp': 'Date'})

# Group by Date and Indicator and aggregate rating
    
st.subheader("Aggregated Counts of Nature Places I visited")
st.dataframe(grouped_data)

st.subheader(" 📆 RPT1: How much time (in minutes) & where did I spend in Nature?")
# Create columns
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

# Stack Bar Chart in the first column
with col1:
# st.subheader(" 📆 StackBar Chart: ")
  chart1 = px.bar(grouped_data, 
    x='Date',
    y='Count',
    color='n_Place',  # Color by place
    title='Count of Places by Date'
   )
 
 # Update the layout to make the legend font size smaller
  chart1.update_layout(
    legend=dict(
        itemwidth=30,  # Adjust the width of individual legend items
        font=dict(size=8) # Adjust the font size of legend items
    )
  )
 
# Display the chart
  # st.write("Count of Places by Date")
  st.plotly_chart(chart1, use_container_width=True)

# Map plot in the second column
with col2:
      # st.subheader("📆 Map: ")
  st.write("Location Map:")
  st.map(grouped_data, latitude='Latitude', longitude='Longitude') 

with col3:
# st.subheader(" 📆 StackBar Chart: ")
  chart2 = px.bar(grouped_data, 
    x='Date',
    y='SumMin',
    color='n_Place',  # Color by place
    title='Total Nature Time by Date'
   )
 
 # Update the layout to make the legend font size smaller
  chart2.update_layout(
    legend=dict(
        itemwidth=30,  # Adjust the width of individual legend items
        font=dict(size=8) # Adjust the font size of legend items
    )
  )
  # Display the chart
  # st.write("Sum of Nature Time by Date")
  st.plotly_chart(chart2, use_container_width=True)

with col4:
    # Get top N places
    # top_places = grouped_data.sort_values(by='SumMin', ascending=False).head(top_n)
    display_top_n = grouped_data.nlargest(top_n, "SumMin")
    st.write(" \n     ")
    # st.write("Content for Row 2, Column 2 TBD")
    st.write(f"**Top {top_n} Places Visited in Selected Date**")
    # st.dataframe(top_places)
    # df = pd.DataFrame(top_places)

    # Create the pie chart
    chart4 = px.pie(display_top_n, values='SumMin', names='Unique_places')
    # Display the pie chart in Streamlit
    chart4.update_layout(
      legend=dict(
        itemwidth=30,  # Adjust the width of individual legend items
        font=dict(size=8) # Adjust the font size of legend items
      )
    )
    chart4.update_traces(textinfo='value+percent', textposition='outside', insidetextorientation='radial')
    st.plotly_chart(chart4, use_container_width=True)
    # st.write("      ")
    # st.write("Content for Row 2, Column 2 TBD")

# save original code 
# chart = alt.Chart(summary).mark_bar().encode(
#    x=alt.X("Indicator:N", sort="-y", title="Indicator"),
#    y=alt.Y("Avg:Q", title="Average Rating"),
#    tooltip=["Indicator", "Avg", "Min", "Max", "Ratings"]
# ).properties(
#    width=500,
#    height=300
#)

# st.altair_chart(chart, use_container_width=True)
# NOTE:
# for admin we need by username
# df = pd.DataFrame(data)
# df['date'] = pd.to_datetime(df['date'])  # Convert to datetime objects

# Determine user type (replace with your logic)
# is_admin = True  # Set to False for regular user

# Group and sort conditionally
# if is_admin:
#    grouped_data = df.groupby(['username', 'date', 'n_Place'])
# else:
#    grouped_data = df.groupby(['date', 'n_Place'])

# You can then perform aggregations if needed
# For example, to get the sum of 'n_Duration' for each group:
# aggregated_data = grouped_data['n_Duration'].sum()

# Reset index to display the grouped columns in the dataframe
# aggregated_data = aggregated_data.reset_index()

# Display the sorted data
# st.write("Aggregated Data (Sorted):")
# st.dataframe(aggregated_data)