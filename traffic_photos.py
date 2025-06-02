from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import cv2
import time
import os

# === KLASÖR AYARLARI ===
base_folder = "/Users/boras/Desktop/boras/Hajj/Hajj_Reports/Traffic"
raw_folder = os.path.join(base_folder, "raw")
cropped_folder = os.path.join(base_folder, "cropped")
os.makedirs(raw_folder, exist_ok=True)
os.makedirs(cropped_folder, exist_ok=True)

# === GÖRSELİ AL (SELENIUM) ===
def take_traffic_screenshot():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--window-size=1280,720")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)

    # Mekke merkezi + trafik katmanı açık
    maps_url = "https://www.google.com/maps/@21.4245033,39.8768942,11012m/data=!3m1!1e3!5m1!1e1?entry=ttu&g_ep=EgoyMDI1MDUyNi4wIKXMDSoASAFQAw%3D%3D"
    driver.get(maps_url)
    time.sleep(15)  # Harita yüklenme süresi

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    raw_path = os.path.join(raw_folder, f"mekke_traffic_{timestamp}.png")
    driver.save_screenshot(raw_path)
    driver.quit()

    return raw_path, timestamp

# === ORTADAN KIRP (OpenCV) ===
def crop_center(image_path, timestamp, crop_width=1000, crop_height=800):
    img = cv2.imread(image_path)
    height, width, _ = img.shape

    center_x = (width // 2) - 150
    center_y = (height // 2) + 0
    
    x1 = center_x - crop_width // 2
    y1 = center_y - crop_height // 2
    x2 = center_x + crop_width // 2
    y2 = center_y + crop_height // 2

    cropped = img[y1:y2, x1:x2]
    cropped_path = os.path.join(cropped_folder, f"mekke_traffic_{timestamp}_cropped.png")
    cv2.imwrite(cropped_path, cropped)

    return cropped_path

# === ÇALIŞTIR ===
if __name__ == "__main__":
    raw_path, timestamp = take_traffic_screenshot()
    cropped_path = crop_center(raw_path, timestamp)
    print(f"✔ Kırpılmış görsel kaydedildi: {cropped_path}")
