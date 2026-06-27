"""
个人任务管理器 — Lithos 风格 · 暗黑主题 · 光标交互背景
"""
import os, json, sqlite3
from flask import Flask, render_template_string, request, redirect, jsonify

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "tasks.db")
SPOTLIGHT_R = 260

app = Flask(__name__)


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL, done INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
    conn.commit()
    conn.close()


def get_stats():
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    done = conn.execute("SELECT COUNT(*) FROM tasks WHERE done = 1").fetchone()[0]
    conn.close()
    return total, done


# ============================================================
# 页面模板 — 内嵌完整 HTML/CSS/JS
# ============================================================

HOME_PAGE = r"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lithos — 任务管理器</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:ital,wght@1,400;1,500;1,600&display=swap" rel="stylesheet">
    <style>
        :root {
            --accent: #e8702a;
            --accent-glow: rgba(232,112,42,0.35);
            --success: #4ade80;
            --danger: rgba(239,68,68,0.85);
            --text: #ffffff;
            --text-secondary: rgba(255,255,255,0.65);
            --text-muted: rgba(255,255,255,0.35);
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', sans-serif;
            background: #000;
            color: var(--text);
            overflow-x: hidden;
            -webkit-font-smoothing: antialiased;
        }
        body.no-anim .hero-anim { animation: none; opacity: 1; }

        /* ===== 背景层 ===== */
        .bg-layer {
            position: fixed; inset: 0; z-index: 0;
            background-size: cover; background-position: center; background-repeat: no-repeat;
        }
        .bg-base {
            z-index: 10;
            animation: heroZoom 2s cubic-bezier(0.16,1,0.3,1) forwards;
        }
        .bg-reveal {
            z-index: 30;
            pointer-events: none;
            transition: opacity 0.5s;
        }
        .bg-overlay {
            position: fixed; inset: 0; z-index: 20;
            background: radial-gradient(ellipse at center, rgba(0,0,0,0.2) 0%, rgba(0,0,0,0.55) 100%);
            pointer-events: none;
        }
        .bg-switcher {
            position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%);
            z-index: 200;
            display: flex; gap: 8px;
            background: rgba(255,255,255,0.08);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(255,255,255,0.12);
            border-radius: 20px; padding: 6px;
        }
        .bg-dot {
            width: 12px; height: 12px; border-radius: 50%;
            cursor: pointer;
            transition: all 0.25s ease;
            border: 2px solid transparent;
        }
        .bg-dot.active {
            border-color: #fff;
            box-shadow: 0 0 12px rgba(255,255,255,0.4);
            transform: scale(1.15);
        }

        /* ===== 导航栏 ===== */
        .nav {
            position: fixed; top: 0; left: 0; right: 0; z-index: 100;
            display: flex; align-items: center; justify-content: space-between;
            padding: 14px 20px;
            background: rgba(0,0,0,0.65);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border-bottom: 1px solid rgba(255,255,255,0.08);
        }
        .nav-brand {
            display: flex; align-items: center; gap: 8px; text-decoration: none;
        }
        .nav-logo-svg { width: 24px; height: 24px; }
        .nav-wordmark {
            font-family: 'Playfair Display', serif; font-style: italic;
            font-size: 20px; color: #fff; letter-spacing: -0.02em;
        }
        .nav-stats { display: flex; align-items: center; gap: 18px; font-size: 13px; color: var(--text-secondary); }
        .nav-stat-val { color: #fff; font-weight: 600; }

        /* ===== 主内容区 ===== */
        .main {
            position: relative; z-index: 50;
            max-width: 640px; margin: 0 auto;
            padding: 120px 20px 100px;
            pointer-events: none;
        }
        .main > * { pointer-events: auto; }

        /* ===== Hero ===== */
        .hero { text-align: center; margin-bottom: 40px; }
        .hero h1 {
            font-size: clamp(2.2rem, 5.5vw, 3.8rem);
            font-weight: 300; letter-spacing: -0.04em; line-height: 0.95;
        }
        .hero .italic-line {
            display: block;
            font-family: 'Playfair Display', serif; font-style: italic; font-weight: 400;
            letter-spacing: -0.05em;
        }
        .hero .bold-line {
            display: block; font-weight: 600; letter-spacing: -0.06em; margin-top: -2px;
        }
        .hero-sub {
            margin-top: 12px; font-size: 14px; color: var(--text-secondary);
            max-width: 360px; margin-left: auto; margin-right: auto; line-height: 1.6;
        }

        /* ===== 进度条 ===== */
        .progress-wrap { margin-bottom: 36px; }
        .progress-bar {
            height: 4px; background: rgba(255,255,255,0.1);
            border-radius: 2px; overflow: hidden;
        }
        .progress-fill {
            height: 100%; border-radius: 2px;
            background: linear-gradient(90deg, var(--accent), #f59e4b);
            transition: width 0.6s cubic-bezier(0.16,1,0.3,1);
        }
        .progress-label {
            display: flex; justify-content: space-between;
            margin-top: 8px; font-size: 12px; color: var(--text-muted);
        }
        .progress-label strong { color: #fff; font-weight: 500; }

        /* ===== 输入 ===== */
        .add-form {
            display: flex; gap: 8px; margin-bottom: 28px;
        }
        .add-form input {
            flex: 1; padding: 13px 18px;
            font-size: 14px; font-family: 'Inter', sans-serif;
            background: rgba(0,0,0,0.55);
            border: 1px solid rgba(255,255,255,0.15);
            border-radius: 12px; color: #fff; outline: none;
            transition: all 0.25s ease;
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
        }
        .add-form input::placeholder { color: rgba(255,255,255,0.4); }
        .add-form input:focus {
            border-color: var(--accent);
            box-shadow: 0 0 0 3px var(--accent-glow);
            background: rgba(0,0,0,0.7);
        }
        .add-form button {
            padding: 13px 24px; font-size: 14px; font-weight: 600;
            font-family: 'Inter', sans-serif;
            background: var(--accent); color: #fff;
            border: none; border-radius: 12px; cursor: pointer;
            white-space: nowrap; letter-spacing: -0.01em;
            transition: all 0.2s ease;
        }
        .add-form button:hover {
            background: #d2611f; transform: scale(1.02);
            box-shadow: 0 6px 20px var(--accent-glow);
        }
        .add-form button:active { transform: scale(0.97); }

        /* ===== 任务卡片 ===== */
        .task-list { list-style: none; display: flex; flex-direction: column; gap: 6px; }
        .task-card {
            display: flex; align-items: center; justify-content: space-between;
            padding: 14px 18px;
            background: rgba(0,0,0,0.55);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 12px; gap: 10px;
            transition: all 0.3s ease;
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
        }
        .task-card:hover {
            background: rgba(0,0,0,0.72);
            border-color: rgba(255,255,255,0.2);
            transform: translateX(4px);
        }
        .task-card.done { opacity: 0.5; }
        .task-card.done:hover { opacity: 0.7; }
        .task-card.removing {
            opacity: 0; transform: translateX(40px);
            transition: all 0.35s ease;
        }
        .task-card.adding {
            animation: slideIn 0.4s cubic-bezier(0.16,1,0.3,1);
        }
        .task-left { display: flex; align-items: center; gap: 12px; min-width: 0; flex: 1; }
        .task-check {
            width: 22px; height: 22px; border-radius: 50%;
            border: 2px solid rgba(255,255,255,0.2);
            display: flex; align-items: center; justify-content: center;
            flex-shrink: 0; cursor: pointer;
            transition: all 0.25s ease;
            color: transparent; font-size: 11px;
            background: none;
        }
        .task-check:hover {
            border-color: var(--success);
            background: rgba(74,222,128,0.12);
        }
        .task-check.done-check {
            border-color: var(--success); background: var(--success); color: #000;
        }
        .task-title {
            font-size: 14px; font-weight: 450; color: #fff;
            overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
            transition: all 0.3s ease;
        }
        .task-card.done .task-title {
            text-decoration: line-through; color: var(--text-muted);
        }
        .task-time { font-size: 11px; color: var(--text-muted); flex-shrink: 0; }
        .task-del {
            width: 30px; height: 30px; border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            cursor: pointer; color: var(--text-muted); font-size: 13px;
            transition: all 0.2s ease; flex-shrink: 0; background: none; border: none;
        }
        .task-del:hover {
            background: rgba(239,68,68,0.18); color: var(--danger);
        }

        /* ===== 空状态 ===== */
        .empty-state {
            text-align: center; padding: 70px 20px; color: var(--text-muted);
        }
        .empty-state .empty-icon { font-size: 48px; margin-bottom: 16px; opacity: 0.35; }
        .empty-state p { font-size: 15px; }

        /* ===== 动画 ===== */
        @keyframes heroZoom { 0%{transform:scale(1.12)} 100%{transform:scale(1)} }
        @keyframes heroReveal { 0%{opacity:0;transform:translateY(28px);filter:blur(12px)} 100%{opacity:1;transform:translateY(0);filter:blur(0)} }
        @keyframes heroFadeUp { 0%{opacity:0;transform:translateY(20px)} 100%{opacity:1;transform:translateY(0)} }
        @keyframes slideIn { 0%{opacity:0;transform:translateY(-12px)} 100%{opacity:1;transform:translateY(0)} }
        .hero-anim { opacity: 0; animation-fill-mode: forwards; animation-timing-function: cubic-bezier(0.16,1,0.3,1); }
        .anim-reveal { animation-name: heroReveal; animation-duration: 1.1s; }
        .anim-fade { animation-name: heroFadeUp; animation-duration: 0.9s; }

        @media (prefers-reduced-motion: reduce) {
            .hero-anim, .bg-base { animation: none; opacity: 1; }
        }

        /* ===== 响应式 ===== */
        @media (max-width: 640px) {
            .nav { padding: 10px 14px; }
            .nav-stats { gap: 10px; font-size: 11px; }
            .nav-wordmark { font-size: 17px; }
            .main { padding: 100px 14px 80px; }
            .hero { margin-bottom: 28px; }
            .add-form { flex-direction: column; }
            .add-form button { width: 100%; }
            .task-card { padding: 12px 14px; }
            .task-time { display: none; }
        }
    </style>
</head>
<body>

    <!-- ==================== 背景层 ==================== -->
    <div class="bg-layer bg-base" id="bgBase"></div>
    <div class="bg-layer bg-reveal" id="bgReveal"></div>
    <div class="bg-overlay"></div>
    <canvas id="maskCanvas" style="display:none;position:fixed;inset:0;pointer-events:none;"></canvas>

    <!-- 背景切换器 -->
    <div class="bg-switcher" id="bgSwitcher"></div>

    <!-- ==================== 导航栏 ==================== -->
    <nav class="nav">
        <a href="/" class="nav-brand" onclick="event.preventDefault();loadTasks();">
            <svg class="nav-logo-svg" viewBox="0 0 256 256" fill="#ffffff">
                <path d="M 256 256 L 128 256 L 0 128 L 128 128 Z M 256 128 L 128 128 L 0 0 L 128 0 Z"/>
            </svg>
            <span class="nav-wordmark">Lithos</span>
        </a>
        <div class="nav-stats">
            <span>全部 <strong class="nav-stat-val" id="statTotal">0</strong></span>
            <span>完成 <strong class="nav-stat-val" id="statDone">0</strong></span>
        </div>
    </nav>

    <!-- ==================== 主内容 ==================== -->
    <main class="main">
        <header class="hero">
            <h1>
                <span class="italic-line hero-anim anim-reveal" style="animation-delay:0.15s">Stay focused,</span>
                <span class="bold-line hero-anim anim-reveal" style="animation-delay:0.35s">stay productive</span>
            </h1>
            <p class="hero-sub hero-anim anim-fade" style="animation-delay:0.6s">
                每一个任务，都是通向目标的一步。
            </p>
        </header>

        <div class="progress-wrap hero-anim anim-fade" style="animation-delay:0.7s">
            <div class="progress-bar"><div class="progress-fill" id="progressFill" style="width:0%"></div></div>
            <div class="progress-label">
                <span>完成进度</span>
                <span id="progressText"><strong>0%</strong> — 0/0</span>
            </div>
        </div>

        <form class="add-form hero-anim anim-fade" style="animation-delay:0.8s" id="addForm" autocomplete="off">
            <input type="text" name="title" id="taskInput" placeholder="添加一个新任务..." required autofocus>
            <button type="submit">添加任务</button>
        </form>

        <ul class="task-list" id="taskList"></ul>
        <div class="empty-state" id="emptyState">
            <div class="empty-icon">☕</div>
            <p>还没有任务，开始规划你的一天吧</p>
        </div>
    </main>

    <!-- ==================== 全部 JavaScript ==================== -->
    <script>
    // ========== 背景数据 ==========
    const BG_SETS = [
        {
            name: '地质层',
            base: 'https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260609_195923_b0ba8ace-1d1d-4f2c-9a28-1ab84b330680.png&w=1280&q=85',
            reveal: 'https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260609_201152_bba90a12-bf12-459f-91f0-51f237dbaf3b.png&w=1280&q=85'
        },
        {
            name: '极简暗色',
            base: 'data:image/svg+xml,' + encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="1" height="1"><rect fill="#0a0a0c"/></svg>'),
            reveal: 'data:image/svg+xml,' + encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="1" height="1"><rect fill="#1a1a20"/></svg>')
        },
        {
            name: '深邃蓝',
            base: 'data:image/svg+xml,' + encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400"><defs><radialGradient id="g" cx="50%" cy="40%"><stop offset="0%" stop-color="#1a1a3e"/><stop offset="100%" stop-color="#080812"/></radialGradient></defs><rect fill="url(#g)" width="400" height="400"/></svg>'),
            reveal: 'data:image/svg+xml,' + encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400"><defs><radialGradient id="g" cx="50%" cy="40%"><stop offset="0%" stop-color="#2a2a5e"/><stop offset="100%" stop-color="#0e0e1a"/></radialGradient></defs><rect fill="url(#g)" width="400" height="400"/></svg>')
        },
        {
            name: '暖橙暗纹',
            base: 'data:image/svg+xml,' + encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400"><defs><radialGradient id="g" cx="60%" cy="30%"><stop offset="0%" stop-color="#2a1a10"/><stop offset="100%" stop-color="#0a0806"/></radialGradient></defs><rect fill="url(#g)" width="400" height="400"/></svg>'),
            reveal: 'data:image/svg+xml,' + encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400"><defs><radialGradient id="g" cx="60%" cy="30%"><stop offset="0%" stop-color="#4a2a18"/><stop offset="100%" stop-color="#120c08"/></radialGradient></defs><rect fill="url(#g)" width="400" height="400"/></svg>')
        }
    ];

    // ========== DOM 引用 ==========
    const bgBase = document.getElementById('bgBase');
    const bgReveal = document.getElementById('bgReveal');
    const maskCanvas = document.getElementById('maskCanvas');
    const ctx = maskCanvas.getContext('2d');
    const taskList = document.getElementById('taskList');
    const emptyState = document.getElementById('emptyState');
    const taskInput = document.getElementById('taskInput');
    const addForm = document.getElementById('addForm');
    const statTotal = document.getElementById('statTotal');
    const statDone = document.getElementById('statDone');
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    const bgSwitcher = document.getElementById('bgSwitcher');

    // ========== 状态 ==========
    let currentBg = 0;
    let mouse = { x: -999, y: -999 };
    let smooth = { x: -999, y: -999 };
    let rafId = null;
    let spotlightActive = false;
    const SPOTLIGHT_R = 260;

    // ========== 背景设置 ==========
    function applyBg(idx) {
        currentBg = idx;
        const set = BG_SETS[idx];
        bgBase.style.backgroundImage = 'url(' + set.base + ')';
        bgReveal.style.backgroundImage = 'url(' + set.reveal + ')';

        // SVG 背景不显示 spotlight
        if (set.base.startsWith('data:')) {
            bgReveal.style.opacity = '0';
            spotlightActive = false;
            bgReveal.style.maskImage = 'none';
            bgReveal.style.webkitMaskImage = 'none';
        } else {
            bgReveal.style.opacity = '1';
            spotlightActive = true;
        }

        // 更新切换器
        document.querySelectorAll('.bg-dot').forEach((dot, i) => {
            dot.classList.toggle('active', i === idx);
        });
    }

    function buildSwitcher() {
        bgSwitcher.innerHTML = BG_SETS.map((s, i) =>
            '<div class="bg-dot' + (i === 0 ? ' active' : '') +
            '" style="background:' + (s.name === '地质层' ? '#8b7355' :
            s.name === '极简暗色' ? '#333' :
            s.name === '深邃蓝' ? '#3a3a7e' : '#c86838') +
            '" title="' + s.name + '" data-idx="' + i + '"></div>'
        ).join('');

        bgSwitcher.addEventListener('click', function(e) {
            const dot = e.target.closest('.bg-dot');
            if (!dot) return;
            applyBg(parseInt(dot.dataset.idx));
        });
    }

    // ========== 光标聚光灯 ==========
    function resizeCanvas() {
        maskCanvas.width = window.innerWidth;
        maskCanvas.height = window.innerHeight;
    }

    function drawSpotlight(cx, cy) {
        ctx.clearRect(0, 0, maskCanvas.width, maskCanvas.height);
        const grad = ctx.createRadialGradient(cx, cy, 0, cx, cy, SPOTLIGHT_R);
        grad.addColorStop(0, 'rgba(255,255,255,1)');
        grad.addColorStop(0.4, 'rgba(255,255,255,1)');
        grad.addColorStop(0.6, 'rgba(255,255,255,0.75)');
        grad.addColorStop(0.75, 'rgba(255,255,255,0.4)');
        grad.addColorStop(0.88, 'rgba(255,255,255,0.12)');
        grad.addColorStop(1, 'rgba(255,255,255,0)');
        ctx.fillStyle = grad;
        ctx.beginPath();
        ctx.arc(cx, cy, SPOTLIGHT_R, 0, Math.PI * 2);
        ctx.fill();

        const dataUrl = maskCanvas.toDataURL();
        bgReveal.style.maskImage = 'url(' + dataUrl + ')';
        bgReveal.style.webkitMaskImage = 'url(' + dataUrl + ')';
        bgReveal.style.maskSize = '100% 100%';
        bgReveal.style.webkitMaskSize = '100% 100%';
    }

    function animateSpotlight() {
        if (!spotlightActive) {
            rafId = requestAnimationFrame(animateSpotlight);
            return;
        }
        smooth.x += (mouse.x - smooth.x) * 0.1;
        smooth.y += (mouse.y - smooth.y) * 0.1;
        drawSpotlight(smooth.x, smooth.y);
        rafId = requestAnimationFrame(animateSpotlight);
    }

    document.addEventListener('mousemove', function(e) {
        mouse.x = e.clientX;
        mouse.y = e.clientY;
    });

    window.addEventListener('resize', resizeCanvas);

    // ========== API 调用（无刷新） ==========
    async function apiAdd(title) {
        const res = await fetch('/api/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title: title })
        });
        return res.json();
    }
    async function apiDone(id) {
        const res = await fetch('/api/done/' + id, { method: 'POST' });
        return res.json();
    }
    async function apiDelete(id) {
        const res = await fetch('/api/delete/' + id, { method: 'POST' });
        return res.json();
    }
    async function apiTasks() {
        const res = await fetch('/api/tasks');
        return res.json();
    }

    // ========== 渲染任务列表 ==========
    function formatTime(ts) {
        if (!ts) return '';
        return ts.substring(0, 16).replace('T', ' ');
    }

    function renderTask(task) {
        const li = document.createElement('li');
        li.className = 'task-card adding' + (task.done ? ' done' : '');
        li.dataset.id = task.id;
        li.innerHTML =
            '<div class="task-left">' +
            (task.done
                ? '<span class="task-check done-check">✓</span>'
                : '<span class="task-check" data-action="done" data-id="' + task.id + '" title="标记完成">✓</span>') +
            '<span class="task-title">' + escapeHtml(task.title) + '</span>' +
            '</div>' +
            '<span class="task-time">' + formatTime(task.created_at) + '</span>' +
            '<button class="task-del" data-action="delete" data-id="' + task.id + '" title="删除">✕</button>';

        // 事件委托
        li.querySelector('[data-action="done"]')?.addEventListener('click', handleDone);
        li.querySelector('[data-action="delete"]')?.addEventListener('click', handleDelete);

        return li;
    }

    function escapeHtml(str) {
        var div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    async function loadTasks() {
        const data = await apiTasks();
        taskList.innerHTML = '';
        if (data.tasks.length === 0) {
            emptyState.style.display = 'block';
            taskList.style.display = 'none';
        } else {
            emptyState.style.display = 'none';
            taskList.style.display = 'flex';
            data.tasks.forEach(function(t, i) {
                const li = renderTask(t);
                li.classList.add('hero-anim', 'anim-fade');
                li.style.animationDelay = (i * 0.04) + 's';
                taskList.appendChild(li);
            });
        }
        updateStats(data.total, data.done);
    }

    function updateStats(total, done) {
        statTotal.textContent = total;
        statDone.textContent = done;
        var pct = total > 0 ? Math.round(done / total * 100) : 0;
        progressFill.style.width = pct + '%';
        progressText.innerHTML = '<strong>' + pct + '%</strong> — ' + done + '/' + total;
    }

    // ========== 事件处理 ==========
    addForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        var title = taskInput.value.trim();
        if (!title) return;
        taskInput.value = '';
        var result = await apiAdd(title);
        if (result.ok) {
            var li = renderTask(result.task);
            taskList.insertBefore(li, taskList.firstChild);
            emptyState.style.display = 'none';
            taskList.style.display = 'flex';
            updateStats(result.total, result.done);
            // 移除 adding 动画 class（动画播完）
            setTimeout(function() { li.classList.remove('adding'); }, 500);

            // 重新绑定事件（对于新元素是直接绑定的）
            li.querySelector('[data-action="done"]')?.addEventListener('click', handleDone);
            li.querySelector('[data-action="delete"]')?.addEventListener('click', handleDelete);
        }
    });

    async function handleDone(e) {
        var el = e.currentTarget;
        var id = el.dataset.id;
        var card = el.closest('.task-card');
        var result = await apiDone(id);
        if (result.ok) {
            card.classList.add('done');
            // 替换为已完成标记
            var span = document.createElement('span');
            span.className = 'task-check done-check';
            span.textContent = '✓';
            el.replaceWith(span);
            updateStats(result.total, result.done);
        }
    }

    async function handleDelete(e) {
        var el = e.currentTarget;
        var id = el.dataset.id;
        var card = el.closest('.task-card');
        var result = await apiDelete(id);
        if (result.ok) {
            card.classList.add('removing');
            updateStats(result.total, result.done);
            setTimeout(function() {
                card.remove();
                if (taskList.children.length === 0) {
                    emptyState.style.display = 'block';
                    taskList.style.display = 'none';
                }
            }, 350);
        }
    }

    // ========== 初始化 ==========
    resizeCanvas();
    applyBg(0);
    buildSwitcher();
    loadTasks();
    animateSpotlight();
    </script>
</body>
</html>
"""


# ============================================================
# 页面路由
# ============================================================

@app.route("/")
def index():
    return render_template_string(HOME_PAGE)


# ============================================================
# JSON API（无刷新操作）
# ============================================================

@app.route("/api/tasks")
def api_tasks():
    conn = get_db()
    rows = conn.execute("SELECT * FROM tasks ORDER BY created_at DESC").fetchall()
    conn.close()
    tasks = [{"id": r["id"], "title": r["title"], "done": bool(r["done"]),
              "created_at": r["created_at"]} for r in rows]
    total, done = get_stats()
    return jsonify({"tasks": tasks, "total": total, "done": done})


@app.route("/api/add", methods=["POST"])
def api_add():
    data = request.get_json(force=True)
    title = data.get("title", "").strip()
    if not title:
        return jsonify({"ok": False, "error": "title required"}), 400
    conn = get_db()
    conn.execute("INSERT INTO tasks (title) VALUES (?)", (title,))
    conn.commit()
    task_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    total, done = get_stats()
    return jsonify({"ok": True, "task": {"id": row["id"], "title": row["title"],
                    "done": bool(row["done"]), "created_at": row["created_at"]},
                    "total": total, "done": done})


@app.route("/api/done/<int:task_id>", methods=["POST"])
def api_done(task_id):
    conn = get_db()
    conn.execute("UPDATE tasks SET done = 1 WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    total, done = get_stats()
    return jsonify({"ok": True, "total": total, "done": done})


@app.route("/api/delete/<int:task_id>", methods=["POST"])
def api_delete(task_id):
    conn = get_db()
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    total, done = get_stats()
    return jsonify({"ok": True, "total": total, "done": done})


# ============================================================
# 传统路由（兜底，非 JS 环境也能用）
# ============================================================

@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title", "").strip()
    if title:
        conn = get_db()
        conn.execute("INSERT INTO tasks (title) VALUES (?)", (title,))
        conn.commit()
        conn.close()
    return redirect("/")


@app.route("/done/<int:task_id>")
def mark_done(task_id):
    conn = get_db()
    conn.execute("UPDATE tasks SET done = 1 WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return redirect("/")


@app.route("/delete/<int:task_id>")
def delete(task_id):
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
    port = int(os.environ.get("PORT", 5000))
    print(f"[OK] DB: {DB_PATH}")
    print(f"[OK] Server: http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
