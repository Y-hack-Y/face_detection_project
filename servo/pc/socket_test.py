import socket
import time

def send_command(ip, command):
    """Send a command to the ESP32."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(10)  # 设置超时时间为10秒
            s.connect((ip, 83))  # 连接到ESP32的IP地址和监听端口
            print(f"Connected to {ip} on port 83")
            s.sendall(command.encode('utf-8') + b'\n')  # 发送命令
            response = s.recv(1024)  # 接收响应
            print('Received:', repr(response))
    except socket.timeout:
        print("Connection attempt timed out.")
    except socket.error as e:
        print(f"Socket error: {e}")

def open_door():
    esp32_ip = "192.168.3.151"
    try:
        send_command(esp32_ip, "OPEN")
        time.sleep(3)
        send_command(esp32_ip, "CLOSE")
    except KeyboardInterrupt:
        print("Interrupted by user")


if __name__ == "__main__":
    open_door()
