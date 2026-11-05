import os
import sqlite3
from flask import Flask, jsonify, render_template_string, request, session
from werkzeug.middleware.proxy_fix import ProxyFix  # <--- 1. Importe o ProxyFix

app = Flask(__name__)


app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

app.secret_key = 'sua_chave_secreta_super_segura_aqui'
DB_NAME = 'database.db'


# Inicializa o Banco de Dados SQLite
def init_db():
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()

  # Tabela de Publicações (Feed)
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

  # Tabela de Comentários
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

  # Tabela do Chat
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

# Template HTML, CSS e JavaScript integrados com Tela de Login
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Comunidade App</title>
    <style>
        :root {
            --primary: #6366f1;
            --primary-hover: #4f46e5;
            --bg: #f8fafc;
            --card-bg: #ffffff;
            --text: #1e293b;
            --border: #e2e8f0;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--bg);
            color: var(--text);
            margin: 0;
            padding: 0;
        }

        /* --- TELA DE LOGIN --- */
        #login-screen {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
        }
        .login-card {
            background: white;
            padding: 2.5rem;
            border-radius: 12px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            width: 100%;
            max-width: 400px;
            box-sizing: border-box;
        }
        .login-card h2 { margin-top: 0; text-align: center; color: var(--primary); margin-bottom: 1.5rem; }
        .tab-buttons { display: flex; margin-bottom: 1.5rem; border-bottom: 2px solid var(--border); }
        .tab-btn {
            flex: 1;
            padding: 10px;
            background: none;
            border: none;
            font-weight: bold;
            cursor: pointer;
            color: #64748b;
            transition: 0.2s;
        }
        .tab-btn.active { color: var(--primary); border-bottom: 2px solid var(--primary); margin-bottom: -2px; }

        .form-group { margin-bottom: 1rem; }
        .form-group label { display: block; font-size: 0.85rem; font-weight: 600; margin-bottom: 4px; }
        .form-group input {
            width: 100%;
            padding: 10px;
            border: 1px solid var(--border);
            border-radius: 6px;
            box-sizing: border-box;
            font-size: 0.95rem;
        }
        .btn-submit {
            width: 100%;
            background: var(--primary);
            color: white;
            border: none;
            padding: 10px;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s;
        }
        .btn-submit:hover { background: var(--primary-hover); }

        /* --- TELA PRINCIPAL (DASHBOARD) --- */
        #app-screen { display: none; }
        header {
            background: var(--primary);
            color: white;
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        header h1 { margin: 0; font-size: 1.3rem; }
        .user-info { display: flex; gap: 15px; align-items: center; font-size: 0.9rem; }
        .btn-logout {
            background: #ef4444;
            color: white;
            border: none;
            padding: 5px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.85rem;
        }
        .btn-logout:hover { background: #dc2626; }

        .container {
            max-width: 1000px;
            margin: 2rem auto;
            padding: 0 1rem;
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 2rem;
        }
        @media(max-width: 768px) {
            .container { grid-template-columns: 1fr; }
        }

        .card {
            background: var(--card-bg);
            border-radius: 10px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            border: 1px solid var(--border);
        }
        .card h2 { margin-top: 0; font-size: 1.1rem; border-bottom: 2px solid var(--border); padding-bottom: 0.5rem; color: #334155; }
        
        input[type="text"], input[type="password"], textarea {
            width: 100%;
            padding: 8px 10px;
            margin-top: 5px;
            margin-bottom: 10px;
            border: 1px solid var(--border);
            border-radius: 6px;
            box-sizing: border-box;
            font-family: inherit;
        }
        button.action-btn {
            background: var(--primary);
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            transition: background 0.2s;
        }
        button.action-btn:hover { background: var(--primary-hover); }

        .admin-badge {
            background: #10b981;
            color: white;
            font-size: 0.75rem;
            padding: 2px 8px;
            border-radius: 10px;
            font-weight: bold;
        }

        .post-item {
            border-bottom: 1px solid var(--border);
            padding-bottom: 1rem;
            margin-bottom: 1rem;
        }
        .post-meta { font-size: 0.8rem; color: #64748b; margin-bottom: 0.3rem; }
        .post-title { font-size: 1.1rem; font-weight: bold; margin-bottom: 0.3rem; }
        .post-actions { display: flex; gap: 10px; margin-top: 0.5rem; align-items: center; }
        
        .comments-box {
            margin-top: 0.8rem;
            background: #f1f5f9;
            padding: 10px;
            border-radius: 6px;
        }
        .comment-item { font-size: 0.85rem; margin-bottom: 4px; border-bottom: 1px dashed #e2e8f0; padding-bottom: 4px; }
        
        .chat-container {
            height: 320px;
            overflow-y: scroll;
            border: 1px solid var(--border);
            padding: 10px;
            background: #fafafa;
            border-radius: 6px;
            margin-bottom: 10px;
            display: flex;
            flex-direction: column;
            gap: 6px;
        }
        .chat-msg { background: #e0e7ff; padding: 6px 10px; border-radius: 6px; font-size: 0.85rem; }
        .chat-msg strong { color: var(--primary); }
    </style>
</head>
<body>

    <!-- TELA DE LOGIN / ENTRADA -->
    <div id="login-screen">
        <div class="login-card">
            <h2>Bem-vindo(a)</h2>
            <div class="tab-buttons">
                <button class="tab-btn active" onclick="switchTab('visitor')" id="btn-tab-visitor">Visitante</button>
                <button class="tab-btn" onclick="switchTab('admin')" id="btn-tab-admin">Administrador</button>
            </div>

            <!-- Formulário Visitante -->
            <div id="form-visitor">
                <div class="form-group">
                    <label>Escolha seu Apelido:</label>
                    <input type="text" id="visitor-name" placeholder="Ex: João Silva">
                </div>
                <button class="btn-submit" onclick="loginAsVisitor()">Entrar como Visitante</button>
            </div>

            <!-- Formulário Administrador -->
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

    <!-- TELA PRINCIPAL DO APLICATIVO -->
    <div id="app-screen">
        <header>
            <h1 id="header-title">📢 Comunidade & Chat</h1>
            <div class="user-info">
                <span id="user-display-info"></span>
                <button class="btn-logout" onclick="logout()">Sair</button>
            </div>
        </header>

        <div class="container">
            <!-- Coluna Esquerda: Painel Admin (Se for adm) e Feed -->
            <div>
                <!-- Caixa de Publicação exclusiva para Admin -->
                <div class="card" id="admin-post-card" style="display: none; border-left: 4px solid #10b981;">
                    <h2>Nova Publicação (Painel Admin)</h2>
                    <label>Título:</label>
                    <input type="text" id="post-title" placeholder="Título da postagem">
                    <label>Conteúdo:</label>
                    <textarea id="post-content" rows="3" placeholder="Escreva o comunicado..."></textarea>
                    <button class="action-btn" onclick="createPost()">Publicar no Feed</button>
                </div>

                <!-- Feed de Publicações -->
                <div class="card">
                    <h2>Feed de Publicações</h2>
                    <div id="feed-container">Carregando feed...</div>
                </div>
            </div>

            <!-- Coluna Direita: Chat Global -->
            <div>
                <div class="card">
                    <h2>Chat Global</h2>
                    <div class="chat-container" id="chat-box">Carregando chat...</div>
                    <input type="text" id="chat-input" placeholder="Digite sua mensagem..." onkeypress="handleChatEnter(event)">
                    <button class="action-btn" onclick="sendChatMessage()" style="width: 100%;">Enviar Mensagem</button>
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
                infoEl.innerHTML = `Logado como: <strong>${username}</strong> <span class="admin-badge">ADMIN</span>`;
                document.getElementById('admin-post-card').style.display = 'block';
            } else {
                infoEl.innerHTML = `Visitante: <strong>${username}</strong>`;
                document.getElementById('admin-post-card').style.display = 'none';
            }

            loadFeed();
            loadChat();
            
            // Intervalo de atualização automática a cada 3 segundos
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

        // Verifica ao carregar se já existe sessão ativa
        window.onload = () => {
            fetch('/api/session')
            .then(res => res.json())
            .then(data => {
                if(data.logged) {
                    initApp(data.user, data.role);
                }
            });
        };

        // --- POSTS & FEED ---
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
                    container.innerHTML = '<p style="color:#64748b; font-size:0.9rem;">Nenhuma publicação no momento.</p>';
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
                        commentsHtml = '<div style="font-size:0.8rem; color:#94a3b8;">Nenhum comentário ainda.</div>';
                    }

                    html += `
                        <div class="post-item">
                            <div class="post-meta">Por <strong style="color:var(--primary);">${p.author}</strong> em ${p.created_at}</div>
                            <div class="post-title">${p.title}</div>
                            <div style="font-size: 0.95rem; margin-bottom: 8px;">${p.content}</div>
                            <div class="post-actions">
                                <button onclick="likePost(${p.id})" class="action-btn" style="background:#10b981; padding:4px 10px; font-size:0.8rem;">❤️ Curtir (${p.likes})</button>
                            </div>
                            <div class="comments-box">
                                <div style="font-size:0.85rem; font-weight:bold; margin-bottom:4px;">Comentários:</div>
                                <div style="margin-bottom:6px;">${commentsHtml}</div>
                                <div style="display:flex; gap:5px;">
                                    <input type="text" id="comment-input-${p.id}" placeholder="Escreva um comentário..." style="margin:0; padding:4px 8px; font-size:0.8rem;">
                                    <button onclick="addComment(${p.id})" class="action-btn" style="padding:4px 10px; font-size:0.8rem;">Enviar</button>
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
                body: JSON.stringify({content})
            })
            .then(res => res.json())
            .then(data => {
                if(data.success) {
                    input.value = '';
                    loadFeed();
                }
            });
        }

        // --- CHAT GLOBAL ---
        function sendChatMessage() {
            const input = document.getElementById('chat-input');
            const content = input.value.trim();
            if(!content) return;

            fetch('/api/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({content})
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
                box.innerHTML = html || '<div style="color:#94a3b8; font-size:0.85rem;">Nenhuma mensagem no chat.</div>';
            });
        }
    </script>
</body>
</html>
"""


# --- ROTAS DE AUTENTICAÇÃO E API ---
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

    # Credenciais de Administrador padrão (você pode alterar aqui)
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
  if 'user' not in session:
    return jsonify({'success': False, 'error': 'Não autenticado'}), 401

  data = request.get_json()
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute(
      'INSERT INTO comments (post_id, author, content) VALUES (?, ?, ?)',
      (post_id, session['user'], data['content']),
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
    if 'user' not in session:
      return jsonify({'success': False, 'error': 'Não autenticado'}), 401

    data = request.get_json()
    cursor.execute(
        'INSERT INTO chat (author, content) VALUES (?, ?)',
        (session['user'], data['content']),
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