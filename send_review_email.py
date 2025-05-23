from datetime import datetime, timedelta
import pandas as pd
import smtplib
from email.mime.text import MIMEText
import os

# Ayarlar
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO = os.getenv("EMAIL_TO", EMAIL_USER)  # default to sender

# Veriyi oku
df = pd.read_csv("reviews/Makkah_Hajj_Reviews_Apify.csv", parse_dates=["publishedAtDate"])
df["publishedAt"] = pd.to_datetime(df["publishedAtDate"], errors="coerce")

# Dünü al
yesterday = datetime.now().date() - timedelta(days=1)

# 1-2 yıldızlı ve dünkü yorumları filtrele
low_reviews = df[
    (df["stars"].isin([1, 2])) &
    (df["publishedAt"].dt.date == yesterday) &
    (df["textTranslated"].notna())
][["place_name", "category", "stars", "textTranslated"]]

# HTML body hazırla
html_body = f"<h2>🟥 1–2 Star Reviews on {yesterday}</h2>"
if low_reviews.empty:
    html_body += "<p>No low-rated reviews found yesterday 👌</p>"
else:
    for _, row in low_reviews.iterrows():
        html_body += f"""
        <p><b>{row['place_name']} ({row['category']})</b><br>
        ⭐ {row['stars']}<br>
        {row['textTranslated']}</p><hr>
        """

# E-posta gönder
msg = MIMEText(html_body, "html")
msg["Subject"] = f"[Daily Hajj Review Report] - {yesterday}"
msg["From"] = EMAIL_USER
msg["To"] = EMAIL_TO

with smtplib.SMTP("smtp.gmail.com", 587) as server:
    server.starttls()
    server.login(EMAIL_USER, EMAIL_PASS)
    server.send_message(msg)

print("✅ Email sent.")
