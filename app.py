"""
个人任务管理器 — 你的第一个 Web 项目
"""
import os
import sqlite3
from flask import Flask, render_template_string, request, redirect

# ---- 配置 ----
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "tasks.db")

app = Flask(__name__)

# ============================================================
# 数据库部分
# ============================================================

def get_db():
    """连接数据库"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """创建 tasks 表"""
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


# ============================================================
# 页面模板
# ============================================================

HOME_PAGE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>任务管理器</title>
    <style>
        body {
            max-width: 600px;
            margin: 50px auto;
            font-family: -apple-system, sans-serif;
        }
        h1 { color: #333; }
        .task-list { list-style: none; padding: 0; }
        .task-item {
            padding: 12px;
            border-bottom: 1px solid #eee;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .task-item.done .task-title {
            text-decoration: line-through;
            color: #999;
        }
        .add-form { margin: 20px 0; }
        .add-form input {
            padding: 8px;
            width: 70%;
            font-size: 16px;
        }
        .add-form button {
            padding: 8px 20px;
            font-size: 16px;
            cursor: pointer;
        }
        .btn { text-decoration: none; padding: 4px 12px; border-radius: 4px; }
        .btn-done { background: #4CAF50; color: white; }
        .btn-delete { background: #f44336; color: white; }
    </style>
</head>
<body>
    <h1>📋 我的任务</h1>

    <form class="add-form" method="POST" action="/add">
        <input type="text" name="title" placeholder="输入新任务..." required autofocus>
        <button type="submit">添加</button>
    </form>

    <ul class="task-list">
        {% for task in tasks %}
        <li class="task-item {% if task.done %}done{% endif %}">
            <span class="task-title">{{ task.title }}</span>
            <span>
                {% if not task.done %}
                <a class="btn btn-done" href="/done/{{ task.id }}">✓ 完成</a>
                {% endif %}
                <a class="btn btn-delete" href="/delete/{{ task.id }}">删除</a>
            </span>
        </li>
        {% endfor %}
    </ul>

    {% if not tasks %}
    <p style="color: #999;">还没有任务，在上面添加一个吧 👆</p>
    {% endif %}
</body>
</html>
"""


# ============================================================
# 路由
# ============================================================

@app.route("/")
def index():
    """首页 — 显示所有任务"""
    conn = get_db()
    tasks = conn.execute("SELECT * FROM tasks ORDER BY created_at DESC").fetchall()
    conn.close()
    return render_template_string(HOME_PAGE, tasks=tasks)


@app.route("/add", methods=["POST"])
def add():
    """添加新任务"""
    title = request.form.get("title", "").strip()
    if title:
        conn = get_db()
        conn.execute("INSERT INTO tasks (title) VALUES (?)", (title,))
        conn.commit()
        conn.close()
    return redirect("/")


@app.route("/done/<int:task_id>")
def mark_done(task_id):
    """标记完成"""
    conn = get_db()
    conn.execute("UPDATE tasks SET done = 1 WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return redirect("/")


@app.route("/delete/<int:task_id>")
def delete(task_id):
    """删除任务"""
    conn = get_db()
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return redirect("/")


# ============================================================
# 启动
# ============================================================

if __name__ == "__main__":
    init_db()
    print(f"[OK] 数据库位置: {DB_PATH}")
    print(f"[OK] 数据库是否存在: {os.path.exists(DB_PATH)}")
    app.run(debug=True, use_reloader=False)  # 暂时关掉 reloader
