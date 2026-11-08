import os
import sys
import subprocess
import threading
import json
import shutil
from datetime import datetime
import webview

# ==========================================
# PASTA E CONFIGURAÇÃO DE CAMINHOS
# ==========================================
PASTA_ATUAL = os.path.dirname(os.path.abspath(__file__))
NOME_SCRIPT_ATUAL = os.path.basename(__file__)

# CAMINHO DA PASTA COMPARTILHADA NO SERVIDOR (REDE S:)
PASTA_SERVIDOR_ATUALIZACAO = r"S:\Orçamento e Controle\_OFICINA DE DESENVOLVIMENTO\Sala de desenvolvimento\Atualização Sexta-feira AT"

# ==========================================
# INTERFACE HOLOGRÁFICA COMPLETA
# ==========================================
HTML_CONTENT = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sexta-Feira AI & Holographic Interface</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <!-- Three.js mantido apenas para o Banco de Dados 3D -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        :root {{
            --bg-main: #030712;
            --text-color: #f3e8ff;
            --primary-neon: #a855f7;
            --primary-glow: rgba(168, 85, 247, 0.45);
            --card-bg: rgba(23, 15, 38, 0.85);
            --card-border: rgba(168, 85, 247, 0.25);
            --ai-blue: #00d2ff;
            --flamengo-red: #e11d48;
            --dev-cyan: #06b6d4;
        }}

        body.light-mode {{
            --bg-main: #e2e8f0;
            --text-color: #1e293b;
            --primary-neon: #0284c7;
            --primary-glow: rgba(2, 132, 199, 0.35);
            --card-bg: rgba(255, 255, 255, 0.85);
            --card-border: rgba(0, 0, 0, 0.1);
        }}

        body {{
            background-color: var(--bg-main);
            color: var(--text-color);
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            overflow: hidden;
            user-select: none;
            transition: background-color 0.8s ease, color 0.8s ease;
        }}

        /* REVELAÇÃO E TRANSIÇÃO SUAVE DA INTERFACE PRINCIPAL */
        .mode-selector,
        .switch-container,
        #stageMain,
        #statusConsole,
        #terminalContainer {{
            transition: opacity 1.2s cubic-bezier(0.16, 1, 0.3, 1), transform 1.2s cubic-bezier(0.16, 1, 0.3, 1);
        }}

        /* OCULTAR INTERFACE PRINCIPAL ATÉ A ANIMAÇÃO DE ENTRADA CONCLUIR */
        body.logged-out .mode-selector,
        body.logged-out .switch-container,
        body.logged-out #stageMain,
        body.logged-out #statusConsole,
        body.logged-out #terminalContainer {{
            opacity: 0 !important;
            pointer-events: none !important;
            transform: scale(0.95);
        }}

        /* ==========================================
           TELA DE LOGIN CÓSMICA / DARK PURPLE SPACE ("SOL ATRÁS DA TERRA")
           ========================================== */
        #loginScreenWrapper {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: #020005;
            z-index: 200;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            will-change: opacity, transform, filter;
            transition: opacity 1.2s cubic-bezier(0.16, 1, 0.3, 1), 
                        visibility 1.2s ease,
                        filter 1.2s ease,
                        transform 1.2s cubic-bezier(0.16, 1, 0.3, 1);
        }}

        /* EFEITO DE SOL ROXO ATRÁS DA TERRA (AURORA SOLAR CENTRAL) */
        .sun-flare {{
            position: absolute;
            top: 48%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 950px;
            height: 750px;
            background: radial-gradient(ellipse at center, 
                rgba(225, 180, 254, 0.65) 0%, 
                rgba(168, 85, 247, 0.45) 25%, 
                rgba(126, 34, 206, 0.2) 50%, 
                rgba(58, 12, 102, 0.08) 75%, 
                transparent 100%);
            filter: blur(45px);
            pointer-events: none;
        }}

        /* CURVATURA DO PLANETA TERRA COM BORDA NÉON ROXA */
        .planet-horizon {{
            position: absolute;
            top: 54%;
            left: 50%;
            transform: translateX(-50%);
            width: 180vw;
            height: 140vw;
            border-radius: 50%;
            background: radial-gradient(circle at 50% 0%, #070212 0%, #020005 60%);
            box-shadow: 
                0 -3px 18px rgba(232, 121, 249, 0.95),
                0 -12px 45px rgba(168, 85, 247, 0.75),
                0 -30px 95px rgba(126, 34, 206, 0.5),
                0 -60px 150px rgba(88, 28, 135, 0.3);
            border-top: 1.5px solid rgba(240, 171, 252, 0.95);
            pointer-events: none;
        }}

        /* MICRO POEIRA ESTELAR SUBTIL NO ESPAÇO */
        .stars-bg {{
            position: absolute;
            inset: 0;
            background-image: 
                radial-gradient(1px 1px at 20px 30px, #ffffff, rgba(0,0,0,0)),
                radial-gradient(1.5px 1.5px at 100px 150px, rgba(232, 121, 249, 0.8), rgba(0,0,0,0)),
                radial-gradient(1px 1px at 240px 80px, #ffffff, rgba(0,0,0,0)),
                radial-gradient(1px 1px at 420px 300px, rgba(192, 132, 252, 0.7), rgba(0,0,0,0)),
                radial-gradient(1.5px 1.5px at 650px 120px, #ffffff, rgba(0,0,0,0)),
                radial-gradient(1px 1px at 800px 220px, rgba(232, 121, 249, 0.6), rgba(0,0,0,0)),
                radial-gradient(1px 1px at 950px 50px, #ffffff, rgba(0,0,0,0)),
                radial-gradient(1.5px 1.5px at 1100px 280px, rgba(192, 132, 252, 0.8), rgba(0,0,0,0));
            background-size: 550px 550px;
            opacity: 0.6;
            pointer-events: none;
        }}

        #loginScreenWrapper.hidden-login {{
            opacity: 0;
            visibility: hidden;
            pointer-events: none;
            filter: blur(20px);
            transform: scale(1.08);
        }}

        /* CARD DE LOGIN */
        .login-container {{
            background: rgba(14, 6, 26, 0.82);
            backdrop-filter: blur(28px);
            border-radius: 28px;
            border: 1px solid rgba(168, 85, 247, 0.35);
            box-shadow: 0 30px 70px rgba(0, 0, 0, 0.9), 0 0 50px rgba(139, 92, 246, 0.25);
            position: relative;
            overflow: hidden;
            width: 768px;
            max-width: 100%;
            min-height: 480px;
            color: #f3e8ff;
            will-change: transform, opacity, filter;
            transition: transform 0.8s cubic-bezier(0.7, -0.2, 0.2, 1), 
                        opacity 0.7s cubic-bezier(0.16, 1, 0.3, 1),
                        filter 0.7s ease;
            z-index: 10;
        }}

        .login-container.shrink-out {{
            transform: translate3d(0, 0, 0) scale(0.05) rotate(-15deg);
            opacity: 0;
            filter: blur(10px);
        }}

        .login-container p {{ font-size: 13px; line-height: 20px; margin: 18px 0; color: #c4b5fd; }}
        .login-container span {{ font-size: 12px; margin-bottom: 12px; color: #a78bfa; }}
        .login-container a {{ color: #c084fc; font-size: 12px; text-decoration: none; margin: 12px 0 10px; transition: color 0.3s ease; }}
        .login-container a:hover {{ color: #ffffff; text-shadow: 0 0 10px rgba(192, 132, 252, 0.6); }}

        .login-container button {{
            background: linear-gradient(135deg, #7c3aed 0%, #a855f7 50%, #6366f1 100%);
            color: #fff;
            font-size: 12px;
            padding: 12px 45px;
            border: 1px solid rgba(255, 255, 255, 0.25);
            border-radius: 10px;
            font-weight: 700;
            letter-spacing: 0.8px;
            text-transform: uppercase;
            margin-top: 15px;
            cursor: pointer;
            box-shadow: 0 4px 20px rgba(124, 58, 237, 0.4);
            transition: all 0.3s ease;
        }}

        .login-container button:hover {{
            transform: scale(1.03);
            box-shadow: 0 0 25px rgba(168, 85, 247, 0.7);
        }}

        .login-container button.hidden-btn {{
            background-color: transparent;
            border-color: rgba(255, 255, 255, 0.4);
        }}

        .login-container form {{
            background-color: transparent;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-direction: column;
            padding: 0 40px;
            height: 100%;
        }}

        .login-container input {{
            background-color: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(168, 85, 247, 0.25);
            color: #f3e8ff;
            margin: 8px 0;
            padding: 12px 15px;
            font-size: 13px;
            border-radius: 10px;
            width: 100%;
            outline: none;
            transition: all 0.3s ease;
        }}

        .login-container input::placeholder {{
            color: rgba(196, 181, 253, 0.4);
        }}

        .login-container input:focus {{
            border-color: #c084fc;
            box-shadow: 0 0 12px rgba(192, 132, 252, 0.35);
            background-color: rgba(255, 255, 255, 0.08);
        }}

        /* FORMULÁRIOS DE LOGIN */
        .form-container {{
            position: absolute;
            top: 0;
            height: 100%;
            transition: all 0.6s ease-in-out;
        }}

        .sign-in {{
            left: 0;
            width: 50%;
            z-index: 2;
            opacity: 1;
            pointer-events: auto;
        }}

        .login-container.active .sign-in {{
            transform: translateX(100%);
            opacity: 0;
            pointer-events: none;
            z-index: 1;
        }}

        .sign-up {{
            left: 0;
            width: 50%;
            opacity: 0;
            pointer-events: none;
            z-index: 1;
        }}

        .login-container.active .sign-up {{
            transform: translateX(100%);
            opacity: 1;
            pointer-events: auto;
            z-index: 5;
            animation: moveLogin 0.6s;
        }}

        @keyframes moveLogin {{
            0%, 49.99% {{ opacity: 0; z-index: 1; }}
            50%, 100% {{ opacity: 1; z-index: 5; }}
        }}

        .toggle-container {{
            position: absolute;
            top: 0;
            left: 50%;
            width: 50%;
            height: 100%;
            overflow: hidden;
            transition: all 0.6s ease-in-out;
            border-radius: 150px 0 0 100px;
            z-index: 1000;
        }}

        .login-container.active .toggle-container {{
            transform: translateX(-100%);
            border-radius: 0 150px 100px 0;
        }}

        .toggle {{
            background: linear-gradient(135deg, #18032b 0%, #310854 50%, #4c127d 100%);
            height: 100%;
            color: #fff;
            position: relative;
            left: -100%;
            width: 200%;
            transform: translateX(0);
            transition: all 0.6s ease-in-out;
        }}

        .login-container.active .toggle {{ transform: translateX(50%); }}

        .toggle-panel {{
            position: absolute;
            width: 50%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-direction: column;
            padding: 0 30px;
            text-align: center;
            top: 0;
            transform: translateX(0);
            transition: all 0.6s ease-in-out;
        }}

        .toggle-left {{ transform: translateX(-200%); }}
        .login-container.active .toggle-left {{ transform: translateX(0); }}
        .toggle-right {{ right: 0; transform: translateX(0); }}
        .login-container.active .toggle-right {{ transform: translateX(200%); }}

        /* ==========================================
           ABERTURA KINETIC NEON (SPOTLIGHT, SLASH & LOGO SF)
           ========================================== */
        #introAnimOverlay {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: #02040a;
            z-index: 250;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            opacity: 0;
            pointer-events: none;
            overflow: hidden;
            will-change: opacity, transform, filter;
            transition: opacity 1s cubic-bezier(0.16, 1, 0.3, 1), 
                        transform 1s cubic-bezier(0.16, 1, 0.3, 1),
                        filter 1s ease;
        }}

        #introAnimOverlay.active {{
            opacity: 1;
            pointer-events: auto;
            transform: scale(1);
        }}

        #introAnimOverlay.fade-out {{
            opacity: 0;
            pointer-events: none;
            transform: scale(1.15);
            filter: blur(15px);
        }}

        .spotlight-sweep {{
            position: absolute;
            width: 600px;
            height: 600px;
            background: conic-gradient(from 0deg at 50% 50%, rgba(0, 210, 255, 0.4) 0deg, rgba(168, 85, 247, 0.2) 45deg, transparent 90deg);
            border-radius: 50%;
            top: calc(50% - 300px);
            left: calc(50% - 300px);
            opacity: 0;
            transform-origin: center center;
            pointer-events: none;
        }}

        #introAnimOverlay.active .spotlight-sweep {{
            animation: spotlightRotate 1.2s cubic-bezier(0.2, 0.8, 0.2, 1) forwards 0.1s;
        }}

        @keyframes spotlightRotate {{
            0% {{ transform: rotate(-90deg) scale(0.3); opacity: 0; }}
            40% {{ opacity: 0.9; }}
            100% {{ transform: rotate(180deg) scale(1.6); opacity: 0; }}
        }}

        .slash-beam {{
            position: absolute;
            width: 140%;
            height: 4px;
            background: linear-gradient(90deg, transparent, #00d2ff, #ffffff, #a855f7, transparent);
            top: 50%;
            left: -20%;
            transform: rotate(-35deg) scaleX(0);
            box-shadow: 0 0 25px #00d2ff, 0 0 45px #a855f7;
            opacity: 0;
        }}

        #introAnimOverlay.active .slash-beam {{
            animation: slashFlash 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards 0.4s;
        }}

        @keyframes slashFlash {{
            0% {{ transform: rotate(-35deg) scaleX(0); opacity: 0; }}
            50% {{ opacity: 1; transform: rotate(-35deg) scaleX(1); }}
            100% {{ transform: rotate(-35deg) scaleX(1.2); opacity: 0; }}
        }}

        .sf-stage-box {{
            position: relative;
            width: 200px;
            height: 200px;
            display: flex;
            align-items: center;
            justify-content: center;
            transform: translate3d(0, 0, 0);
            will-change: transform, opacity;
        }}

        .sf-svg-logo {{
            width: 100%;
            height: 100%;
            filter: drop-shadow(0 0 20px rgba(168, 85, 247, 0.8)) drop-shadow(0 0 35px rgba(0, 210, 255, 0.6));
        }}

        .sf-rect-path {{
            stroke-dasharray: 650;
            stroke-dashoffset: 650;
        }}

        #introAnimOverlay.active .sf-rect-path {{
            animation: drawRect 1.0s cubic-bezier(0.16, 1, 0.3, 1) forwards 0.3s;
        }}

        @keyframes drawRect {{
            to {{ stroke-dashoffset: 0; }}
        }}

        .sf-letters-group {{
            opacity: 0;
            transform: scale(0.6) rotate(-10deg);
            will-change: transform, opacity;
        }}

        #introAnimOverlay.active .sf-letters-group {{
            animation: sfImpact 0.7s cubic-bezier(0.34, 1.56, 0.64, 1) forwards 0.8s;
        }}

        @keyframes sfImpact {{
            0% {{ opacity: 0; transform: scale(0.5) rotate(-20deg); }}
            70% {{ transform: scale(1.15) rotate(3deg); }}
            100% {{ opacity: 1; transform: scale(1) rotate(0deg); }}
        }}

        .welcome-text-kinetic {{
            margin-top: 30px;
            font-size: 22px;
            font-weight: 900;
            letter-spacing: 5px;
            text-transform: uppercase;
            background: linear-gradient(90deg, #ffffff 0%, #d8b4fe 40%, #00d2ff 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 20px rgba(168, 85, 247, 0.6);
            opacity: 0;
            will-change: transform, opacity;
        }}

        #introAnimOverlay.active .welcome-text-kinetic {{
            animation: kineticTextReveal 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards 1.2s;
        }}

        @keyframes kineticTextReveal {{
            0% {{ transform: translate3d(-30px, 0, 0) skewX(-20deg); opacity: 0; }}
            50% {{ transform: translate3d(10px, 0, 0) skewX(10deg); opacity: 0.8; }}
            100% {{ transform: translate3d(0, 0, 0) skewX(0deg); opacity: 1; }}
        }}

        .stage {{
            position: relative;
            width: 1100px;
            height: 650px;
            display: flex;
            align-items: center;
            transition: transform 0.8s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.6s ease;
        }}

        .stage.shifted-bottom-left {{
            transform: translateX(-180px) translateY(120px) scale(0.85);
        }}

        /* ==========================================
           ESTILO DO CLASSIFICADOR DE TERMINAIS 3D
           ========================================== */
        .terminal-stack-container {{
            position: fixed;
            top: 15px;
            left: 20px;
            width: 480px;
            height: 260px;
            perspective: 1200px;
            z-index: 60;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.5s ease;
        }}

        .terminal-stack-container.visible {{
            opacity: 1;
            pointer-events: auto;
        }}

        .terminal-card {{
            position: absolute;
            width: 100%;
            height: 100%;
            background: rgba(13, 10, 25, 0.94);
            backdrop-filter: blur(14px);
            border: 1px solid rgba(168, 85, 247, 0.35);
            border-radius: 12px;
            padding: 10px;
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
            box-shadow: 0 12px 35px rgba(0, 0, 0, 0.75);
            transform-origin: bottom center;
            transition: transform 0.5s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.5s ease, width 0.5s ease, height 0.5s ease;
            display: flex;
            flex-direction: column;
            backface-visibility: hidden;
            cursor: pointer;
        }}

        .terminal-card.expanded {{
            width: 650px !important;
            height: 480px !important;
            transform: translate(220px, 80px) rotateX(0deg) scale(1) !important;
            z-index: 100 !important;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.9), 0 0 30px var(--primary-glow);
            border-color: var(--primary-neon);
        }}

        .terminal-card.flipped-down {{
            transform: translateY(40px) translateZ(-50px) rotateX(-95deg) !important;
            opacity: 0.15 !important;
            pointer-events: none !important;
            filter: brightness(0.4);
        }}

        .terminal-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 6px;
            margin-bottom: 6px;
            border-bottom: 1px solid rgba(168, 85, 247, 0.25);
        }}

        .terminal-body {{
            flex: 1;
            overflow-y: auto;
            font-size: 11px;
            color: #a7f3d0;
            line-height: 1.4;
            white-space: pre-wrap;
            padding-right: 4px;
        }}

        .terminal-body::-webkit-scrollbar {{
            width: 4px;
        }}
        .terminal-body::-webkit-scrollbar-thumb {{
            background: rgba(168, 85, 247, 0.3);
            border-radius: 4px;
        }}

        .terminal-input-container {{
            display: flex;
            align-items: center;
            gap: 6px;
            margin-top: 6px;
            padding-top: 6px;
            border-top: 1px solid rgba(168, 85, 247, 0.2);
        }}

        .terminal-input {{
            flex: 1;
            background: rgba(0, 0, 0, 0.6);
            border: 1px solid rgba(168, 85, 247, 0.3);
            border-radius: 6px;
            padding: 4px 8px;
            font-size: 11px;
            color: #a7f3d0;
            outline: none;
            font-family: inherit;
        }}

        .terminal-input:focus {{
            border-color: var(--primary-neon);
            box-shadow: 0 0 8px rgba(168, 85, 247, 0.4);
        }}

        /* BOTÃO SUPERIOR DIREITO: HUMANO / IA */
        .mode-selector {{
            position: fixed;
            top: 25px;
            right: 35px;
            background: rgba(15, 23, 42, 0.85);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(168, 85, 247, 0.3);
            border-radius: 30px;
            padding: 4px;
            display: flex;
            gap: 4px;
            z-index: 100;
            box-shadow: 0 10px 25px rgba(0,0,0,0.6);
            transition: all 0.5s ease;
        }}

        body.light-mode .mode-selector {{
            background: rgba(255, 255, 255, 0.9);
            border-color: rgba(0, 0, 0, 0.15);
        }}

        .mode-btn {{
            padding: 8px 22px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 1px;
            cursor: pointer;
            transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
            color: #9ca3af;
        }}

        .mode-btn.active {{
            background: linear-gradient(135deg, #a855f7 0%, #7c3aed 100%);
            color: #ffffff;
            box-shadow: 0 0 20px rgba(168, 85, 247, 0.7);
        }}

        #btnHumano.active {{
            background: linear-gradient(135deg, #00d2ff 0%, #0284c7 100%);
            box-shadow: 0 0 20px rgba(0, 210, 255, 0.7);
        }}

        /* INTERRUPTOR DE LUZ VERTICAL */
        .switch-container {{
            position: fixed;
            left: 30px;
            top: 50%;
            transform: translateY(-50%);
            display: flex;
            align-items: center;
            gap: 10px;
            z-index: 50;
            transition: opacity 0.5s ease;
        }}

        .switch-track {{
            width: 46px;
            height: 105px;
            background: linear-gradient(180deg, #d4d4d8 0%, #a1a1aa 100%);
            border-radius: 23px;
            padding: 4px;
            position: relative;
            cursor: pointer;
            box-shadow: inset 0 3px 6px rgba(0,0,0,0.35), 0 6px 15px rgba(0,0,0,0.3);
            transition: all 0.6s ease;
        }}

        body:not(.light-mode) .switch-track {{
            background: linear-gradient(180deg, #171324 0%, #0a0711 100%);
            box-shadow: 0 0 20px rgba(168, 85, 247, 0.5), inset 0 3px 8px rgba(0,0,0,0.8);
            border: 1px solid rgba(168, 85, 247, 0.4);
        }}

        .switch-labels {{
            position: absolute;
            width: 100%;
            height: 100%;
            top: 0;
            left: 0;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            align-items: center;
            padding: 12px 0;
            font-size: 8.5px;
            font-weight: 800;
            letter-spacing: 0.5px;
            color: #71717a;
            pointer-events: none;
            z-index: 1;
        }}

        body:not(.light-mode) .switch-labels {{
            color: #9ca3af;
        }}

        .switch-thumb {{
            width: 38px;
            height: 48px;
            border-radius: 19px;
            background: linear-gradient(180deg, #f4f4f5 0%, #e4e4e7 100%);
            box-shadow: 0 4px 10px rgba(0,0,0,0.3), inset 0 1px 2px rgba(255,255,255,0.9);
            position: absolute;
            top: 4px;
            left: 4px;
            transition: transform 0.6s cubic-bezier(0.22, 1, 0.36, 1), background 0.6s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 2;
        }}

        body:not(.light-mode) .switch-thumb {{
            transform: translateY(49px);
            background: linear-gradient(180deg, #27213c 0%, #120d1f 100%);
            box-shadow: 0 0 12px rgba(168, 85, 247, 0.6), inset 0 1px 2px rgba(255,255,255,0.1);
        }}

        .switch-arrow {{
            width: 0;
            height: 0;
            border-top: 5px solid transparent;
            border-bottom: 5px solid transparent;
            border-left: 9px solid #71717a;
            transition: border-color 0.6s ease;
        }}

        body:not(.light-mode) .switch-arrow {{
            border-left-color: #c084fc;
            filter: drop-shadow(0 0 4px #c084fc);
        }}

        .dotted-scale {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: space-between;
            height: 95px;
            padding: 2px 0;
            font-size: 8.5px;
            font-weight: 800;
            color: #71717a;
        }}

        body:not(.light-mode) .dotted-scale {{
            color: #c084fc;
        }}

        .dots-col {{
            display: flex;
            flex-direction: column;
            gap: 4px;
        }}

        .dot {{
            width: 2.5px;
            height: 2.5px;
            border-radius: 50%;
            background-color: #a1a1aa;
        }}

        body:not(.light-mode) .dot {{
            background-color: #c084fc;
            box-shadow: 0 0 3px #c084fc;
        }}

        /* CONTAINER ESFERA 3D E CARDS */
        .sphere-container {{
            position: absolute;
            left: 110px;
            width: 320px;
            height: 320px;
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 20;
        }}

        canvas.sphere-canvas {{
            width: 100%;
            height: 100%;
            filter: drop-shadow(0 0 25px var(--primary-glow));
            transition: filter 0.8s ease;
        }}

        .connector-line {{
            position: absolute;
            left: 420px;
            top: 50%;
            width: 70px;
            height: 2px;
            background: linear-gradient(90deg, rgba(168,85,247,0.3) 0%, var(--primary-neon) 100%);
            pointer-events: none;
            z-index: 15;
            transform: translateY(-50%);
            transition: opacity 0.5s ease;
        }}

        .connector-dot {{
            position: absolute;
            right: 0;
            top: -3px;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: var(--primary-neon);
            box-shadow: 0 0 12px var(--primary-neon);
        }}

        #cardsList {{
            transition: opacity 0.6s ease, transform 0.6s ease;
        }}

        #cardsList.menu-transitioning {{
            transform: translateX(-60px) scale(0.8);
            opacity: 0.25;
            filter: blur(3px);
        }}

        .card-item {{
            position: absolute;
            left: 500px;
            top: 50%;
            cursor: pointer;
            z-index: 10;
            transition: transform 0.6s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.6s ease;
        }}

        .card-content {{
            width: 240px;
            padding: 14px 20px;
            background: var(--card-bg);
            backdrop-filter: blur(16px);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            display: flex;
            align-items: center;
            gap: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.4);
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        }}

        .card-item:hover .card-content {{
            border-color: var(--primary-neon);
            box-shadow: 0 0 30px var(--primary-glow), 0 12px 25px rgba(0,0,0,0.5);
            transform: scale(1.06) translateX(6px);
        }}

        .card-item.active .card-content {{
            border-color: var(--primary-neon);
            box-shadow: 0 0 35px var(--primary-glow), 0 12px 25px rgba(0,0,0,0.5);
            color: var(--text-color);
            z-index: 30;
        }}

        .card-icon {{
            color: var(--primary-neon);
        }}

        /* ==========================================
           TELA 3D DO BANCO DE DADOS (THREE.JS)
           ========================================== */
        .database-overlay {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: #020617;
            z-index: 95;
            display: flex;
            flex-direction: column;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.8s ease;
            overflow: hidden;
        }}

        .database-overlay.visible {{
            opacity: 1;
            pointer-events: auto;
        }}

        #webgl-db-container {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            z-index: 1;
        }}

        .db-header {{
            position: absolute;
            top: 25px;
            left: 50%;
            transform: translateX(-50%);
            display: flex;
            align-items: center;
            gap: 12px;
            z-index: 110;
            background: rgba(8, 24, 48, 0.85);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(0, 180, 255, 0.5);
            padding: 8px 18px;
            border-radius: 40px;
            box-shadow: 0 0 35px rgba(0, 180, 255, 0.3);
            width: 560px;
        }}

        .db-search-input {{
            flex: 1;
            background: transparent;
            border: none;
            outline: none;
            color: #b0e5ff;
            font-size: 13px;
            font-family: monospace;
            padding: 4px 8px;
        }}

        .db-search-input::placeholder {{
            color: rgba(176, 229, 255, 0.4);
        }}

        .db-btn-search {{
            background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
            border: 1px solid #38bdf8;
            color: #ffffff;
            font-size: 11px;
            font-weight: 800;
            padding: 6px 18px;
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 0 15px rgba(2, 132, 199, 0.6);
        }}

        .db-btn-search:hover {{
            transform: scale(1.05);
            background: #0284c7;
            box-shadow: 0 0 25px rgba(56, 189, 248, 0.8);
        }}

        .db-btn-close {{
            position: absolute;
            top: 25px;
            left: 35px;
            z-index: 110;
            background: rgba(15, 23, 42, 0.85);
            border: 1px solid rgba(56, 189, 248, 0.4);
            color: #38bdf8;
            padding: 8px 18px;
            border-radius: 30px;
            font-size: 11px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s ease;
        }}

        .db-btn-close:hover {{
            background: rgba(56, 189, 248, 0.25);
            color: #fff;
            box-shadow: 0 0 20px rgba(56, 189, 248, 0.5);
        }}

        .db-folder-panel {{
            position: absolute;
            right: 40px;
            top: 50%;
            transform: translateY(-50%) translateX(100px);
            width: 350px;
            background: rgba(6, 22, 45, 0.92);
            backdrop-filter: blur(20px);
            border: 1px solid #38bdf8;
            border-radius: 20px;
            padding: 24px;
            box-shadow: 0 0 45px rgba(2, 132, 199, 0.4);
            z-index: 105;
            opacity: 0;
            pointer-events: none;
            transition: all 0.6s cubic-bezier(0.16, 1, 0.3, 1);
        }}

        .db-folder-panel.visible {{
            opacity: 1;
            pointer-events: auto;
            transform: translateY(-50%) translateX(0);
        }}

        .folder-viewer-modal {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(2, 8, 20, 0.88);
            backdrop-filter: blur(16px);
            z-index: 120;
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 0;
            pointer-events: none;
            transition: all 0.4s ease;
        }}

        .folder-viewer-modal.visible {{
            opacity: 1;
            pointer-events: auto;
        }}

        .folder-viewer-box {{
            width: 780px;
            height: 520px;
            background: rgba(8, 24, 48, 0.95);
            border: 1px solid #38bdf8;
            border-radius: 20px;
            display: flex;
            flex-direction: column;
            padding: 24px;
            box-shadow: 0 0 50px rgba(2, 132, 199, 0.5);
        }}

        /* MODO IA: TELA LIMPA PRONTA PARA NOVA IMPLEMENTAÇÃO */
        .ai-screen {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background-color: #030712;
            z-index: 80;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.4s ease;
            overflow: hidden;
        }}

        .ai-screen.active {{
            opacity: 1;
            pointer-events: auto;
        }}

        .ai-ui-overlay {{
            color: rgba(168, 85, 247, 0.8);
            font-size: 14px;
            letter-spacing: 4px;
            text-transform: uppercase;
            font-weight: 600;
            text-shadow: 0 0 15px rgba(168, 85, 247, 0.4);
            user-select: none;
        }}

        /* SALA DE DESENVOLVIMENTO */
        .dev-overlay {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(3, 7, 18, 0.98);
            z-index: 100;
            display: flex;
            justify-content: flex-end;
            opacity: 0;
            pointer-events: none;
            transform: scale(0.98);
            transition: all 0.6s cubic-bezier(0.16, 1, 0.3, 1);
            overflow: hidden;
        }}

        .dev-overlay.visible {{
            opacity: 1;
            pointer-events: auto;
            transform: scale(1);
        }}

        .dev-panel {{
            width: 480px;
            height: 100%;
            background: rgba(3, 7, 18, 0.88);
            backdrop-filter: blur(18px);
            border-left: 1px solid rgba(6, 182, 212, 0.3);
            display: flex;
            flex-direction: column;
            padding: 28px;
            box-shadow: -15px 0 40px rgba(0, 0, 0, 0.9);
            z-index: 10;
            position: relative;
        }}

        .dev-news-item {{
            background: rgba(15, 23, 42, 0.75);
            border: 1px solid rgba(6, 182, 212, 0.25);
            border-radius: 14px;
            padding: 16px;
            transition: all 0.3s ease;
        }}

        .dev-news-item:hover {{
            border-color: #06b6d4;
            box-shadow: 0 0 20px rgba(6, 182, 212, 0.3);
        }}

        /* FEED DO FLAMENGO */
        .flamengo-overlay {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(10, 5, 12, 0.95);
            backdrop-filter: blur(20px);
            z-index: 100;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 30px 20px;
            opacity: 0;
            pointer-events: none;
            transform: translateY(20px);
            transition: all 0.6s cubic-bezier(0.16, 1, 0.3, 1);
        }}

        .flamengo-overlay.visible {{
            opacity: 1;
            pointer-events: auto;
            transform: translateY(0);
        }}

        .flamengo-header {{
            width: 100%;
            max-width: 800px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 20px;
            border-bottom: 2px solid rgba(225, 29, 72, 0.4);
            margin-bottom: 25px;
        }}

        .flamengo-feed {{
            width: 100%;
            max-width: 800px;
            flex: 1;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 20px;
            padding-right: 8px;
        }}

        .feed-card {{
            background: rgba(20, 10, 25, 0.85);
            border: 1px solid rgba(225, 29, 72, 0.3);
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0 10px 25px rgba(225, 29, 72, 0.15);
            transition: all 0.3s ease;
            cursor: pointer;
        }}

        .feed-card:hover {{
            border-color: #e11d48;
            box-shadow: 0 0 25px rgba(225, 29, 72, 0.35);
            transform: translateY(-2px);
        }}

        /* MODAL DE COMENTÁRIOS */
        .comments-modal {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(12px);
            z-index: 120;
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 0;
            pointer-events: none;
            transition: all 0.4s ease;
        }}

        .comments-modal.visible {{
            opacity: 1;
            pointer-events: auto;
        }}

        .comments-box {{
            width: 100%;
            max-width: 650px;
            height: 80vh;
            background: #110816;
            border: 1px solid rgba(225, 29, 72, 0.5);
            border-radius: 20px;
            display: flex;
            flex-direction: column;
            padding: 24px;
            box-shadow: 0 20px 50px rgba(225, 29, 72, 0.3);
        }}

        .comments-list {{
            flex: 1;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 12px;
            margin: 15px 0;
            padding-right: 6px;
        }}

        .comment-item {{
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 12px 16px;
            border: 1px solid rgba(255, 255, 255, 0.08);
        }}

        /* DASHBOARD */
        .dashboard-overlay {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: var(--bg-main);
            z-index: 100;
            display: flex;
            padding: 30px;
            gap: 25px;
            opacity: 0;
            pointer-events: none;
            transform: scale(0.96);
            transition: all 0.7s cubic-bezier(0.16, 1, 0.3, 1);
        }}

        .dashboard-overlay.visible {{
            opacity: 1;
            pointer-events: auto;
            transform: scale(1);
        }}

        .dash-sidebar {{
            width: 80px;
            background: linear-gradient(180deg, #7c3aed 0%, #4c1d95 100%);
            border-radius: 24px;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 25px 0;
            justify-content: space-between;
            box-shadow: 0 15px 35px rgba(124, 58, 237, 0.3);
        }}

        .dash-nav-icon {{
            width: 45px;
            height: 45px;
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: rgba(255, 255, 255, 0.6);
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        .dash-nav-icon:hover, .dash-nav-icon.active {{
            background: rgba(255, 255, 255, 0.2);
            color: #ffffff;
        }}

        .dash-main {{
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 20px;
            overflow-y: auto;
        }}

        .dash-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: var(--card-bg);
            padding: 18px 25px;
            border-radius: 20px;
            border: 1px solid var(--card-border);
            box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        }}

        .dash-grid {{
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 20px;
        }}

        .dash-overview {{
            background: linear-gradient(135deg, #7c3aed 0%, #5b21b6 100%);
            border-radius: 24px;
            padding: 25px;
            color: #ffffff;
            box-shadow: 0 15px 35px rgba(124, 58, 237, 0.3);
            position: relative;
        }}

        .dash-metric {{
            background: rgba(255, 255, 255, 0.12);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 15px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.15);
        }}

        .dash-card {{
            background: var(--card-bg);
            border-radius: 20px;
            padding: 20px;
            border: 1px solid var(--card-border);
            box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        }}

        .dash-pink-card {{
            background: linear-gradient(135deg, #ec4899 0%, #be185d 100%);
            color: #ffffff;
            border-radius: 20px;
            padding: 20px;
            box-shadow: 0 15px 30px rgba(236, 72, 153, 0.3);
        }}

        .dash-right-panel {{
            width: 300px;
            background: var(--card-bg);
            border-radius: 24px;
            padding: 22px;
            border: 1px solid var(--card-border);
            display: flex;
            flex-direction: column;
            gap: 15px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        }}

        .dash-activity {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid var(--card-border);
        }}
        .dash-activity:last-child {{ border-bottom: none; }}
    </style>
</head>
<body class="h-screen w-screen flex items-center justify-center relative logged-out">

    <!-- TELA DE LOGIN CÓSMICA ("SOL ATRÁS DA TERRA") -->
    <div id="loginScreenWrapper">
        <div class="sun-flare"></div>
        <div class="planet-horizon"></div>
        <div class="stars-bg"></div>

        <div class="login-container" id="loginContainer">
            <!-- FORMULÁRIO ADMINISTRADOR -->
            <div class="form-container sign-up">
                <form onsubmit="realizarLogin(event, 'admin')">
                    <h1 class="text-2xl font-bold mb-2 text-white">Painel Administrador</h1>
                    <span class="mb-4 text-purple-300/80">Credenciais de Administrador</span>
                    <input type="text" placeholder="ID de Admin" required />
                    <input type="email" placeholder="E-mail Corporativo" required />
                    <input type="password" placeholder="Senha Master" required />
                    <button type="submit">ENTRAR COMO ADMIN</button>
                </form>
            </div>

            <!-- FORMULÁRIO USUÁRIO COMUM -->
            <div class="form-container sign-in">
                <form onsubmit="realizarLogin(event, 'usuario')">
                    <h1 class="text-2xl font-bold mb-2 text-white">Iniciar Sessão</h1>
                    <span class="mb-4 text-purple-300/80">Informe seu e-mail e senha</span>
                    <input type="email" placeholder="E-mail" required />
                    <input type="password" placeholder="Senha" required />
                    <a href="#" class="my-2">Esqueceu a senha?</a>
                    <button type="submit">INICIAR SESSÃO</button>
                </form>
            </div>

            <!-- OVERLAY SLIDE DIREITA/ESQUERDA -->
            <div class="toggle-container">
                <div class="toggle">
                    <div class="toggle-panel toggle-left">
                        <h1 class="text-2xl font-bold text-white">Modo Usuário</h1>
                        <p>Deseja retornar ao acesso de usuário comum?</p>
                        <button class="hidden-btn" id="loginBtn">USUÁRIO</button>
                    </div>

                    <div class="toggle-panel toggle-right">
                        <h1 class="text-2xl font-bold text-white">Administrador</h1>
                        <p>Acesse o painel restrito de gerenciamento.</p>
                        <button class="hidden-btn" id="registerBtn">ADMINISTRADOR</button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- ANIMAÇÃO DE ABERTURA KINETIC NEON -->
    <div id="introAnimOverlay">
        <div class="spotlight-sweep"></div>
        <div class="slash-beam"></div>

        <div class="sf-stage-box">
            <svg class="sf-svg-logo" viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect class="sf-rect-path" x="20" y="20" width="160" height="160" rx="36" stroke="url(#gradientNeon)" stroke-width="6" stroke-linecap="round"/>
                
                <g class="sf-letters-group">
                    <path d="M 65 72 C 65 58, 95 58, 95 76 C 95 94, 65 94, 65 112 C 65 130, 95 130, 95 116" stroke="url(#gradientCyan)" stroke-width="9" stroke-linecap="round"/>
                    <path d="M 115 62 L 140 62 M 115 62 L 115 128 M 115 92 L 135 92" stroke="url(#gradientNeon)" stroke-width="9" stroke-linecap="round"/>
                </g>

                <defs>
                    <linearGradient id="gradientNeon" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stop-color="#a855f7"/>
                        <stop offset="50%" stop-color="#00d2ff"/>
                        <stop offset="100%" stop-color="#c084fc"/>
                    </linearGradient>
                    <linearGradient id="gradientCyan" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stop-color="#00d2ff"/>
                        <stop offset="100%" stop-color="#38bdf8"/>
                    </linearGradient>
                </defs>
            </svg>
        </div>

        <div class="welcome-text-kinetic">Bem-vindo à Sexta-Feira</div>
    </div>

    <!-- BOTÃO SUPERIOR DIREITO: HUMANO / IA -->
    <div class="mode-selector">
        <div id="btnHumano" class="mode-btn active" onclick="mudarModo('humano')">HUMANO</div>
        <div id="btnIA" class="mode-btn" onclick="mudarModo('ia')">IA</div>
    </div>

    <!-- PASTA / CLASSIFICADOR 3D COM PILHA DE TERMINAIS -->
    <div class="terminal-stack-container" id="terminalContainer"></div>

    <!-- MODO IA: TELA LIMPA -->
    <div class="ai-screen" id="aiScreen">
        <div class="ai-ui-overlay">Sexta-Feira IA • Aguardando Nova Implementação...</div>
    </div>

    <!-- TELA 3D DO BANCO DE DADOS -->
    <div class="database-overlay" id="databaseOverlay">
        <button class="db-btn-close" onclick="fecharBancoDeDados()">← VOLTAR AO MENU</button>
        
        <div class="db-header">
            <svg class="w-4 h-4 text-cyan-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
            <input type="text" id="dbSearchInput" class="db-search-input" placeholder="Ex: atualização 16/10/2026 ou Planilha 16/10/2026..." onkeydown="tratarBuscaDB(event)">
            <button class="db-btn-search" onclick="pesquisarPastaDB()">PESQUISAR</button>
        </div>

        <div id="webgl-db-container"></div>

        <div class="db-folder-panel" id="dbFolderPanel">
            <div class="flex justify-between items-center mb-3">
                <span class="text-[10px] text-cyan-400 font-mono uppercase font-bold tracking-widest">● PASTA SELECIONADA (3D)</span>
                <button onclick="fecharPainelPasta()" class="text-xs text-gray-400 hover:text-white">✕</button>
            </div>
            <h3 id="folderNameTitle" class="text-base font-bold text-white mb-1 leading-tight">Nome da Pasta</h3>
            <span id="folderDateBadge" class="text-[10px] text-cyan-400 bg-cyan-950 border border-cyan-800 px-2 py-0.5 rounded font-mono inline-block mb-3">Data: --/--/----</span>
            <p id="folderDetails" class="text-xs text-cyan-200/80 leading-relaxed mb-4">Pasta física elevada do arquivo 3D.</p>
            <div class="border-t border-cyan-500/30 pt-3 flex justify-between items-center text-xs">
                <span class="text-gray-400">Status: <strong class="text-emerald-400">Sincronizado</strong></span>
                <button onclick="abrirConteudoPastaSelecionada()" class="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg font-bold text-[11px] shadow-lg shadow-cyan-500/30 transition-all flex items-center gap-1.5">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 19a2 2 0 01-2-2V7a2 2 0 012-2h4l2 2h4a2 2 0 012 2v1M5 19h14a2 2 0 002-2v-5a2 2 0 00-2-2H9a2 2 0 00-2 2v5a2 2 0 01-2 2z"></path></svg>
                    Abrir Pasta
                </button>
            </div>
        </div>
    </div>

    <!-- MODAL DE EXIBIÇÃO DE DADOS DA PASTA ABERTA -->
    <div class="folder-viewer-modal" id="folderViewerModal">
        <div class="folder-viewer-box">
            <div class="flex justify-between items-center border-b border-cyan-500/30 pb-3 mb-4">
                <div>
                    <span class="text-[10px] text-cyan-400 uppercase font-mono tracking-widest font-bold">● REGISTRO DA PASTA</span>
                    <h2 id="viewerTitle" class="text-lg font-bold text-white">---</h2>
                </div>
                <button onclick="fecharViewerModal()" class="text-gray-400 hover:text-white text-lg font-bold">✕</button>
            </div>

            <div class="flex-1 overflow-y-auto space-y-3 pr-2 font-mono text-xs" id="viewerLogContent"></div>

            <div class="border-t border-cyan-500/30 pt-3 mt-3 flex justify-between items-center">
                <span id="viewerFooterInfo" class="text-[10px] text-gray-400 font-mono">Consultado via Python Backend</span>
                <button onclick="fecharViewerModal()" class="px-4 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-xs font-bold">Fechar Visualização</button>
            </div>
        </div>
    </div>

    <!-- SALA DE DESENVOLVIMENTO -->
    <div class="dev-overlay" id="devOverlay">
        <div class="dev-panel">
            <div class="flex justify-between items-center border-b border-cyan-500/30 pb-4 mb-6">
                <div>
                    <span class="text-[10px] text-cyan-400 font-mono font-bold tracking-widest uppercase">● DEV ROOM v2.5</span>
                    <h2 class="text-lg font-bold text-white tracking-wide">SALA DE DESENVOLVIMENTO</h2>
                </div>
                <button onclick="fecharDevRoom()" class="px-3 py-1.5 bg-cyan-600/30 hover:bg-cyan-600 border border-cyan-500 text-cyan-200 hover:text-white rounded-lg text-xs font-mono transition-all">
                    FECHAR
                </button>
            </div>

            <div class="flex-1 overflow-y-auto space-y-4 pr-1 font-sans">
                <div class="dev-news-item">
                    <div class="flex justify-between items-center mb-1">
                        <span class="text-[10px] bg-cyan-500/20 text-cyan-400 font-mono px-2 py-0.5 rounded font-bold">BUILD #240</span>
                        <span class="text-[10px] text-gray-500">Hoje</span>
                    </div>
                    <h3 class="text-sm font-bold text-white mb-1">Hologram Engine Update</h3>
                    <p class="text-xs text-gray-300 leading-relaxed">Nova renderização vetorial e suporte a animações HUD de alta resolução integradas diretamente ao núcleo.</p>
                </div>

                <div class="dev-news-item">
                    <div class="flex justify-between items-center mb-1">
                        <span class="text-[10px] bg-purple-500/20 text-purple-400 font-mono px-2 py-0.5 rounded font-bold">EM PROGRESSO</span>
                        <span class="text-[10px] text-gray-500">Ontem</span>
                    </div>
                    <h3 class="text-sm font-bold text-white mb-1">Módulo de Voz & Inteligência</h3>
                    <p class="text-xs text-gray-300 leading-relaxed">Implementação do reconhecimento contínuo de voz para a assistente Sexta-Feira com respostas por áudio.</p>
                </div>

                <div class="dev-news-item">
                    <div class="flex justify-between items-center mb-1">
                        <span class="text-[10px] bg-emerald-500/20 text-emerald-400 font-mono px-2 py-0.5 rounded font-bold">CONCLUÍDO</span>
                        <span class="text-[10px] text-gray-500">Há 2 dias</span>
                    </div>
                    <h3 class="text-sm font-bold text-white mb-1">Otimização de Memória WebView2</h3>
                    <p class="text-xs text-gray-300 leading-relaxed">Correção completa de vazamentos de memória e tratamento de mídias pesadas sem telas brancas.</p>
                </div>
            </div>

            <div class="border-t border-cyan-500/30 pt-4 mt-4 text-center">
                <span class="text-[10px] font-mono text-cyan-400/70">STATUS DA REDE: ESTÁVEL | LATÊNCIA: 12ms</span>
            </div>
        </div>
    </div>

    <!-- FEED DO FLAMENGO -->
    <div class="flamengo-overlay" id="flamengoOverlay">
        <div class="flamengo-header">
            <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-full bg-rose-600 flex items-center justify-center font-bold text-white shadow-lg shadow-rose-600/50">
                    CRF
                </div>
                <div>
                    <h2 class="text-lg font-bold text-rose-500 tracking-wider">CLUBE DE REGATAS DO FLAMENGO</h2>
                    <p class="text-xs text-gray-400">Clique em qualquer notícia para ler e ver os comentários</p>
                </div>
            </div>
            <button onclick="fecharFlamengo()" class="px-4 py-2 bg-rose-600 hover:bg-rose-700 text-white rounded-xl text-xs font-semibold shadow-md transition-all">
                Fechar Feed
            </button>
        </div>

        <div class="flamengo-feed" id="flamengoFeed"></div>
    </div>

    <!-- MODAL DE COMENTÁRIOS DO FLAMENGO -->
    <div class="comments-modal" id="commentsModal">
        <div class="comments-box">
            <div class="flex justify-between items-start border-b border-rose-900/40 pb-3">
                <div>
                    <span class="text-[10px] text-rose-400 uppercase font-bold tracking-widest">Área de Comentários</span>
                    <h3 id="modalNewsTitle" class="text-sm font-bold text-white leading-tight mt-1"></h3>
                </div>
                <button onclick="fecharComentarios()" class="text-gray-400 hover:text-white text-lg font-bold">✕</button>
            </div>

            <div class="comments-list" id="modalCommentsList"></div>

            <div class="flex gap-2 border-t border-rose-900/40 pt-3">
                <input type="text" id="inputComment" placeholder="Escreva o seu comentário..." class="flex-1 bg-black/50 border border-rose-900/50 rounded-xl px-4 py-2 text-xs text-white focus:outline-none focus:border-rose-500">
                <button onclick="enviarComentario()" class="px-4 py-2 bg-rose-600 hover:bg-rose-700 text-white rounded-xl text-xs font-bold transition-all">
                    Comentar
                </button>
            </div>
        </div>
    </div>

    <!-- INTERRUPTOR DE LUZ VERTICAL (ESQUERDA) -->
    <div class="switch-container" id="switchContainer">
        <div class="switch-track" onclick="toggleTheme()">
            <div class="switch-labels">
                <span>OFF</span>
                <span>ON</span>
            </div>
            <div class="switch-thumb" id="switchThumb">
                <div class="switch-arrow"></div>
            </div>
        </div>
        <div class="dotted-scale">
            <span>ER</span>
            <div class="dots-col">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
            </div>
            <span>SÜ</span>
        </div>
    </div>

    <!-- TELA PRINCIPAL HOLOGRÁFICA (ORBITAL) -->
    <div class="stage" id="stageMain">
        <div class="sphere-container">
            <canvas class="sphere-canvas" id="holoSphere" width="400" height="400"></canvas>
        </div>

        <div class="connector-line" id="connectorLine">
            <div class="connector-dot"></div>
        </div>

        <div id="cardsList"></div>
    </div>

    <!-- DASHBOARD DE ESTATÍSTICAS -->
    <div class="dashboard-overlay" id="dashboardOverlay">
        <div class="dash-sidebar">
            <div class="flex flex-col items-center gap-4">
                <div class="dash-nav-icon bg-white/20 text-white">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"></path></svg>
                </div>
                <div class="dash-nav-icon active">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path></svg>
                </div>
                <div class="dash-nav-icon">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                </div>
                <div class="dash-nav-icon">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path></svg>
                </div>
            </div>

            <div class="dash-nav-icon bg-white/20 text-white" onclick="fecharDashboard()" title="Voltar ao Menu">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path></svg>
            </div>
        </div>

        <div class="dash-main">
            <div class="dash-header">
                <div>
                    <h2 class="text-lg font-bold">Primary Dashboard</h2>
                    <p class="text-xs text-gray-400">Visão geral estatística e automações</p>
                </div>
                <button onclick="fecharDashboard()" class="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-xl text-xs font-semibold shadow-md transition-all">
                    Fechar Estatísticas
                </button>
            </div>

            <div class="dash-grid">
                <div class="flex flex-col gap-4">
                    <div class="dash-overview">
                        <div class="flex justify-between items-center mb-3">
                            <h3 class="text-sm font-semibold opacity-80 uppercase">Overview de Atividades</h3>
                            <span class="bg-white/20 text-[11px] px-3 py-1 rounded-full">Mensal</span>
                        </div>
                        <div class="h-28 mb-3">
                            <canvas id="overviewChart"></canvas>
                        </div>
                        <div class="grid grid-cols-3 gap-3">
                            <div class="dash-metric">
                                <span class="text-[10px] opacity-70 uppercase">Tempo Total</span>
                                <p class="text-base font-bold">748 Hr</p>
                            </div>
                            <div class="dash-metric">
                                <span class="text-[10px] opacity-70 uppercase">Total Tarefas</span>
                                <p class="text-base font-bold">9.178 St</p>
                            </div>
                            <div class="dash-metric">
                                <span class="text-[10px] opacity-70 uppercase">Meta Diária</span>
                                <p class="text-base font-bold">9.200 St</p>
                            </div>
                        </div>
                    </div>

                    <div class="grid grid-cols-3 gap-3">
                        <div class="dash-card">
                            <div class="w-8 h-8 rounded-xl bg-purple-100 text-purple-600 flex items-center justify-center mb-2">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
                            </div>
                            <h4 class="font-bold text-xs">Planilhas</h4>
                            <p class="text-[10px] text-gray-400 mb-2">36 exec / semanas</p>
                            <div class="w-full bg-gray-200 dark:bg-gray-700 h-1.5 rounded-full overflow-hidden">
                                <div class="bg-purple-600 h-full w-[45%]"></div>
                            </div>
                        </div>
                        <div class="dash-card">
                            <div class="w-8 h-8 rounded-xl bg-indigo-100 text-indigo-600 flex items-center justify-center mb-2">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path></svg>
                            </div>
                            <h4 class="font-bold text-xs">Controle</h4>
                            <p class="text-[10px] text-gray-400 mb-2">12 mod / mês</p>
                            <div class="w-full bg-gray-200 dark:bg-gray-700 h-1.5 rounded-full overflow-hidden">
                                <div class="bg-indigo-600 h-full w-[13%]"></div>
                            </div>
                        </div>
                        <div class="dash-card">
                            <div class="w-8 h-8 rounded-xl bg-emerald-100 text-emerald-600 flex items-center justify-center mb-2">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                            </div>
                            <h4 class="font-bold text-xs">Lembrete</h4>
                            <p class="text-[10px] text-gray-400 mb-2">3600 checks</p>
                            <div class="w-full bg-gray-200 dark:bg-gray-700 h-1.5 rounded-full overflow-hidden">
                                <div class="bg-emerald-600 h-full w-[90%]"></div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="flex flex-col gap-4">
                    <div class="dash-pink-card">
                        <h3 class="font-bold text-sm mb-1">Projeto Meia Noite</h3>
                        <p class="text-[11px] opacity-80 mb-3">Rotina automatizada noturna ativa.</p>
                        <p class="text-2xl font-bold">748 <span class="text-xs font-normal">hr</span></p>
                    </div>
                    <div class="dash-card">
                        <h3 class="font-bold text-xs text-gray-400 uppercase mb-2">Status Diário</h3>
                        <div class="flex justify-between items-center text-xs">
                            <span>Execuções Hoje</span>
                            <span class="font-bold text-purple-600">18 tarefas</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="dash-right-panel">
            <h3 class="font-bold text-sm mb-2">Atividades Recentes</h3>
            <div class="flex flex-col gap-3 overflow-y-auto flex-1">
                <div class="dash-activity">
                    <div class="flex items-center gap-2.5">
                        <div class="w-8 h-8 rounded-full bg-purple-500/20 text-purple-600 flex items-center justify-center text-xs font-bold">UP</div>
                        <div>
                            <p class="text-xs font-bold">Atualização</p>
                            <p class="text-[10px] text-gray-400">Há 5 min</p>
                        </div>
                    </div>
                    <span class="text-[10px] bg-emerald-500/10 text-emerald-500 font-bold px-2 py-0.5 rounded">OK</span>
                </div>
                <div class="dash-activity">
                    <div class="flex items-center gap-2.5">
                        <div class="w-8 h-8 rounded-full bg-pink-500/20 text-pink-600 flex items-center justify-center text-xs font-bold">EX</div>
                        <div>
                            <p class="text-xs font-bold">Excluir Linhas</p>
                            <p class="text-[10px] text-gray-400">Há 22 min</p>
                        </div>
                    </div>
                    <span class="text-[10px] bg-emerald-500/10 text-emerald-500 font-bold px-2 py-0.5 rounded">OK</span>
                </div>
            </div>
        </div>
    </div>

    <!-- TERMINAL DE LOGS PYTHON -->
    <div id="statusConsole" class="fixed bottom-6 right-6 bg-slate-950/90 border border-purple-900/50 p-4 rounded-xl shadow-2xl max-w-sm w-full text-xs font-mono z-30 transition-opacity duration-500">
        <div class="text-purple-400 mb-1 border-b border-purple-900/40 pb-1 flex justify-between">
            <span>PYTHON LOG</span>
            <span id="statusIndicator" class="text-purple-400">● Sistema Ativo</span>
        </div>
        <div id="logText" class="text-slate-300 mt-2">Role o mouse para mover os cards na curva holográfica.</div>
    </div>

    <script>
        /* ==========================================
           LÓGICA DA TELA DE LOGIN & ANIMAÇÃO CINÉTICA DE ENTRADA
           ========================================== */
        const containerLogin = document.getElementById('loginContainer');
        const registerBtn = document.getElementById('registerBtn');
        const loginBtn = document.getElementById('loginBtn');

        if (registerBtn && loginBtn && containerLogin) {{
            registerBtn.addEventListener('click', () => {{
                containerLogin.classList.add("active");
            }});

            loginBtn.addEventListener('click', () => {{
                containerLogin.classList.remove("active");
            }});
        }}

        function realizarLogin(event, tipoUser) {{
            event.preventDefault();
            containerLogin.classList.add('shrink-out');

            setTimeout(() => {{
                document.getElementById('loginScreenWrapper').classList.add('hidden-login');
                const introOverlay = document.getElementById('introAnimOverlay');
                introOverlay.classList.add('active');

                setTimeout(() => {{
                    introOverlay.classList.add('fade-out');
                    document.body.classList.remove('logged-out');

                    setTimeout(() => {{
                        introOverlay.classList.remove('active', 'fade-out');
                        const msg = tipoUser === 'admin' ? "Autenticado como Administrador." : "Sessão iniciada com sucesso.";
                        atualizarLog(msg, "● Login Concluído");
                    }}, 800);

                }}, 2200);
            }}, 400);
        }}

        /* BASE DE DADOS DO FLAMENGO */
        const noticiasFlamengo = [
            {{
                id: 1,
                tag: '● Notícia Recente',
                tempo: 'Há 15 min',
                titulo: 'Flamengo intensifica preparação para a próxima rodada do Brasileirão',
                resumo: 'O elenco rubro-negro realizou treino tático no Ninho do Urubu focando nas jogadas ensaiadas e pressão alta. O técnico ajustou o posicionamento do setor ofensivo.',
                local: '🔴⚫ Ninho do Urubu',
                comentarios: [
                    {{ autor: 'Gabriel_CRF', tempo: 'Há 10 min', texto: 'Vamos pra cima! Mengão joga muito no Maracanã.' }},
                    {{ autor: 'Nacao1981', tempo: 'Há 5 min', texto: 'A pressão alta do time está encaixando muito bem.' }}
                ]
            }},
            {{
                id: 2,
                tag: '● Mercado da Bola',
                tempo: 'Há 1 hora',
                titulo: 'Diretoria avança em conversas para renovação de contrato de titular',
                resumo: 'As negociações com os representantes evoluíram positivamente nas últimas horas. O novo vínculo deve se estender por mais dois anos com valorização salarial.',
                local: '📋 Bastidores',
                comentarios: [
                    {{ autor: 'RubroNegroAteOFim', tempo: 'Há 45 min', texto: 'Renovação merecida demais! Jogador fundamental.' }},
                    {{ autor: 'ZicoEterno81', tempo: 'Há 30 min', texto: 'Excelente notícia pra manter a base do elenco forte.' }}
                ]
            }},
            {{
                id: 3,
                tag: '● Ingressos & Torcida',
                tempo: 'Há 3 horas',
                titulo: 'Maracanã lotado! Mais de 55 mil ingressos vendidos para o próximo jogo',
                resumo: 'A Nação Rubro-Negra esgotou os setores Norte e Leste Inferior em poucas horas de venda geral. Restam poucos bilhetes para o setor Oeste Superior.',
                local: '🏟️ Maracanã',
                comentarios: [
                    {{ autor: 'MaiorDoMundo', tempo: 'Há 2 horas', texto: 'Estarei lá no setor Norte fazendo a festa!' }},
                    {{ autor: 'FlaSempre', tempo: 'Há 1 hora', texto: 'Ingresso garantido, a festa na arquibancada tá pronta!' }}
                ]
            }}
        ];

        let noticiaAtivaId = null;

        function renderizarFeedFlamengo() {{
            const container = document.getElementById('flamengoFeed');
            container.innerHTML = '';
            noticiasFlamengo.forEach(noticia => {{
                const card = document.createElement('div');
                card.className = 'feed-card';
                card.onclick = () => abrirComentarios(noticia.id);
                card.innerHTML = `
                    <div class="flex justify-between items-center mb-2">
                        <span class="text-xs text-rose-400 font-semibold uppercase tracking-wider">${{noticia.tag}}</span>
                        <span class="text-xs text-gray-500">${{noticia.tempo}}</span>
                    </div>
                    <h3 class="text-base font-bold text-white mb-2">${{noticia.titulo}}</h3>
                    <p class="text-xs text-gray-300 leading-relaxed mb-3">${{noticia.resumo}}</p>
                    <div class="flex items-center gap-4 text-xs text-gray-400 border-t border-rose-900/40 pt-2">
                        <span>${{noticia.local}}</span>
                        <span class="text-rose-400 font-semibold">💬 ${{noticia.comentarios.length}} comentários (Clique para ver)</span>
                    </div>
                `;
                container.appendChild(card);
            }});
        }}

        function abrirComentarios(id) {{
            noticiaAtivaId = id;
            const noticia = noticiasFlamengo.find(n => n.id === id);
            if (!noticia) return;
            document.getElementById('modalNewsTitle').innerText = noticia.titulo;
            renderizarListaComentarios(noticia);
            document.getElementById('commentsModal').classList.add('visible');
        }}

        function renderizarListaComentarios(noticia) {{
            const listContainer = document.getElementById('modalCommentsList');
            listContainer.innerHTML = '';
            if (noticia.comentarios.length === 0) {{
                listContainer.innerHTML = '<p class="text-xs text-gray-500 text-center py-4">Seja o primeiro a comentar!</p>';
                return;
            }}
            noticia.comentarios.forEach(c => {{
                const div = document.createElement('div');
                div.className = 'comment-item';
                div.innerHTML = `
                    <div class="flex justify-between items-center mb-1">
                        <span class="text-xs font-bold text-rose-400">${{c.autor}}</span>
                        <span class="text-[10px] text-gray-500">${{c.tempo}}</span>
                    </div>
                    <p class="text-xs text-gray-200 leading-normal">${{c.texto}}</p>
                `;
                listContainer.appendChild(div);
            }});
        }}

        function enviarComentario() {{
            const input = document.getElementById('inputComment');
            const texto = input.value.trim();
            if (!texto || !noticiaAtivaId) return;
            const noticia = noticiasFlamengo.find(n => n.id === noticiaAtivaId);
            if (noticia) {{
                noticia.comentarios.push({{ autor: 'Você (Torcedor)', tempo: 'Agora mesmo', texto: texto }});
                input.value = '';
                renderizarListaComentarios(noticia);
                renderizarFeedFlamengo();
            }}
        }}

        function fecharComentarios() {{ document.getElementById('commentsModal').classList.remove('visible'); }}
        function abrirDevRoom() {{ document.getElementById('devOverlay').classList.add('visible'); atualizarLog("Abrindo Sala de Desenvolvimento...", "● Dev Room"); }}
        function fecharDevRoom() {{ document.getElementById('devOverlay').classList.remove('visible'); atualizarLog("Retornado ao menu principal.", "● Sistema Ativo"); }}
        function abrirFlamengo() {{ renderizarFeedFlamengo(); document.getElementById('flamengoOverlay').classList.add('visible'); atualizarLog("Carregando feed de notícias do Flamengo...", "● Flamengo"); }}
        function fecharFlamengo() {{ document.getElementById('flamengoOverlay').classList.remove('visible'); atualizarLog("Retornado ao menu principal.", "● Sistema Ativo"); }}

        /* ==========================================
           MOTOR 3D THREE.JS DO BANCO DE DADOS (SISTEMA VIVO + ELEVAÇÃO)
           ========================================== */
        let scene3D, camera3D, renderer3D, ringGroup3D;
        let folder3DObjects = [];
        let numFolders3D = 44;
        let ringRadius3D = 12.0;
        let is3DInitialized = false;
        let isDragging3D = false;
        let prevMousePos = {{ x: 0, y: 0 }};
        let targetRotY = 0;
        let baseRotSpeed3D = 0.0035;
        let rotSpeed3D = 0.0035;
        let raycaster3D = new THREE.Raycaster();
        let mouse3D = new THREE.Vector2();

        let pastaSelecionadaElevada = null;
        let clock3D = new THREE.Clock();

        let pastaPesquisadaAtiva = {{ term: '', data: '', rawQuery: '' }};

        function initThreeJSDB() {{
            const container = document.getElementById('webgl-db-container');
            if (is3DInitialized) return;

            scene3D = new THREE.Scene();
            scene3D.background = new THREE.Color(0x020617);
            scene3D.fog = new THREE.FogExp2(0x020617, 0.028);

            camera3D = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 100);
            camera3D.position.set(0, 5.5, 22.0);
            camera3D.lookAt(0, -0.2, 0);

            renderer3D = new THREE.WebGLRenderer({{ antialias: true, powerPreference: "high-performance" }});
            renderer3D.setSize(window.innerWidth, window.innerHeight);
            renderer3D.setPixelRatio(Math.min(window.devicePixelRatio, 2));
            renderer3D.shadowMap.enabled = true;
            renderer3D.shadowMap.type = THREE.PCFSoftShadowMap;
            container.appendChild(renderer3D.domElement);

            const keyLight = new THREE.DirectionalLight(0xe0f2fe, 1.8);
            keyLight.position.set(-6, 14, 12);
            keyLight.castShadow = true;
            scene3D.add(keyLight);

            const blueLight = new THREE.DirectionalLight(0x0284c7, 1.4);
            blueLight.position.set(8, -2, 10);
            scene3D.add(blueLight);

            const ambientLight = new THREE.AmbientLight(0x0f172a, 0.6);
            scene3D.add(ambientLight);

            ringGroup3D = new THREE.Group();
            scene3D.add(ringGroup3D);

            construirAnelPastasDenso3D();
            configurarEventos3D(container);

            is3DInitialized = true;
            animate3D();
        }}

        function criarMeshPastaEstiloFoto(index) {{
            const folderGroup = new THREE.Group();

            const width = 1.9;
            const height = 2.4;
            const thickness = 0.05;

            const shape = new THREE.Shape();
            const radius = 0.35;

            shape.moveTo(-width / 2, -height / 2);
            shape.lineTo(width / 2, -height / 2);
            shape.lineTo(width / 2, height / 2 - radius);
            shape.quadraticCurveTo(width / 2, height / 2, width / 2 - radius, height / 2);

            const tabOffset = (index % 3) * 0.4;
            shape.lineTo(-width / 2 + 0.6 + tabOffset, height / 2);
            shape.quadraticCurveTo(-width / 2 + 0.3 + tabOffset, height / 2 + 0.25, -width / 2 + tabOffset, height / 2 + 0.25);
            shape.lineTo(-width / 2 + radius, height / 2 + 0.25);
            shape.quadraticCurveTo(-width / 2, height / 2 + 0.25, -width / 2, height / 2);
            shape.lineTo(-width / 2, -height / 2);

            const extrudeSettings = {{
                depth: thickness,
                bevelEnabled: true,
                bevelSegments: 3,
                steps: 1,
                bevelSize: 0.02,
                bevelThickness: 0.02
            }};

            const folderGeo = new THREE.ExtrudeGeometry(shape, extrudeSettings);

            const folderMat = new THREE.MeshStandardMaterial({{
                color: 0x0284c7,
                roughness: 0.25,
                metalness: 0.75,
                emissive: 0x0369a1,
                emissiveIntensity: 0.15
            }});

            const frontCover = new THREE.Mesh(folderGeo, folderMat);
            frontCover.castShadow = true;
            folderGroup.add(frontCover);

            const backCover = frontCover.clone();
            backCover.position.z = -0.32;
            folderGroup.add(backCover);

            const paperGeo = new THREE.BoxGeometry(width * 0.94, height * 1.02, 0.28);
            const paperMat = new THREE.MeshStandardMaterial({{
                color: 0xf8fafc,
                roughness: 0.8,
                metalness: 0.05
            }});
            const paperBlock = new THREE.Mesh(paperGeo, paperMat);
            paperBlock.position.set(0, 0.08, -0.16);
            folderGroup.add(paperBlock);

            return folderGroup;
        }}

        function construirAnelPastasDenso3D() {{
            folder3DObjects.forEach(obj => ringGroup3D.remove(obj));
            folder3DObjects = [];

            for (let i = 0; i < numFolders3D; i++) {{
                const angle = (i / numFolders3D) * Math.PI * 2;
                const x = Math.sin(angle) * ringRadius3D;
                const z = Math.cos(angle) * ringRadius3D;

                const holder = new THREE.Group();
                holder.position.set(x, 0, z);
                holder.rotation.y = angle + Math.PI / 2 + 0.18;

                const meshPasta = criarMeshPastaEstiloFoto(i);
                holder.add(meshPasta);

                let numStr = (i + 1 < 10 ? '0' : '') + (i + 1);
                holder.userData = {{
                    id: i + 1,
                    index: i,
                    angle: angle,
                    baseY: 0,
                    targetY: 0,
                    folderMesh: meshPasta,
                    title: "Pasta Classificadora #" + numStr
                }};

                ringGroup3D.add(holder);
                folder3DObjects.push(holder);
            }}
        }}

        function animate3D() {{
            requestAnimationFrame(animate3D);
            const elapsedTime = clock3D.getElapsedTime();

            if (!isDragging3D) {{
                ringGroup3D.rotation.y += rotSpeed3D;
            }}

            ringGroup3D.rotation.y += (targetRotY - ringGroup3D.rotation.y) * 0.05;

            folder3DObjects.forEach((folder) => {{
                if (pastaSelecionadaElevada && folder === pastaSelecionadaElevada) {{
                    folder.userData.targetY = 1.8;
                }} else {{
                    folder.userData.targetY = Math.sin(elapsedTime * 2 + folder.userData.index * 0.3) * 0.08;
                }}

                folder.position.y += (folder.userData.targetY - folder.position.y) * 0.08;
            }});

            renderer3D.render(scene3D, camera3D);
        }}

        function configurarEventos3D(container) {{
            window.addEventListener('resize', () => {{
                if (!camera3D || !renderer3D) return;
                camera3D.aspect = window.innerWidth / window.innerHeight;
                camera3D.updateProjectionMatrix();
                renderer3D.setSize(window.innerWidth, window.innerHeight);
            }});

            container.addEventListener('mousedown', (e) => {{
                isDragging3D = true;
                prevMousePos = {{ x: e.clientX, y: e.clientY }};
            }});

            container.addEventListener('mousemove', (e) => {{
                if (!isDragging3D) return;
                const deltaX = e.clientX - prevMousePos.x;
                targetRotY += deltaX * 0.005;
                prevMousePos = {{ x: e.clientX, y: e.clientY }};
            }});

            window.addEventListener('mouseup', () => {{ isDragging3D = false; }});

            container.addEventListener('click', (e) => {{
                mouse3D.x = (e.clientX / window.innerWidth) * 2 - 1;
                mouse3D.y = -(e.clientY / window.innerHeight) * 2 + 1;

                raycaster3D.setFromCamera(mouse3D, camera3D);
                const intersects = raycaster3D.intersectObjects(ringGroup3D.children, true);

                if (intersects.length > 0) {{
                    let obj = intersects[0].object;
                    while (obj.parent && !obj.userData.id && obj.parent !== ringGroup3D) {{
                        obj = obj.parent;
                    }}
                    if (obj.userData && obj.userData.id) {{
                        elevarEAtivarPasta3D(obj);
                    }}
                }}
            }});
        }}

        function elevarEAtivarPasta3D(folderObj) {{
            pastaSelecionadaElevada = folderObj;
            rotSpeed3D = 0;

            targetRotY = -folderObj.userData.angle + Math.PI / 2;

            document.getElementById('folderNameTitle').innerText = folderObj.userData.title;
            document.getElementById('folderDateBadge').innerText = "Data: 16/10/2026";
            document.getElementById('folderDetails').innerText = "Pasta fisicamente levantada no anel 3D de banco de dados.";
            document.getElementById('dbFolderPanel').classList.add('visible');
        }}

        function abrirBancoDeDados() {{
            document.getElementById('databaseOverlay').classList.add('visible');
            mudarModoInterfaceParaOculto(true);
            atualizarLog("Carregando Anel 3D de Banco de Dados...", "● Three.js DB");
            initThreeJSDB();
        }}

        function fecharBancoDeDados() {{
            document.getElementById('databaseOverlay').classList.remove('visible');
            mudarModoInterfaceParaOculto(false);
            fecharPainelPasta();
            atualizarLog("Retornado ao menu principal.", "● Sistema Ativo");
        }}

        function tratarBuscaDB(e) {{
            if (e.key === 'Enter') pesquisarPastaDB();
        }}

        function pesquisarPastaDB() {{
            const query = document.getElementById('dbSearchInput').value.trim();
            if (!query) return;

            let termo = query;
            let dataStr = "16/10/2026";

            const matchData = query.match(/(\\d{{1,2}}\\/\\d{{1,2}}\\/\\d{{4}})/);
            if (matchData) {{
                dataStr = matchData[1];
                termo = query.replace(matchData[1], '').trim();
            }}

            pastaPesquisadaAtiva = {{ term: termo, data: dataStr, rawQuery: query }};

            fecharPainelPasta();
            atualizarLog("Sincronizando Anel 3D para '" + query + "'...", "● Pesquisando...");

            const targetIndex = Math.abs(termo.length * 5) % numFolders3D;
            const pastaEncontrada = folder3DObjects[targetIndex];

            setTimeout(() => {{
                elevarEAtivarPasta3D(pastaEncontrada);
                document.getElementById('folderNameTitle').innerText = termo.toUpperCase() || "REGISTRO DE ARQUIVOS";
                document.getElementById('folderDateBadge').innerText = "Data da Pasta: " + dataStr;
                document.getElementById('folderDetails').innerText = "Pasta localizada e elevada no arquivo para a pesquisa: '" + query + "'.";
                atualizarLog("Pasta localizada e elevada no 3D!", "● Localizado");
            }}, 600);
        }}

        async function abrirConteudoPastaSelecionada() {{
            const query = pastaPesquisadaAtiva.rawQuery || "Consulta Generica";
            atualizarLog("Carregando dados da pasta: '" + query + "'...", "● Lendo arquivos...");

            document.getElementById('viewerTitle').innerText = "CONTEÚDO DE: " + query.toUpperCase();
            document.getElementById('viewerLogContent').innerHTML = '<p class="text-cyan-400 animate-pulse py-6 text-center">Abrindo arquivos e relatórios do Python backend...</p>';
            document.getElementById('folderViewerModal').classList.add('visible');

            try {{
                if (window.pywebview && window.pywebview.api) {{
                    let jsonRes = await pywebview.api.buscar_historico_pasta(pastaPesquisadaAtiva.term, pastaPesquisadaAtiva.data);
                    let dados = JSON.parse(jsonRes);
                    
                    renderizarLogsViewerModal(dados);
                }} else {{
                    setTimeout(() => {{
                        renderizarLogsViewerModal({{
                            status: "Sucesso",
                            data: pastaPesquisadaAtiva.data,
                            termo: pastaPesquisadaAtiva.term,
                            registros: [
                                {{ hora: "08:30:12", script: "rodar_planilhas.py", evento: "Início do processamento de tabelas diárias." }},
                                {{ hora: "08:32:45", script: "execucao_linhas.py", evento: "Remoção de 140 linhas duplicadas concluída." }},
                                {{ hora: "09:15:00", script: "script_atualizacao.py", evento: "Sincronização do banco de dados efetuada com êxito." }}
                            ]
                        }});
                    }}, 800);
                }}
            }} catch(err) {{
                document.getElementById('viewerLogContent').innerHTML = '<p class="text-rose-400">Erro ao carregar pasta: ' + err + '</p>';
            }}
        }}

        function renderizarLogsViewerModal(dados) {{
            const container = document.getElementById('viewerLogContent');
            container.innerHTML = '';

            if (!dados.registros || dados.registros.length === 0) {{
                container.innerHTML = '<p class="text-gray-400 text-center py-8">Nenhum histórico encontrado para esta data.</p>';
                return;
            }}

            dados.registros.forEach((reg, i) => {{
                const div = document.createElement('div');
                div.className = 'bg-slate-900/80 border border-cyan-800/60 p-3 rounded-xl flex flex-col gap-1';
                div.innerHTML = `
                    <div class="flex justify-between items-center text-[11px] border-b border-cyan-900/50 pb-1">
                        <span class="text-cyan-300 font-bold">● SCRIPT: ${{reg.script}}</span>
                        <span class="text-gray-400">${{reg.hora}}</span>
                    </div>
                    <p class="text-gray-200 text-xs mt-1 leading-normal">${{reg.evento}}</p>
                `;
                container.appendChild(div);
            }});
        }}

        function fecharViewerModal() {{
            document.getElementById('folderViewerModal').classList.remove('visible');
        }}

        function fecharPainelPasta() {{
            document.getElementById('dbFolderPanel').classList.remove('visible');
            pastaSelecionadaElevada = null;
            rotSpeed3D = baseRotSpeed3D;
        }}

        function mudarModoInterfaceParaOculto(ocultar) {{
            const stageMain = document.getElementById('stageMain');
            const modeSelector = document.querySelector('.mode-selector');
            const switchContainer = document.getElementById('switchContainer');

            if (ocultar) {{
                stageMain.style.opacity = '0';
                stageMain.style.pointerEvents = 'none';
                modeSelector.style.opacity = '0';
                modeSelector.style.pointerEvents = 'none';
                switchContainer.style.opacity = '0';
                switchContainer.style.pointerEvents = 'none';
            }} else {{
                stageMain.style.opacity = '1';
                stageMain.style.pointerEvents = 'auto';
                modeSelector.style.opacity = '1';
                modeSelector.style.pointerEvents = 'auto';
                switchContainer.style.opacity = '1';
                switchContainer.style.pointerEvents = 'auto';
            }}
        }}

        /* ==========================================
           LÓGICA DO CLASSIFICADOR 3D / FOCO / EXPANSÃO / INPUT
           ========================================== */
        let terminaisPilha = [];

        function trazerTerminalParaFrente(scriptId) {{
            const term = terminaisPilha.find(t => t.id === scriptId);
            if (term) {{
                term.isFlipped = false;
                terminaisPilha = terminaisPilha.filter(t => t.id !== scriptId);
                terminaisPilha.push(term);
                renderizarPilhaTerminais();
            }}
        }}

        function alternarExpansaoTerminal(scriptId, event) {{
            if (event) event.stopPropagation();
            const term = terminaisPilha.find(t => t.id === scriptId);
            if (term) {{
                term.isExpanded = !term.isExpanded;
                trazerTerminalParaFrente(scriptId);
            }}
        }}

        function enviarRespostaTerminal(scriptId, event) {{
            if (event) event.stopPropagation();
            const inputEl = document.getElementById(`termInput_${{scriptId}}`);
            if (!inputEl) return;
            const texto = inputEl.value.trim();
            if (!texto) return;

            adicionarTextoTerminalId(scriptId, `> ${{texto}}`);
            inputEl.value = '';

            if (window.pywebview && window.pywebview.api) {{
                pywebview.api.responder_script(scriptId, texto);
            }}
        }}

        function tratarKeyInputTerminal(event, scriptId) {{
            event.stopPropagation();
            if (event.key === 'Enter') {{
                enviarRespostaTerminal(scriptId, event);
            }}
        }}

        function criarOuAtualizarTerminal(scriptId, scriptName) {{
            let term = terminaisPilha.find(t => t.id === scriptId);

            if (!term) {{
                const terminalObj = {{
                    id: scriptId,
                    name: scriptName,
                    logs: [],
                    isFlipped: false,
                    isExpanded: false
                }};
                terminaisPilha.push(terminalObj);
            }} else {{
                term.isFlipped = false;
                terminaisPilha = terminaisPilha.filter(t => t.id !== scriptId);
                terminaisPilha.push(term);
            }}

            renderizarPilhaTerminais();
            document.getElementById('terminalContainer').classList.add('visible');
        }}

        function renderizarPilhaTerminais() {{
            const container = document.getElementById('terminalContainer');
            container.innerHTML = '';
            const total = terminaisPilha.length;

            terminaisPilha.forEach((term, index) => {{
                const card = document.createElement('div');
                card.className = 'terminal-card';
                if (term.isFlipped) card.classList.add('flipped-down');
                if (term.isExpanded) card.classList.add('expanded');

                const offsetFromTop = total - 1 - index;
                const translateY = offsetFromTop * -14;
                const translateZ = offsetFromTop * -25;
                const rotateX = offsetFromTop * 3;
                const opacity = Math.max(0.4, 1 - (offsetFromTop * 0.15));

                if (!term.isFlipped && !term.isExpanded) {{
                    card.style.transform = `translateY(${{translateY}}px) translateZ(${{translateZ}}px) rotateX(${{rotateX}}deg)`;
                    card.style.opacity = opacity;
                }}
                card.style.zIndex = index + 10;

                card.onclick = () => trazerTerminalParaFrente(term.id);

                card.innerHTML = `
                    <div class="terminal-header">
                        <div class="flex items-center gap-2">
                            <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                            <span class="text-[11px] font-bold text-purple-400 tracking-wide uppercase">${{term.name}}</span>
                        </div>
                        <div class="flex items-center gap-1">
                            <button onclick="alternarExpansaoTerminal('${{term.id}}', event)" class="text-[9px] text-cyan-300 hover:text-white px-1.5 py-0.5 rounded bg-cyan-900/30 hover:bg-cyan-800/50 border border-cyan-500/30 transition-all">
                                ${{term.isExpanded ? '⤓ Reduzir' : '⤢ Ampliar'}}
                            </button>
                            <button onclick="fecharAbaTerminal('${{term.id}}', event)" class="text-[10px] text-gray-400 hover:text-white px-2 py-0.5 rounded bg-white/5 hover:bg-white/10 transition-all">
                                ✕
                            </button>
                        </div>
                    </div>
                    <div class="terminal-body" id="termBody_${{term.id}}"></div>
                    <div class="terminal-input-container" onclick="event.stopPropagation()">
                        <input type="text" id="termInput_${{term.id}}" class="terminal-input" placeholder="Digite sua resposta e pressione Enter..." onkeydown="tratarKeyInputTerminal(event, '${{term.id}}')">
                        <button onclick="enviarRespostaTerminal('${{term.id}}', event)" class="px-2 py-0.5 bg-purple-600/40 hover:bg-purple-600 border border-purple-500/50 rounded text-[10px] text-purple-200 transition-all">Enviar</button>
                    </div>
                `;

                container.appendChild(card);

                const bodyEl = card.querySelector(`#termBody_${{term.id}}`);
                if (bodyEl) {{
                    bodyEl.innerHTML = term.logs.join('\\n');
                    bodyEl.scrollTop = bodyEl.scrollHeight;
                }}
            }});
        }}

        function adicionarTextoTerminalId(scriptId, texto) {{
            const term = terminaisPilha.find(t => t.id === scriptId);
            if (term) {{
                term.logs.push(texto);
                const bodyEl = document.getElementById(`termBody_${{scriptId}}`);
                if (bodyEl) {{
                    bodyEl.innerHTML = term.logs.join('\\n');
                    bodyEl.scrollTop = bodyEl.scrollHeight;
                }}
            }}
        }}

        function fecharAbaTerminal(scriptId, event) {{
            if (event) event.stopPropagation();
            terminaisPilha = terminaisPilha.filter(t => t.id !== scriptId);
            renderizarPilhaTerminais();
            if (terminaisPilha.length === 0) {{
                document.getElementById('terminalContainer').classList.remove('visible');
                document.getElementById('stageMain').classList.remove('shifted-bottom-left');
            }}
        }}

        function fecharTerminalEmbutido() {{
            document.getElementById('terminalContainer').classList.remove('visible');
            document.getElementById('stageMain').classList.remove('shifted-bottom-left');
        }}

        document.getElementById('terminalContainer').addEventListener('wheel', (e) => {{
            e.stopPropagation();
            if (terminaisPilha.length <= 1) return;

            if (e.deltaY > 0) {{
                for (let i = terminaisPilha.length - 1; i >= 0; i--) {{
                    if (!terminaisPilha[i].isFlipped) {{
                        terminaisPilha[i].isFlipped = true;
                        break;
                    }}
                }}
            }} else if (e.deltaY < 0) {{
                for (let i = 0; i < terminaisPilha.length; i++) {{
                    if (terminaisPilha[i].isFlipped) {{
                        terminaisPilha[i].isFlipped = false;
                        break;
                    }}
                }}
            }}

            renderizarPilhaTerminais();
        }});

        function mudarModo(modo) {{
            const btnHumano = document.getElementById('btnHumano');
            const btnIA = document.getElementById('btnIA');
            const aiScreen = document.getElementById('aiScreen');
            const switchContainer = document.getElementById('switchContainer');
            const stageMain = document.getElementById('stageMain');
            const statusConsole = document.getElementById('statusConsole');

            if (modo === 'ia') {{
                btnHumano.classList.remove('active');
                btnIA.classList.add('active');
                switchContainer.style.opacity = '0';
                switchContainer.style.pointerEvents = 'none';
                stageMain.style.opacity = '0';
                stageMain.style.pointerEvents = 'none';
                statusConsole.style.opacity = '0';
                statusConsole.style.pointerEvents = 'none';
                aiScreen.classList.add('active');

                atualizarLog("Modo IA (Sexta-Feira) Ativado.", "● Sexta-Feira Ativa");
            }} else {{
                btnIA.classList.remove('active');
                btnHumano.classList.add('active');
                aiScreen.classList.remove('active');

                switchContainer.style.opacity = '1';
                switchContainer.style.pointerEvents = 'auto';
                stageMain.style.opacity = '1';
                stageMain.style.pointerEvents = 'auto';
                statusConsole.style.opacity = '1';
                statusConsole.style.pointerEvents = 'auto';
                atualizarLog("Retornado ao Modo Humano.", "● Sistema Ativo");
            }}
        }}

        let isDarkMode = true;
        function toggleTheme() {{
            isDarkMode = !isDarkMode;
            if (isDarkMode) {{
                document.body.classList.remove('light-mode');
                atualizarLog("Modo Noturno / Neon Ativado", "● Tema Noturno");
            }} else {{
                document.body.classList.add('light-mode');
                atualizarLog("Modo Claro Ativado", "● Tema Claro");
            }}
            if (overviewChart) atualizarCoresGrafico();
        }}

        /* ESFERA HOLOGRÁFICA 3D DA TELA INICIAL */
        const canvas = document.getElementById('holoSphere');
        const ctx = canvas.getContext('2d');
        let angleX = 0, angleY = 0;
        const numPoints = 180, points = [], radius = 110;

        for (let i = 0; i < numPoints; i++) {{
            const phi = Math.acos(-1 + (2 * i) / numPoints);
            const theta = Math.sqrt(numPoints * Math.PI) * phi;
            points.push({{
                x: radius * Math.cos(theta) * Math.sin(phi),
                y: radius * Math.sin(theta) * Math.sin(phi),
                z: radius * Math.cos(phi)
            }});
        }}

        function renderHoloSphere() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            const cx = canvas.width / 2, cy = canvas.height / 2;
            angleX += 0.008; angleY += 0.012;

            const mainColor = isDarkMode ? 'rgba(168, 85, 247, ' : 'rgba(2, 132, 199, ';
            ctx.strokeStyle = mainColor + '0.22)';
            ctx.lineWidth = 0.8;

            const projected = points.map(p => {{
                let x = p.x;
                let y = p.y * Math.cos(angleX) - p.z * Math.sin(angleX);
                let z = p.y * Math.sin(angleX) + p.z * Math.cos(angleX);
                let x2 = x * Math.cos(angleY) + z * Math.sin(angleY);
                let y2 = y;
                let z2 = -x * Math.sin(angleY) + z * Math.cos(angleY);
                const fov = 350;
                const scale = fov / (fov + z2);
                return {{ x: cx + x2 * scale, y: cy + y2 * scale, z: z2 }};
            }});

            for (let i = 0; i < projected.length; i++) {{
                for (let j = i + 1; j < projected.length; j++) {{
                    const dx = projected[i].x - projected[j].x;
                    const dy = projected[i].y - projected[j].y;
                    if (Math.sqrt(dx * dx + dy * dy) < 32) {{
                        ctx.beginPath();
                        ctx.moveTo(projected[i].x, projected[i].y);
                        ctx.lineTo(projected[j].x, projected[j].y);
                        ctx.stroke();
                    }}
                }}
            }}

            const coreGradient = ctx.createRadialGradient(cx, cy, 2, cx, cy, 45);
            coreGradient.addColorStop(0, isDarkMode ? 'rgba(192, 132, 252, 1)' : 'rgba(2, 132, 199, 1)');
            coreGradient.addColorStop(0.5, isDarkMode ? 'rgba(168, 85, 247, 0.4)' : 'rgba(14, 165, 233, 0.4)');
            coreGradient.addColorStop(1, 'transparent');
            ctx.fillStyle = coreGradient;
            ctx.beginPath();
            ctx.arc(cx, cy, 45, 0, Math.PI * 2);
            ctx.fill();

            projected.forEach(p => {{
                const alpha = (p.z + radius) / (radius * 2);
                ctx.fillStyle = mainColor + `${{Math.max(0.2, alpha)}})`;
                ctx.beginPath();
                ctx.arc(p.x, p.y, 1.8, 0, Math.PI * 2);
                ctx.fill();
            }});

            requestAnimationFrame(renderHoloSphere);
        }}
        renderHoloSphere();

        /* ==========================================
           ATUALIZAÇÃO AUTOMÁTICA DA SEXTA-FEIRA AT
           ========================================== */
        async function executarAtualizacaoSextaFeiraAT() {{
            atualizarLog("Buscando atualizações na rede...", "● SEXTA-FEIRA AT");
            try {{
                if (window.pywebview && window.pywebview.api) {{
                    let res = await pywebview.api.verificar_e_atualizar_sistema();
                    atualizarLog(res, "● Status Atualização");
                }} else {{
                    atualizarLog("[SIMULAÇÃO] Verificação de atualização concluída.", "● Simulação");
                }}
            }} catch(err) {{
                atualizarLog("[ERRO ATUALIZAÇÃO] " + err, "● Erro");
            }}
        }}

        /* MENUS DA APLICAÇÃO (COM CARD PROCESSOS E CARD SEXTA-FEIRA AT) */
        const menus = {{
            main: [
                {{ id: 'sexta_feira_at', name: 'SEXTA-FEIRA AT', icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>' }},
                {{ id: 'meu_time', name: 'Meu time', icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15l-2 5l-4 -2l1.4 -5.6a8 8 0 1 1 9.2 0l1.4 5.6l-4 2z"></path>' }},
                {{ id: 'desenvolvimento', name: 'Desenvolvimento', icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"></path>' }},
                {{ id: 'processos', name: 'Processos', icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2"></path>' }},
                {{ id: 'estatisticas', name: 'Estatísticas', icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>' }},
                {{ id: 'planilha', name: 'Planilha', icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h18v18H3V3zm4 4h10v2H7V7zm0 4h10v2H7v-2zm0 4h7v2H7v-2z"></path>' }},
                {{ id: 'controle', name: 'Controle', icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"></path>' }},
                {{ id: 'lembrete', name: 'Lembrete', icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"></path>' }},
                {{ id: 'chat', name: 'Chat', icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>' }},
                {{ id: 'projeto_meia_noite', name: 'Projeto Meia Noite', icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"></path>' }},
                {{ id: 'api_card', name: 'API', icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>' }},
                {{ id: 'informakon', name: 'Informakon', icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>' }},
                {{ id: 'banco_de_dados', name: 'Banco de dados', icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4"></path>' }}
            ],
            planilha_sub: [
                {{ id: 'voltar', name: 'Voltar ao Menu', icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path>' }},
                {{ id: 'atualizacao', name: 'Atualização', icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>' }},
                {{ id: 'dividir', name: 'Dividir', icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7v8a2 2 0 002 2h6M8 7V5a2 2 0 012-2h4.586a1 1 0 01.707.293l4.414 4.414a1 1 0 01.293.707V15a2 2 0 01-2 2h-2M8 7H6a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2v-2"></path>' }},
                {{ id: 'excluir_linhas', name: 'Excluir Linhas', icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>' }},
                {{ id: 'criar_abas', name: 'Criar Abas', icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 13h6m-3-3v6m-9 1V7a2 2 0 012-2h6l2 2h6a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2z"></path>' }},
                {{ id: 'criar_aditivo', name: 'Criar Aditivo', icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v3m0 0v3m0-3h3m-3 0H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z"></path>' }},
                {{ id: 'excluir_abas', name: 'Excluir Abas', icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>' }}
            ]
        }};

        let currentMenuKey = 'main';
        let activeIndex = 0;
        let isTransitioning = false;
        let isDashboardOpen = false;
        const radiusCurve = 260; 
        const angleStep = 0.28; 

        function renderizarMenu() {{
            const container = document.getElementById('cardsList');
            container.innerHTML = '';
            
            const currentItems = menus[currentMenuKey];
            if (activeIndex >= currentItems.length) activeIndex = 0;

            currentItems.forEach((item, i) => {{
                const card = document.createElement('div');
                card.className = 'card-item';
                card.setAttribute('data-id', item.id);
                card.onclick = () => selecionarPorIndice(i);
                card.innerHTML = `
                    <div class="card-content">
                        <svg class="w-5 h-5 card-icon shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">${{item.icon}}</svg>
                        <span class="font-medium text-sm truncate">${{item.name}}</span>
                    </div>
                `;
                container.appendChild(card);
            }});

            atualizarPosicaoCards();
        }}

        function atualizarPosicaoCards() {{
            const cards = document.querySelectorAll('.card-item');
            cards.forEach((card, i) => {{
                const offset = i - activeIndex; 
                const angle = offset * angleStep;
                const x = (Math.cos(angle) - 1) * radiusCurve; 
                const y = Math.sin(angle) * radiusCurve;
                const opacity = Math.max(0.15, 1 - Math.abs(offset) * 0.35);
                
                card.style.transform = `translate(${{x}}px, ${{y - 22}}px) rotate(${{angle * 12}}deg)`;
                card.style.opacity = opacity;

                if (i === activeIndex) card.classList.add('active');
                else card.classList.remove('active');
            }});
        }}

        function selecionarPorIndice(index) {{
            if (isTransitioning || isDashboardOpen) return;
            const currentItems = menus[currentMenuKey];
            if (index < 0 || index >= currentItems.length) return;
            activeIndex = index;
            atualizarPosicaoCards();

            const scriptId = currentItems[activeIndex].id;
            const scriptName = currentItems[activeIndex].name;

            if (scriptId === 'sexta_feira_at') {{
                executarAtualizacaoSextaFeiraAT();
                return;
            }}

            if (scriptId === 'meu_time') {{ abrirFlamengo(); return; }}
            if (scriptId === 'desenvolvimento') {{ abrirDevRoom(); return; }}
            if (scriptId === 'estatisticas') {{ abrirDashboard(); return; }}
            if (scriptId === 'banco_de_dados') {{ abrirBancoDeDados(); return; }}

            if (currentMenuKey === 'main' && scriptId === 'planilha') {{
                isTransitioning = true;
                const cardsListEl = document.getElementById('cardsList');
                cardsListEl.classList.add('menu-transitioning');
                atualizarLog("Entrando no menu de Planilhas...", "● Submenu");

                if (terminaisPilha.length > 0) {{
                    document.getElementById('terminalContainer').classList.add('visible');
                    document.getElementById('stageMain').classList.add('shifted-bottom-left');
                }}

                setTimeout(() => {{
                    currentMenuKey = 'planilha_sub';
                    activeIndex = 1; 
                    renderizarMenu();
                    cardsListEl.classList.remove('menu-transitioning');
                    isTransitioning = false;
                }}, 500);
                return;
            }}

            if (currentMenuKey === 'planilha_sub' && scriptId === 'voltar') {{
                fecharTerminalEmbutido();
                isTransitioning = true;
                const cardsListEl = document.getElementById('cardsList');
                cardsListEl.classList.add('menu-transitioning');
                atualizarLog("Retornando ao menu principal...", "● Principal");

                setTimeout(() => {{
                    currentMenuKey = 'main';
                    activeIndex = 5;
                    renderizarMenu();
                    cardsListEl.classList.remove('menu-transitioning');
                    isTransitioning = false;
                }}, 500);
                return;
            }}

            if (currentMenuKey === 'planilha_sub' && scriptId !== 'voltar') {{
                document.getElementById('stageMain').classList.add('shifted-bottom-left');
                criarOuAtualizarTerminal(scriptId, scriptName);
            }}

            executarScriptPython(scriptId);
        }}

        function abrirDashboard() {{
            isDashboardOpen = true;
            document.getElementById('dashboardOverlay').classList.add('visible');
            atualizarLog("Dashboard de Estatísticas aberto.", "● Dashboard");
            inicializarGrafico();
        }}

        function fecharDashboard() {{
            isDashboardOpen = false;
            document.getElementById('dashboardOverlay').classList.remove('visible');
            atualizarLog("Retornado ao menu holográfico.", "● Sistema Ativo");
        }}

        let overviewChart = null;

        function inicializarGrafico() {{
            const ctxChart = document.getElementById('overviewChart').getContext('2d');
            if (overviewChart) overviewChart.destroy();

            overviewChart = new Chart(ctxChart, {{
                type: 'line',
                data: {{
                    labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out'],
                    datasets: [{{
                        data: [35, 42, 38, 65, 50, 75, 88, 70, 95, 110],
                        borderColor: '#ffffff',
                        borderWidth: 3,
                        fill: true,
                        backgroundColor: 'rgba(255, 255, 255, 0.15)',
                        tension: 0.4,
                        pointRadius: 0
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{ legend: {{ display: false }} }},
                    scales: {{
                        x: {{ display: false }},
                        y: {{ display: false }}
                    }}
                }}
            }});
        }}

        function atualizarCoresGrafico() {{
            if (!overviewChart) return;
            overviewChart.update();
        }}

        function atualizarLog(mensagem, statusTexto = "● Executando...") {{
            document.getElementById('statusIndicator').innerText = statusTexto;
            document.getElementById('logText').innerText = mensagem;
        }}

        async function executarScriptPython(scriptId) {{
            atualizarLog("A executar script no Python: [" + scriptId + "]...", "● A executar...");
            try {{
                if (window.pywebview && window.pywebview.api) {{
                    let resposta = await pywebview.api.executar_script(scriptId);
                    atualizarLog("[OK] " + resposta, "● Concluído");
                }} else {{
                    atualizarLog("[SIMULAÇÃO] Card '" + scriptId + "' acionado com sucesso.", "● Simulação");
                }}
            }} catch (err) {{
                atualizarLog("[ERRO] " + err, "● Erro");
            }}
        }}

        window.addEventListener('wheel', (e) => {{
            if (isDashboardOpen || isTransitioning) return;
            const currentItems = menus[currentMenuKey];
            if (e.deltaY > 0 && activeIndex < currentItems.length - 1) activeIndex++;
            else if (e.deltaY < 0 && activeIndex > 0) activeIndex--;
            atualizarPosicaoCards();
        }});

        renderizarMenu();
    </script>
</body>
</html>
"""

# ==========================================
# BACKEND PYTHON - MAPEAMENTO E ATUALIZADOR
# ==========================================
SCRIPT_MAP = {
    'atualizacao': 'script_atualizacao.py',
    'dividir': 'script_divisao.py',
    'excluir_linhas': 'execucao_linhas.py',
    'criar_abas': 'rodar_planilhas.py',
    'criar_aditivo': 'rodar_planilhas.py',
    'excluir_abas': 'execucao_abas.py',
    'processos': 'teste_qt.py'
}

class API:
    def __init__(self):
        self.processos_ativos = {}

    def verificar_e_atualizar_sistema(self):
        print(f"\n[SEXTA-FEIRA AT] Conectando ao servidor: {PASTA_SERVIDOR_ATUALIZACAO}")

        if not os.path.exists(PASTA_SERVIDOR_ATUALIZACAO):
            return f"Erro: Pasta do servidor não encontrada em '{PASTA_SERVIDOR_ATUALIZACAO}'"

        arquivo_servidor = os.path.join(PASTA_SERVIDOR_ATUALIZACAO, NOME_SCRIPT_ATUAL)
        arquivo_local = os.path.join(PASTA_ATUAL, NOME_SCRIPT_ATUAL)

        if os.path.exists(arquivo_servidor):
            mtime_servidor = os.path.getmtime(arquivo_servidor)
            mtime_local = os.path.getmtime(arquivo_local) if os.path.exists(arquivo_local) else 0

            if mtime_servidor > mtime_local:
                try:
                    shutil.copy2(arquivo_servidor, arquivo_local)
                    print("[SEXTA-FEIRA AT] Arquivo atualizado com sucesso! Reiniciando aplicação...")

                    def reiniciar_app():
                        subprocess.Popen([sys.executable, arquivo_local], cwd=PASTA_ATUAL)
                        if webview.windows:
                            webview.windows[0].destroy()

                    threading.Timer(1.0, reiniciar_app).start()
                    return "Atualização concluída! A reiniciar a Sexta-Feira..."

                except Exception as e:
                    return f"Erro ao copiar atualização: {str(e)}"
            else:
                return "Sua versão da Sexta-Feira já está totalmente atualizada!"
        else:
            return f"Nenhum arquivo '{NOME_SCRIPT_ATUAL}' encontrado na pasta de atualização do servidor."

    def executar_script(self, script_id):
        print(f"\n[PYTHON] Recebido comando para: {script_id}")

        if script_id in SCRIPT_MAP:
            nome_arquivo = SCRIPT_MAP[script_id]
            script_path = os.path.join(PASTA_ATUAL, nome_arquivo)

            if os.path.exists(script_path):
                def rodar_processo():
                    try:
                        env = os.environ.copy()
                        env["PYTHONIOENCODING"] = "utf-8"
                        env["PYTHONUNBUFFERED"] = "1"

                        proc = subprocess.Popen(
                            [sys.executable, "-u", script_path],
                            cwd=PASTA_ATUAL,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            text=False,
                            env=env,
                            bufsize=0
                        )

                        self.processos_ativos[script_id] = proc

                        buffer_acumulado = ""
                        while True:
                            char_bytes = proc.stdout.read(1)
                            if not char_bytes:
                                break
                            
                            try:
                                char = char_bytes.decode("utf-8", errors="replace")
                            except Exception:
                                char = str(char_bytes)

                            if char == "\n":
                                linha_limpa = buffer_acumulado.strip().replace("\\", "\\\\").replace("'", "\\'").replace('"', '\\"')
                                if linha_limpa and webview.windows:
                                    webview.windows[0].evaluate_js(f"adicionarTextoTerminalId('{script_id}', '{linha_limpa}')")
                                buffer_acumulado = ""
                            elif char == ":" or char == "?":
                                buffer_acumulado += char
                                linha_limpa = buffer_acumulado.strip().replace("\\", "\\\\").replace("'", "\\'").replace('"', '\\"')
                                if linha_limpa and webview.windows:
                                    webview.windows[0].evaluate_js(f"adicionarTextoTerminalId('{script_id}', '{linha_limpa}')")
                                buffer_acumulado = ""
                            else:
                                buffer_acumulado += char

                        if buffer_acumulado.strip() and webview.windows:
                            linha_limpa = buffer_acumulado.strip().replace("\\", "\\\\").replace("'", "\\'").replace('"', '\\"')
                            webview.windows[0].evaluate_js(f"adicionarTextoTerminalId('{script_id}', '{linha_limpa}')")

                        proc.stdout.close()
                        proc.wait()
                        self.processos_ativos.pop(script_id, None)

                        if webview.windows:
                            webview.windows[0].evaluate_js(f"adicionarTextoTerminalId('{script_id}', '\\n[PROCESSO CONCLUÍDO] {nome_arquivo} finalizado.')")
                    except Exception as e:
                        if webview.windows:
                            webview.windows[0].evaluate_js(f"adicionarTextoTerminalId('{script_id}', '[ERRO AO EXECUTAR]: {str(e)}')")

                threading.Thread(target=rodar_processo, daemon=True).start()
                return f"Script '{nome_arquivo}' iniciado na pasta de terminais!"
            else:
                return f"Erro: O arquivo '{nome_arquivo}' não foi encontrado na pasta."

        return f"Módulo '{script_id}' acionado com sucesso!"

    def responder_script(self, script_id, resposta):
        if script_id in self.processos_ativos:
            proc = self.processos_ativos[script_id]
            if proc and proc.stdin:
                try:
                    proc.stdin.write(f"{resposta}\n".encode("utf-8"))
                    proc.stdin.flush()
                    return "Enviado com sucesso!"
                except Exception as e:
                    return f"Erro ao enviar resposta: {str(e)}"
        return "Processo não encontrado ou já finalizado."

    def buscar_historico_pasta(self, termo, data_str):
        print(f"[PYTHON BACKEND] Pesquisando registros do termo '{termo}' na data '{data_str}'...")

        termo_clean = termo.lower().strip()
        registros = []

        is_planilha_geral = "planilha" in termo_clean

        scripts_relacionados = []
        if is_planilha_geral:
            scripts_relacionados = ["script_atualizacao.py", "script_divisao.py", "execucao_linhas.py", "rodar_planilhas.py", "execucao_abas.py"]
        elif "atualiza" in termo_clean:
            scripts_relacionados = ["script_atualizacao.py"]
        elif "divi" in termo_clean:
            scripts_relacionados = ["script_divisao.py"]
        elif "linha" in termo_clean:
            scripts_relacionados = ["execucao_linhas.py"]
        elif "aba" in termo_clean:
            scripts_relacionados = ["execucao_abas.py", "rodar_planilhas.py"]
        else:
            scripts_relacionados = ["script_geral.py"]

        for sc in scripts_relacionados:
            registros.append({
                "hora": "08:45:10",
                "script": sc,
                "evento": f"Execução automática iniciada para data {data_str}. Todos os parâmetros validados."
            })
            registros.append({
                "hora": "08:46:22",
                "script": sc,
                "evento": f"Operação concluída com sucesso em {data_str}. Arquivos gerados e salvos na pasta central."
            })

        resultado = {
            "status": "sucesso",
            "termo": termo,
            "data": data_str,
            "registros": registros
        }
        return json.dumps(resultado)

if __name__ == '__main__':
    html_file_path = os.path.join(PASTA_ATUAL, "index_temp.html")
    with open(html_file_path, "w", encoding="utf-8") as f:
        f.write(HTML_CONTENT)

    api = API()
    
    window = webview.create_window(
        title='Sexta-Feira AI & Holographic Interface', 
        url=html_file_path,
        js_api=api,
        width=1220,
        height=750,
        resizable=True
    )
    
    webview.start(http_server=True)