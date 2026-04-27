import socket
import time
import threading

ESP32_IP = "192.168.120.151"
ESP32_PORT = 83

last_trigger_time = 0
COOLDOWN_SECONDS = 10

def send_angle(angle):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect((ESP32_IP, ESP32_PORT))
            command = f"ANGLE:{angle}"
            s.sendall(command.encode('utf-8') + b'\n')
            response = s.recv(1024)
            print(f"[舵机] 发送命令: {command}, 响应: {response.decode('utf-8').strip()}")
            return True
    except socket.timeout:
        print("[舵机] 连接超时")
        return False
    except socket.error as e:
        print(f"[舵机] Socket错误: {e}")
        return False

def _rotate_async():
    send_angle(90)
    time.sleep(3)
    send_angle(0)
    print("[舵机] 旋转完成")

def trigger_servo():
    global last_trigger_time
    
    current_time = time.time()
    if current_time - last_trigger_time < COOLDOWN_SECONDS:
        remaining = int(COOLDOWN_SECONDS - (current_time - last_trigger_time))
        print(f"[舵机] 冷却中，还需等待 {remaining} 秒")
        return False
    
    last_trigger_time = current_time
    thread = threading.Thread(target=_rotate_async, daemon=True)
    thread.start()
    print("[舵机] 触发旋转: 90度 -> 等待3秒 -> 0度")
    return True

def set_cooldown(seconds):
    global COOLDOWN_SECONDS
    COOLDOWN_SECONDS = seconds
    print(f"[舵机] 冷却时间设置为 {seconds} 秒")
