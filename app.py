import os
import sqlite3
from flask import Flask, jsonify, render_template_string, request, session
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
app.secret_key = 'sua_chave_secreta_super_segura_aqui'
DB_NAME = 'database.db'


# Inicializa o Banco de Dados SQLite
def init_db():
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()

  cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            author TEXT NOT NULL,
            likes INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

  cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER,
            author TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES posts (id)
        )
    ''')

  cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

  conn.commit()
  conn.close()


init_db()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ADEFS - Comunidade & Chat</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #2563eb;
            --primary-hover: #1d4ed8;
            --bg: #0b1329;
            --surface: #111e38;
            --surface-card: #1e293b;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --border: #2a3d66;
            --accent-green: #10b981;
            --accent-red: #ef4444;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
            background-color: var(--bg);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }

        /* --- TELA DE LOGIN --- */
        #login-screen {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background: linear-gradient(135deg, #070d1d 0%, #172554 100%);
            padding: 1rem;
        }

        .login-wrapper {
            display: flex;
            background: rgba(17, 30, 56, 0.85);
            backdrop-filter: blur(12px);
            border: 1px solid var(--border);
            border-radius: 24px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7);
            width: 100%;
            max-width: 850px;
            overflow: hidden;
        }

        .login-image-side {
            flex: 1;
            background: #070e1c;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 2.5rem;
            border-right: 1px solid var(--border);
            text-align: center;
        }

        .login-image-side img {
            width: 130px;
            height: 130px;
            object-fit: contain;
            border-radius: 16px;
            margin-bottom: 1.2rem;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.5);
        }

        .login-image-side h3 {
            color: #ffffff;
            font-size: 1.15rem;
            font-weight: 600;
            margin-bottom: 0.3rem;
        }

        .login-image-side p {
            color: var(--text-muted);
            font-size: 0.78rem;
            letter-spacing: 1px;
            text-transform: uppercase;
        }

        .login-form-side {
            flex: 1.2;
            padding: 3rem 2.5rem;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }

        .login-form-side h2 {
            font-size: 1.8rem;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 1.5rem;
            text-align: left;
        }

        .tab-buttons {
            display: flex;
            background: var(--bg);
            padding: 4px;
            border-radius: 10px;
            margin-bottom: 1.5rem;
            border: 1px solid var(--border);
        }

        .tab-btn {
            flex: 1;
            padding: 8px;
            background: none;
            border: none;
            font-weight: 600;
            cursor: pointer;
            color: var(--text-muted);
            border-radius: 8px;
            font-size: 0.85rem;
            transition: all 0.2s ease;
        }

        .tab-btn.active {
            background: var(--primary);
            color: white;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4);
        }

        .form-group {
            margin-bottom: 1.2rem;
        }

        .form-group label {
            display: block;
            font-size: 0.82rem;
            font-weight: 500;
            margin-bottom: 6px;
            color: var(--text-muted);
        }

        .form-group input, input[type="text"], input[type="password"], textarea {
            width: 100%;
            padding: 12px 14px;
            background: var(--bg);
            border: 1px solid var(--border);
            border-radius: 8px;
            color: var(--text-main);
            font-size: 0.95rem;
            outline: none;
            transition: border-color 0.2s ease;
        }

        .form-group input:focus, input[type="text"]:focus, input[type="password"]:focus, textarea:focus {
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15);
        }

        .btn-submit, .action-btn {
            width: 100%;
            background: linear-gradient(135deg, #3b82f6, var(--primary));
            color: white;
            border: none;
            padding: 12px;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.1s ease, box-shadow 0.2s ease;
            box-shadow: 0 4px 14px rgba(37, 99, 235, 0.3);
            margin-top: 5px;
        }

        .btn-submit:hover, .action-btn:hover {
            transform: translateY(-1px);
            box-shadow: 0 6px 20px rgba(37, 99, 235, 0.5);
        }

        @media(max-width: 768px) {
            .login-wrapper { flex-direction: column; max-width: 400px; }
            .login-image-side { padding: 1.5rem; }
            .login-form-side { padding: 2rem 1.5rem; }
        }

        /* --- DASHBOARD PRINCIPAL --- */
        #app-screen { display: none; }

        header {
            background: var(--surface);
            border-bottom: 1px solid var(--border);
            padding: 1.2rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky;
            top: 0;
            z-index: 100;
        }

        header h1 {
            font-size: 1.3rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 10px;
            color: #60a5fa;
        }

        .user-info {
            display: flex;
            gap: 15px;
            align-items: center;
            font-size: 0.9rem;
        }

        .admin-badge {
            background: rgba(16, 185, 129, 0.2);
            color: var(--accent-green);
            border: 1px solid var(--accent-green);
            font-size: 0.75rem;
            padding: 3px 10px;
            border-radius: 20px;
            font-weight: 600;
        }

        .btn-logout {
            background: rgba(239, 68, 68, 0.15);
            color: var(--accent-red);
            border: 1px solid var(--accent-red);
            padding: 6px 14px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.85rem;
            font-weight: 600;
            transition: all 0.2s ease;
        }

        .btn-logout:hover {
            background: var(--accent-red);
            color: white;
        }

        .container {
            max-width: 1200px;
            margin: 2rem auto;
            padding: 0 1.5rem;
            display: grid;
            grid-template-columns: 1.8fr 1.2fr;
            gap: 2rem;
            width: 100%;
        }

        @media(max-width: 868px) {
            .container { grid-template-columns: 1fr; }
        }

        .card {
            background: var(--surface);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            border: 1px solid var(--border);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
        }

        .card h2 {
            font-size: 1.15rem;
            font-weight: 600;
            margin-bottom: 1.2rem;
            padding-bottom: 0.6rem;
            border-bottom: 1px solid var(--border);
            display: flex;
            align-items: center;
            gap: 8px;
        }

        /* --- FEED & POSTS --- */
        .post-item {
            background: var(--bg);
            border-radius: 10px;
            padding: 1.2rem;
            margin-bottom: 1.2rem;
            border: 1px solid var(--border);
        }

        .post-meta {
            font-size: 0.82rem;
            color: var(--text-muted);
            margin-bottom: 0.4rem;
        }

        .post-title {
            font-size: 1.2rem;
            font-weight: 600;
            color: var(--text-main);
            margin-bottom: 0.5rem;
        }

        .post-content {
            font-size: 0.95rem;
            color: #cbd5e1;
            line-height: 1.5;
            margin-bottom: 1rem;
        }

        .comments-box {
            margin-top: 1rem;
            background: var(--surface);
            padding: 1rem;
            border-radius: 8px;
            border: 1px solid var(--border);
        }

        .comment-item {
            font-size: 0.88rem;
            padding: 6px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }

        .comment-item:last-child { border-bottom: none; }

        /* --- CHAT --- */
        .chat-container {
            height: 380px;
            overflow-y: auto;
            background: var(--bg);
            border-radius: 10px;
            padding: 12px;
            border: 1px solid var(--border);
            margin-bottom: 12px;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .chat-msg {
            background: var(--surface);
            padding: 8px 12px;
            border-radius: 8px;
            font-size: 0.9rem;
            border-left: 3px solid var(--primary);
        }

        .chat-msg strong {
            color: #60a5fa;
            margin-right: 5px;
        }
    </style>
</head>
<body>

    <!-- TELA DE LOGIN ESTILIZADA -->
    <div id="login-screen">
        <div class="login-wrapper">
            <!-- Lado esquerdo com a Logo Local do Projeto -->
            <div class="login-image-side">
                <img src="/static/logo.png" alt="ADEFS Logo">
                <h3>Assembleia de Deus</h3>
                <p>Feira de Santana - ADEFS</p>
            </div>

            <!-- Lado direito com o formulário de Login Azul -->
            <div class="login-form-side">
                <h2>Login</h2>
                <div class="tab-buttons">
                    <button class="tab-btn active" onclick="switchTab('visitor')" id="btn-tab-visitor">Visitante</button>
                    <button class="tab-btn" onclick="switchTab('admin')" id="btn-tab-admin">Admin</button>
                </div>

                <!-- Form Visitante -->
                <div id="form-visitor">
                    <div class="form-group">
                        <label>Seu Apelido / Nome:</label>
                        <input type="text" id="visitor-name" placeholder="Ex: Irmão João">
                    </div>
                    <button class="btn-submit" onclick="loginAsVisitor()">Entrar</button>
                </div>

                <!-- Form Administrador -->
                <div id="form-admin" style="display: none;">
                    <div class="form-group">
                        <label>Usuário Admin:</label>
                        <input type="text" id="admin-user" placeholder="Usuário">
                    </div>
                    <div class="form-group">
                        <label>Senha:</label>
                        <input type="password" id="admin-pass" placeholder="Senha">
                    </div>
                    <button class="btn-submit" onclick="loginAsAdmin()">Entrar como Admin</button>
                </div>
            </div>
        </div>
    </div>

    <!-- TELA PRINCIPAL (DASHBOARD) -->
    <div id="app-screen">
        <header>
            <h1>🔥 ADEFS - Comunidade & Chat</h1>
            <div class="user-info">
                <span id="user-display-info"></span>
                <button class="btn-logout" onclick="logout()">Sair</button>
            </div>
        </header>

        <div class="container">
            <!-- Feed e Painel de Admin -->
            <div>
                <div class="card" id="admin-post-card" style="display: none; border-left: 4px solid var(--accent-green);">
                    <h2>📌 Painel do Administrador</h2>
                    <div class="form-group">
                        <label>Título da Publicação:</label>
                        <input type="text" id="post-title" placeholder="Escreva o título...">
                    </div>
                    <div class="form-group">
                        <label>Conteúdo:</label>
                        <textarea id="post-content" rows="3" placeholder="Escreva o comunicado..."></textarea>
                    </div>
                    <button class="action-btn" onclick="createPost()">Publicar no Feed</button>
                </div>

                <div class="card">
                    <h2>📰 Feed de Publicações</h2>
                    <div id="feed-container">Carregando conteúdos...</div>
                </div>
            </div>

            <!-- Chat Global -->
            <div>
                <div class="card">
                    <h2>💬 Chat Global</h2>
                    <div class="chat-container" id="chat-box">Carregando chat...</div>
                    <input type="text" id="chat-input" placeholder="Digite uma mensagem..." onkeypress="handleChatEnter(event)">
                    <button class="action-btn" onclick="sendChatMessage()" style="margin-top: 5px;">Enviar Mensagem</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentUser = null;
        let userRole = null;

        function switchTab(type) {
            if(type === 'visitor') {
                document.getElementById('btn-tab-visitor').classList.add('active');
                document.getElementById('btn-tab-admin').classList.remove('active');
                document.getElementById('form-visitor').style.display = 'block';
                document.getElementById('form-admin').style.display = 'none';
            } else {
                document.getElementById('btn-tab-admin').classList.add('active');
                document.getElementById('btn-tab-visitor').classList.remove('active');
                document.getElementById('form-admin').style.display = 'block';
                document.getElementById('form-visitor').style.display = 'none';
            }
        }

        function loginAsVisitor() {
            const name = document.getElementById('visitor-name').value.trim();
            if(!name) { alert('Por favor, informe seu apelido.'); return; }
            
            fetch('/api/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({type: 'visitor', name: name})
            })
            .then(res => res.json())
            .then(data => {
                if(data.success) {
                    initApp(data.user, data.role);
                }
            });
        }

        function loginAsAdmin() {
            const user = document.getElementById('admin-user').value.trim();
            const pass = document.getElementById('admin-pass').value;
            
            fetch('/api/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({type: 'admin', username: user, password: pass})
            })
            .then(res => res.json())
            .then(data => {
                if(data.success) {
                    initApp(data.user, data.role);
                } else {
                    alert('Usuário ou senha de administrador incorretos!');
                }
            });
        }

        function initApp(username, role) {
            currentUser = username;
            userRole = role;

            document.getElementById('login-screen').style.display = 'none';
            document.getElementById('app-screen').style.display = 'block';

            const infoEl = document.getElementById('user-display-info');
            if(role === 'admin') {
                infoEl.innerHTML = `<strong>${username}</strong> <span class="admin-badge">ADMIN</span>`;
                document.getElementById('admin-post-card').style.display = 'block';
            } else {
                infoEl.innerHTML = `Visitante: <strong>${username}</strong>`;
                document.getElementById('admin-post-card').style.display = 'none';
            }

            loadFeed();
            loadChat();
            
            setInterval(() => {
                loadFeed();
                loadChat();
            }, 3000);
        }

        function logout() {
            fetch('/api/logout', {method: 'POST'}).then(() => {
                window.location.reload();
            });
        }

        window.onload = () => {
            fetch('/api/session')
            .then(res => res.json())
            .then(data => {
                if(data.logged) {
                    initApp(data.user, data.role);
                }
            });
        };

        function createPost() {
            const title = document.getElementById('post-title').value;
            const content = document.getElementById('post-content').value;
            if(!title || !content) { alert('Preencha todos os campos!'); return; }

            fetch('/api/posts', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({title, content})
            })
            .then(res => res.json())
            .then(data => {
                if(data.success) {
                    document.getElementById('post-title').value = '';
                    document.getElementById('post-content').value = '';
                    loadFeed();
                } else {
                    alert(data.error);
                }
            });
        }

        function loadFeed() {
            fetch('/api/posts')
            .then(res => res.json())
            .then(posts => {
                const container = document.getElementById('feed-container');
                if(posts.length === 0) {
                    container.innerHTML = '<p style="color:var(--text-muted); font-size:0.9rem;">Nenhuma publicação no momento.</p>';
                    return;
                }
                let html = '';
                posts.forEach(p => {
                    let commentsHtml = '';
                    if(p.comments && p.comments.length > 0) {
                        p.comments.forEach(c => {
                            commentsHtml += `<div class="comment-item"><strong>${c.author}:</strong> ${c.content}</div>`;
                        });
                    } else {
                        commentsHtml = '<div style="font-size:0.8rem; color:var(--text-muted);">Nenhum comentário ainda.</div>';
                    }

                    html += `
                        <div class="post-item">
                            <div class="post-meta">Por <strong style="color:#60a5fa;">${p.author}</strong> • ${p.created_at}</div>
                            <div class="post-title">${p.title}</div>
                            <div class="post-content">${p.content}</div>
                            <div class="post-actions">
                                <button onclick="likePost(${p.id})" class="action-btn" style="background:rgba(16, 185, 129, 0.2); border:1px solid var(--accent-green); color:var(--accent-green); width:auto; padding:5px 12px; font-size:0.85rem;">❤️ Curtir (${p.likes})</button>
                            </div>
                            <div class="comments-box">
                                <div style="font-size:0.85rem; font-weight:600; margin-bottom:6px;">Comentários:</div>
                                <div style="margin-bottom:8px;">${commentsHtml}</div>
                                <div style="display:flex; gap:8px;">
                                    <input type="text" id="comment-input-${p.id}" placeholder="Escreva um comentário..." style="margin:0; padding:8px 10px; font-size:0.85rem;">
                                    <button onclick="addComment(${p.id})" class="action-btn" style="width:auto; padding:8px 14px; font-size:0.85rem;">Enviar</button>
                                </div>
                            </div>
                        </div>
                    `;
                });
                container.innerHTML = html;
            });
        }

        function likePost(id) {
            fetch(`/api/posts/${id}/like`, {method: 'POST'}).then(() => loadFeed());
        }

        function addComment(postId) {
            const input = document.getElementById(`comment-input-${postId}`);
            const content = input.value.trim();
            if(!content) return;

            fetch(`/api/posts/${postId}/comment`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({author: currentUser, content: content})
            })
            .then(res => res.json())
            .then(data => {
                if(data.success) {
                    input.value = '';
                    loadFeed();
                }
            });
        }

        function sendChatMessage() {
            const input = document.getElementById('chat-input');
            const content = input.value.trim();
            if(!content) return;

            fetch('/api/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({author: currentUser, content: content})
            })
            .then(res => res.json())
            .then(data => {
                if(data.success) {
                    input.value = '';
                    loadChat();
                    const chatBox = document.getElementById('chat-box');
                    chatBox.scrollTop = chatBox.scrollHeight;
                }
            });
        }

        function handleChatEnter(e) {
            if(e.key === 'Enter') sendChatMessage();
        }

        function loadChat() {
            fetch('/api/chat')
            .then(res => res.json())
            .then(msgs => {
                const box = document.getElementById('chat-box');
                let html = '';
                msgs.forEach(m => {
                    html += `<div class="chat-msg"><strong>${m.author}:</strong> ${m.content}</div>`;
                });
                box.innerHTML = html || '<div style="color:var(--text-muted); font-size:0.85rem;">Nenhuma mensagem no chat.</div>';
            });
        }
    </script>
</body>
</html>
"""


@app.route('/')
def index():
  return render_template_string(HTML_TEMPLATE)


@app.route('/api/session', methods=['GET'])
def check_session():
  if 'user' in session:
    return jsonify(
        {'logged': True, 'user': session['user'], 'role': session['role']}
    )
  return jsonify({'logged': False})


@app.route('/api/login', methods=['POST'])
def login():
  data = request.get_json()
  login_type = data.get('type')

  if login_type == 'visitor':
    name = data.get('name', '').strip()
    if not name:
      return jsonify({'success': False, 'error': 'Nome obrigatório'})
    session['user'] = name
    session['role'] = 'visitor'
    return jsonify({'success': True, 'user': name, 'role': 'visitor'})

  elif login_type == 'admin':
    username = data.get('username')
    password = data.get('password')

    ADMIN_USER = 'admin'
    ADMIN_PASS = 'admin123'

    if username == ADMIN_USER and password == ADMIN_PASS:
      session['user'] = 'Administrador'
      session['role'] = 'admin'
      return jsonify({'success': True, 'user': 'Administrador', 'role': 'admin'})
    else:
      return jsonify({'success': False, 'error': 'Credenciais inválidas'})

  return jsonify({'success': False})


@app.route('/api/logout', methods=['POST'])
def logout():
  session.clear()
  return jsonify({'success': True})


@app.route('/api/posts', methods=['GET', 'POST'])
def manage_posts():
  conn = sqlite3.connect(DB_NAME)
  conn.row_factory = sqlite3.Row
  cursor = conn.cursor()

  if request.method == 'POST':
    if session.get('role') != 'admin':
      return (
          jsonify({
              'success': False,
              'error': 'Apenas administradores podem publicar.',
          }),
          403,
      )

    data = request.get_json()
    cursor.execute(
        'INSERT INTO posts (title, content, author) VALUES (?, ?, ?)',
        (data['title'], data['content'], session.get('user', 'Administrador')),
    )
    conn.commit()
    conn.close()
    return jsonify({'success': True})

  cursor.execute('SELECT * FROM posts ORDER BY id DESC')
  posts_rows = cursor.fetchall()
  posts = []
  for row in posts_rows:
    post = dict(row)
    cursor.execute(
        'SELECT * FROM comments WHERE post_id = ? ORDER BY id ASC',
        (post['id'],),
    )
    post['comments'] = [dict(c) for c in cursor.fetchall()]
    posts.append(post)

  conn.close()
  return jsonify(posts)


@app.route('/api/posts/<int:post_id>/like', methods=['POST'])
def like_post(post_id):
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute('UPDATE posts SET likes = likes + 1 WHERE id = ?', (post_id,))
  conn.commit()
  conn.close()
  return jsonify({'success': True})


@app.route('/api/posts/<int:post_id>/comment', methods=['POST'])
def add_comment(post_id):
  data = request.get_json()
  author = data.get('author') or 'Visitante'
  content = data.get('content')
  if not content:
    return jsonify({'success': False, 'error': 'Conteúdo vazio'}), 400

  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute(
      'INSERT INTO comments (post_id, author, content) VALUES (?, ?, ?)',
      (post_id, author, content),
  )
  conn.commit()
  conn.close()
  return jsonify({'success': True})


@app.route('/api/chat', methods=['GET', 'POST'])
def manage_chat():
  conn = sqlite3.connect(DB_NAME)
  conn.row_factory = sqlite3.Row
  cursor = conn.cursor()

  if request.method == 'POST':
    data = request.get_json()
    author = data.get('author') or 'Visitante'
    content = data.get('content')
    if not content:
      return jsonify({'success': False, 'error': 'Mensagem vazia'}), 400

    cursor.execute(
        'INSERT INTO chat (author, content) VALUES (?, ?)',
        (author, content),
    )
    conn.commit()
    conn.close()
    return jsonify({'success': True})

  cursor.execute('SELECT * FROM chat ORDER BY id ASC LIMIT 50')
  messages = [dict(row) for row in cursor.fetchall()]
  conn.close()
  return jsonify(messages)


if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0', port=5000)