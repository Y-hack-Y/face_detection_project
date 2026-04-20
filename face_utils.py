import cv2
import numpy as np
import database
import os
import requests

CAMERA_URL = 'http://10.17.137.10'

face_cascade = None

def init_face_cascade():
    global face_cascade
    if face_cascade is None:
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    return face_cascade

def get_camera_image():
    try:
        response = requests.get(f'{CAMERA_URL}/capture', timeout=10)
        if response.status_code == 200:
            img_array = np.asarray(bytearray(response.content), dtype=np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            return img
        return None
    except Exception as e:
        print(f"获取摄像头图像失败: {e}")
        return None

def get_camera_stream_url():
    return f'{CAMERA_URL}:81/stream'

def detect_faces(image):
    if image is None:
        return [], []
    
    cascade = init_face_cascade()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    
    face_locations = []
    face_rects = []
    for (x, y, w, h) in faces:
        face_locations.append((y, x + w, y + h, x))
        face_rects.append((x, y, w, h))
    
    return face_locations, face_rects

def extract_face_encoding(gray_image, face_rect):
    try:
        x, y, w, h = face_rect
        face = gray_image[y:y+h, x:x+w]
        face = cv2.resize(face, (50, 50))
        face = face.flatten().astype(np.float32) / 255.0
        return face
    except Exception as e:
        print(f"提取人脸特征失败: {e}")
        return None

def recognize_faces(image):
    if image is None:
        return [], [], []
    
    face_locations, face_rects = detect_faces(image)
    
    if not face_locations:
        return [], [], []
    
    known_faces = database.get_all_faces()
    known_encodings = []
    known_names = []
    
    for face in known_faces:
        encoding = np.frombuffer(face['encoding'], dtype=np.float32)
        known_encodings.append(encoding)
        known_names.append(face['name'])
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    names = []
    confidences = []
    
    for i, face_rect in enumerate(face_rects):
        face_encoding = extract_face_encoding(gray, face_rect)
        
        if face_encoding is None or len(known_encodings) == 0:
            names.append("未知")
            confidences.append(0.0)
            continue
        
        best_match_name = "未知"
        best_match_distance = float('inf')
        
        for known_encoding, known_name in zip(known_encodings, known_names):
            distance = np.linalg.norm(face_encoding - known_encoding)
            
            if distance < best_match_distance:
                best_match_distance = distance
                best_match_name = known_name
        
        threshold = 25.0
        if best_match_distance < threshold:
            confidence = float((1 - best_match_distance / threshold) * 100)  # 转换为 Python float
            names.append(best_match_name)
            confidences.append(confidence)
        else:
            names.append("未知")
            confidences.append(0.0)
    
    return face_locations, names, confidences

def register_face(image, name):
    if image is None:
        return False, "无法获取图像"
    
    face_locations, face_rects = detect_faces(image)
    
    if not face_locations:
        return False, "未检测到人脸，请确保人脸正对摄像头"
    
    if len(face_locations) > 1:
        return False, "检测到多张人脸，请只保留一张"
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    face_encoding = extract_face_encoding(gray, face_rects[0])
    
    if face_encoding is None:
        return False, "人脸特征提取失败"
    
    face_id = database.add_face(name, face_encoding)
    
    return True, f"成功录入 {name} 的人脸信息"

def draw_face_boxes(image, face_locations, names, confidences):
    if image is None:
        return None
    
    result = image.copy()
    
    for i, (top, right, bottom, left) in enumerate(face_locations):
        color = (0, 255, 0) if names[i] != "未知" else (0, 0, 255)
        
        cv2.rectangle(result, (left, top), (right, bottom), color, 2)
        
        label = f"{names[i]}"
        if confidences and i < len(confidences):
            label += f" ({confidences[i]:.1f}%)"
        
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        thickness = 1
        
        (text_width, text_height), baseline = cv2.getTextSize(label, font, font_scale, thickness)
        
        cv2.rectangle(result, (left, top - text_height - 10), (left + text_width, top), color, -1)
        
        cv2.putText(result, label, (left, top - 5), font, font_scale, (255, 255, 255), thickness)
    
    return result

def image_to_base64(image):
    import base64
    _, buffer = cv2.imencode('.jpg', image)
    return base64.b64encode(buffer).decode('utf-8')
