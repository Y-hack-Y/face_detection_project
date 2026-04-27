from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
import database
import face_utils
import os
import servo_controller

app = Flask(__name__)
app.secret_key = 'your_secret_key_here_change_in_production'

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        if session.get('role') != 'admin':
            return redirect(url_for('user_dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('user_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = database.verify_user(username, password)
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('user_dashboard'))
        else:
            error = '用户名或密码错误'
    
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/user')
@login_required
def user_dashboard():
    return render_template('user.html', username=session.get('username'))

@app.route('/admin')
@admin_required
def admin_dashboard():
    faces = database.get_all_faces()
    return render_template('admin.html', 
                           username=session.get('username'),
                           faces=faces)

@app.route('/api/detect', methods=['POST'])
@login_required
def detect():
    image = face_utils.get_camera_image()
    
    if image is None:
        return jsonify({'success': False, 'message': '无法获取摄像头图像'})
    
    face_locations, names, confidences = face_utils.recognize_faces(image)
    
    result_image = face_utils.draw_face_boxes(image, face_locations, names, confidences)
    
    image_base64 = face_utils.image_to_base64(result_image)
    
    for i, name in enumerate(names):
        if name != "未知":
            database.add_detection_log(
                session['user_id'],
                name,
                confidences[i]
            )
            if not database.is_blacklisted(name):
                servo_controller.trigger_servo()
            else:
                print(f"[舵机] {name} 在黑名单中，跳过触发")
    
    return jsonify({
        'success': True,
        'image': image_base64,
        'faces': [{
            'name': names[i],
            'confidence': confidences[i] if confidences else 0
        } for i in range(len(names))]
    })

@app.route('/api/register_face', methods=['POST'])
@admin_required
def register_face():
    name = request.form.get('name')
    
    if not name:
        return jsonify({'success': False, 'message': '请输入姓名'})
    
    image = face_utils.get_camera_image()
    
    if image is None:
        return jsonify({'success': False, 'message': '无法获取摄像头图像'})
    
    success, message = face_utils.register_face(image, name)
    
    return jsonify({'success': success, 'message': message})

@app.route('/api/delete_face/<int:face_id>', methods=['POST'])
@admin_required
def delete_face(face_id):
    database.delete_face(face_id)
    return jsonify({'success': True, 'message': '删除成功'})

@app.route('/api/faces')
@admin_required
def get_faces():
    faces = database.get_all_faces()
    # 排除 encoding 字段，因为它是 bytes 类型无法 JSON 序列化
    faces_without_encoding = []
    for face in faces:
        face_dict = dict(face)
        if 'encoding' in face_dict:
            del face_dict['encoding']
        faces_without_encoding.append(face_dict)
    return jsonify({'success': True, 'faces': faces_without_encoding})

@app.route('/api/logs')
@login_required
def get_logs():
    user_id = session['user_id'] if session.get('role') != 'admin' else None
    logs = database.get_detection_logs(user_id)
    serializable_logs = []
    for log in logs:
        log_dict = {}
        for key, value in log.items():
            if isinstance(value, bytes):
                log_dict[key] = value.decode('utf-8', errors='replace')
            else:
                log_dict[key] = value
        serializable_logs.append(log_dict)
    return jsonify({'success': True, 'logs': serializable_logs})

@app.route('/api/stream_url')
@login_required
def get_stream_url():
    return jsonify({
        'success': True,
        'url': face_utils.get_camera_stream_url()
    })

@app.route('/api/blacklist', methods=['GET'])
@admin_required
def get_blacklist():
    blacklist = database.get_all_blacklist()
    return jsonify({'success': True, 'blacklist': blacklist})

@app.route('/api/blacklist/add', methods=['POST'])
@admin_required
def add_blacklist():
    name = request.form.get('name')
    
    if not name:
        return jsonify({'success': False, 'message': '请输入姓名'})
    
    success = database.add_to_blacklist(name)
    if success:
        return jsonify({'success': True, 'message': f'成功添加 {name} 到黑名单'})
    else:
        return jsonify({'success': False, 'message': f'{name} 已在黑名单中'})

@app.route('/api/blacklist/remove', methods=['POST'])
@admin_required
def remove_blacklist():
    name = request.form.get('name')
    
    if not name:
        return jsonify({'success': False, 'message': '请输入姓名'})
    
    success = database.remove_from_blacklist(name)
    if success:
        return jsonify({'success': True, 'message': f'成功从黑名单中移除 {name}'})
    else:
        return jsonify({'success': False, 'message': f'{name} 不在黑名单中'})

if __name__ == '__main__':
    database.init_db()
    print("=" * 50)
    print("人脸检测系统启动中...")
    print("=" * 50)
    print("默认账号信息：")
    print("管理员 - 用户名: admin, 密码: admin123")
    print("普通用户 - 用户名: user, 密码: user123")
    print("=" * 50)
    app.run(host='0.0.0.0', port=8080, debug=True)
