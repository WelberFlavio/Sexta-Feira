import os
import sys
import json
import webview

# ==========================================
# VARREDURA DAS PASTAS REAIS NO DISCO C:\Projetos
# ==========================================
def ler_planilhas_reais():
    base_dir = r"C:\Projetos"
    
    pastas_alvo = {
        "atualizacao": {
            "caminhos_possiveis": [
                os.path.join(base_dir, "Atualização"),
                os.path.join(base_dir, "Atualizacao")
            ],
            "titulo": "Atualização",
            "cor": "#f59e0b",
            "icon": "🔄",
            "acoes_padrao": ["Ativar script Atualização"]
        },
        "divisao": {
            "caminhos_possiveis": [
                os.path.join(base_dir, "Divisao"),
                os.path.join(base_dir, "Divisão")
            ],
            "titulo": "Divisão",
            "cor": "#38bdf8",
            "icon": "✂️",
            "acoes_padrao": ["Script de Divisão", "Excluir Linhas"]
        },
        "planilhas": {
            "caminhos_possiveis": [
                os.path.join(base_dir, "Planilhas")
            ],
            "titulo": "Planilhas",
            "cor": "#ec4899",
            "icon": "📊",
            "acoes_padrao": ["Criar Abas", "Criar Aditivo"]
        }
    }

    resultado = {}
    
    for key, info in pastas_alvo.items():
        arquivos = []
        caminho_encontrado = ""

        for caminho in info["caminhos_possiveis"]:
            if os.path.exists(caminho):
                caminho_encontrado = caminho
                try:
                    for item in os.listdir(caminho):
                        full_path = os.path.join(caminho, item)
                        if os.path.isfile(full_path) and not item.startswith("~$"):
                            arquivos.append(item)
                except Exception as e:
                    print(f"Erro ao acessar {caminho}: {e}")
                break

        if key == "atualizacao" and not arquivos:
            arquivos = ["CED_PCMS_Autoeng_Parte 02_Rev.01.xlsx"]
        elif key == "divisao" and not arquivos:
            arquivos = ["ACII_PCMS_Valmir Lima_Rev.01.xlsx", "ACII_PCMS_Valmir Lima_Rev.02.xlsx"]
        elif key == "planilhas" and not arquivos:
            arquivos = ["CED_PCMS_Autoeng_Parte 01.xlsx", "CED_PCMS_Autoeng_Parte 02.xlsx"]

        resultado[key] = {
            "titulo": info["titulo"],
            "caminho": caminho_encontrado or info["caminhos_possiveis"][0],
            "cor": info["cor"],
            "icon": info["icon"],
            "acoes_padrao": info["acoes_padrao"],
            "arquivos": arquivos
        }

    return resultado


# ==========================================
# ENGINE HTML / CANVAS / FLUXOGRAMA
# ==========================================
HTML_CONTENT = r"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sexta-Feira AI • Engine de Fluxograma de Processos</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background-color: #080a11;
            color: #f3e8ff;
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            overflow: hidden;
            width: 100vw;
            height: 100vh;
        }

        /* MODAL DE ENTRADA DE PROCESSOS */
        #modalContainer {
            position: fixed;
            inset: 0;
            background: rgba(4, 6, 14, 0.95);
            backdrop-filter: blur(20px);
            z-index: 50;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: opacity 0.4s ease, visibility 0.4s ease;
        }

        #modalContainer.hidden-modal {
            opacity: 0;
            visibility: hidden;
            pointer-events: none;
        }

        .modal-box {
            width: 740px;
            max-width: 94vw;
            background: rgba(15, 18, 30, 0.96);
            border: 1px solid rgba(168, 85, 247, 0.4);
            border-radius: 22px;
            padding: 28px;
            box-shadow: 0 20px 50px rgba(0,0,0,0.9), 0 0 40px rgba(168, 85, 247, 0.25);
        }

        .tab-btn {
            padding: 8px 16px;
            border-radius: 10px;
            font-size: 11.5px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s ease;
            color: #a78bfa;
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(168, 85, 247, 0.2);
        }

        .tab-btn.active {
            background: linear-gradient(135deg, #7c3aed 0%, #00d2ff 100%);
            color: #fff;
            border-color: transparent;
            box-shadow: 0 0 15px rgba(0, 210, 255, 0.4);
        }

        .task-textarea {
            width: 100%;
            height: 150px;
            background: rgba(8, 10, 18, 0.85);
            border: 1px solid rgba(168, 85, 247, 0.35);
            border-radius: 14px;
            padding: 16px;
            font-size: 13.5px;
            color: #f3e8ff;
            outline: none;
            resize: none;
            font-family: inherit;
            line-height: 1.6;
        }

        .task-textarea:focus {
            border-color: #00d2ff;
            box-shadow: 0 0 20px rgba(0, 210, 255, 0.35);
        }

        .history-card {
            background: rgba(124, 58, 237, 0.1);
            border: 1px solid rgba(168, 85, 247, 0.3);
            border-radius: 12px;
            padding: 12px;
            margin-bottom: 10px;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .history-card:hover {
            background: rgba(124, 58, 237, 0.22);
            border-color: #00d2ff;
            transform: translateX(4px);
        }

        .btn-generate {
            background: linear-gradient(135deg, #7c3aed 0%, #00d2ff 100%);
            color: #fff;
            font-weight: 800;
            font-size: 12px;
            letter-spacing: 1px;
            padding: 13px 26px;
            border-radius: 12px;
            cursor: pointer;
            border: none;
            text-transform: uppercase;
            box-shadow: 0 0 22px rgba(124, 58, 237, 0.5);
            transition: all 0.3s ease;
        }

        .btn-generate:hover {
            transform: scale(1.03);
            box-shadow: 0 0 32px rgba(0, 210, 255, 0.85);
        }

        /* PAINEL SELETOR DE DIRETRIZES DA PLANILHA */
        #actionSelectorPanel {
            position: fixed;
            top: 80px;
            right: 25px;
            width: 330px;
            background: rgba(15, 18, 30, 0.96);
            border: 1px solid rgba(0, 210, 255, 0.5);
            border-radius: 18px;
            padding: 20px;
            z-index: 30;
            backdrop-filter: blur(15px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.8), 0 0 20px rgba(0, 210, 255, 0.25);
            display: none;
        }

        #actionSelectorPanel.active { display: block; }

        .action-checkbox-item {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 8px 12px;
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 8px;
            margin-bottom: 8px;
            cursor: pointer;
            font-size: 12px;
            color: #e2e8f0;
        }

        .action-checkbox-item:hover {
            background: rgba(0, 210, 255, 0.12);
            border-color: rgba(0, 210, 255, 0.4);
        }

        .action-checkbox-item input {
            accent-color: #00d2ff;
            width: 16px;
            height: 16px;
            cursor: pointer;
        }

        /* CANVAS OVERLAY DO FLUXOGRAMA */
        #canvasContainer {
            position: fixed;
            inset: 0;
            background: #080a11;
            z-index: 10;
            display: flex;
            flex-direction: column;
            opacity: 0;
            visibility: hidden;
            pointer-events: none;
            transition: opacity 0.5s ease, visibility 0.5s ease;
        }

        #canvasContainer.active {
            opacity: 1;
            visibility: visible;
            pointer-events: auto;
        }

        #workflowCanvas {
            width: 100vw;
            height: 100vh;
            display: block;
            cursor: grab;
        }

        #workflowCanvas:active {
            cursor: grabbing;
        }

        .top-bar {
            position: absolute;
            top: 20px;
            left: 25px;
            right: 25px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            z-index: 20;
            pointer-events: none;
        }

        .top-bar * { pointer-events: auto; }

        .badge-title {
            background: rgba(14, 18, 30, 0.92);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(0, 210, 255, 0.4);
            padding: 8px 22px;
            border-radius: 25px;
            font-size: 12px;
            font-weight: 800;
            color: #00d2ff;
            letter-spacing: 1px;
            box-shadow: 0 0 22px rgba(0, 210, 255, 0.25);
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .progress-badge {
            background: rgba(16, 185, 129, 0.15);
            border: 1px solid rgba(16, 185, 129, 0.4);
            color: #6ee7b7;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 700;
        }

        .btn-action {
            background: rgba(225, 29, 72, 0.2);
            border: 1px solid rgba(225, 29, 72, 0.5);
            color: #fda4af;
            padding: 8px 18px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .btn-action:hover {
            background: rgba(225, 29, 72, 0.7);
            color: #fff;
        }

        .btn-add-card {
            background: rgba(168, 85, 247, 0.25);
            border: 1px solid rgba(168, 85, 247, 0.6);
            color: #e9d5ff;
            padding: 8px 18px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .btn-add-card:hover {
            background: rgba(168, 85, 247, 0.7);
            color: #fff;
        }

        .btn-clear-cables {
            background: rgba(245, 158, 11, 0.2);
            border: 1px solid rgba(245, 158, 11, 0.5);
            color: #fde68a;
            padding: 8px 18px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .btn-clear-cables:hover {
            background: rgba(245, 158, 11, 0.7);
            color: #fff;
        }

        .hint-bar {
            position: absolute;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(15, 18, 30, 0.88);
            border: 1px solid rgba(255, 255, 255, 0.12);
            padding: 8px 20px;
            border-radius: 20px;
            font-size: 11.5px;
            color: #a7f3d0;
            z-index: 20;
            pointer-events: none;
            box-shadow: 0 10px 25px rgba(0,0,0,0.5);
        }
    </style>
</head>
<body>

    <!-- MODAL DE ENTRADA DE PROCESSOS -->
    <div id="modalContainer">
        <div class="modal-box">
            <div class="flex justify-between items-center border-b border-purple-900/50 pb-3 mb-4">
                <div class="flex items-center gap-2.5">
                    <span class="w-3.5 h-3.5 rounded-full bg-cyan-400 animate-pulse"></span>
                    <h2 class="text-lg font-bold text-white tracking-wide">PAINEL DE PROCESSOS & DIAGRAMAS</h2>
                </div>
            </div>

            <!-- ABAS DE NAVEGAÇÃO -->
            <div class="flex gap-2 mb-4">
                <button id="btnTabMeiaNoite" class="tab-btn active" onclick="trocarAba('meiaNoite')">🌙 FLUXOGRAMA MEIA NOITE</button>
                <button id="btnTabManual" class="tab-btn" onclick="trocarAba('manual')">📝 Digitar Manualmente</button>
                <button id="btnTabIA" class="tab-btn" onclick="trocarAba('ia')">🧠 Rotinas Recorrentes (IA)</button>
            </div>

            <!-- ABA 1: MEIA NOITE -->
            <div id="tabContentMeiaNoite">
                <div class="bg-purple-950/40 border border-purple-500/30 rounded-xl p-4 mb-4">
                    <h3 class="text-sm font-bold text-cyan-300 mb-1">🌙 IA MEIA NOITE • MAPEAMENTO DIRETO DE PASTAS</h3>
                    <p class="text-xs text-gray-300 leading-relaxed">
                        Lê a pasta <b>C:\Projetos</b>, organiza a ramificação com as planilhas reais e finaliza com o <b>Salvamento de Histórico</b> e card de <b>Conclusão</b>!
                    </p>
                </div>
                <div class="flex justify-end gap-3">
                    <button onclick="carregarEGerarMeiaNoite()" class="btn-generate">🚀 GERAR FLUXOGRAMA MEIA NOITE</button>
                </div>
            </div>

            <!-- ABA 2: MANUAL -->
            <div id="tabContentManual" class="hidden">
                <p class="text-xs text-purple-200/80 mb-3 leading-relaxed">
                    Digite ou cole abaixo as tarefas da sua rotina diária. A inteligência categoriza e organiza o fluxograma em nós paralelos.
                </p>
                <textarea id="txtTasks" class="task-textarea mb-4" placeholder="ligar o pc&#10;bater o ponto&#10;verificar e-mails&#10;criar automações&#10;script de verificação"></textarea>
                <div class="flex justify-end gap-3">
                    <button onclick="gerarFluxogramaManual()" class="btn-generate">⚡ MAPEAR COM IA</button>
                </div>
            </div>

            <!-- ABA 3: HISTÓRICO IA -->
            <div id="tabContentIA" class="hidden">
                <p class="text-xs text-cyan-200/80 mb-3 leading-relaxed">
                    Escolha uma das rotinas preditivas detectadas:
                </p>

                <div class="history-card" onclick="gerarPorHistorico('matinal')">
                    <div class="flex justify-between items-center mb-1">
                        <span class="text-xs font-bold text-cyan-300">⚡ ROTINA DIÁRIA MATINAL (Frequência: 98%)</span>
                        <span class="text-[10px] bg-cyan-950 text-cyan-400 px-2 py-0.5 rounded border border-cyan-800">AUTOMÁTICO</span>
                    </div>
                    <p class="text-xs text-gray-300">ligar o pc ➔ bater o ponto ➔ verificar e-mails corporativos ➔ checar pendências ➔ iniciar scripts</p>
                </div>

                <div class="history-card" onclick="gerarPorHistorico('desenvolvimento')">
                    <div class="flex justify-between items-center mb-1">
                        <span class="text-xs font-bold text-purple-300">🚀 FLUXO DE DESENVOLVIMENTO & AUTOMAÇÕES</span>
                        <span class="text-[10px] bg-purple-950 text-purple-400 px-2 py-0.5 rounded border border-purple-800">AUTOMÁTICO</span>
                    </div>
                    <p class="text-xs text-gray-300">abrir VS Code / Python ➔ extrair dados corporativos ➔ rodar automação de planilhas ➔ compilar aditivos</p>
                </div>

                <div class="history-card" onclick="gerarPorHistorico('fechamento')">
                    <div class="flex justify-between items-center mb-1">
                        <span class="text-xs font-bold text-emerald-300">📊 ROTINA DE FECHAMENTO SEMANAL</span>
                        <span class="text-[10px] bg-emerald-950 text-emerald-400 px-2 py-0.5 rounded border border-emerald-800">RECORRENTE</span>
                    </div>
                    <p class="text-xs text-gray-300">consolidar relatórios da equipe ➔ notificar diretoria via Teams/E-mail ➔ bater o ponto de saída ➔ desligar pc</p>
                </div>
            </div>
        </div>
    </div>

    <!-- PAINEL DE DIRETRIZES DA PLANILHA -->
    <div id="actionSelectorPanel">
        <div class="flex justify-between items-center border-b border-cyan-800/50 pb-2 mb-3">
            <h4 id="panelCardTitle" class="text-xs font-bold text-cyan-300">⚙️ DIRETRIZES DA PLANILHA</h4>
            <button onclick="fecharPainelSeletor()" class="text-gray-400 hover:text-white text-xs">✕</button>
        </div>
        <p class="text-[11px] text-purple-200 mb-3">Marque quais scripts/diretrizes executar para esta planilha:</p>
        <div id="checkboxesContainer"></div>
    </div>

    <!-- CANVAS ENGINE DO FLUXOGRAMA -->
    <div id="canvasContainer">
        <div class="top-bar">
            <div class="badge-title">
                <svg class="w-4 h-4 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
                <span id="badgeTitleText">SEXTA-FEIRA ENGINE • MEIA NOITE</span>
                <span id="progressIndicator" class="progress-badge">Progresso: 0/0 (0%)</span>
            </div>
            <div class="flex gap-2">
                <button class="btn-clear-cables" onclick="limparTodasConexoes()">🔌 REESTRUTURAR CABOS</button>
                <button class="btn-add-card" onclick="adicionarCardPersonalizado()">➕ CRIAR CARD SEPARADO</button>
                <button class="btn-action" onclick="reabrirModal()">✕ ALTERAR MODO</button>
            </div>
        </div>

        <div class="hint-bar" id="statusHintText">💡 Clique no conector DIREITO e depois no ESQUERDO de outro para LIGAR/DESLIGAR cabos | Clique na planilha para editar diretrizes</div>

        <canvas id="workflowCanvas"></canvas>
    </div>

    <script>
        function drawRoundRect(ctx, x, y, w, h, r) {
            if (w < 2 * r) r = w / 2;
            if (h < 2 * r) r = h / 2;
            ctx.beginPath();
            ctx.moveTo(x + r, y);
            ctx.arcTo(x + w, y, x + w, y + h, r);
            ctx.arcTo(x + w, y + h, x, y + h, r);
            ctx.arcTo(x, y + h, x, y, r);
            ctx.arcTo(x, y, x + w, y, r);
            ctx.closePath();
        }

        let canvas, ctx;
        let animationId = null;
        let nodes = [];
        let connections = [];
        let particles = [];
        
        let transformX = 60;
        let transformY = 40;
        let scale = 0.85;

        let isDraggingMap = false;
        let draggedNode = null;
        let activeCardForPanel = null;
        let nodeDragOffsetX = 0, nodeDragOffsetY = 0;
        let startDragX = 0, startDragY = 0;
        let selectedSourceSocketNode = null;
        let mouseDownTime = 0, mouseDownPos = { x: 0, y: 0 };

        const DIRETRIZES_TODAS = [
            'Ativar script Atualização',
            'Script de Divisão',
            'Excluir Linhas',
            'Excluir Abas',
            'Criar Abas',
            'Criar Aditivo'
        ];

        function trocarAba(aba) {
            document.getElementById('btnTabMeiaNoite').classList.remove('active');
            document.getElementById('btnTabManual').classList.remove('active');
            document.getElementById('btnTabIA').classList.remove('active');

            document.getElementById('tabContentMeiaNoite').classList.add('hidden');
            document.getElementById('tabContentManual').classList.add('hidden');
            document.getElementById('tabContentIA').classList.add('hidden');

            if (aba === 'meiaNoite') {
                document.getElementById('btnTabMeiaNoite').classList.add('active');
                document.getElementById('tabContentMeiaNoite').classList.remove('hidden');
            } else if (aba === 'manual') {
                document.getElementById('btnTabManual').classList.add('active');
                document.getElementById('tabContentManual').classList.remove('hidden');
            } else if (aba === 'ia') {
                document.getElementById('btnTabIA').classList.add('active');
                document.getElementById('tabContentIA').classList.remove('hidden');
            }
        }

        function reabrirModal() {
            fecharPainelSeletor();
            document.getElementById('canvasContainer').classList.remove('active');
            document.getElementById('modalContainer').classList.remove('hidden-modal');
            if (animationId) cancelAnimationFrame(animationId);
        }

        function fecharPainelSeletor() {
            document.getElementById('actionSelectorPanel').classList.remove('active');
            activeCardForPanel = null;
        }

        function abrirPainelSelecaoDiretrizes(node) {
            if (!node.isPlanilha) return;

            activeCardForPanel = node;
            document.getElementById('panelCardTitle').innerText = `⚙️ ${node.fullTitle.toUpperCase()}`;

            const container = document.getElementById('checkboxesContainer');
            container.innerHTML = '';

            DIRETRIZES_TODAS.forEach(opt => {
                const isChecked = node.activeActions && node.activeActions.includes(opt);

                const label = document.createElement('label');
                label.className = 'action-checkbox-item';

                const input = document.createElement('input');
                input.type = 'checkbox';
                input.checked = isChecked;
                input.onchange = (e) => {
                    if (!node.activeActions) node.activeActions = [];
                    if (e.target.checked) {
                        if (!node.activeActions.includes(opt)) node.activeActions.push(opt);
                    } else {
                        node.activeActions = node.activeActions.filter(a => a !== opt);
                    }
                };

                const span = document.createElement('span');
                span.innerText = opt;

                label.appendChild(input);
                label.appendChild(span);
                container.appendChild(label);
            });

            document.getElementById('actionSelectorPanel').classList.add('active');
        }

        function gerarPorHistorico(tipo) {
            let tarefas = "";
            if (tipo === 'matinal') {
                tarefas = "ligar o pc\nbater o ponto\nverificar e-mails corporativos\nchecar pendências do sistema\niniciar scripts diários";
            } else if (tipo === 'desenvolvimento') {
                tarefas = "abrir VS Code / Python\nextrair dados corporativos\nrodar automação de planilhas\ncompilar aditivos e relatórios";
            } else if (tipo === 'fechamento') {
                tarefas = "consolidar relatórios da equipe\nnotificar diretoria via Teams/E-mail\nbater o ponto de saída\ndesligar pc";
            }
            document.getElementById('txtTasks').value = tarefas;
            gerarFluxogramaManual();
        }

        function carregarEGerarMeiaNoite() {
            document.getElementById('modalContainer').classList.add('hidden-modal');
            document.getElementById('canvasContainer').classList.add('active');
            document.getElementById('badgeTitleText').innerText = "SEXTA-FEIRA ENGINE • MEIA NOITE";
            document.getElementById('progressIndicator').style.display = 'none';

            const dadosPastas = DATA_PASTAS_PYTHON;

            setTimeout(() => {
                construirFluxogramaMeiaNoitePuro(dadosPastas);
            }, 50);
        }

        function gerarFluxogramaManual() {
            const text = document.getElementById('txtTasks').value.trim();
            if (!text) {
                alert("Por favor, digite ou selecione uma rotina.");
                return;
            }

            document.getElementById('modalContainer').classList.add('hidden-modal');
            document.getElementById('canvasContainer').classList.add('active');
            document.getElementById('badgeTitleText').innerText = "SEXTA-FEIRA ENGINE • DIAGRAMA DE PROCESSO EM NÓS";
            document.getElementById('progressIndicator').style.display = 'inline-block';

            setTimeout(() => {
                construirFluxogramaSemantico(text);
            }, 50);
        }

        // CONSTRÓI O FLUXOGRAMA MEIA NOITE FINALIZANDO COM SALVAMENTO DE HISTÓRICO E CONCLUSÃO
        function construirFluxogramaMeiaNoitePuro(dadosPastas) {
            canvas = document.getElementById('workflowCanvas');
            ctx = canvas.getContext('2d');

            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;

            const H = window.innerHeight;
            const midY = H / 2 - 40;
            nodes = [];
            connections = [];

            // 1. TRIGGER IA MEIA NOITE
            nodes.push({
                id: 'n_meia_noite',
                title: 'IA Meia Noite',
                fullTitle: 'IA Meia Noite',
                subtitle: 'Motor Automático',
                badge: 'TRIGGER',
                x: 80, y: midY, width: 220, height: 84, color: '#a855f7', icon: '🌙', isUserTask: false
            });

            // 2. RAIZ PROJETOS
            nodes.push({
                id: 'n_projetos',
                title: 'Projetos',
                fullTitle: 'Projetos',
                subtitle: 'Diretório Raiz (C:\\Projetos)',
                badge: 'RAIZ',
                x: 360, y: midY, width: 210, height: 84, color: '#00d2ff', icon: '📁', isUserTask: false
            });

            addConn('n_meia_noite', 'n_projetos', '#a855f7');

            // 3. AS PASTAS ALINHADAS HORIZONTALMENTE COM AS PLANILHAS À DIREITA
            const posPastas = [
                { key: 'atualizacao', y: midY - 170 },
                { key: 'divisao', y: midY },
                { key: 'planilhas', y: midY + 170 }
            ];

            let maxPlanilhaX = 990;
            let ultimasPlanilhasIds = [];

            posPastas.forEach((p) => {
                const pastaData = dadosPastas[p.key];
                const pastaId = `pasta_${p.key}`;
                const pastaX = 660;

                nodes.push({
                    id: pastaId,
                    title: pastaData.titulo,
                    fullTitle: pastaData.titulo,
                    subtitle: `Pasta C:\\Projetos\\${pastaData.titulo}`,
                    badge: 'PASTA',
                    x: pastaX, y: p.y, width: 240, height: 84,
                    color: pastaData.cor, icon: pastaData.icon, isUserTask: true, isPasta: true
                });

                addConn('n_projetos', pastaId, '#00d2ff');

                if (pastaData.arquivos.length === 0) {
                    ultimasPlanilhasIds.push(pastaId);
                }

                pastaData.arquivos.forEach((nomeArq, idx) => {
                    const planilhaId = `planilha_${p.key}_${idx}`;
                    const planilhaX = 990 + (idx * 390);
                    const planilhaY = p.y;

                    if (planilhaX > maxPlanilhaX) maxPlanilhaX = planilhaX;

                    let tituloExibicao = nomeArq;
                    if (nomeArq.length > 22) {
                        tituloExibicao = nomeArq.substring(0, 20) + '...';
                    }

                    nodes.push({
                        id: planilhaId,
                        title: tituloExibicao,
                        fullTitle: nomeArq,
                        subtitle: `${pastaData.titulo} • Excel`,
                        badge: 'PLANILHA',
                        x: planilhaX, y: planilhaY, width: 250, height: 84,
                        color: pastaData.cor, icon: '📄', isUserTask: true, isPlanilha: true,
                        activeActions: [...pastaData.acoes_padrao]
                    });

                    if (idx === 0) {
                        addConn(pastaId, planilhaId, pastaData.cor);
                    } else {
                        const planilhaAnteriorId = `planilha_${p.key}_${idx - 1}`;
                        addConn(planilhaAnteriorId, planilhaId, pastaData.cor);
                    }

                    if (idx === pastaData.arquivos.length - 1) {
                        ultimasPlanilhasIds.push(planilhaId);
                    }
                });
            });

            // 4. CARD: SALVAMENTO DE HISTÓRICO (APÓS AS PLANILHAS)
            const salvamentoX = maxPlanilhaX + 390;
            nodes.push({
                id: 'n_salvamento',
                title: 'Salvamento de Histórico',
                fullTitle: 'Salvamento de Histórico',
                subtitle: 'Gravação & Logs',
                badge: 'HISTÓRICO',
                x: salvamentoX, y: midY, width: 240, height: 84,
                color: '#00d2ff', icon: '💾', isUserTask: false
            });

            // Conecta os últimos nós de cada linha no Salvamento de Histórico
            ultimasPlanilhasIds.forEach(idUltimo => {
                addConn(idUltimo, 'n_salvamento');
            });

            // 5. CARD: CONCLUSÃO (APÓS O SALVAMENTO DE HISTÓRICO)
            nodes.push({
                id: 'n_conclusao',
                title: 'Conclusão',
                fullTitle: 'Conclusão',
                subtitle: 'Rotina 100% Finalizada',
                badge: 'SUCCESS',
                x: salvamentoX + 310, y: midY, width: 215, height: 84,
                color: '#10b981', icon: '✅', isPulseSphere: true, isUserTask: false, completed: true
            });

            addConn('n_salvamento', 'n_conclusao', '#10b981');

            reconstruirParticulas();
            iniciarEventosCanvas();
        }

        // CONSTRÓI O FLUXOGRAMA DE TAREFAS DIÁRIAS (SEMÂNTICO)
        function construirFluxogramaSemantico(userText) {
            canvas = document.getElementById('workflowCanvas');
            ctx = canvas.getContext('2d');

            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;

            const rawLines = userText.split('\n').map(l => l.replace(/^[-*\d.\s]+/, '').trim()).filter(l => l.length > 0);
            
            const categories = [
                { id: 'setup', name: 'INICIALIZAÇÃO & ACESSO', icon: '💻', color: '#f59e0b', items: [] },
                { id: 'comm', name: 'COMUNICAÇÃO & CHECAGEM', icon: '✉️', color: '#38bdf8', items: [] },
                { id: 'dev', name: 'DESENVOLVIMENTO & AUTOMAÇÃO', icon: '⚡', color: '#a855f7', items: [] },
                { id: 'report', name: 'RELATÓRIOS & ANÁLISE', icon: '📊', color: '#ec4899', items: [] }
            ];

            rawLines.forEach(item => {
                const s = item.toLowerCase();
                if (s.includes('pc') || s.includes('ligar') || s.includes('ponto') || s.includes('bater') || s.includes('login') || s.includes('iniciar') || s.includes('abrir') || s.includes('sistema') || s.includes('senha') || s.includes('desligar')) {
                    categories[0].items.push(item);
                } else if (s.includes('email') || s.includes('e-mail') || s.includes('mensagem') || s.includes('slack') || s.includes('teams') || s.includes('verificar') || s.includes('checar') || s.includes('ler') || s.includes('pendenci') || s.includes('caixa') || s.includes('notificar')) {
                    categories[1].items.push(item);
                } else if (s.includes('script') || s.includes('automa') || s.includes('codigo') || s.includes('código') || s.includes('desenvolv') || s.includes('program') || s.includes('python') || s.includes('bot') || s.includes('criar') || s.includes('ferramenta') || s.includes('vs code')) {
                    categories[2].items.push(item);
                } else {
                    categories[3].items.push(item);
                }
            });

            const activeCategories = categories.filter(c => c.items.length > 0);
            const H = window.innerHeight;
            const midY = H / 2 - 40;
            nodes = [];
            connections = [];

            nodes.push({
                id: 'n_exec', title: 'Executes Workflow', fullTitle: 'Executes Workflow',
                subtitle: 'Trigger Automático', badge: 'TRIGGER', originalBadge: 'TRIGGER',
                x: 80, y: midY, width: 210, height: 84, color: '#f97316', icon: '⚡', isUserTask: false, completed: false
            });

            nodes.push({
                id: 'n_prompt', title: 'Agente AI Sexta-Feira', fullTitle: 'Agente AI Sexta-Feira',
                subtitle: 'Histórico & Padrões', badge: 'AI ENGINE', originalBadge: 'AI ENGINE',
                x: 350, y: midY, width: 220, height: 84, color: '#00d2ff', icon: '🤖', isUserTask: false, completed: false
            });

            addConn('n_exec', 'n_prompt', '#f97316');

            let currentX = 650;
            let taskIndex = 1;

            activeCategories.forEach((cat) => {
                const numItems = cat.items.length;
                const spacingY = 105;
                const startY = midY - ((numItems - 1) * spacingY) / 2;

                cat.items.forEach((itemText, idx) => {
                    const nodeId = `task_${cat.id}_${idx}`;
                    nodes.push({
                        id: nodeId,
                        title: itemText.length > 20 ? itemText.substring(0, 19) + '...' : itemText,
                        fullTitle: itemText,
                        subtitle: `${cat.name} • #${taskIndex}`,
                        badge: cat.id.toUpperCase(), originalBadge: cat.id.toUpperCase(),
                        x: currentX, y: startY + (idx * spacingY),
                        width: 230, height: 84, color: cat.color, icon: cat.icon,
                        catId: cat.id, isUserTask: true, completed: false
                    });
                    taskIndex++;
                });

                currentX += 290;
            });

            nodes.push({
                id: 'n_bundle', title: 'Consolidador de Dados', fullTitle: 'Consolidador de Dados',
                subtitle: 'Merged Streams', badge: 'MERGER', originalBadge: 'MERGER',
                x: currentX, y: midY, width: 215, height: 84, color: '#06b6d4', icon: '🔀', isUserTask: false, completed: false
            });

            nodes.push({
                id: 'n_success', title: 'Rotina Concluída', fullTitle: 'Rotina Concluída',
                subtitle: 'Status: 100% Finalizada', badge: 'SUCCESS', originalBadge: 'SUCCESS',
                x: currentX + 280, y: midY, width: 215, height: 84, color: '#10b981', icon: '✅', isPulseSphere: true, isUserTask: false, completed: false
            });

            const userNodes = nodes.filter(n => n.isUserTask);
            const categoriesInUse = [...new Set(userNodes.map(n => n.catId))];

            if (categoriesInUse.length > 0) {
                const firstCatNodes = userNodes.filter(n => n.catId === categoriesInUse[0]);
                firstCatNodes.forEach(n => addConn('n_prompt', n.id));

                for (let i = 0; i < categoriesInUse.length - 1; i++) {
                    const currentCatNodes = userNodes.filter(n => n.catId === categoriesInUse[i]);
                    const nextCatNodes = userNodes.filter(n => n.catId === categoriesInUse[i + 1]);

                    currentCatNodes.forEach(src => {
                        nextCatNodes.forEach(tgt => addConn(src.id, tgt.id));
                    });
                }

                const lastCatNodes = userNodes.filter(n => n.catId === categoriesInUse[categoriesInUse.length - 1]);
                lastCatNodes.forEach(n => addConn(n.id, 'n_bundle'));
            } else {
                addConn('n_prompt', 'n_bundle');
            }

            addConn('n_bundle', 'n_success');

            reconstruirParticulas();
            atualizarProgressoUI();
            iniciarEventosCanvas();
        }

        function addConn(srcId, tgtId, color) {
            const src = nodes.find(n => n.id === srcId);
            const tgt = nodes.find(n => n.id === tgtId);
            if (!src || !tgt) return;

            connections.push({
                srcId: srcId, tgtId: tgtId,
                sx: src.x + src.width, sy: src.y + src.height / 2,
                tx: tgt.x, ty: tgt.y + tgt.height / 2,
                color: color || src.color
            });
        }

        function alternarConexaoCabo(src, tgt) {
            const index = connections.findIndex(c => c.srcId === src.id && c.tgtId === tgt.id);
            if (index !== -1) {
                connections.splice(index, 1);
            } else {
                addConn(src.id, tgt.id, src.color);
            }
            reconstruirParticulas();
        }

        function iniciarEventosCanvas() {
            canvas.onmousedown = (e) => {
                const mouseCanvasX = (e.clientX - transformX) / scale;
                const mouseCanvasY = (e.clientY - transformY) / scale;

                // Botão Excluir ✕
                for (let n of nodes) {
                    if (n.isUserTask) {
                        const btnX = n.x + n.width - 12;
                        const btnY = n.y + 12;
                        if (Math.hypot(mouseCanvasX - btnX, mouseCanvasY - btnY) < 14) {
                            excluirCard(n.id);
                            return;
                        }
                    }
                }

                // Sockets de Conexão
                for (let n of nodes) {
                    const socketOutX = n.x + n.width;
                    const socketOutY = n.y + n.height / 2;
                    if (Math.hypot(mouseCanvasX - socketOutX, mouseCanvasY - socketOutY) < 14) {
                        selectedSourceSocketNode = n;
                        return;
                    }

                    const socketInX = n.x;
                    const socketInY = n.y + n.height / 2;
                    if (Math.hypot(mouseCanvasX - socketInX, mouseCanvasY - socketInY) < 14) {
                        if (selectedSourceSocketNode && selectedSourceSocketNode.id !== n.id) {
                            alternarConexaoCabo(selectedSourceSocketNode, n);
                            selectedSourceSocketNode = null;
                            return;
                        }
                    }
                }

                // Arraste / Hit do Nó
                let nodeHit = null;
                for (let i = nodes.length - 1; i >= 0; i--) {
                    const n = nodes[i];
                    if (mouseCanvasX >= n.x && mouseCanvasX <= n.x + n.width &&
                        mouseCanvasY >= n.y && mouseCanvasY <= n.y + n.height) {
                        nodeHit = n;
                        break;
                    }
                }

                mouseDownTime = Date.now();
                mouseDownPos = { x: e.clientX, y: e.clientY };

                if (nodeHit) {
                    draggedNode = nodeHit;
                    nodeDragOffsetX = mouseCanvasX - nodeHit.x;
                    nodeDragOffsetY = mouseCanvasY - nodeHit.y;
                    isDraggingMap = false;

                    if (nodeHit.isPlanilha) {
                        abrirPainelSelecaoDiretrizes(nodeHit);
                    }
                } else {
                    draggedNode = null;
                    isDraggingMap = true;
                    startDragX = e.clientX - transformX;
                    startDragY = e.clientY - transformY;
                }
            };

            canvas.onmousemove = (e) => {
                const mouseCanvasX = (e.clientX - transformX) / scale;
                const mouseCanvasY = (e.clientY - transformY) / scale;

                if (draggedNode) {
                    draggedNode.x = mouseCanvasX - nodeDragOffsetX;
                    draggedNode.y = mouseCanvasY - nodeDragOffsetY;
                    atualizarCorCardDinamico(draggedNode);
                    atualizarPontosDeConexao();
                } else if (isDraggingMap) {
                    transformX = e.clientX - startDragX;
                    transformY = e.clientY - startDragY;
                }
            };

            canvas.onmouseup = (e) => {
                const dist = Math.hypot(e.clientX - mouseDownPos.x, e.clientY - mouseDownPos.y);
                const timeDiff = Date.now() - mouseDownTime;

                if (dist < 6 && timeDiff < 300 && draggedNode && !draggedNode.isPlanilha) {
                    draggedNode.completed = !draggedNode.completed;
                    draggedNode.badge = draggedNode.completed ? '✓ CONCLUÍDO' : (draggedNode.originalBadge || 'PENDENTE');
                    atualizarConexoesEStatusGeral();
                    atualizarProgressoUI();
                }

                draggedNode = null;
                isDraggingMap = false;
            };

            canvas.onmouseleave = () => { draggedNode = null; isDraggingMap = false; };

            canvas.onwheel = (e) => {
                e.preventDefault();
                const zoomFactor = e.deltaY < 0 ? 1.06 : 0.94;
                scale = Math.min(Math.max(0.35, scale * zoomFactor), 2.2);
            };

            window.onresize = () => {
                if (!canvas) return;
                canvas.width = window.innerWidth;
                canvas.height = window.innerHeight;
            };

            if (animationId) cancelAnimationFrame(animationId);
            renderLoop(performance.now());
        }

        function atualizarCorCardDinamico(node) {
            if (!node.isCustom) return;

            let closestNode = null;
            let minDistance = 99999;

            nodes.forEach(other => {
                if (other.id !== node.id && other.isUserTask && !other.isCustom) {
                    const dist = Math.hypot(node.x - other.x, node.y - other.y);
                    if (dist < minDistance) {
                        minDistance = dist;
                        closestNode = other;
                    }
                }
            });

            if (closestNode && minDistance < 220) {
                node.color = closestNode.color;
                node.subtitle = `${closestNode.badge} • MANUAL`;
                node.badge = closestNode.badge;
            } else {
                node.color = '#ec4899';
                node.subtitle = 'Card Personalizado';
                node.badge = 'MANUAL';
            }
        }

        function adicionarCardPersonalizado() {
            const titulo = prompt("Digite o nome do novo card:");
            if (!titulo || !titulo.trim()) return;

            const id = `task_custom_${Date.now()}`;
            const canvasCenterX = (window.innerWidth / 2 - transformX) / scale;
            const canvasCenterY = (window.innerHeight / 2 - transformY) / scale;

            const novoNo = {
                id: id,
                title: titulo.trim().length > 20 ? titulo.trim().substring(0, 19) + '...' : titulo.trim(),
                fullTitle: titulo.trim(),
                subtitle: 'Card Personalizado',
                badge: 'MANUAL', originalBadge: 'MANUAL',
                x: canvasCenterX - 110, y: canvasCenterY - 40,
                width: 230, height: 84, color: '#ec4899', icon: '📌',
                isUserTask: true, isCustom: true, completed: false
            };

            nodes.push(novoNo);
            atualizarCorCardDinamico(novoNo);
            atualizarProgressoUI();
        }

        function excluirCard(nodeId) {
            nodes = nodes.filter(n => n.id !== nodeId);
            connections = connections.filter(c => c.srcId !== nodeId && c.tgtId !== nodeId);
            reconstruirParticulas();
            atualizarProgressoUI();
        }

        function limparTodasConexoes() {
            connections = [];
            particles = [];
            selectedSourceSocketNode = null;
        }

        function reconstruirParticulas() {
            particles = [];
            connections.forEach((c, idx) => {
                for (let p = 0; p < 3; p++) {
                    particles.push({
                        connIndex: idx,
                        progress: (p / 3) + Math.random() * 0.05,
                        speed: 0.003 + Math.random() * 0.002
                    });
                }
            });
        }

        function atualizarPontosDeConexao() {
            connections.forEach(c => {
                const src = nodes.find(n => n.id === c.srcId);
                const tgt = nodes.find(n => n.id === c.tgtId);
                if (src && tgt) {
                    c.sx = src.x + src.width;
                    c.sy = src.y + src.height / 2;
                    c.tx = tgt.x;
                    c.ty = tgt.y + tgt.height / 2;
                }
            });
        }

        function atualizarProgressoUI() {
            const tarefasProcesso = nodes.filter(n => n.isUserTask);
            const total = tarefasProcesso.length;
            const concluidas = tarefasProcesso.filter(n => n.completed).length;
            const perc = total > 0 ? Math.round((concluidas / total) * 100) : 0;

            const badge = document.getElementById('progressIndicator');
            if (badge) {
                badge.innerText = `Progresso: ${concluidas}/${total} Concluídas (${perc}%)`;
                if (perc === 100 && total > 0) {
                    badge.style.background = 'rgba(16, 185, 129, 0.35)';
                    badge.style.borderColor = '#10b981';
                    badge.innerText = `🎉 Todas as ${total} Tarefas Concluídas!`;
                } else {
                    badge.style.background = 'rgba(16, 185, 129, 0.15)';
                    badge.style.borderColor = 'rgba(16, 185, 129, 0.4)';
                }
            }
        }

        function atualizarConexoesEStatusGeral() {
            connections.forEach(c => {
                const src = nodes.find(n => n.id === c.srcId);
                if (src && src.completed) {
                    c.color = '#10b981';
                } else if (src) {
                    c.color = src.color;
                }
            });

            const tarefasProcesso = nodes.filter(n => n.isUserTask);
            const todasConcluidas = tarefasProcesso.length > 0 && tarefasProcesso.every(n => n.completed);
            const noSucesso = nodes.find(n => n.id === 'n_success');
            if (noSucesso) {
                noSucesso.completed = todasConcluidas;
            }
        }

        function renderLoop(time) {
            animationId = requestAnimationFrame(renderLoop);

            const W = canvas.width;
            const H = canvas.height;

            ctx.fillStyle = '#080a11';
            ctx.fillRect(0, 0, W, H);

            ctx.save();
            ctx.translate(transformX, transformY);
            ctx.scale(scale, scale);

            // Grade de Fundo
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.035)';
            ctx.lineWidth = 1;
            const gridSize = 36;
            const minX = -transformX / scale - 400;
            const maxX = (W - transformX) / scale + 800;
            const minY = -transformY / scale - 400;
            const maxY = (H - transformY) / scale + 800;

            for (let x = Math.floor(minX / gridSize) * gridSize; x < maxX; x += gridSize) {
                ctx.beginPath(); ctx.moveTo(x, minY); ctx.lineTo(x, maxY); ctx.stroke();
            }
            for (let y = Math.floor(minY / gridSize) * gridSize; y < maxY; y += gridSize) {
                ctx.beginPath(); ctx.moveTo(minX, y); ctx.lineTo(maxX, y); ctx.stroke();
            }

            // Conexões
            connections.forEach((c) => {
                const dx = (c.tx - c.sx) * 0.45;
                ctx.beginPath();
                ctx.moveTo(c.sx, c.sy);
                ctx.bezierCurveTo(c.sx + dx, c.sy, c.tx - dx, c.ty, c.tx, c.ty);
                
                ctx.strokeStyle = 'rgba(255, 255, 255, 0.16)';
                ctx.lineWidth = 3.5;
                ctx.stroke();

                ctx.strokeStyle = c.color;
                ctx.lineWidth = 1.8;
                ctx.stroke();
            });

            // Partículas de Energia
            particles.forEach((p) => {
                p.progress += p.speed;
                if (p.progress > 1) p.progress = 0;

                const c = connections[p.connIndex];
                if (!c) return;

                const t = p.progress;
                const dx = (c.tx - c.sx) * 0.45;
                const p0 = { x: c.sx, y: c.sy };
                const p1 = { x: c.sx + dx, y: c.sy };
                const p2 = { x: c.tx - dx, y: c.ty };
                const p3 = { x: c.tx, y: c.ty };

                const cx = Math.pow(1 - t, 3) * p0.x + 3 * Math.pow(1 - t, 2) * t * p1.x + 3 * (1 - t) * Math.pow(t, 2) * p2.x + Math.pow(t, 3) * p3.x;
                const cy = Math.pow(1 - t, 3) * p0.y + 3 * Math.pow(1 - t, 2) * t * p1.y + 3 * (1 - t) * Math.pow(t, 2) * p2.y + Math.pow(t, 3) * p3.y;

                ctx.shadowColor = c.color || '#00d2ff';
                ctx.shadowBlur = 10;
                ctx.fillStyle = '#ffffff';
                ctx.beginPath();
                ctx.arc(cx, cy, 4, 0, Math.PI * 2);
                ctx.fill();
                ctx.shadowBlur = 0;
            });

            // Cards
            nodes.forEach((n) => {
                const isComp = n.completed;
                const mainColor = isComp ? '#10b981' : n.color;

                ctx.fillStyle = isComp ? '#09231b' : '#121622';
                ctx.strokeStyle = mainColor;
                ctx.lineWidth = isComp ? 2.4 : 1.8;

                if (isComp) {
                    ctx.shadowColor = '#10b981';
                    ctx.shadowBlur = 15;
                } else if (draggedNode === n || activeCardForPanel === n || selectedSourceSocketNode === n) {
                    ctx.shadowColor = '#00d2ff';
                    ctx.shadowBlur = 20;
                }

                drawRoundRect(ctx, n.x, n.y, n.width, n.height, 14);
                ctx.fill();
                ctx.stroke();
                ctx.shadowBlur = 0;

                ctx.fillStyle = isComp ? 'rgba(16, 185, 129, 0.25)' : 'rgba(0, 0, 0, 0.45)';
                drawRoundRect(ctx, n.x + 10, n.y + 12, 46, 60, 8);
                ctx.fill();

                ctx.font = '20px system-ui';
                ctx.fillText(isComp ? '✅' : n.icon, n.x + 20, n.y + 49);

                ctx.fillStyle = isComp ? '#6ee7b7' : '#ffffff';
                ctx.font = 'bold 11.5px system-ui';
                ctx.fillText(n.title, n.x + 64, n.y + 38);

                ctx.fillStyle = isComp ? '#a7f3d0' : '#9ca3af';
                ctx.font = '10px system-ui';
                ctx.fillText(n.subtitle, n.x + 64, n.y + 56);

                ctx.fillStyle = mainColor;
                drawRoundRect(ctx, n.x + 64, n.y + 60, 80, 16, 5);
                ctx.fill();

                ctx.fillStyle = '#000000';
                ctx.font = 'bold 8.5px system-ui';
                ctx.fillText(n.badge, n.x + 70, n.y + 71);

                if (n.isUserTask) {
                    const btnX = n.x + n.width - 12;
                    const btnY = n.y + 12;
                    ctx.fillStyle = '#ef4444';
                    ctx.beginPath();
                    ctx.arc(btnX, btnY, 8.5, 0, Math.PI * 2);
                    ctx.fill();

                    ctx.fillStyle = '#ffffff';
                    ctx.font = 'bold 10px system-ui';
                    ctx.fillText('✕', btnX - 3.5, btnY + 3.5);
                }

                // Marcadores Visíveis de Diretrizes ao Lado da Planilha
                if (n.activeActions && n.activeActions.length > 0) {
                    let startLineX = n.x + n.width + 10;

                    ctx.strokeStyle = mainColor;
                    ctx.lineWidth = 1.5;
                    ctx.beginPath();
                    ctx.moveTo(n.x + n.width, n.y + n.height / 2);
                    ctx.lineTo(startLineX + 4, n.y + n.height / 2);
                    ctx.stroke();

                    n.activeActions.forEach((actText, idx) => {
                        const tagY = n.y + 8 + (idx * 24);
                        const tagW = ctx.measureText(`⚡ ${actText}`).width + 16;

                        ctx.fillStyle = 'rgba(15, 23, 42, 0.95)';
                        ctx.strokeStyle = mainColor;
                        ctx.lineWidth = 1;
                        drawRoundRect(ctx, startLineX + 4, tagY, tagW, 20, 6);
                        ctx.fill();
                        ctx.stroke();

                        ctx.fillStyle = '#7dd3fc';
                        ctx.font = 'bold 10px system-ui';
                        ctx.fillText(`⚡ ${actText}`, startLineX + 10, tagY + 14);
                    });
                }

                // Sockets para conexões manuais
                ctx.fillStyle = '#080a11';
                ctx.strokeStyle = mainColor;
                ctx.lineWidth = 2.5;
                ctx.beginPath();
                ctx.arc(n.x, n.y + n.height / 2, 6.5, 0, Math.PI * 2);
                ctx.fill();
                ctx.stroke();

                if (selectedSourceSocketNode === n) {
                    ctx.fillStyle = '#00d2ff';
                    ctx.shadowColor = '#00d2ff';
                    ctx.shadowBlur = 12;
                } else {
                    ctx.fillStyle = '#080a11';
                }
                ctx.beginPath();
                ctx.arc(n.x + n.width, n.y + n.height / 2, 6.5, 0, Math.PI * 2);
                ctx.fill();
                ctx.stroke();
                ctx.shadowBlur = 0;

                if (n.isPulseSphere) {
                    const pulse = Math.sin(time * 0.006) * 10;
                    const centerX = n.x + n.width + 45;
                    const centerY = n.y + n.height / 2;

                    const grad = ctx.createRadialGradient(centerX, centerY, 2, centerX, centerY, 38 + pulse);
                    grad.addColorStop(0, isComp ? '#10b981' : '#00d2ff');
                    grad.addColorStop(0.35, isComp ? 'rgba(16, 185, 129, 0.7)' : 'rgba(0, 210, 255, 0.6)');
                    grad.addColorStop(0.7, 'rgba(16, 185, 129, 0.2)');
                    grad.addColorStop(1, 'transparent');

                    ctx.fillStyle = grad;
                    ctx.beginPath();
                    ctx.arc(centerX, centerY, 45 + pulse, 0, Math.PI * 2);
                    ctx.fill();
                }
            });

            ctx.restore();
        }
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    dados_reais_pastas = ler_planilhas_reais()
    json_dados = json.dumps(dados_reais_pastas, ensure_ascii=False)
    html_final = HTML_CONTENT.replace("DATA_PASTAS_PYTHON", json_dados)

    PASTA_ATUAL = os.path.dirname(os.path.abspath(__file__))
    html_file = os.path.join(PASTA_ATUAL, "temp_fluxograma.html")

    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_final)

    print("Iniciando Módulo Integrado teste_qt.py com Salvamento de Histórico e Conclusão no Meia Noite...")
    window = webview.create_window(
        title='Sexta-Feira AI • Engine de Fluxograma de Processos Integrado',
        url=html_file,
        width=1380,
        height=840,
        resizable=True
    )
    webview.start()