import streamlit as st
import pandas as pd
import datetime
import altair as alt
from datetime import timedelta
import datetime

st.set_page_config(page_title="Hajj Dashboard", layout="wide")
st.sidebar.title("📊 Dashboard Navigation")
page = st.sidebar.radio("Sayfa Seç", ["Traffic Trends", "Review Trends"])

# === PAGE 1: TRAFFIC TRENDS ===
if page == "Traffic Trends":
    st.title("🕋 Hajj Period - Makkah Traffic Report")
    
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
        st.subheader(f"⬅️ From Masjid al-Haram (avg. {from_haram_avg_distance:.1f} km)")
        st.caption("(Includes routes to: Al Aziziyah, Al Andulus, Al Diyafah, Al Rusayfah, Kudai))")
        st.metric("Average Duration (min)", f"{from_haram_overall:.1f}" if from_haram_overall else "N/A")
        chart = alt.Chart(from_haram_combined).mark_line(point=True).encode(
            x=alt.X("Hour", sort=list(from_haram_combined["Hour"].unique())),
            y="Average Duration (min)",
            color="Day",
            tooltip=["Hour", "Average Duration (min)", "Day"]
        ).properties(height=300)
        st.altair_chart(chart, use_container_width=True)

        df_bar = df.copy()
        df_bar["Date"] = pd.to_datetime(df_bar["Date"]).dt.strftime("%Y-%m-%d")
        from_haram_daily = df_bar[df_bar["Origin Name"].str.lower().str.contains("haram")] \
            .groupby("Date")["Duration (min)"].mean().reset_index(name="Average Duration (min)")

        bar_chart_from = alt.Chart(from_haram_daily).mark_line(point=True).encode(
            x=alt.X("Date:O", title="Date"),
            y=alt.Y("Average Duration (min)", title="Avg Duration (min)"),
            tooltip=["Date", "Average Duration (min)"]
        ).properties(title="📊 From Masjid al-Haram - Daily Average Duration", height=400)

        st.altair_chart(bar_chart_from, use_container_width=True)

    with col2:
        st.subheader(f"➡️ To Masjid al-Haram (avg. {to_haram_avg_distance:.1f} km)")
        st.caption("(Includes routes from: Al Aziziyah, Al Andulus, Al Diyafah, Al Rusayfah, Kudai)")
        st.metric("Average Duration (min)", f"{to_haram_overall:.1f}" if to_haram_overall else "N/A")
        chart = alt.Chart(to_haram_combined).mark_line(point=True).encode(
            x=alt.X("Hour", sort=list(to_haram_combined["Hour"].unique())),
            y="Average Duration (min)",
            color="Day",
            tooltip=["Hour", "Average Duration (min)", "Day"]
        ).properties(height=300)
        st.altair_chart(chart, use_container_width=True)

        df_bar = df.copy()
        df_bar["Date"] = pd.to_datetime(df_bar["Date"]).dt.strftime("%Y-%m-%d")
        to_haram_daily = df_bar[df_bar["Destination Name"].str.lower().str.contains("haram")] \
            .groupby("Date")["Duration (min)"].mean().reset_index(name="Average Duration (min)")

        bar_chart_to = alt.Chart(to_haram_daily).mark_line(point=True).encode(
            x=alt.X("Date:O", title="Date"),
            y=alt.Y("Average Duration (min)", title="Avg Duration (min)"),
            tooltip=["Date", "Average Duration (min)"]
        ).properties(title="📊 To Masjid al-Haram - Daily Average Duration", height=400)

        st.altair_chart(bar_chart_to, use_container_width=True)
    
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
    ).properties(height=400)
    
    st.altair_chart(route_chart, use_container_width=True)
    
    # 🛣 Real road route (OSRM)
    import folium
    from streamlit_folium import st_folium
    import requests
    
    # 🗺️ Map View with route and OSRM polyline
    def draw_osrm_route_map(origin_lat, origin_lng, dest_lat, dest_lng):
        try:
            url = f"http://router.project-osrm.org/route/v1/driving/{origin_lng},{origin_lat};{dest_lng},{dest_lat}?overview=full&geometries=geojson"
            response = requests.get(url)
            route_data = response.json()
    
            if not route_data.get("routes"):
                st.warning("No OSRM route found.")
                return
    
            coords = route_data["routes"][0]["geometry"]["coordinates"]
            coords_latlng = [(lat, lng) for lng, lat in coords]
    
            midpoint = [(origin_lat + dest_lat) / 2, (origin_lng + dest_lng) / 2]
            m = folium.Map(location=midpoint, zoom_start=13)
    
            folium.Marker([origin_lat, origin_lng], tooltip="Origin", icon=folium.Icon(color='green')).add_to(m)
            folium.Marker([dest_lat, dest_lng], tooltip="Destination", icon=folium.Icon(color='red')).add_to(m)
            folium.PolyLine(locations=coords_latlng, color="purple", weight=5, tooltip="OSRM Route").add_to(m)
    
            st.subheader("🚣 Route Map")
            st_folium(m, width=500, height=300)
    
        except Exception as e:
            st.warning(f"OSRM route could not be displayed: {e}")
    
    sample_row = filtered.dropna(subset=["Origin Lat", "Origin Lng", "Destination Lat", "Destination Lng"]).head(1)
    if not sample_row.empty:
        origin_lat = sample_row["Origin Lat"].values[0]
        origin_lng = sample_row["Origin Lng"].values[0]
        dest_lat = sample_row["Destination Lat"].values[0]
        dest_lng = sample_row["Destination Lng"].values[0]
        draw_osrm_route_map(origin_lat, origin_lng, dest_lat, dest_lng)


# === PAGE 2: REVIEW TRENDS ===
elif page == "Review Trends":
    st.title("📅 Hajj Period - Google Review Trends")

    df = pd.read_csv("Makkah_Hajj_Reviews_Apify.csv", parse_dates=["publishedAtDate"])
    df["date"] = pd.to_datetime(df["publishedAtDate"], errors="coerce").dt.date
    df = df[pd.notnull(df["date"])]

    today = datetime.date.today()
    yesterday = today - timedelta(days=1)
    day_before = today - timedelta(days=2)

    df_yesterday = df[df["date"] == yesterday]
    df_day_before = df[df["date"] == day_before]

    mean_all = df["stars"].mean()
    mean_yesterday = df_yesterday["stars"].mean()
    mean_day_before = df_day_before["stars"].mean()

    count_all = len(df)
    count_yesterday = len(df_yesterday)
    count_day_before = len(df_day_before)

    def display_metrics_block(title, df, yesterday, day_before, category=None):
        if category:
            df = df[df["category"] == category]
    
        st.subheader(title)
    
        # Ratings
        col1, col2, col3 = st.columns(3)
        col1.metric("Avg Rating (Yesterday)", f"{df[df['date'] == yesterday]['stars'].mean():.2f}" if not df[df['date'] == yesterday].empty else "—")
        col2.metric("Avg Rating (Previous Day)", f"{df[df['date'] == day_before]['stars'].mean():.2f}" if not df[df['date'] == day_before].empty else "—")
        col3.metric("Avg Rating (Overall)", f"{df['stars'].mean():.2f}" if not df.empty else "—")
    
        # Review counts
        col4, col5, col6 = st.columns(3)
        col4.metric("Review Count (Yesterday)", len(df[df["date"] == yesterday]))
        col5.metric("Review Count (Previous Day)", len(df[df["date"] == day_before]))
        col6.metric("Review Count (Overall)", len(df))

    # 1️⃣ OVERALL
    display_metrics_block("⭐ Overall", df, yesterday, day_before)

    # 2️⃣ CATEGORY-WISE
    for cat in ["Cafes & Restaurants", "Hotels", "Masjid al-Haram", "Mosques & Religious Places"]:
        display_metrics_block(f"🏷 {cat}", df, yesterday, day_before, category=cat)

    # 3️⃣ Filtered Trend Chart
    st.markdown("---")
    st.subheader("📈 Daily Average Rating Trend")

    category_options = ["All"] + sorted(df["category"].dropna().unique())
    selected_category = st.selectbox("Filter by Category", category_options)

    if selected_category != "All":
        df_filtered = df[df["category"] == selected_category]
    else:
        df_filtered = df

    daily_avg = df_filtered.groupby("date")["stars"].mean().reset_index()

    chart = alt.Chart(daily_avg).mark_line(point=True).encode(
        x=alt.X("date:T", title="Date"),
        y=alt.Y("stars:Q", title="Average Rating"),
        tooltip=["date", "stars"]
    ).properties(
        width=700,
        height=300
    )

    st.altair_chart(chart, use_container_width=True)

        # 1-2 Star Reviews from Yesterday
        st.markdown("---")
        st.subheader("❗ 1–2 Star Reviews from Last 3 Days")
    
        # Tarihi datetime objesine çevir
        df["publishedAt"] = pd.to_datetime(df["publishedAtDate"], errors="coerce")
    
    # Son 3 günü al
    last_3_days = datetime.datetime.now().date() - timedelta(days=3)
    low_reviews = df[
        (df["stars"].isin([1, 2])) &
        (df["publishedAt"].dt.date >= last_3_days) &
        (df["textTranslated"].notna())
    ].copy()
    
    # Tarih biçimlendir
    low_reviews["publishedAtFormatted"] = low_reviews["publishedAt"].dt.strftime("%Y-%m-%d %H:%M")
    
    # Yeniden eskiye sırala
    low_reviews = low_reviews.sort_values("publishedAt", ascending=False)
    
    # Sadece belirli alanları göster
    display_cols = ["publishedAtFormatted", "place_name", "category", "textTranslated", "stars"]
    st.dataframe(low_reviews[display_cols].rename(columns={
        "publishedAtFormatted": "Date",
        "place_name": "Place",
        "category": "Category",
        "textTranslated": "Review",
        "stars": "Rating"
    }), use_container_width=True)
