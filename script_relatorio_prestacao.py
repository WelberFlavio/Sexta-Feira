import os
import io
import threading
import webbrowser
from flask import Flask, render_template_string, request, send_file
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

# Inicialização correta da aplicação Flask
app = Flask(__name__)

# Mapeamento de categorias e códigos PCG
CATEGORIAS_MAP = {
    "Refeição / Alimentação": "03",
    "Pedágio": "02",
    "Hospedagem": "05",
    "Transporte / Uber / Táxi": "02",
    "Combustível": "06",
    "Estacionamento": "07",
    "Passagem Aérea": "01",
    "Diversos / Outros": "09"
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Estação 1 Corporativo - Prestação de Contas & Reembolsos</title>
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- FontAwesome Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <!-- Google Fonts Inter -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">

    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    fontFamily: {
                        sans: ['Inter', 'sans-serif'],
                    },
                    colors: {
                        brand: {
                            50: '#fef2f2',
                            100: '#ffe1e1',
                            500: '#c82e2b',
                            600: '#b52522',
                            700: '#961c1a',
                            accent: '#2d272c'
                        },
                        darkbg: '#1d1b1e',
                        darkcard: '#242125',
                        darkborder: '#3a353b'
                    }
                }
            }
        }
    </script>
    <style>
        body {
            font-family: 'Inter', sans-serif;
            background-color: #1d1b1e;
            color: #f8fafc;
        }
        ::-webkit-scrollbar { width: 8px; height: 8px; }
        ::-webkit-scrollbar-track { background: #242125; }
        ::-webkit-scrollbar-thumb { background: #3a353b; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #524b53; }

        @media print {
            body { background-color: #ffffff !important; color: #000000 !important; }
            .no-print { display: none !important; }
            .print-only { display: block !important; }
            .print-container { box-shadow: none !important; border: none !important; background: white !important; color: black !important; padding: 0 !important; margin: 0 !important; width: 100% !important; }
            table { border-collapse: collapse !important; width: 100% !important; }
            th, td { border: 1px solid #cbd5e1 !important; color: #000 !important; padding: 6px 10px !important; }
            .print-card { border: 1px solid #cbd5e1 !important; background: #f8fafc !important; color: #000 !important; }
        }
        .print-only { display: none; }
    </style>
</head>
<body class="min-h-screen flex flex-col antialiased selection:bg-brand-500 selection:text-white">

    <!-- Header Principal -->
    <header class="border-b border-darkborder bg-darkcard/90 backdrop-blur-md sticky top-0 z-50 no-print">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
            <div class="flex items-center space-x-3">
                <div class="bg-brand-500 px-3.5 py-2 rounded-xl shadow-lg shadow-brand-500/20 flex items-center justify-center font-black text-white text-xl tracking-wider">
                    ESTAÇÃO<span class="ml-1 bg-white text-brand-500 px-1.5 rounded text-lg">1</span>
                </div>
                <div>
                    <h1 class="font-bold text-lg text-slate-100 leading-tight">Estação 1 Corporativo <span class="text-xs bg-brand-500/20 text-brand-500 font-semibold px-2 py-0.5 rounded-full border border-brand-500/30 ml-2">Enterprise</span></h1>
                    <p class="text-xs text-slate-400">Sistema Integrado de Prestação de Contas</p>
                </div>
            </div>

            <div class="flex items-center space-x-2 sm:space-x-3">
                <button onclick="carregarExemploModelo()" class="text-xs sm:text-sm px-3 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium transition border border-slate-700 flex items-center gap-2" title="Carregar Dados de Exemplo">
                    <i class="fa-solid fa-wand-magic-sparkles text-amber-400"></i>
                    <span class="hidden sm:inline">Exemplo Preenchido</span>
                </button>

                <label class="cursor-pointer text-xs sm:text-sm px-3 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium transition border border-slate-700 flex items-center gap-2">
                    <i class="fa-solid fa-file-import text-indigo-400"></i>
                    <span class="hidden sm:inline">Importar JSON</span>
                    <input type="file" id="jsonInput" accept=".json" class="hidden" onchange="importarJSON(event)">
                </label>

                <button onclick="exportarJSON()" class="text-xs sm:text-sm px-3 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium transition border border-slate-700 flex items-center gap-2">
                    <i class="fa-solid fa-download text-emerald-400"></i>
                    <span class="hidden sm:inline">Salvar JSON</span>
                </button>

                <button onclick="exportarExcelPython()" class="text-xs sm:text-sm px-3 py-2 rounded-lg bg-emerald-700/80 hover:bg-emerald-600 text-white font-medium transition flex items-center gap-2 shadow-sm">
                    <i class="fa-solid fa-file-excel"></i>
                    <span class="hidden sm:inline">Exportar Excel (Python)</span>
                </button>

                <button onclick="imprimirRelatorio()" class="text-xs sm:text-sm px-3.5 py-2 rounded-lg bg-brand-500 hover:bg-brand-600 text-white font-medium transition flex items-center gap-2 shadow-lg shadow-brand-500/25">
                    <i class="fa-solid fa-print"></i>
                    <span>Imprimir / PDF</span>
                </button>
            </div>
        </div>
    </header>

    <!-- Toast -->
    <div id="toast" class="fixed bottom-5 right-5 z-50 transform translate-y-20 opacity-0 transition-all duration-300 ease-in-out no-print">
        <div class="flex items-center gap-3 bg-slate-800 border border-slate-700 text-slate-100 px-4 py-3 rounded-xl shadow-2xl">
            <i id="toastIcon" class="fa-solid fa-circle-check text-emerald-400 text-lg"></i>
            <span id="toastMessage" class="text-sm font-medium">Operação realizada com sucesso!</span>
        </div>
    </div>

    <!-- Conteúdo -->
    <main class="flex-grow max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 print-container">
        
        <div class="print-only mb-6 border-b pb-4">
            <div class="flex justify-between items-start">
                <div>
                    <h1 class="text-2xl font-bold text-slate-900">ESTAÇÃO 1 CORPORATIVO - RELATÓRIO DE PRESTAÇÃO DE CONTAS</h1>
                    <p class="text-sm text-slate-600">Comprovante de Despesas e Reembolso Corporativo</p>
                </div>
                <div class="text-right text-xs text-slate-500">
                    <p>Emissão: <span id="printDataEmissao">--/--/----</span></p>
                    <p>Ref: Reembolso Financeiro</p>
                </div>
            </div>
        </div>

        <!-- KPIs -->
        <section class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
            <div class="bg-darkcard border border-darkborder rounded-2xl p-5 shadow-lg relative overflow-hidden group hover:border-slate-600 transition print-card">
                <div class="flex justify-between items-start mb-3">
                    <div>
                        <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total de Despesas</p>
                        <h3 class="text-2xl font-bold text-slate-100 mt-1" id="kpiTotalDespesas">R$ 0,00</h3>
                    </div>
                    <div class="p-2.5 bg-rose-500/10 text-brand-500 border border-rose-500/20 rounded-xl">
                        <i class="fa-solid fa-receipt text-lg"></i>
                    </div>
                </div>
                <div class="flex items-center text-xs text-slate-400 gap-1.5">
                    <span class="font-medium text-slate-300" id="kpiQtdItens">0</span> itens lançados
                </div>
            </div>

            <div class="bg-darkcard border border-darkborder rounded-2xl p-5 shadow-lg relative overflow-hidden group hover:border-slate-600 transition print-card">
                <div class="flex justify-between items-start mb-3">
                    <div>
                        <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Adiantamento Recebido</p>
                        <h3 class="text-2xl font-bold text-slate-100 mt-1" id="kpiTotalAdiantamento">R$ 0,00</h3>
                    </div>
                    <div class="p-2.5 bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 rounded-xl">
                        <i class="fa-solid fa-hand-holding-dollar text-lg"></i>
                    </div>
                </div>
                <div class="flex items-center text-xs text-slate-400 gap-1.5">
                    <span class="font-medium text-slate-300" id="kpiQtdAdiantamentos">0</span> adiantamentos
                </div>
            </div>

            <div class="bg-darkcard border border-darkborder rounded-2xl p-5 shadow-lg relative overflow-hidden group hover:border-slate-600 transition print-card" id="cardSaldoContainer">
                <div class="flex justify-between items-start mb-3">
                    <div>
                        <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider" id="kpiSaldoLabel">Saldo Final</p>
                        <h3 class="text-2xl font-bold text-emerald-400 mt-1" id="kpiSaldoFinal">R$ 0,00</h3>
                    </div>
                    <div class="p-2.5 rounded-xl border" id="kpiSaldoIconBg">
                        <i class="fa-solid fa-scale-balanced text-lg" id="kpiSaldoIcon"></i>
                    </div>
                </div>
                <div>
                    <span id="badgeStatusSaldo" class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                        <i class="fa-solid fa-circle text-[8px] mr-1.5"></i> Reembolso a Pagar
                    </span>
                </div>
            </div>

            <div class="bg-darkcard border border-darkborder rounded-2xl p-5 shadow-lg relative overflow-hidden group hover:border-slate-600 transition print-card">
                <div class="flex justify-between items-start mb-3">
                    <div>
                        <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Maior Despesa</p>
                        <h3 class="text-2xl font-bold text-amber-400 mt-1" id="kpiMaiorDespesa">R$ 0,00</h3>
                    </div>
                    <div class="p-2.5 bg-amber-500/10 text-amber-400 border border-amber-500/20 rounded-xl">
                        <i class="fa-solid fa-crown text-lg"></i>
                    </div>
                </div>
                <p class="text-xs text-slate-400 truncate" id="kpiMaiorDespesaNome">Nenhum item lançado</p>
            </div>
        </section>

        <!-- Formulário -->
        <form id="formPrestacao" onsubmit="event.preventDefault();" class="space-y-8">
            <div class="bg-darkcard border border-darkborder rounded-2xl p-6 shadow-xl print-card">
                <div class="flex items-center gap-3 mb-6 pb-4 border-b border-darkborder">
                    <div class="w-8 h-8 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center font-bold text-sm">1</div>
                    <div>
                        <h2 class="text-lg font-bold text-slate-100">Dados do Colaborador & Conta para Crédito</h2>
                        <p class="text-xs text-slate-400">Informações cadastrais e dados bancários para acerto financeiro</p>
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
                    <div>
                        <label class="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">Nome do Colaborador *</label>
                        <input type="text" id="colaboradorNome" required placeholder="Ex: Thiago Machado" class="w-full bg-darkbg border border-darkborder rounded-xl px-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-brand-500 transition">
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">Setor / Departamento *</label>
                        <input type="text" id="colaboradorSetor" required placeholder="Ex: Figueiras" class="w-full bg-darkbg border border-darkborder rounded-xl px-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-brand-500 transition">
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">Data da Prestação *</label>
                        <input type="date" id="dataPrestacao" required class="w-full bg-darkbg border border-darkborder rounded-xl px-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-brand-500 transition">
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">Chave PIX</label>
                        <input type="text" id="chavePix" placeholder="CPF, Email, Telefone ou Aleatória" class="w-full bg-darkbg border border-darkborder rounded-xl px-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-brand-500 transition">
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">Banco</label>
                        <input type="text" id="bancoNome" placeholder="Ex: Banco do Brasil / Itaú" class="w-full bg-darkbg border border-darkborder rounded-xl px-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-brand-500 transition">
                    </div>
                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <label class="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">Agência</label>
                            <input type="text" id="bancoAgencia" placeholder="0000" class="w-full bg-darkbg border border-darkborder rounded-xl px-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-brand-500 transition">
                        </div>
                        <div>
                            <label class="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">Conta Corrente</label>
                            <input type="text" id="bancoConta" placeholder="00000-0" class="w-full bg-darkbg border border-darkborder rounded-xl px-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-brand-500 transition">
                        </div>
                    </div>
                </div>
            </div>

            <!-- Despesas -->
            <div class="bg-darkcard border border-darkborder rounded-2xl p-6 shadow-xl print-card">
                <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6 pb-4 border-b border-darkborder">
                    <div class="flex items-center gap-3">
                        <div class="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold text-sm">2</div>
                        <div>
                            <h2 class="text-lg font-bold text-slate-100">Lançamento de Despesas Realizadas</h2>
                            <p class="text-xs text-slate-400">Adicione os comprovantes e gastos detalhados</p>
                        </div>
                    </div>
                    <button type="button" onclick="adicionarLinhaDespesa()" class="no-print self-start sm:self-auto px-4 py-2 bg-brand-500 hover:bg-brand-600 text-white rounded-xl text-xs font-semibold flex items-center gap-2 transition shadow-md shadow-brand-500/20">
                        <i class="fa-solid fa-plus"></i> Adicionar Despesa
                    </button>
                </div>

                <div class="overflow-x-auto">
                    <table class="w-full text-left text-sm" id="tabelaDespesas">
                        <thead>
                            <tr class="border-b border-darkborder text-xs uppercase tracking-wider text-slate-400 bg-darkbg/40">
                                <th class="p-3 rounded-l-lg">Data</th>
                                <th class="p-3">Descrição / Histórico</th>
                                <th class="p-3">Tipo de Despesa</th>
                                <th class="p-3">Centro de Custo (CR)</th>
                                <th class="p-3 text-right">Valor (R$)</th>
                                <th class="p-3 text-center w-12 no-print">Ação</th>
                            </tr>
                        </thead>
                        <tbody id="tbodyDespesas" class="divide-y divide-darkborder/50"></tbody>
                    </table>
                </div>
            </div>

            <!-- Adiantamentos -->
            <div class="bg-darkcard border border-darkborder rounded-2xl p-6 shadow-xl print-card">
                <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6 pb-4 border-b border-darkborder">
                    <div class="flex items-center gap-3">
                        <div class="w-8 h-8 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-400 flex items-center justify-center font-bold text-sm">3</div>
                        <div>
                            <h2 class="text-lg font-bold text-slate-100">Adiantamentos Recebidos (Opcional)</h2>
                            <p class="text-xs text-slate-400">Valores adiantados previamente pela empresa para a viagem/projeto</p>
                        </div>
                    </div>
                    <button type="button" onclick="adicionarLinhaAdiantamento()" class="no-print self-start sm:self-auto px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-xl text-xs font-semibold flex items-center gap-2 transition">
                        <i class="fa-solid fa-plus"></i> Adicionar Adiantamento
                    </button>
                </div>

                <div class="overflow-x-auto">
                    <table class="w-full text-left text-sm" id="tabelaAdiantamentos">
                        <thead>
                            <tr class="border-b border-darkborder text-xs uppercase tracking-wider text-slate-400 bg-darkbg/40">
                                <th class="p-3 rounded-l-lg">Data do Crédito</th>
                                <th class="p-3">Descrição / Origem</th>
                                <th class="p-3 text-right">Valor Recebido (R$)</th>
                                <th class="p-3 text-center w-12 no-print">Ação</th>
                            </tr>
                        </thead>
                        <tbody id="tbodyAdiantamentos" class="divide-y divide-darkborder/50"></tbody>
                    </table>
                </div>
            </div>
        </form>

        <!-- Resumo & Assinaturas -->
        <section class="mt-8 grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div class="lg:col-span-2 bg-darkcard border border-darkborder rounded-2xl p-6 shadow-xl print-card">
                <div class="flex items-center justify-between mb-4 pb-3 border-b border-darkborder">
                    <h3 class="font-bold text-slate-100 flex items-center gap-2 text-base">
                        <i class="fa-solid fa-chart-pie text-brand-500"></i> Resumo Sintético por Categoria / Natureza
                    </h3>
                    <span class="text-xs text-slate-400">Cálculo Automático</span>
                </div>

                <div class="overflow-x-auto">
                    <table class="w-full text-sm text-left">
                        <thead>
                            <tr class="border-b border-darkborder text-xs uppercase tracking-wider text-slate-400">
                                <th class="py-2.5">Categoria</th>
                                <th class="py-2.5 text-center">Itens</th>
                                <th class="py-2.5 text-right">Total Acumulado</th>
                                <th class="py-2.5 text-right w-1/3">Proporção Visual</th>
                            </tr>
                        </thead>
                        <tbody id="tbodyResumoNatureza" class="divide-y divide-darkborder/40"></tbody>
                    </table>
                </div>
            </div>

            <div class="bg-darkcard border border-darkborder rounded-2xl p-6 shadow-xl flex flex-col justify-between print-card">
                <div>
                    <h3 class="font-bold text-slate-100 mb-4 pb-3 border-b border-darkborder flex items-center gap-2 text-base">
                        <i class="fa-solid fa-calculator text-indigo-400"></i> Balanço da Prestação
                    </h3>
                    <div class="space-y-3 text-sm">
                        <div class="flex justify-between text-slate-300">
                            <span>(+) Total Despesas Comprovadas:</span>
                            <span class="font-semibold text-slate-100" id="resumoTotalDespesas">R$ 0,00</span>
                        </div>
                        <div class="flex justify-between text-slate-300">
                            <span>(-) Total Adiantamentos Recebidos:</span>
                            <span class="font-semibold text-slate-100" id="resumoTotalAdiantamentos">R$ 0,00</span>
                        </div>
                        <div class="pt-3 border-t border-darkborder flex justify-between items-center">
                            <span class="font-bold text-slate-200">Resultado Acerto:</span>
                            <span class="text-lg font-bold text-brand-500" id="resumoResultadoFinal">R$ 0,00</span>
                        </div>
                    </div>
                </div>

                <div class="mt-8 pt-6 border-t border-slate-700/60 print-only">
                    <div class="grid grid-cols-2 gap-8 text-center text-xs text-slate-700">
                        <div>
                            <div class="border-b border-slate-400 mb-1 h-12"></div>
                            <p class="font-bold" id="printAssinaturaNome">Assinatura Colaborador</p>
                            <p class="text-[10px]">Declaro a veracidade dos comprovantes</p>
                        </div>
                        <div>
                            <div class="border-b border-slate-400 mb-1 h-12"></div>
                            <p class="font-bold">Aprovação Gestor / Financeiro</p>
                            <p class="text-[10px]">Conferido e Aprovado</p>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    </main>

    <footer class="border-t border-darkborder py-6 text-center text-xs text-slate-500 no-print">
        <p>Estação 1 Construções e Empreendimentos Ltda &copy; 2026 - Módulo Executivo de Prestação de Contas.</p>
    </footer>

    <script>
        const CATEGORIAS_DESPESA = [
            "Refeição / Alimentação", "Pedágio", "Hospedagem", 
            "Transporte / Uber / Táxi", "Combustível", "Estacionamento", 
            "Passagem Aérea", "Diversos / Outros"
        ];

        let despesas = [];
        let adiantamentos = [];

        document.addEventListener('DOMContentLoaded', () => {
            document.getElementById('dataPrestacao').valueAsDate = new Date();
            carregarExemploModelo();
        });

        function showToast(msg, isSuccess = true) {
            const toast = document.getElementById('toast');
            const toastMessage = document.getElementById('toastMessage');
            const toastIcon = document.getElementById('toastIcon');
            toastMessage.textContent = msg;
            toastIcon.className = isSuccess ? "fa-solid fa-circle-check text-emerald-400 text-lg" : "fa-solid fa-circle-exclamation text-amber-400 text-lg";
            toast.classList.remove('translate-y-20', 'opacity-0');
            setTimeout(() => { toast.classList.add('translate-y-20', 'opacity-0'); }, 3000);
        }

        function formatarMoeda(valor) {
            return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(valor || 0);
        }

        function adicionarLinhaDespesa(dados = {}) {
            const tbody = document.getElementById('tbodyDespesas');
            const tr = document.createElement('tr');
            tr.className = "hover:bg-slate-800/40 transition group";
            const dataHoje = dados.data || new Date().toISOString().split('T')[0];
            let optionsHtml = CATEGORIAS_DESPESA.map(cat => `<option value="${cat}" ${dados.tipo === cat ? 'selected' : ''}>${cat}</option>`).join('');

            tr.innerHTML = `
                <td class="p-2"><input type="date" value="${dataHoje}" class="input-despesa-data bg-darkbg border border-darkborder rounded-lg px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-brand-500 w-full"></td>
                <td class="p-2"><input type="text" value="${dados.descricao || ''}" placeholder="Ex: Almoço de Negócios" class="input-despesa-desc bg-darkbg border border-darkborder rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-brand-500 w-full"></td>
                <td class="p-2"><select onchange="atualizarCalculos()" class="select-despesa-tipo bg-darkbg border border-darkborder rounded-lg px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-brand-500 w-full">${optionsHtml}</select></td>
                <td class="p-2"><input type="text" value="${dados.cr || ''}" placeholder="Ex: CR-1020" class="input-despesa-cr bg-darkbg border border-darkborder rounded-lg px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-brand-500 w-full uppercase"></td>
                <td class="p-2"><input type="number" step="0.01" value="${dados.valor || ''}" placeholder="0,00" oninput="atualizarCalculos()" class="input-despesa-valor bg-darkbg border border-darkborder rounded-lg px-3 py-1.5 text-xs text-slate-200 text-right focus:outline-none focus:border-brand-500 w-full font-mono"></td>
                <td class="p-2 text-center no-print"><button type="button" onclick="removerLinha(this)" class="text-slate-500 hover:text-rose-400 p-1.5 rounded-lg transition"><i class="fa-solid fa-trash-can"></i></button></td>
            `;
            tbody.appendChild(tr);
            atualizarCalculos();
        }

        function adicionarLinhaAdiantamento(dados = {}) {
            const tbody = document.getElementById('tbodyAdiantamentos');
            const tr = document.createElement('tr');
            tr.className = "hover:bg-slate-800/40 transition group";
            const dataHoje = dados.data || new Date().toISOString().split('T')[0];

            tr.innerHTML = `
                <td class="p-2"><input type="date" value="${dataHoje}" class="input-adiantamento-data bg-darkbg border border-darkborder rounded-lg px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-brand-500 w-full"></td>
                <td class="p-2"><input type="text" value="${dados.descricao || ''}" placeholder="Ex: Adiantamento Pix Viagem" class="input-adiantamento-desc bg-darkbg border border-darkborder rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-brand-500 w-full"></td>
                <td class="p-2"><input type="number" step="0.01" value="${dados.valor || ''}" placeholder="0,00" oninput="atualizarCalculos()" class="input-adiantamento-valor bg-darkbg border border-darkborder rounded-lg px-3 py-1.5 text-xs text-slate-200 text-right focus:outline-none focus:border-brand-500 w-full font-mono"></td>
                <td class="p-2 text-center no-print"><button type="button" onclick="removerLinha(this)" class="text-slate-500 hover:text-rose-400 p-1.5 rounded-lg transition"><i class="fa-solid fa-trash-can"></i></button></td>
            `;
            tbody.appendChild(tr);
            atualizarCalculos();
        }

        function removerLinha(btn) {
            btn.closest('tr').remove();
            atualizarCalculos();
        }

        function atualizarCalculos() {
            let totalDespesas = 0, qtdDespesas = 0, maiorDespesaValor = 0, maiorDespesaNome = "Nenhum item";
            const resumoCategorias = {};
            CATEGORIAS_DESPESA.forEach(cat => { resumoCategorias[cat] = { total: 0, qtd: 0 }; });

            document.querySelectorAll('#tbodyDespesas tr').forEach(row => {
                const desc = row.querySelector('.input-despesa-desc')?.value || 'Sem Descrição';
                const tipo = row.querySelector('.select-despesa-tipo')?.value || CATEGORIAS_DESPESA[0];
                const valor = parseFloat(row.querySelector('.input-despesa-valor')?.value) || 0;
                if (valor > 0 || desc.trim() !== '') {
                    totalDespesas += valor;
                    qtdDespesas++;
                    if (valor > maiorDespesaValor) { maiorDespesaValor = valor; maiorDespesaNome = desc || tipo; }
                    if (resumoCategorias[tipo]) { resumoCategorias[tipo].total += valor; resumoCategorias[tipo].qtd++; }
                }
            });

            let totalAdiantamento = 0, qtdAdiantamentos = 0;
            document.querySelectorAll('#tbodyAdiantamentos tr').forEach(row => {
                const valor = parseFloat(row.querySelector('.input-adiantamento-valor')?.value) || 0;
                if (valor > 0) { totalAdiantamento += valor; qtdAdiantamentos++; }
            });

            const saldoFinal = totalDespesas - totalAdiantamento;
            document.getElementById('kpiTotalDespesas').textContent = formatarMoeda(totalDespesas);
            document.getElementById('kpiQtdItens').textContent = qtdDespesas;
            document.getElementById('kpiTotalAdiantamento').textContent = formatarMoeda(totalAdiantamento);
            document.getElementById('kpiQtdAdiantamentos').textContent = qtdAdiantamentos;
            document.getElementById('kpiMaiorDespesa').textContent = formatarMoeda(maiorDespesaValor);
            document.getElementById('kpiMaiorDespesaNome').textContent = maiorDespesaNome;

            const badge = document.getElementById('badgeStatusSaldo');
            const kpiSaldoFinal = document.getElementById('kpiSaldoFinal');
            const kpiSaldoIconBg = document.getElementById('kpiSaldoIconBg');
            const kpiSaldoIcon = document.getElementById('kpiSaldoIcon');

            if (saldoFinal >= 0) {
                kpiSaldoFinal.textContent = formatarMoeda(saldoFinal);
                kpiSaldoFinal.className = "text-2xl font-bold text-emerald-400 mt-1";
                badge.className = "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30";
                badge.innerHTML = `<i class="fa-solid fa-arrow-down-left text-[10px] mr-1.5"></i> Reembolso a Pagar ao Colaborador`;
                kpiSaldoIconBg.className = "p-2.5 bg-emerald-500/10 text-emerald-400 border-emerald-500/20 rounded-xl";
                kpiSaldoIcon.className = "fa-solid fa-hand-holding-dollar text-lg";
            } else {
                kpiSaldoFinal.textContent = formatarMoeda(Math.abs(saldoFinal));
                kpiSaldoFinal.className = "text-2xl font-bold text-rose-400 mt-1";
                badge.className = "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-500/20 text-rose-400 border border-rose-500/30";
                badge.innerHTML = `<i class="fa-solid fa-arrow-up-right text-[10px] mr-1.5"></i> Devolução a Pagar à Empresa`;
                kpiSaldoIconBg.className = "p-2.5 bg-rose-500/10 text-rose-400 border-rose-500/20 rounded-xl";
                kpiSaldoIcon.className = "fa-solid fa-building-columns text-lg";
            }

            document.getElementById('resumoTotalDespesas').textContent = formatarMoeda(totalDespesas);
            document.getElementById('resumoTotalAdiantamentos').textContent = formatarMoeda(totalAdiantamento);
            document.getElementById('resumoResultadoFinal').textContent = formatarMoeda(Math.abs(saldoFinal)) + (saldoFinal < 0 ? ' (Devolução)' : ' (Reembolso)');

            renderizarResumoNatureza(resumoCategorias, totalDespesas);
        }

        function renderizarResumoNatureza(resumo, totalGeral) {
            const tbody = document.getElementById('tbodyResumoNatureza');
            tbody.innerHTML = '';
            let temItens = false;

            for (const [categoria, dados] of Object.entries(resumo)) {
                if (dados.total > 0) {
                    temItens = true;
                    const percentual = totalGeral > 0 ? ((dados.total / totalGeral) * 100).toFixed(1) : 0;
                    const tr = document.createElement('tr');
                    tr.className = "hover:bg-slate-800/30 transition";
                    tr.innerHTML = `
                        <td class="py-2.5 text-slate-200 font-medium">${categoria}</td>
                        <td class="py-2.5 text-center text-slate-400">${dados.qtd}</td>
                        <td class="py-2.5 text-right font-mono text-slate-200">${formatarMoeda(dados.total)}</td>
                        <td class="py-2.5 text-right pl-4">
                            <div class="flex items-center justify-end gap-2">
                                <span class="text-xs text-slate-400 font-mono w-10 text-right">${percentual}%</span>
                                <div class="w-20 bg-slate-800 rounded-full h-2 overflow-hidden border border-slate-700">
                                    <div class="bg-gradient-to-r from-brand-500 to-indigo-500 h-2 rounded-full" style="width: ${percentual}%"></div>
                                </div>
                            </div>
                        </td>
                    `;
                    tbody.appendChild(tr);
                }
            }

            if (!temItens) {
                tbody.innerHTML = `<tr><td colspan="4" class="py-4 text-center text-slate-500 text-xs italic">Nenhuma despesa lançada no momento.</td></tr>`;
            }
        }

        function carregarExemploModelo() {
            document.getElementById('colaboradorNome').value = "THIAGO MACHADO";
            document.getElementById('colaboradorSetor').value = "FIGUEIRAS";
            document.getElementById('chavePix').value = "75999994816";
            document.getElementById('bancoNome').value = "Banco do Brasil";
            document.getElementById('bancoAgencia').value = "0123";
            document.getElementById('bancoConta').value = "45678-9";

            document.getElementById('tbodyDespesas').innerHTML = '';
            document.getElementById('tbodyAdiantamentos').innerHTML = '';

            const despesasExemplo = [
                { data: '2026-10-08', descricao: 'PEDAGIO', tipo: 'Pedágio', cr: 'CR-101', valor: 7.70 },
                { data: '2026-10-08', descricao: 'PEDAGIO', tipo: 'Pedágio', cr: 'CR-101', valor: 7.70 },
                { data: '2026-10-08', descricao: 'LANCHE', tipo: 'Refeição / Alimentação', cr: 'CR-101', valor: 38.00 },
                { data: '2026-10-08', descricao: 'PEGAGIO PRAIA DO FORTE', tipo: 'Pedágio', cr: 'CR-101', valor: 9.90 }
            ];

            despesasExemplo.forEach(d => adicionarLinhaDespesa(d));
            showToast("Dados de exemplo carregados!");
        }

        function obterPayloadCompleto() {
            const despesasLista = [];
            document.querySelectorAll('#tbodyDespesas tr').forEach(row => {
                const data = row.querySelector('.input-despesa-data')?.value;
                const descricao = row.querySelector('.input-despesa-desc')?.value;
                const tipo = row.querySelector('.select-despesa-tipo')?.value;
                const cr = row.querySelector('.input-despesa-cr')?.value;
                const valor = parseFloat(row.querySelector('.input-despesa-valor')?.value) || 0;
                if (descricao || valor > 0) despesasLista.push({ data, descricao, tipo, cr, valor });
            });

            const adiantamentosLista = [];
            document.querySelectorAll('#tbodyAdiantamentos tr').forEach(row => {
                const data = row.querySelector('.input-adiantamento-data')?.value;
                const descricao = row.querySelector('.input-adiantamento-desc')?.value;
                const valor = parseFloat(row.querySelector('.input-adiantamento-valor')?.value) || 0;
                if (descricao || valor > 0) adiantamentosLista.push({ data, descricao, valor });
            });

            return {
                nome: document.getElementById('colaboradorNome').value,
                setor: document.getElementById('colaboradorSetor').value,
                data: document.getElementById('dataPrestacao').value,
                pix: document.getElementById('chavePix').value,
                banco: document.getElementById('bancoNome').value,
                agencia: document.getElementById('bancoAgencia').value,
                cc: document.getElementById('bancoConta').value,
                despesas: despesasLista,
                adiantamentos: adiantamentosLista
            };
        }

        function exportarJSON() {
            const payload = obterPayloadCompleto();
            const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(payload, null, 2));
            const downloadAnchor = document.createElement('a');
            downloadAnchor.setAttribute("href", dataStr);
            downloadAnchor.setAttribute("download", `Reembolso_${(payload.nome || 'Estacao1').replace(/\\s+/g, '_')}.json`);
            document.body.appendChild(downloadAnchor);
            downloadAnchor.click();
            downloadAnchor.remove();
            showToast("Arquivo JSON baixado!");
        }

        function importarJSON(event) {
            const file = event.target.files[0];
            if (!file) return;
            const reader = new FileReader();
            reader.onload = function(e) {
                try {
                    const dados = JSON.parse(e.target.result);
                    document.getElementById('colaboradorNome').value = dados.nome || '';
                    document.getElementById('colaboradorSetor').value = dados.setor || '';
                    document.getElementById('dataPrestacao').value = dados.data || '';
                    document.getElementById('chavePix').value = dados.pix || '';
                    document.getElementById('bancoNome').value = dados.banco || '';
                    document.getElementById('bancoAgencia').value = dados.agencia || '';
                    document.getElementById('bancoConta').value = dados.cc || '';

                    document.getElementById('tbodyDespesas').innerHTML = '';
                    document.getElementById('tbodyAdiantamentos').innerHTML = '';

                    if (Array.isArray(dados.despesas) && dados.despesas.length > 0) {
                        dados.despesas.forEach(d => adicionarLinhaDespesa(d));
                    } else { adicionarLinhaDespesa(); }

                    if (Array.isArray(dados.adiantamentos) && dados.adiantamentos.length > 0) {
                        dados.adiantamentos.forEach(a => adicionarLinhaAdiantamento(a));
                    }
                    showToast("Dados importados!");
                } catch (err) { alert("Erro ao importar JSON."); }
            };
            reader.readAsText(file);
        }

        async function exportarExcelPython() {
            const payload = obterPayloadCompleto();
            try {
                const response = await fetch('/export-excel', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                if (!response.ok) throw new Error('Erro ao gerar Excel.');

                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `Prestacao_Contas_${(payload.nome || 'Estacao1').replace(/\\s+/g, '_')}.xlsx`;
                document.body.appendChild(a);
                a.click();
                a.remove();
                window.URL.revokeObjectURL(url);
                showToast("Excel gerado com sucesso!");
            } catch (err) {
                alert('Erro ao exportar Excel: ' + err.message);
            }
        }

        function imprimirRelatorio() {
            document.getElementById('printAssinaturaNome').textContent = `Assinatura: ${document.getElementById('colaboradorNome').value || 'Colaborador'}`;
            document.getElementById('printDataEmissao').textContent = new Date().toLocaleDateString('pt-BR');
            window.print();
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/export-excel', methods=['POST'])
def export_excel():
    data = request.get_json() or {}
    nome = data.get('nome', '')
    setor = data.get('setor', '')
    data_relatorio = data.get('data', '')
    cc = data.get('cc', '')
    agencia = data.get('agencia', '')
    banco = data.get('banco', '')
    pix = data.get('pix', '')
    
    despesas = data.get('despesas', [])
    adiantamentos = data.get('adiantamentos', [])

    wb = Workbook()
    ws = wb.active
    ws.title = "Prestação de Contas"
    ws.views.sheetView[0].showGridLines = True

    RED_HEADER = "C82E2B"
    DARK_BG = "1D1B1E"
    LIGHT_GRAY = "F4F4F5"
    BORDER_COLOR = "D1D5DB"

    font_title = Font(name="Calibri", size=14, bold=True, color="FFFFFF")
    font_header_sub = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
    font_bold = Font(name="Calibri", size=11, bold=True)
    font_regular = Font(name="Calibri", size=11)

    fill_red = PatternFill(start_color=RED_HEADER, end_color=RED_HEADER, fill_type="solid")
    fill_dark = PatternFill(start_color=DARK_BG, end_color=DARK_BG, fill_type="solid")
    fill_light = PatternFill(start_color=LIGHT_GRAY, end_color=LIGHT_GRAY, fill_type="solid")

    thin_side = Side(border_style="thin", color=BORDER_COLOR)
    border_all = Border(left=thin_side, right=thin_side, top=thin_side, bottom=thin_side)

    col_widths = {'A': 32, 'B': 18, 'C': 18, 'D': 25, 'E': 16, 'F': 16}
    for col, width in col_widths.items():
        ws.column_dimensions[col].width = width

    ws.merge_cells('A1:F1')
    cell_title = ws['A1']
    cell_title.value = "ESTAÇÃO 1 CORPORATIVO - RELATÓRIO DE PRESTAÇÃO DE CONTAS"
    cell_title.font = font_title
    cell_title.fill = fill_dark
    cell_title.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 32

    meta_labels = [
        ("A2", "Nome do Colaborador:", "B2", nome),
        ("C2", "Setor/Centro:", "D2", setor),
        ("E2", "Data:", "F2", data_relatorio),
        ("A3", "Banco:", "B3", banco),
        ("C3", "Agência/CC:", "D3", f"{agencia} / {cc}" if agencia or cc else ""),
        ("E3", "Chave PIX:", "F3", pix),
    ]

    for lbl_cell, lbl, val_cell, val in meta_labels:
        ws[lbl_cell] = lbl
        ws[lbl_cell].font = font_bold
        ws[val_cell] = val
        ws[val_cell].font = font_regular
        ws[lbl_cell].border = border_all
        ws[val_cell].border = border_all

    ws.cell(row=5, column=1, value="HISTÓRICO DA DESPESA")
    ws.cell(row=5, column=4, value="NATUREZA / TIPO")
    ws.cell(row=5, column=5, value="CÓDIGO")
    ws.cell(row=5, column=6, value="VALOR (R$)")

    for col_idx in [1, 2, 3, 4, 5, 6]:
        c = ws.cell(row=5, column=col_idx)
        c.fill = fill_red
        c.font = font_header_sub
        c.alignment = Alignment(horizontal="center", vertical="center")
        c.border = border_all
    
    ws.merge_cells('A5:C5')
    ws.row_dimensions[5].height = 22

    current_row = 6
    if not despesas:
        ws.cell(row=current_row, column=1, value="Nenhuma despesa lançada").font = font_regular
        ws.merge_cells(start_row=current_row, start_column=1, end_row=current_row, end_column=6)
        current_row += 1
    else:
        for idx, item in enumerate(despesas):
            ws.cell(row=current_row, column=1, value=item.get('descricao', '')).font = font_regular
            ws.merge_cells(start_row=current_row, start_column=1, end_row=current_row, end_column=3)
            
            tipo_nome = item.get('tipo', 'Diversos / Outros')
            cat_code = CATEGORIAS_MAP.get(tipo_nome, '09')
            
            ws.cell(row=current_row, column=4, value=tipo_nome).font = font_regular
            ws.cell(row=current_row, column=5, value=cat_code).alignment = Alignment(horizontal="center")
            
            val_cell = ws.cell(row=current_row, column=6, value=float(item.get('valor', 0)))
            val_cell.number_format = 'R$ #,##0.00'
            val_cell.font = font_regular

            for c in range(1, 7):
                ws.cell(row=current_row, column=c).border = border_all
                if idx % 2 == 1:
                    ws.cell(row=current_row, column=c).fill = fill_light
            current_row += 1

    total_desp_row = current_row
    ws.merge_cells(start_row=total_desp_row, start_column=1, end_row=total_desp_row, end_column=5)
    lbl_tot = ws.cell(row=total_desp_row, column=1, value="TOTAL DAS DESPESAS")
    lbl_tot.font = font_bold
    lbl_tot.alignment = Alignment(horizontal="right")
    
    val_tot_desp = ws.cell(row=total_desp_row, column=6, value=f"=SUM(F6:F{total_desp_row-1})")
    val_tot_desp.font = font_bold
    val_tot_desp.number_format = 'R$ #,##0.00'
    
    for c in range(1, 7):
        ws.cell(row=total_desp_row, column=c).border = border_all
        ws.cell(row=total_desp_row, column=c).fill = fill_light

    current_row += 2

    ws.merge_cells(start_row=current_row, start_column=1, end_row=current_row, end_column=3)
    ws.cell(row=current_row, column=1, value="DESCRIÇÃO DOS ADIANTAMENTOS").fill = fill_dark
    ws.cell(row=current_row, column=1).font = font_header_sub
    
    ws.cell(row=current_row, column=4, value="DATA").fill = fill_dark
    ws.cell(row=current_row, column=4).font = font_header_sub
    
    ws.merge_cells(start_row=current_row, start_column=5, end_row=current_row, end_column=6)
    ws.cell(row=current_row, column=5, value="VALOR RECEBIDO").fill = fill_dark
    ws.cell(row=current_row, column=5).font = font_header_sub

    for c in range(1, 7):
        ws.cell(row=current_row, column=c).alignment = Alignment(horizontal="center")
        ws.cell(row=current_row, column=c).border = border_all
    
    start_ad_row = current_row + 1
    current_row += 1

    if not adiantamentos:
        ws.cell(row=current_row, column=1, value="Nenhum adiantamento").font = font_regular
        ws.merge_cells(start_row=current_row, start_column=1, end_row=current_row, end_column=6)
        current_row += 1
    else:
        for item in adiantamentos:
            ws.cell(row=current_row, column=1, value=item.get('descricao', '')).font = font_regular
            ws.merge_cells(start_row=current_row, start_column=1, end_row=current_row, end_column=3)
            ws.cell(row=current_row, column=4, value=item.get('data', '')).alignment = Alignment(horizontal="center")
            
            ws.merge_cells(start_row=current_row, start_column=5, end_row=current_row, end_column=6)
            v_cell = ws.cell(row=current_row, column=5, value=float(item.get('valor', 0)))
            v_cell.number_format = 'R$ #,##0.00'
            v_cell.font = font_regular
            
            for c in range(1, 7):
                ws.cell(row=current_row, column=c).border = border_all
            current_row += 1

    end_ad_row = current_row - 1
    total_ad_row = current_row

    ws.merge_cells(start_row=total_ad_row, start_column=1, end_row=total_ad_row, end_column=4)
    lbl_ad = ws.cell(row=total_ad_row, column=1, value="TOTAL DE ADIANTAMENTOS RECEBIDOS")
    lbl_ad.font = font_bold
    lbl_ad.alignment = Alignment(horizontal="right")

    ws.merge_cells(start_row=total_ad_row, start_column=5, end_row=total_ad_row, end_column=6)
    val_tot_ad = ws.cell(row=total_ad_row, column=5, value=f"=SUM(E{start_ad_row}:E{end_ad_row})" if adiantamentos else 0)
    val_tot_ad.font = font_bold
    val_tot_ad.number_format = 'R$ #,##0.00'

    for c in range(1, 7):
        ws.cell(row=total_ad_row, column=c).border = border_all
        ws.cell(row=total_ad_row, column=c).fill = fill_light

    current_row += 2

    ws.merge_cells(start_row=current_row, start_column=1, end_row=current_row, end_column=6)
    sec_title = ws.cell(row=current_row, column=1, value="RESUMO BALANÇO FINANCEIRO")
    sec_title.fill = fill_dark
    sec_title.font = font_header_sub
    sec_title.alignment = Alignment(horizontal="center")
    current_row += 1

    summary_rows = [
        ("Total de Despesas", f"=F{total_desp_row}"),
        ("(-) Adiantamentos Recebidos", f"=E{total_ad_row}"),
        ("SALDO FINAL (A Reembolsar / A Devolver)", f"=F{current_row}-F{current_row+1}")
    ]

    for label, formula in summary_rows:
        ws.merge_cells(start_row=current_row, start_column=1, end_row=current_row, end_column=4)
        lbl_c = ws.cell(row=current_row, column=1, value=label)
        lbl_c.font = font_bold
        
        ws.merge_cells(start_row=current_row, start_column=5, end_row=current_row, end_column=6)
        val_c = ws.cell(row=current_row, column=5, value=formula)
        val_c.font = font_bold
        val_c.number_format = 'R$ #,##0.00'
        
        for c in range(1, 7):
            ws.cell(row=current_row, column=c).border = border_all
            if "SALDO FINAL" in label:
                ws.cell(row=current_row, column=c).fill = fill_light
        current_row += 1

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    filename = f"Prestacao_Contas_{nome.replace(' ', '_') or 'Estacao1'}.xlsx"
    return send_file(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=filename
    )

if __name__ == '__main__':
    port = 5000
    
    # Abre o navegador automaticamente após 1 segundo em segundo plano
    def abrir_navegador():
        webbrowser.open(f'http://127.0.0.1:{port}')

    threading.Timer(1.0, abrir_navegador).start()

    # Roda o servidor Flask integrado
    app.run(host='127.0.0.1', port=port, debug=False)