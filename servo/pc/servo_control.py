import socket
import time

ESP32_IP = "192.168.120.151"
ESP32_PORT = 83

def send_angle(angle):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect((ESP32_IP, ESP32_PORT))
            print(f"已连接到 {ESP32_IP}:{ESP32_PORT}")
            command = f"ANGLE:{angle}"
            s.sendall(command.encode('utf-8') + b'\n')
            print(f"发送命令: {command}")
            response = s.recv(1024)
            print(f"收到响应: {response.decode('utf-8').strip()}")
    except socket.timeout:
        print("连接超时")
    except socket.error as e:
        print(f"Socket错误: {e}")

def rotate_90_and_back():
    print("舵机旋转到90度...")
    send_angle(90)
    print("等待3秒...")
    time.sleep(3)
    print("舵机旋转回0度...")
    send_angle(0)
    print("完成!")

def main():
    print("舵机控制程序")
    print("输入 1: 舵机旋转90度，等待3秒后返回")
    print("输入 q: 退出程序")
    print("-" * 40)
    
    while True:
        user_input = input("请输入命令: ").strip()
        
        if user_input == '1':
            rotate_90_and_back()
        elif user_input.lower() == 'q':
            print("退出程序")
            break
        else:
            print("无效命令，请输入 1 或 q")

if __name__ == "__main__":
    main()
