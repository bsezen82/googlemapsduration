import streamlit as st
import pandas as pd

st.set_page_config(page_title="Hajj Travel Dashboard", layout="wide")
st.title("⏱️ Hajj Route Travel Durations")

# Load CSV
def load_data():
    df = pd.read_csv("travel_durations.csv")
    df["API Call Time"] = pd.to_datetime(df["API Call Time"])
    return df

df = load_data()

# Filters
with st.sidebar:
    origins = st.multiselect("From", options=sorted(df["Origin Name"].unique()), default=None)
    destinations = st.multiselect("To", options=sorted(df["Destination Name"].unique()), default=None)
    df_filtered = df.copy()
    if origins:
        df_filtered = df_filtered[df_filtered["Origin Name"].isin(origins)]
    if destinations:
        df_filtered = df_filtered[df_filtered["Destination Name"].isin(destinations)]

# Display
st.dataframe(df_filtered)

# Chart
if not df_filtered.empty:
    st.line_chart(
        df_filtered.set_index("API Call Time")[["Travel Duration"]],
        use_container_width=True
    )
