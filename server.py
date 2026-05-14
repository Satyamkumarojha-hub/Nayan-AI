from flask import Flask, request, jsonify
from flask_cors import CORS
from detection import detect_frame
from navigation import generate_guidance
from alerts import send_rescue_alert
import base64
import time

app = Flask(__name__)
CORS(app)

last_alert_time = 0
ALERT_COOLDOWN = 30

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    frame_b64 = data.get('frame')
    latitude = data.get('lat')
    longitude = data.get('lng')
    floor = data.get('floor', 'Unknown')
    
    frame_bytes = base64.b64decode(frame_b64)
    
    detections = detect_frame(frame_bytes)
    
    guidance = generate_guidance(detections)
    
    global last_alert_time
    if detections['fire'] and (time.time() - last_alert_time > ALERT_COOLDOWN):
        send_rescue_alert(
            lat=latitude,
            lng=longitude,
            floor=floor,
            detections=detections,
            frame_bytes=frame_bytes
        )
        last_alert_time = time.time()
    
    return jsonify({
        'detections': detections,
        'guidance': guidance
    })

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({'status': 'NAYAN AI server is running'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)