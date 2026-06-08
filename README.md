# 文件管理平台

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

## 安装依赖

```bash
pip install -r requirements.txt
```

---

## 配置

复制示例配置并修改密钥和管理员密码：

```bash
cp .env.example .env
```

必须设置：

- `SECRET_KEY`：Flask 会话密钥，请使用长随机字符串
- `ADMIN_USERNAME`：初始化管理员用户名
- `ADMIN_PASSWORD`：初始化管理员密码

`.env`、`database.db` 和 `uploads/` 是本地运行数据，已被 Git 忽略，不应上传到 GitHub。

---

## 初始化数据库

```bash
python app.py
```

浏览器访问：

http://127.0.0.1:5000/init

管理员账号使用 `.env` 中的 `ADMIN_USERNAME` 和 `ADMIN_PASSWORD`。

---

## 启动

```bash
python app.py
```

---

## 访问

http://127.0.0.1:5000