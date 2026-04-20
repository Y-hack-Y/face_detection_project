import tkinter as tk
from tkinter import ttk
import socket
import threading


class ServoController:
    def __init__(self, root):
        self.root = root
        self.root.title("舵机控制面板")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        self.esp32_ip = "192.168.3.151"
        self.esp32_port = 83
        self.last_send_time = 0
        self.debounce_interval = 100  # 防抖间隔（毫秒）
        
        self.setup_ui()
    
    def setup_ui(self):
        ip_frame = ttk.LabelFrame(self.root, text="ESP32连接设置", padding=10)
        ip_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(ip_frame, text="IP地址:").grid(row=0, column=0, sticky="w", padx=5)
        self.ip_entry = ttk.Entry(ip_frame, width=20)
        self.ip_entry.insert(0, self.esp32_ip)
        self.ip_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(ip_frame, text="端口:").grid(row=0, column=2, sticky="w", padx=5)
        self.port_entry = ttk.Entry(ip_frame, width=8)
        self.port_entry.insert(0, str(self.esp32_port))
        self.port_entry.grid(row=0, column=3, padx=5, pady=5)
        
        servo_frame = ttk.LabelFrame(self.root, text="舵机角度控制", padding=10)
        servo_frame.pack(fill="x", padx=10, pady=10)
        
        self.angle_var = tk.IntVar(value=0)
        
        ttk.Label(servo_frame, text="角度:").grid(row=0, column=0, sticky="w", padx=5)
        
        self.angle_slider = ttk.Scale(
            servo_frame, 
            from_=0, 
            to=180, 
            orient="horizontal",
            variable=self.angle_var,
            command=self.on_slider_change,
            length=250
        )
        self.angle_slider.grid(row=0, column=1, padx=5, pady=5)
        
        self.angle_label = ttk.Label(servo_frame, text="0°", width=6)
        self.angle_label.grid(row=0, column=2, padx=5)
        
        btn_frame = ttk.Frame(servo_frame)
        btn_frame.grid(row=1, column=0, columnspan=3, pady=10)
        
        ttk.Button(btn_frame, text="0°", width=8, command=lambda: self.set_angle(0)).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="90°", width=8, command=lambda: self.set_angle(90)).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="180°", width=8, command=lambda: self.set_angle(180)).pack(side="left", padx=5)
        
        status_frame = ttk.LabelFrame(self.root, text="状态", padding=10)
        status_frame.pack(fill="x", padx=10, pady=10)
        
        self.status_label = ttk.Label(status_frame, text="就绪", foreground="green")
        self.status_label.pack()
    
    def on_slider_change(self, value):
        angle = int(float(value))
        self.angle_label.config(text=f"{angle}°")
        self.send_angle(angle)
    
    def set_angle(self, angle):
        self.angle_var.set(angle)
        self.angle_label.config(text=f"{angle}°")
        self.send_angle(angle)
    
    def send_angle(self, angle):
        import time
        current_time = time.time() * 1000  # 转换为毫秒
        
        # 防抖处理
        if current_time - self.last_send_time < self.debounce_interval:
            return
        
        self.last_send_time = current_time
        
        ip = self.ip_entry.get()
        try:
            port = int(self.port_entry.get())
        except ValueError:
            self.status_label.config(text="端口无效", foreground="red")
            return
        
        self.status_label.config(text="正在发送...", foreground="blue")
        thread = threading.Thread(target=self._send_angle_thread, args=(ip, port, angle))
        thread.daemon = True
        thread.start()
    
    def _send_angle_thread(self, ip, port, angle):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(3)
                s.connect((ip, port))
                command = f"ANGLE:{angle}"
                s.sendall(command.encode('utf-8') + b'\n')
                response = s.recv(1024)
                self.root.after(0, lambda: self.status_label.config(text=f"已设置角度: {angle}°", foreground="green"))
        except socket.timeout:
            self.root.after(0, lambda: self.status_label.config(text="连接超时", foreground="red"))
        except socket.error as e:
            self.root.after(0, lambda: self.status_label.config(text=f"连接错误: {e}", foreground="red"))


def main():
    root = tk.Tk()
    app = ServoController(root)
    root.mainloop()


if __name__ == "__main__":
    main()
