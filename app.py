import streamlit as st
import pandas as pd
import datetime
import altair as alt

st.set_page_config(page_title="Hajj Travel Dashboard", layout="wide")
st.title("🕋 Hajj Travel Durations - Haram Focus")

def load_data():
    df = pd.read_csv("travel_durations.csv")
    df["API Call Time"] = pd.to_datetime(df["API Call Time"])
    df["Date"] = df["API Call Time"].dt.date
    df["Hour"] = df["API Call Time"].dt.strftime("%H:00")

    df["Duration (min)"] = df["Travel Duration"].apply(lambda x: round(float(x) / 60, 1) if pd.notnull(x) else None)
    df["Distance (km)"] = df["Distance"] / 1000
    return df

df = load_data()

# Split coordinates into numeric latitude and longitude
# Assumes no missing values and proper formatting

df[["Origin Lat", "Origin Lng"]] = df["Origin Coords"].str.split(",", expand=True).astype(float)
df[["Destination Lat", "Destination Lng"]] = df["Destination Coords"].str.split(",", expand=True).astype(float)

today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)

df_today = df[df["Date"] == today]
df_yesterday = df[df["Date"] == yesterday]

# FROM HARAM
def prepare_line_data(df_source, label):
    from_haram = df_source[df_source["Origin Name"].str.lower().str.contains("haram")]
    grouped = from_haram.groupby("Hour").apply(
        lambda g: pd.Series({
            "Average Duration (min)": (g["Duration (min)"] * g["Distance (km)"].fillna(0)).sum() / g["Distance (km)"].fillna(0).sum()
        })
    ).reset_index()
    grouped["Day"] = label
    return grouped

from_haram_today = prepare_line_data(df_today, "Today")
from_haram_yesterday = prepare_line_data(df_yesterday, "Yesterday")
from_haram_combined = pd.concat([from_haram_today, from_haram_yesterday])
from_haram_overall = (df_today[df_today["Origin Name"].str.lower().str.contains("haram")]["Duration (min)"] * df_today[df_today["Origin Name"].str.lower().str.contains("haram")]["Distance (km)"].fillna(0)).sum() / df_today[df_today["Origin Name"].str.lower().str.contains("haram")]["Distance (km)"].fillna(0).sum()
from_haram_avg_distance = df_today[df_today["Origin Name"].str.lower().str.contains("haram")]["Distance (km)"].mean()

# TO HARAM
def prepare_line_data_to(df_source, label):
    to_haram = df_source[df_source["Destination Name"].str.lower().str.contains("haram")]
    grouped = to_haram.groupby("Hour").apply(
        lambda g: pd.Series({
            "Average Duration (min)": (g["Duration (min)"] * g["Distance (km)"].fillna(0)).sum() / g["Distance (km)"].fillna(0).sum()
        })
    ).reset_index()
    grouped["Day"] = label
    return grouped

to_haram_today = prepare_line_data_to(df_today, "Today")
to_haram_yesterday = prepare_line_data_to(df_yesterday, "Yesterday")
to_haram_combined = pd.concat([to_haram_today, to_haram_yesterday])
to_haram_overall = (df_today[df_today["Destination Name"].str.lower().str.contains("haram")]["Duration (min)"] * df_today[df_today["Destination Name"].str.lower().str.contains("haram")]["Distance (km)"].fillna(0)).sum() / df_today[df_today["Destination Name"].str.lower().str.contains("haram")]["Distance (km)"].fillna(0).sum()
to_haram_avg_distance = df_today[df_today["Destination Name"].str.lower().str.contains("haram")]["Distance (km)"].mean()

col1, col2 = st.columns(2)

with col1:
    st.subheader(f"⬅️ From Haram (avg. {from_haram_avg_distance:.1f} km)")
    st.metric("Average Duration (min)", f"{from_haram_overall:.1f}" if from_haram_overall else "N/A")
    chart = alt.Chart(from_haram_combined).mark_line(point=True).encode(
        x=alt.X("Hour", sort=list(from_haram_combined["Hour"].unique())),
        y="Average Duration (min)",
        color="Day",
        tooltip=["Hour", "Average Duration (min)", "Day"]
    ).properties(height=300)
    st.altair_chart(chart, use_container_width=True)

with col2:
    st.subheader(f"➡️ To Haram (avg. {to_haram_avg_distance:.1f} km)")
    st.metric("Average Duration (min)", f"{to_haram_overall:.1f}" if to_haram_overall else "N/A")
    chart = alt.Chart(to_haram_combined).mark_line(point=True).encode(
        x=alt.X("Hour", sort=list(to_haram_combined["Hour"].unique())),
        y="Average Duration (min)",
        color="Day",
        tooltip=["Hour", "Average Duration (min)", "Day"]
    ).properties(height=300)
    st.altair_chart(chart, use_container_width=True)

# Route-specific comparison
st.markdown("---")
st.header("📍 Route-Specific Comparison")
route_df = df[df["Date"].isin([today, yesterday])].copy()
from_options = sorted(route_df["Origin Name"].dropna().unique())
selected_from = st.selectbox("Select Origin", from_options, key="route_origin")

filtered_df = route_df[route_df["Origin Name"] == selected_from]
to_options = sorted(filtered_df["Destination Name"].dropna().unique())

selected_to = st.selectbox("Select Destination", to_options, key="route_destination")

filtered = route_df[(route_df["Origin Name"] == selected_from) & (route_df["Destination Name"] == selected_to)]

grouped = filtered.groupby(["Hour", "Date"]).agg({"Duration (min)": "mean"}).reset_index()
grouped["Day"] = grouped["Date"].apply(lambda d: "Today" if d == today else "Yesterday")

route_chart = alt.Chart(grouped).mark_line(point=True).encode(
    x=alt.X("Hour", sort=sorted(grouped["Hour"].unique())),
    y="Duration (min)",
    color="Day",
    tooltip=["Hour", "Duration (min)", "Day"]
).properties(height=300)

st.altair_chart(route_chart, use_container_width=True)

# 🗺️ Route Map Visualization
import folium
from streamlit_folium import st_folium

expected_columns = {"Origin Lat", "Origin Lng", "Destination Lat", "Destination Lng"}
if expected_columns.issubset(filtered.columns):
    sample_row = filtered[(filtered["Origin Name"] == selected_from) & (filtered["Destination Name"] == selected_to)].dropna(subset=["Origin Lat", "Origin Lng", "Destination Lat", "Destination Lng"]).head(1)

    if not sample_row.empty:
        origin_lat = sample_row["Origin Lat"].values[0]
        origin_lng = sample_row["Origin Lng"].values[0]
        dest_lat = sample_row["Destination Lat"].values[0]
        dest_lng = sample_row["Destination Lng"].values[0]

        midpoint = [(origin_lat + dest_lat) / 2, (origin_lng + dest_lng) / 2]

        m = folium.Map(location=midpoint, zoom_start=13)

        folium.Marker([origin_lat, origin_lng], tooltip="Origin", icon=folium.Icon(color='green')).add_to(m)
        folium.Marker([dest_lat, dest_lng], tooltip="Destination", icon=folium.Icon(color='red')).add_to(m)

        st.subheader("🗺️ Selected Points")
        st_folium(m, width=500, height=300)
# Show average distance for the selected route
distance_avg = filtered[(filtered["Origin Name"] == selected_from) & (filtered["Destination Name"] == selected_to)]["Distance (km)"].mean()
if not pd.isna(distance_avg):
    st.write(f"**Average Distance:** {distance_avg:.2f} km")
