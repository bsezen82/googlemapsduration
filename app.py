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
today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)

# ROTAYA GÖRE FİLTRELEME
unique_from = df["Origin Name"].dropna().unique()
unique_to = df["Destination Name"].dropna().unique()

col_from, col_to = st.columns(2)
with col_from:
    selected_from = st.selectbox("Select From Location", sorted(unique_from))
with col_to:
    selected_to = st.selectbox("Select To Location", sorted(unique_to))

# Filtrelenmiş veri (Today ve Yesterday)
df_today = df[(df["Date"] == today) & (df["Origin Name"] == selected_from) & (df["Destination Name"] == selected_to)]
df_yesterday = df[(df["Date"] == yesterday) & (df["Origin Name"] == selected_from) & (df["Destination Name"] == selected_to)]

# Saatlik ortalamaları hesapla
def hourly_weighted(df_part, label):
    grouped = df_part.groupby("Hour").apply(
        lambda g: pd.Series({
            "Average Duration (min)": (g["Duration (min)"] * g["Distance (km)"].fillna(0)).sum() / g["Distance (km)"].fillna(0).sum()
        })
    ).reset_index()
    grouped["Day"] = label
    return grouped

hourly_today = hourly_weighted(df_today, "Today")
hourly_yesterday = hourly_weighted(df_yesterday, "Yesterday")
hourly_combined = pd.concat([hourly_today, hourly_yesterday])

st.subheader(f"📈 Duration Trend for Route: {selected_from} → {selected_to}")
route_chart = alt.Chart(hourly_combined).mark_line(point=True).encode(
    x=alt.X("Hour", sort=list(hourly_combined["Hour"].unique())),
    y="Average Duration (min)",
    color="Day",
    tooltip=["Hour", "Average Duration (min)", "Day"]
).properties(height=350)
st.altair_chart(route_chart, use_container_width=True)
