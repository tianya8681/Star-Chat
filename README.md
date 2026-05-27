# 微信风格聊天社交软件 -- [✨星聊 Star Chat]

一个基于 Flask + Socket.IO 开发的现代化聊天社交软件，支持文字、图片、视频消息，以及完整的好友关系管理功能。界面风格参考微信设计，提供流畅的聊天体验。
> ![star chat](/star chat.png "star chat")
## ✨ 功能特性

### 👤 用户功能
- **用户注册/登录**：支持用户名密码注册登录，密码采用 SHA-256 加密
- **头像上传**：支持自定义头像上传，显示圆形缩略图
- **昵称管理**：支持修改昵称，聊天中显示昵称而非账号名
- **消息发送**：支持文字、图片、视频消息
- **表情功能**：丰富的 emoji 表情选择器，6大分类
- **实时聊天**：基于 WebSocket 的实时消息推送
- **消息预览**：好友列表显示最后一条消息预览

### 💬 聊天界面
- **微信风格对话**：左边显示接收消息，右边显示发送消息
- **头像显示**：双方头像都清晰显示，形成完整对话流
- **绿色背景**：微信风格的绿色方格纹理背景
- **气泡样式**：发送消息绿色气泡，接收消息白色气泡
- **即时刷新**：发送消息后立即刷新显示对话流

### 👥 社交好友功能
- **好友搜索**：支持按用户名/昵称搜索用户
- **好友请求**：发送、接受、拒绝好友请求
- **好友列表**：展示好友列表及最后消息预览
- **好友删除**：长按好友列表项弹出删除菜单
- **请求提示**：实时红点提示待处理请求数量

### 🔧 管理员功能
- **管理员登录**：独立的管理员登录入口，仅管理员可登录
- **用户管理**：查看、编辑、删除用户
- **权限控制**：管理用户聊天权限、上传权限
- **状态管理**：设置用户注册状态（pending/active）
- **密码修改**：管理员支持修改密码
- **消息管理**：查看和删除消息记录

### 🎨 界面设计
- **科技感登录页**：渐变背景、公告栏、现代化表单设计
- **响应式布局**：适配桌面端和移动端
- **绿色主题**：微信风格的绿色配色方案
- **平滑动画**：按钮悬停效果、过渡动画

## 🛠️ 技术栈

| 分类 | 技术 | 版本 |
|------|------|------|
| 后端框架 | Flask | 2.x |
| 实时通信 | Flask-SocketIO | 5.x |
| 数据库 | SQLite | 内置 |
| 前端 | HTML5 / CSS3 / JavaScript | - |
| 文件上传 | Werkzeug | 内置 |
| 异步驱动 | Eventlet | 0.33.x |

## 🚀 快速开始

### 环境要求
- Python 3.8+
- pip 包管理工具

### 安装依赖

```bash
# 进入项目目录
cd backend

# 安装依赖
pip install flask flask-socketio eventlet
```

### 启动服务

```bash
# 进入后端目录
cd backend

# 启动开发服务器
python app.py
```

服务将在 `http://localhost:9999` 启动。

### 访问地址

| 页面 | URL |
|------|-----|
| 用户登录 | http://localhost:9999/login |
| 用户注册 | http://localhost:9999/register |
| 管理员登录 | http://localhost:9999/admin/login |

## 📁 项目结构

```
CODE TARE/
├── backend/
│   └── app.py                 # 后端主程序（路由、数据库、API）
├── templates/                 # HTML模板
│   ├── chat.html              # 聊天界面
│   ├── login.html             # 用户登录页（科技感设计）
│   ├── register.html          # 用户注册页
│   ├── admin.html             # 管理后台
│   └── admin_login.html       # 管理员登录页
├── static/                    # 静态资源
│   ├── css/
│   │   └── style.css          # 样式文件（微信风格）
│   └── js/
│       └── chat.js            # 前端聊天逻辑
├── uploads/                   # 上传文件存储目录
├── chat.db                    # SQLite数据库文件
└── README.md                  # 项目说明文档
```

## 🔌 API 接口

### 用户接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/users` | GET | 获取用户列表 |
| `/api/user/nickname` | PUT | 修改昵称 |
| `/api/avatar` | POST | 上传头像 |
| `/api/avatar` | GET | 获取当前用户头像 |

### 好友接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/friends` | GET | 获取好友列表 |
| `/api/friend-requests` | GET | 获取好友请求列表 |
| `/api/friend-requests/count` | GET | 获取请求数量（红点提示） |
| `/api/friend-requests/{id}/accept` | POST | 接受好友请求 |
| `/api/friend-requests/{id}/reject` | POST | 拒绝好友请求 |
| `/api/friends/{id}` | DELETE | 删除好友 |
| `/api/search-users?q=keyword` | GET | 搜索用户 |

### 消息接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/messages/{receiver_id}` | GET | 获取与指定用户的消息 |
| `/api/upload` | POST | 上传图片/视频 |

### Socket.IO 事件

| 事件 | 说明 |
|------|------|
| `send_message` | 发送消息 |
| `receive_message` | 接收消息 |
| `send_friend_request` | 发送好友请求 |
| `friend_request_notification` | 好友请求通知 |
| `friend_request_accepted` | 好友请求接受通知 |

## 🔐 管理员说明

### 默认管理员账号

| 字段 | 值 |
|------|-----|
| 用户名 | `admin` |
| 密码 | `admin123` |

### 管理员功能

1. **用户管理**：查看所有用户，支持编辑用户昵称、状态、权限
2. **权限控制**：开启/关闭用户聊天权限、文件上传权限
3. **状态管理**：设置用户注册状态（pending/active）
4. **密码修改**：管理员可修改自己的密码
5. **消息管理**：查看和删除系统消息

## 📱 响应式设计

- **桌面端**：完整的双栏布局，左侧好友列表，右侧聊天区域
- **移动端**：自适应布局，支持触控操作

## 🗄️ 数据库结构

### users 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | TEXT | 用户唯一标识（UUID） |
| username | TEXT | 用户名（唯一） |
| password | TEXT | SHA-256 加密后的密码 |
| nickname | TEXT | 用户昵称 |
| avatar | TEXT | 头像URL |
| status | TEXT | 注册状态（pending/active） |
| chat_enabled | INTEGER | 聊天权限（1/0） |
| upload_enabled | INTEGER | 上传权限（1/0） |
| created_at | TEXT | 创建时间 |

### messages 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | TEXT | 消息唯一标识（UUID） |
| sender_id | TEXT | 发送者ID |
| receiver_id | TEXT | 接收者ID |
| content | TEXT | 消息内容 |
| file_type | TEXT | 文件类型（image/video） |
| file_url | TEXT | 文件URL |
| timestamp | TEXT | 发送时间 |

### friendships 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | TEXT | 关系唯一标识（UUID） |
| user1_id | TEXT | 用户1ID |
| user2_id | TEXT | 用户2ID |
| created_at | TEXT | 创建时间 |

### friend_requests 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | TEXT | 请求唯一标识（UUID） |
| sender_id | TEXT | 发送者ID |
| receiver_id | TEXT | 接收者ID |
| status | TEXT | 状态（pending/accepted/rejected） |
| created_at | TEXT | 创建时间 |

### admins 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | TEXT | 管理员唯一标识（UUID） |
| username | TEXT | 管理员用户名（唯一） |
| password | TEXT | SHA-256 加密后的密码 |
| created_at | TEXT | 创建时间 |

## ⚠️ 注意事项

1. **端口占用**：确保端口 9999 未被占用，如被占用可修改 `app.py` 中的端口配置
2. **文件存储**：上传的文件存储在 `uploads/` 目录下，请确保该目录存在且有写入权限
3. **密码安全**：生产环境请修改默认管理员密码，并使用 HTTPS 协议
4. **数据库备份**：定期备份 `chat.db` 文件以防数据丢失
5. **Eventlet 警告**：Eventlet 已弃用，生产环境建议迁移到其他异步框架

## 📄 许可证

MIT License

---

## 📊 功能完成度

| 功能模块 | 状态 | 说明 |
|----------|------|------|
| 用户注册/登录 | ✅ | 完成 |
| 头像上传 | ✅ | 完成 |
| 昵称管理 | ✅ | 完成 |
| 文字消息 | ✅ | 完成 |
| 图片消息 | ✅ | 完成 |
| 视频消息 | ✅ | 完成 |
| 表情功能 | ✅ | 完成（6大分类） |
| 好友搜索 | ✅ | 完成 |
| 好友请求 | ✅ | 完成 |
| 好友列表 | ✅ | 完成（带消息预览） |
| 好友删除 | ✅ | 完成（长按弹出） |
| 红点提示 | ✅ | 完成 |
| 管理员登录 | ✅ | 完成 |
| 用户管理 | ✅ | 完成 |
| 权限控制 | ✅ | 完成 |
| 密码修改 | ✅ | 完成 |
| 微信风格界面 | ✅ | 完成 |
| 响应式设计 | ✅ | 完成 |

**项目状态**：✅ 稳定运行

如有问题或建议，欢迎反馈！

---

*✨ 星聊 Star Chat - 让沟通更简单*
