import socket

def test_send_angle(angle):
    ip = "192.168.3.151"
    port = 83
    
    try:
        print(f"Sending angle: {angle}°")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(3)
            s.connect((ip, port))
            print(f"Connected to {ip}:{port}")
            command = f"ANGLE:{angle}"
            s.sendall(command.encode('utf-8') + b'\n')
            print(f"Sent command: {command}")
            response = s.recv(1024)
            print(f"Received response: {response.decode('utf-8').strip()}")
    except socket.timeout:
        print("Connection timeout")
    except socket.error as e:
        print(f"Socket error: {e}")

if __name__ == '__main__':
    test_send_angle(90)  # 测试90度
