# measurement_utils.py
import numpy as np
import mediapipe as mp

mp_pose = mp.solutions.pose

# Standard measurements for different sizes (in cm)
STANDARD_MEASUREMENTS = {
    'tshirt': {
        'xs': {'chest': 46, 'length': 66},
        'sm': {'chest': 48, 'length': 68},
        'md': {'chest': 50, 'length': 70},
        'lg': {'chest': 52, 'length': 72},
        'xl': {'chest': 54, 'length': 74}
    },
    'pants': {
        'xs': {'waist': 36, 'inseam': 76},
        'sm': {'waist': 38, 'inseam': 78},
        'md': {'waist': 40, 'inseam': 80},
        'lg': {'waist': 42, 'inseam': 82},
        'xl': {'waist': 44, 'inseam': 84}
    },
    'jacket': {
        'xs': {'chest': 50, 'length': 68},
        'sm': {'chest': 52, 'length': 70},
        'md': {'chest': 54, 'length': 72},
        'lg': {'chest': 56, 'length': 74},
        'xl': {'chest': 58, 'length': 76}
    }
}

def calculate_distance(landmark1, landmark2, image_width, image_height):
    """Calculate pixel distance between two landmarks"""
    x1, y1 = landmark1.x * image_width, landmark1.y * image_height
    x2, y2 = landmark2.x * image_width, landmark2.y * image_height
    return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def estimate_garment_size(measurements, garment_type):
    """Estimate size based on measurements"""
    if garment_type not in STANDARD_MEASUREMENTS:
        return 'md'
    
    sizes = STANDARD_MEASUREMENTS[garment_type]
    
    # Simple size estimation based on chest/waist
    key_measurement = 'chest' if garment_type in ['tshirt', 'jacket'] else 'waist'
    if key_measurement not in measurements:
        return 'md'
    
    measured_value = measurements[key_measurement]
    
    # Find closest size
    closest_size = 'md'
    min_diff = float('inf')
    
    for size, standards in sizes.items():
        if key_measurement in standards:
            diff = abs(standards[key_measurement] - measured_value)
            if diff < min_diff:
                min_diff = diff
                closest_size = size
    
    return closest_size

def get_measurement_points(garment_type):
    """Get relevant MediaPipe landmarks for garment type"""
    points = {
        'tshirt': {
            'shoulder_left': mp_pose.PoseLandmark.LEFT_SHOULDER,
            'shoulder_right': mp_pose.PoseLandmark.RIGHT_SHOULDER,
            'hip_left': mp_pose.PoseLandmark.LEFT_HIP,
            'hip_right': mp_pose.PoseLandmark.RIGHT_HIP,
            'wrist_left': mp_pose.PoseLandmark.LEFT_WRIST,
            'wrist_right': mp_pose.PoseLandmark.RIGHT_WRIST,
        },
        'pants': {
            'hip_left': mp_pose.PoseLandmark.LEFT_HIP,
            'hip_right': mp_pose.PoseLandmark.RIGHT_HIP,
            'knee_left': mp_pose.PoseLandmark.LEFT_KNEE,
            'knee_right': mp_pose.PoseLandmark.RIGHT_KNEE,
            'ankle_left': mp_pose.PoseLandmark.LEFT_ANKLE,
            'ankle_right': mp_pose.PoseLandmark.RIGHT_ANKLE,
        },
        'jacket': {
            'shoulder_left': mp_pose.PoseLandmark.LEFT_SHOULDER,
            'shoulder_right': mp_pose.PoseLandmark.RIGHT_SHOULDER,
            'hip_left': mp_pose.PoseLandmark.LEFT_HIP,
            'hip_right': mp_pose.PoseLandmark.RIGHT_HIP,
            'wrist_left': mp_pose.PoseLandmark.LEFT_WRIST,
            'wrist_right': mp_pose.PoseLandmark.RIGHT_WRIST,
            'elbow_left': mp_pose.PoseLandmark.LEFT_ELBOW,
            'elbow_right': mp_pose.PoseLandmark.RIGHT_ELBOW,
        }
    }
    return points.get(garment_type, points['tshirt'])
