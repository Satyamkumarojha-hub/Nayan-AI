def generate_guidance(detections):
    messages = []
    priority = 'normal'
    
    fire_items = detections.get('fire', [])
    exit_items = detections.get('exit', [])
    obstacle_items = detections.get('obstacles', [])
    
    if fire_items:
        nearest_fire = min(fire_items, key=lambda x: x['distance_m'])
        dist = nearest_fire['distance_m']
        pos = nearest_fire['position']
        priority = 'urgent'
        
        if dist < 2:
            messages.append("DANGER! Fire immediately ahead! Turn around now!")
        else:
            direction = f"to your {pos}" if pos != 'center' else "ahead"
            messages.append(
                f"Warning! Fire detected {direction}, "
                f"{nearest_fire['footsteps']} footsteps away. Avoid this direction."
            )
    
    if exit_items:
        nearest_exit = min(exit_items, key=lambda x: x['distance_m'])
        pos = nearest_exit['position']
        steps = nearest_exit['footsteps']
        
        if pos == 'center':
            messages.append(f"Exit straight ahead. Walk {steps} footsteps forward.")
        elif pos == 'left':
            messages.append(f"Exit to your left. Turn left, then walk {steps} footsteps.")
        else:
            messages.append(f"Exit to your right. Turn right, then walk {steps} footsteps.")
    elif not fire_items:
        messages.append("Scanning for exit. Keep walking slowly.")
    
    if obstacle_items:
        nearest = min(obstacle_items, key=lambda x: x['distance_m'])
        if nearest['distance_m'] < 1.5:
            pos = nearest['position']
            if pos == 'center':
                messages.append("Obstacle directly ahead. Stop. Step to the right.")
            else:
                messages.append(f"Obstacle to your {pos}. Stay to the opposite side.")
    
    return {
        'instructions': ' '.join(messages),
        'priority': priority,
        'has_exit': len(exit_items) > 0,
        'has_fire': len(fire_items) > 0,
        'has_obstacle': len(obstacle_items) > 0
    }