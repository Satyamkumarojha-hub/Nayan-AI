from ultralytics import YOLO
import cv2
import numpy as np

fire_model = YOLO('yolov8n.pt')

OBSTACLE_CLASSES = ['person', 'chair', 'table', 'bench', 'suitcase', 
                    'backpack', 'bottle', 'cup', 'laptop']

def estimate_distance(cls_name, size_ratio):
    REFERENCE = {
        'door': (0.02, 3.0),
        'exit sign': (0.01, 4.0),
        'person': (0.05, 2.5),
        'default': (0.03, 3.0)
    }
    ref_ratio, ref_dist = REFERENCE.get(cls_name, REFERENCE['default'])
    if size_ratio == 0:
        return 10.0
    return ref_dist * (ref_ratio / size_ratio) ** 0.5

def meters_to_footsteps(metres):
    return max(1, round(metres / 0.75))

def get_position(center_x, frame_width):
    third = frame_width / 3
    if center_x < third:
        return 'left'
    elif center_x > 2 * third:
        return 'right'
    return 'center'

def detect_frame(frame_bytes):
    nparr = np.frombuffer(frame_bytes, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    h, w = frame.shape[:2]
    
    results = fire_model(frame, conf=0.45, verbose=False)[0]
    
    detections = {
        'fire': [],
        'exit': [],
        'obstacles': [],
        'frame_size': {'w': w, 'h': h}
    }
    
    for box in results.boxes:
        cls_name = fire_model.names[int(box.cls)]
        conf = float(box.conf)
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        
        center_x = (x1 + x2) / 2
        box_area = (x2 - x1) * (y2 - y1)
        frame_area = w * h
        
        size_ratio = box_area / frame_area
        approx_distance_m = estimate_distance(cls_name, size_ratio)
        footsteps = meters_to_footsteps(approx_distance_m)
        
        item = {
            'class': cls_name,
            'confidence': round(conf, 2),
            'bbox': [x1, y1, x2, y2],
            'distance_m': round(approx_distance_m, 1),
            'footsteps': footsteps,
            'position': get_position(center_x, w)
        }
        
        if any(f in cls_name.lower() for f in ['fire', 'smoke', 'flame']):
            detections['fire'].append(item)
        elif any(e in cls_name.lower() for e in ['exit', 'door', 'stair']):
            detections['exit'].append(item)
        else:
            detections['obstacles'].append(item)
    
    return detections