from apify_client import ApifyClient
import pandas as pd
import time
from datetime import datetime, timedelta
import os

yesterday = (datetime.utcnow() + timedelta(hours=3) - timedelta(days=1)).strftime("%Y-%m-%d")

API_TOKEN = os.getenv('APIFY_TOKEN') 
REVIEWS_START_DATE = yesterday
MAX_REVIEWS = 200
SLEEP_SECONDS = 10
# ==================

df_places = pd.read_excel("Traffic_Locations.xlsx")


# 1. Apify client başlat
client = ApifyClient(API_TOKEN)


# 3. Tüm yorumları tutacak liste
all_rows = []

# 4. Her place için actor'ı çalıştır

for _, row in df_places.iterrows():
    place_id = row["Place_Id"]
    place_name = row["Place_Name"]
    category = row["Place_Category"]

    print(f"🚀 Running for: {place_name}")

    run_input = {
        "placeIds": [place_id],
        "reviewsStartDate": REVIEWS_START_DATE,
        "maxReviews": MAX_REVIEWS,
        "reviewsSort": "newest"
    }

    try:
        run = client.actor("compass/google-maps-reviews-scraper").call(run_input=run_input)
        dataset_id = run["defaultDatasetId"]

        for item in client.dataset(dataset_id).iterate_items():
            # Add metadata manually
            item["place_name"] = place_name
            item["place_id"] = place_id
            item["category"] = category
            all_rows.append(item)

        print(f"✅ {place_name} tamamlandı ({len(all_rows)} toplam kayıt)")

    except Exception as e:
        print(f"❌ Hata oluştu {place_name} için: {e}")
        time.sleep(5)

df_all = pd.DataFrame(all_rows)
if not df_all.empty:
    df_all.to_csv(("Makkah_Hajj_Reviews_Apify.csv"), mode='a', index=False, header=not pd.io.common.file_exists("Makkah_Hajj_Reviews_Apify.csv"))
else:
    print("ℹ️ Yeni yorum bulunamadı.")
