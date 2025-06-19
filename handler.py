import runpod
import base64
import cv2
import numpy as np
import mediapipe as mp
from PIL import Image
import io
import json

# Initialize MediaPipe
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(
    static_image_mode=True,
    model_complexity=2,
    enable_segmentation=True,
    min_detection_confidence=0.5
)

# Garment-specific landmark mappings
GARMENT_LANDMARKS = {
    'tshirt': {
        'shoulder_left': mp_pose.PoseLandmark.LEFT_SHOULDER,
        'shoulder_right': mp_pose.PoseLandmark.RIGHT_SHOULDER,
        'elbow_left': mp_pose.PoseLandmark.LEFT_ELBOW,
        'elbow_right': mp_pose.PoseLandmark.RIGHT_ELBOW,
        'wrist_left': mp_pose.PoseLandmark.LEFT_WRIST,
        'wrist_right': mp_pose.PoseLandmark.RIGHT_WRIST,
        'hip_left': mp_pose.PoseLandmark.LEFT_HIP,
        'hip_right': mp_pose.PoseLandmark.RIGHT_HIP,
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
        'elbow_left': mp_pose.PoseLandmark.LEFT_ELBOW,
        'elbow_right': mp_pose.PoseLandmark.RIGHT_ELBOW,
        'wrist_left': mp_pose.PoseLandmark.LEFT_WRIST,
        'wrist_right': mp_pose.PoseLandmark.RIGHT_WRIST,
        'hip_left': mp_pose.PoseLandmark.LEFT_HIP,
        'hip_right': mp_pose.PoseLandmark.RIGHT_HIP,
    }
}

def calculate_distance(landmark1, landmark2, image_width, image_height):
    """Calculate pixel distance between two landmarks"""
    x1, y1 = landmark1.x * image_width, landmark1.y * image_height
    x2, y2 = landmark2.x * image_width, landmark2.y * image_height
    return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def estimate_scale_factor(landmarks, garment_type, image_shape):
    """Estimate cm per pixel based on standard sizing"""
    # Standard measurements for medium size (in cm)
    STANDARD_MEASUREMENTS = {
        'tshirt': {'chest_width': 50, 'body_length': 70},
        'pants': {'waist_width': 40, 'inseam': 80},
        'jacket': {'chest_width': 55, 'body_length': 75}
    }
    
    if garment_type == 'tshirt' or garment_type == 'jacket':
        # Use shoulder width as reference
        shoulder_width_px = calculate_distance(
            landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER],
            landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER],
            image_shape[1], image_shape[0]
        )
        return STANDARD_MEASUREMENTS[garment_type]['chest_width'] / shoulder_width_px
    
    elif garment_type == 'pants':
        # Use hip width as reference
        hip_width_px = calculate_distance(
            landmarks[mp_pose.PoseLandmark.LEFT_HIP],
            landmarks[mp_pose.PoseLandmark.RIGHT_HIP],
            image_shape[1], image_shape[0]
        )
        return STANDARD_MEASUREMENTS[garment_type]['waist_width'] / hip_width_px
    
    # Default fallback
    return image_shape[1] / 100.0

def extract_measurements(image_np, garment_type):
    """Extract measurements from image using MediaPipe"""
    results = pose.process(cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB))
    
    if not results.pose_landmarks:
        return {
            'success': False,
            'error': 'No pose landmarks detected',
            'measurements': {},
            'confidence_scores': {}
        }
    
    landmarks = results.pose_landmarks.landmark
    h, w = image_np.shape[:2]
    
    # Estimate scale
    scale_factor = estimate_scale_factor(landmarks, garment_type, image_np.shape)
    
    measurements = {}
    confidence_scores = {}
    
    if garment_type == 'tshirt':
        # Chest width
        chest_width_px = calculate_distance(
            landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER],
            landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER],
            w, h
        )
        measurements['chest_width'] = round(chest_width_px * scale_factor, 1)
        confidence_scores['chest_width'] = round(
            (landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].visibility +
             landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].visibility) / 2, 2
        )
        
        # Body length (neck to hip midpoint)
        neck = landmarks[mp_pose.PoseLandmark.NOSE]  # Approximate neck position
        hip_mid_y = (landmarks[mp_pose.PoseLandmark.LEFT_HIP].y + 
                     landmarks[mp_pose.PoseLandmark.RIGHT_HIP].y) / 2
        body_length_px = abs(neck.y - hip_mid_y) * h
        measurements['body_length'] = round(body_length_px * scale_factor, 1)
        confidence_scores['body_length'] = round(
            (landmarks[mp_pose.PoseLandmark.LEFT_HIP].visibility +
             landmarks[mp_pose.PoseLandmark.RIGHT_HIP].visibility) / 2, 2
        )
        
        # Sleeve length (shoulder to wrist)
        sleeve_length_px = calculate_distance(
            landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER],
            landmarks[mp_pose.PoseLandmark.LEFT_WRIST],
            w, h
        )
        measurements['sleeve_length'] = round(sleeve_length_px * scale_factor, 1)
        confidence_scores['sleeve_length'] = round(
            (landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].visibility +
             landmarks[mp_pose.PoseLandmark.LEFT_WRIST].visibility) / 2, 2
        )
    
    elif garment_type == 'pants':
        # Waist width
        waist_width_px = calculate_distance(
            landmarks[mp_pose.PoseLandmark.LEFT_HIP],
            landmarks[mp_pose.PoseLandmark.RIGHT_HIP],
            w, h
        )
        measurements['waist_width'] = round(waist_width_px * scale_factor, 1)
        confidence_scores['waist_width'] = round(
            (landmarks[mp_pose.PoseLandmark.LEFT_HIP].visibility +
             landmarks[mp_pose.PoseLandmark.RIGHT_HIP].visibility) / 2, 2
        )
        
        # Inseam (hip to ankle)
        inseam_px = calculate_distance(
            landmarks[mp_pose.PoseLandmark.LEFT_HIP],
            landmarks[mp_pose.PoseLandmark.LEFT_ANKLE],
            w, h
        )
        measurements['inseam'] = round(inseam_px * scale_factor, 1)
        confidence_scores['inseam'] = round(
            (landmarks[mp_pose.PoseLandmark.LEFT_HIP].visibility +
             landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].visibility) / 2, 2
        )
        
        # Rise (hip to crotch approximation)
        rise_px = abs(landmarks[mp_pose.PoseLandmark.LEFT_HIP].y - 
                     landmarks[mp_pose.PoseLandmark.LEFT_KNEE].y) * h * 0.4
        measurements['rise'] = round(rise_px * scale_factor, 1)
        confidence_scores['rise'] = round(landmarks[mp_pose.PoseLandmark.LEFT_HIP].visibility, 2)
    
    # Generate visualization
    annotated_image = image_np.copy()
    mp.solutions.drawing_utils.draw_landmarks(
        annotated_image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
    
    # Convert to base64
    _, buffer = cv2.imencode('.png', annotated_image)
    vis_base64 = base64.b64encode(buffer).decode('utf-8')
    
    return {
        'success': True,
        'measurements': measurements,
        'confidence_scores': confidence_scores,
        'visualization': f'data:image/png;base64,{vis_base64}',
        'unit': 'cm',
        'scale_factor': scale_factor
    }

def handler(job):
    """RunPod handler function"""
    try:
        job_input = job['input']
        
        # Decode base64 image
        image_data = base64.b64decode(job_input['image'])
        image = Image.open(io.BytesIO(image_data))
        image_np = np.array(image)
        
        # Extract garment type
        garment_type = job_input.get('garment_type', 'tshirt')
        
        # Extract measurements
        result = extract_measurements(image_np, garment_type)
        
        return result
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'measurements': {},
            'confidence_scores': {}
        }

# RunPod serverless handler
runpod.serverless.start({"handler": handler})
