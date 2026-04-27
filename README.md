# 人脸识别与舵机控制系统

一个基于Flask和OpenCV的智能人脸识别系统，集成了舵机控制功能，支持实时人脸检测、识别、黑名单管理和远程舵机控制。

## 📋 项目简介

本项目是一个完整的人脸识别与舵机控制系统，主要功能包括：
- 实时人脸检测与识别
- 舵机自动控制（基于人脸识别结果）
- 用户权限管理（管理员/普通用户）
- 黑名单功能（防止特定用户触发舵机）
- 检测日志记录
- 美观的Web界面

## ✨ 主要功能

### 人脸识别
- 基于OpenCV的实时人脸检测
- 支持多人脸同时识别
- 人脸特征提取与匹配
- 识别置信度显示

### 舵机控制
- ESP32舵机控制（通过Socket通信）
- 人脸识别成功自动触发舵机
- 旋转90度后自动复位
- 冷却机制防止频繁触发

### 用户管理
- 管理员和普通用户权限分离
- 安全的密码加密存储
- 会话管理

### 黑名单功能
- 管理员可添加/删除黑名单用户
- 黑名单用户不会触发舵机
- 黑名单记录管理

### 数据记录
- 人脸识别日志
- 检测时间、用户、置信度记录
- 历史数据查询

## 🛠️ 技术栈

- **后端框架**: Flask 3.0.0
- **图像处理**: OpenCV 4.8.1.78
- **数值计算**: NumPy 1.24.3
- **网络请求**: Requests 2.31.0
- **数据库**: SQLite3
- **前端**: HTML5, CSS3, JavaScript
- **硬件控制**: ESP32 + 舵机

## 📦 安装说明

### 环境要求

- Python 3.8+
- ESP32开发板
- 舵机（SG90或类似）
- 摄像头（支持HTTP流媒体）

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/yourusername/face_detection_project.git
cd face_detection_project
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置ESP32**

将ESP32代码上传到开发板，确保以下配置：
- ESP32 IP地址：`192.168.120.151`
- Socket端口：`83`
- 舵机连接到GPIO引脚

4. **配置摄像头**

修改 `face_utils.py` 中的摄像头URL：
```python
CAMERA_URL = 'http://192.168.120.10'  # 修改为你的摄像头IP
```

5. **初始化数据库**

首次运行时会自动创建数据库和默认用户：
- 管理员账号：`admin` / `admin123`
- 普通用户：`user` / `user123`

## 🚀 使用方法

### 启动应用

```bash
python app.py
```

应用将在 `http://localhost:5000` 启动。

### 用户界面

1. **登录页面**
   - 使用管理员或普通用户账号登录

2. **管理员界面** (`/admin`)
   - 查看和管理已注册人脸
   - 添加/删除黑名单用户
   - 查看检测日志
   - 管理系统统计信息

3. **用户界面** (`/user`)
   - 实时人脸检测
   - 查看识别结果
   - 查看舵机状态
   - 查看个人检测记录

### 舵机控制测试

```bash
# 测试舵机连接
cd servo/pc
python test_connection.py

# 手动控制舵机
python servo_control.py
```

## 📁 项目结构

```
face_detection_project/
├── app.py                 # Flask主应用
├── database.py            # 数据库操作
├── face_utils.py          # 人脸识别工具
├── servo_controller.py    # 舵机控制模块
├── requirements.txt       # Python依赖
├── templates/             # HTML模板
│   ├── login.html        # 登录页面
│   ├── admin.html        # 管理员界面
│   └── user.html         # 用户界面
└── servo/                # 舵机相关代码
    ├── esp32/            # ESP32代码
    └── pc/               # PC端测试代码
```

## ⚙️ 配置说明

### 舵机配置

修改 `servo_controller.py` 中的配置：
```python
ESP32_IP = "192.168.120.151"  # ESP32 IP地址
ESP32_PORT = 83                # Socket端口
COOLDOWN_SECONDS = 10          # 冷却时间（秒）
```

### 摄像头配置

修改 `face_utils.py` 中的配置：
```python
CAMERA_URL = 'http://192.168.120.10'  # 摄像头IP地址
```

### Flask配置

修改 `app.py` 中的配置：
```python
app.secret_key = 'your_secret_key_here_change_in_production'  # 会话密钥
```

## 🔧 API接口

### 人脸检测
```
POST /api/detect
Content-Type: application/json

Response:
{
  "success": true,
  "image": "base64_encoded_image",
  "faces": [
    {
      "name": "张三",
      "confidence": 0.95
    }
  ]
}
```

### 黑名单管理
```
POST /api/blacklist/add
POST /api/blacklist/remove
GET /api/blacklist/list
```

## 📸 界面截图

### 管理员界面
- 人脸管理
- 黑名单管理
- 检测日志

### 用户界面
- 实时人脸检测
- 舵机状态显示
- 识别结果展示

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📝 许可证

本项目采用 MIT 许可证 - 详见 LICENSE 文件

## 👥 作者

- **项目作者** - [Y_hack_Y]

## 🙏 致谢

- OpenCV团队
- Flask社区
- ESP32社区

## 📮 联系方式

如有问题或建议，请通过以下方式联系：
- 提交 Issue
- 发送邮件：your.email@example.com

## 📄 更新日志

### v1.0.0 (2026-04-27)
- 初始版本发布
- 实现基础人脸识别功能
- 集成舵机控制
- 添加用户管理系统
- 实现黑名单功能
- 完善Web界面

---

⭐ 如果这个项目对你有帮助，请给个Star！
