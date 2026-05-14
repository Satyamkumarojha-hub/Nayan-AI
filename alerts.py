import requests
import io
from PIL import Image, ImageDraw
from datetime import datetime

TELEGRAM_TOKEN = "8884903213:AAG_oRuKdoNPvnb5qXB_JHxfGcr0KluMYcc"
CONTACT_CHAT_IDS = ["8229599480","709794209","6540564214"]

def annotate_screenshot(frame_bytes, detections):
    img = Image.open(io.BytesIO(frame_bytes)).convert('RGB')
    draw = ImageDraw.Draw(img)
    
    colors = {'fire': 'red', 'exit': 'green', 'obstacles': 'orange'}
    
    for category, color in colors.items():
        for item in detections.get(category, []):
            x1, y1, x2, y2 = item['bbox']
            draw.rectangle([x1, y1, x2, y2], outline=color, width=3)
            label = f"{item['class']} {item['distance_m']}m"
            draw.text((x1, max(0, y1 - 20)), label, fill=color)
    
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=85)
    buf.seek(0)
    return buf

def send_rescue_alert(lat, lng, floor, detections, frame_bytes):
    now = datetime.now().strftime("%H:%M:%S")
    google_maps_url = f"https://maps.google.com/?q={lat},{lng}"
    
    fire_count = len(detections.get('fire', []))
    exit_found = len(detections.get('exit', []))
    
    message = (
        f"NAYAN AI EMERGENCY ALERT\n\n"
        f"Time: {now}\n"
        f"Location: {lat:.6f}, {lng:.6f}\n"
        f"Floor: {floor}\n"
        f"Maps: {google_maps_url}\n\n"
        f"Detections:\n"
        f"Fire sources: {fire_count}\n"
        f"Exits visible: {'Yes' if exit_found else 'No'}\n\n"
        f"A blind person is trapped and needs rescue. "
        f"Share this with the fire brigade immediately."
    )
    
    annotated = annotate_screenshot(frame_bytes, detections)
    
    for chat_id in CONTACT_CHAT_IDS:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendLocation",
            data={'chat_id': chat_id, 'latitude': lat, 'longitude': lng}
        )
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto",
            data={'chat_id': chat_id, 'caption': message},
            files={'photo': ('alert.jpg', annotated, 'image/jpeg')}
        )