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

    # Parse duration in minutes
    def parse_duration(d):
        try:
            d = d.lower().replace("mins", "min")
            parts = d.split()
            m = 0
            for i, p in enumerate(parts):
                if p in ["hour", "hours"]:
                    m += int(parts[i-1]) * 60
                elif p == "min":
                    m += int(parts[i-1])
            return m
        except:
            return None

    df["Duration (min)"] = df["Travel Duration"].apply(parse_duration)
    df["Distance (km)"] = df["Distance"].str.replace("km", "").str.strip().astype(float)
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
