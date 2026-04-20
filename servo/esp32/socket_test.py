from machine import Pin, PWM
import socket
import time
import network

# 配置舵机连接的引脚（代码不完整，请自行补全）
servo_pin = Pin(15)  # 假设舵机连接在GPIO4引脚上
servo = PWM(servo_pin, freq=50)  # 设置PWM频率为50Hz，适用于多数舵机

def set_servo_angle(angle):
    """根据给定的角度设置舵机的位置"""
    # 舵机占空比校准参数（根据实际舵机调整）
    min_duty = 25  # 0°
    max_duty = 125 # 180°
    # 确保角度在0-180范围内
    # 线性映射角度到占空比
    angle = max(0, min(180, angle))
    duty = int(min_duty + (angle * (max_duty - min_duty) / 180))
    print(f'Setting angle: {angle}°, duty: {duty}')
    servo.duty(duty)
    time.sleep_ms(100)  # 减少等待时间，提高响应速度

def start_server():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    print('Connecting to WiFi...')
    wlan.connect("qazwsx", "qwertyuiop")
    
    # 等待网络连接
    max_attempts = 30
    for i in range(max_attempts):
        if wlan.isconnected():
            break
        print(f'Waiting for connection... {i+1}/{max_attempts}')
        time.sleep(1)
    
    if wlan.isconnected():
        print('WiFi connected!')
        print('IP address:', wlan.ifconfig()[0])
        print('Network config:', wlan.ifconfig())
    else:
        print('WiFi connection failed!')
        return

    addr = socket.getaddrinfo('0.0.0.0', 83)[0][-1]  # 监听所有接口的8080端口
    s = socket.socket()
    s.bind(addr)
    s.listen(1)
    print('listening on', addr)

    while True:
        cl, addr = s.accept()
        print('client connected from', addr)
        cl_file = cl.makefile('rwb', 0)
        try:
            while True:
                line = cl_file.readline()
                if not line:
                    break  # 连接关闭
                command = line.decode('utf-8').strip()
                if command == 'OPEN':
                    set_servo_angle(90)
                    cl.send(b'Door opened\n')
                    print('Door opened')
                elif command == 'CLOSE':
                    set_servo_angle(0)
                    cl.send(b'Door closed\n')
                    print('Door closed')
                elif command.startswith('ANGLE:'):
                    angle = int(command.split(':')[1])
                    set_servo_angle(angle)
                    response = f'Angle set to {angle}\n'
                    cl.send(response.encode('utf-8'))
                    print(f'Angle set to {angle}')
        except Exception as e:
            print(f'Error: {e}')
        finally:
            cl.close()
            print('Client disconnected')

start_server()
