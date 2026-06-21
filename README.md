# 文件管理平台

基于 Flask + SQLite 的文件管理平台，支持用户登录鉴、文件上传下载、多版本管理和会话持久化。

## 功能

- 登录鉴权
- 30天会话保持
- 文件上传
- 创建任务后继续追加上传文件
- 补充任务说明
- 删除任务时清理数据库记录和服务器文件
- 文件下载
- 多版本管理
- Flask + SQLite

---

## 环境要求

- Python 3.8+
- pip

---

## 快速开始

```bash
# 1. 克隆项目
git clone <repo-url>
cd filehub

# 2. 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env，设置 SECRET_KEY、ADMIN_USERNAME 和 ADMIN_PASSWORD

# 5. 启动
python app.py

# 6. 初始化管理员账号
# 浏览器访问: http://127.0.0.1:5000/init

# 7. 开始使用
# 浏览器访问: http://127.0.0.1:5000
```

---

## 配置

复制示例配置并修改密钥和管理员密码：

```bash
cp .env.example .env
```

必须设置：

| 变量 | 说明 |
|------|------|
| `SECRET_KEY` | Flask 会话密钥，请使用长随机字符串（建议 `python -c "import secrets; print(secrets.token_hex(32))"` 生成） |
| `ADMIN_USERNAME` | 初始化管理员用户名 |
| `ADMIN_PASSWORD` | 初始化管理员密码 |

可选配置：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `DATABASE_PATH` | `database.db` | SQLite 数据库文件路径 |
| `UPLOAD_FOLDER` | `uploads` | 上传文件存储目录 |
| `MAX_CONTENT_LENGTH` | `5368709120` (5GB) | 单次请求最大上传大小 |
| `REMEMBER_COOKIE_DAYS` | `30` | 会话保持天数 |
| `HOST` | `127.0.0.1` | 绑定地址 |
| `PORT` | `5000` | 绑定端口 |
| `FLASK_DEBUG` | `0` | 调试模式 (`1`/`true`/`yes` 开启) |

`.env`、`database.db` 和 `uploads/` 是本地运行数据，已被 Git 忽略，不应上传到 GitHub。

---

## 初始化数据库

启动应用后，**只需访问一次** `/init` 路由即可完成数据库表创建和管理员账号初始化：

```
http://127.0.0.1:5000/init
```

数据库表会在应用启动时自动创建，无需手动操作。`/init` 仅用于创建初始管理员账号。

如需重置，手动删除 `database.db` 文件并重新启动应用，然后再次访问 `/init`。

---

## 启动

```bash
python app.py
```

---

## 访问

http://127.0.0.1:5000

---

## 故障排除

### 端口 5000 被占用（macOS）

macOS 的 AirPlay Receiver 默认占用 5000 端口。解决方法：

- **方法一**：更换端口，启动前设置 `PORT=8080`，或在 `.env` 中设置 `PORT=8080`
- **方法二**：关闭 AirPlay：系统偏好设置 → 通用 → AirPlay接收器 → 关闭

### 数据库错误 `no such table`

如果手动删除了 `database.db` 但表未重建，重启应用即可自动重新创建。

### 上传目录不存在

`uploads/` 目录会在首次上传文件时自动创建，无需手动创建。
