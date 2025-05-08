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

    # 7-day trend for From Haram
    recent_from = df[df["Origin Name"].str.lower().str.contains("haram")]
    recent_from_grouped = recent_from.groupby("Date").apply(
        lambda g: (g["Duration (min)"] * g["Distance (km)"].fillna(0)).sum() / g["Distance (km)"].fillna(0).sum()
    ).reset_index(name="Average Duration (min)")
    recent_from_grouped = recent_from_grouped[recent_from_grouped["Date"] >= today - datetime.timedelta(days=6)]
    st.subheader("📈 7-Day Trend (From Haram)")
    trend_chart = alt.Chart(recent_from_grouped).mark_line(point=True).encode(
        x=alt.X("Date:T"),
        y="Average Duration (min)",
        tooltip=["Date", "Average Duration (min)"]
    ).properties(height=300)
    st.altair_chart(trend_chart, use_container_width=True)

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

    # 7-day trend for To Haram
    recent_to = df[df["Destination Name"].str.lower().str.contains("haram")]
    recent_to_grouped = recent_to.groupby("Date").apply(
        lambda g: (g["Duration (min)"] * g["Distance (km)"].fillna(0)).sum() / g["Distance (km)"].fillna(0).sum()
    ).reset_index(name="Average Duration (min)")
    recent_to_grouped = recent_to_grouped[recent_to_grouped["Date"] >= today - datetime.timedelta(days=6)]
    st.subheader("📈 7-Day Trend (To Haram)")
    trend_chart = alt.Chart(recent_to_grouped).mark_line(point=True).encode(
        x=alt.X("Date:T"),
        y="Average Duration (min)",
        tooltip=["Date", "Average Duration (min)"]
    ).properties(height=300)
    st.altair_chart(trend_chart, use_container_width=True)
