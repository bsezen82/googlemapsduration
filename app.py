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
df_today = df[df["Date"] == today]

# FROM HARAM
from_haram = df_today[df_today["Origin Name"].str.lower().str.contains("haram")]
from_haram_grouped = from_haram.groupby("Hour").apply(
    lambda g: pd.Series({
        "Average Duration (min)": (g["Duration (min)"] * g["Distance (km)"].fillna(0)).sum() / g["Distance (km)"].fillna(0).sum()
    })
).reset_index()
from_haram_overall_duration = (from_haram["Duration (min)"] * from_haram["Distance (km)"].fillna(0)).sum() / from_haram["Distance (km)"].fillna(0).sum()
from_haram_avg_distance = from_haram["Distance (km)"].mean()

# TO HARAM
to_haram = df_today[df_today["Destination Name"].str.lower().str.contains("haram")]
to_haram_grouped = to_haram.groupby("Hour").apply(
    lambda g: pd.Series({
        "Average Duration (min)": (g["Duration (min)"] * g["Distance (km)"].fillna(0)).sum() / g["Distance (km)"].fillna(0).sum()
    })
).reset_index()
to_haram_overall_duration = (to_haram["Duration (min)"] * to_haram["Distance (km)"].fillna(0)).sum() / to_haram["Distance (km)"].fillna(0).sum()
to_haram_avg_distance = to_haram["Distance (km)"].mean()

col1, col2 = st.columns(2)

with col1:
    st.subheader(f"⬅️ From Haram (avg. {from_haram_avg_distance:.1f} km)")
    st.metric("Average Duration (min)", f"{from_haram_overall_duration:.1f}" if from_haram_overall_duration else "N/A")
    chart = alt.Chart(from_haram_grouped).mark_line(point=True).encode(
        x=alt.X("Hour", sort=list(from_haram_grouped["Hour"])),
        y="Average Duration (min)",
        tooltip=["Hour", "Average Duration (min)"]
    ).properties(height=300)
    st.altair_chart(chart, use_container_width=True)

with col2:
    st.subheader(f"➡️ To Haram (avg. {to_haram_avg_distance:.1f} km)")
    st.metric("Average Duration (min)", f"{to_haram_overall_duration:.1f}" if to_haram_overall_duration else "N/A")
    chart = alt.Chart(to_haram_grouped).mark_line(point=True).encode(
        x=alt.X("Hour", sort=list(to_haram_grouped["Hour"])),
        y="Average Duration (min)",
        tooltip=["Hour", "Average Duration (min)"]
    ).properties(height=300)
    st.altair_chart(chart, use_container_width=True)
