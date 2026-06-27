# 📋 个人任务管理器

一个简洁实用的在线任务管理工具，支持任务的增删改查和完成标记。

## ✨ 功能

- ➕ 添加新任务
- ✅ 标记任务为已完成
- 🗑️ 删除不需要的任务
- 📊 任务列表按时间倒序排列
- 📱 响应式设计，手机电脑都能用

## 🛠️ 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python 3 + Flask |
| 数据库 | SQLite |
| 前端 | HTML + CSS + Jinja2 模板 |

## 🚀 本地运行

```bash
# 1. 克隆项目
git clone https://github.com/whk985211/todo-manager.git
cd todo-manager

# 2. 创建并激活虚拟环境
python -m venv venv

# Windows:
venv\Scripts\activate.bat

# Mac/Linux:
# source venv/bin/activate

# 3. 安装依赖
pip install flask

# 4. 运行
python app.py

# 5. 打开浏览器访问
# http://127.0.0.1:5000
```

## 📁 项目结构

```
todo-manager/
├── app.py          # 主程序
├── requirements.txt # 依赖列表
├── .gitignore      # Git 忽略规则
└── README.md       # 项目说明
```

## 📸 项目截图

> 运行后在浏览器中访问 http://127.0.0.1:5000 即可看到效果

## 🔮 后续计划

- [ ] 用户注册/登录
- [ ] 任务分类标签
- [ ] 截止日期提醒
- [ ] 云端部署
