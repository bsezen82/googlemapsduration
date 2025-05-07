import streamlit as st
import pandas as pd
import datetime
import altair as alt

st.set_page_config(page_title="Hajj Travel Dashboard", layout="wide")
st.title("🕋 Hajj Travel Durations - Haram Focus")

@st.cache_data
def load_data():
    df = pd.read_csv("travel_durations.csv")
    df["API Call Time"] = pd.to_datetime(df["API Call Time"])
    df["Date"] = df["API Call Time"].dt.date
    df["Hour"] = df["API Call Time"].dt.strftime("%H:00")

    # Duration is in seconds; convert to minutes
    df["Duration (min)"] = df["Travel Duration"].apply(lambda x: round(float(x) / 60, 1) if pd.notnull(x) else None)
    # Distance is in meters; convert to km
    df["Distance (km)"] = df["Distance"] / 1000
    return df

df = load_data()
today = datetime.date.today()
df_today = df[df["Date"] == today]

# FROM HARAM
from_haram = df_today[df_today["Origin Name"].str.lower().str.contains("haram")]
from_haram_avg = from_haram.groupby("Hour")["Duration (min)"].mean().reset_index()
from_haram_overall = from_haram["Duration (min)"].mean()

# TO HARAM
to_haram = df_today[df_today["Destination Name"].str.lower().str.contains("haram")]
to_haram_avg = to_haram.groupby("Hour")["Duration (min)"].mean().reset_index()
to_haram_overall = to_haram["Duration (min)"].mean()

col1, col2 = st.columns(2)

with col1:
    st.subheader("⬅️ From Haram")
    st.metric("Today's Avg Duration (min)", f"{from_haram_overall:.1f}" if from_haram_overall else "N/A")
    chart = alt.Chart(from_haram_avg).mark_line(point=True).encode(
        x=alt.X("Hour", sort=list(from_haram_avg["Hour"])),
        y="Duration (min)",
        tooltip=["Hour", "Duration (min)"]
    ).properties(height=300)
    st.altair_chart(chart, use_container_width=True)

with col2:
    st.subheader("➡️ To Haram")
    st.metric("Today's Avg Duration (min)", f"{to_haram_overall:.1f}" if to_haram_overall else "N/A")
    chart = alt.Chart(to_haram_avg).mark_line(point=True).encode(
        x=alt.X("Hour", sort=list(to_haram_avg["Hour"])),
        y="Duration (min)",
        tooltip=["Hour", "Duration (min)"]
    ).properties(height=300)
    st.altair_chart(chart, use_container_width=True)
