from machine import Pin, PWM
import time

# 配置舵机连接的引脚
servo_pin = Pin(15)  # 假设舵机连接在GPIO4引脚上
servo = PWM(servo_pin, freq=50)  # 设置PWM频率为50Hz，适用于多数舵机

def set_servo_angle(angle):
    """根据给定的角度设置舵机的位置"""
    duty = int(angle * 2.5 + 2.5)
    servo.duty(duty)
    time.sleep_ms(500)  # 给予时间让舵机完成动作

try:
    # 模拟开门 - 顺时针转90°
    print("Opening door...")
    set_servo_angle(90)

    # 等待2秒
    time.sleep(2)

    # 模拟关门 - 逆时针转回初始位置
    print("Closing door...")
    set_servo_angle(0)

finally:
    # 清理资源，在实际应用中可能不需要这一步，因为程序结束时会自动清理
    servo.deinit()
