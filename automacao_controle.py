import os
import re
import time
import threading
from datetime import datetime

import xlwings as xw
import tkinter as tk
from tkinter import simpledialog, messagebox

# try win32 for MsgBoxKiller
try:
    import win32gui
    import win32con
except Exception:
    win32gui = None
    win32con = None

# === CONFIGURAÇÕES ===
PASTA_LOCAL = r"C:\Users\Welber\Desktop\Projetos\Controle"
PASTA_REDE = r"\\10.2.1.253\Engenharia\Setor_de_ORÇAMENTO E  CONTROLE\_ABAS\CONTROLE"
EXTENSOES = (".xls", ".xlsx", ".xlsm", ".xlsb")
EXCEL_VISIBLE = False  # app invisível para performance
LOG_FOLDER = os.path.join(PASTA_LOCAL, "Logs")
LOG_FILE = os.path.join(LOG_FOLDER, f"duplicidades_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")

# intervalo de busca dentro das abas da rede
SEARCH_COL_START = 3   # C
SEARCH_COL_END = 27    # AA

# intervalo onde estão cores/empresas (G..AA linhas 1..6)
COR_COL_START = 7   # G
COR_COL_END = 27    # AA
COR_ROW_START = 1
COR_ROW_END = 6

# ajustes de performance / tolerância
EXCEL_RETRY_WAIT = 0.25
SIMILARITY_THRESHOLD = 0.85  # não muito usado — buscamos direto + número fallback

# === UTILITÁRIOS DE LOG / TEXT ===
def ensure_log_folder():
    os.makedirs(LOG_FOLDER, exist_ok=True)

def log_message(msg):
    ensure_log_folder()
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().isoformat()} - {msg}\n")

def normalize_text(val):
    if val is None:
        return ""
    return " ".join(str(val).split()).strip().upper()

def concat_range_values(vals):
    if not vals:
        return ""
    parts = [normalize_text(v) for v in vals if v and str(v).strip() != ""]
    return " | ".join(parts)

def extrair_numero_parenteses(texto):
    if not texto:
        return None
    m = re.search(r"\((\d+)\)", str(texto))
    if m:
        return m.group(1)
    return None

def is_cell_color_empty(color_value):
    if color_value is None:
        return True
    try:
        if int(color_value) == 16777215:  # branco
            return True
    except Exception:
        pass
    return False

# === MsgBoxKiller (fecha dialog boxes do Excel em background) ===
def _close_dialog(hwnd, extra):
    try:
        cls = win32gui.GetClassName(hwnd)
        title = win32gui.GetWindowText(hwnd) or ""
        if cls == '#32770':  # dialog class common
            t = title.upper()
            keys = ["MICROSOFT EXCEL", "AVISO", "CONFIRMA", "ERRO", "ALERTA", "DUPLICIDADE", "LINKS", "ATUALIZAR", "SALVAR"]
            if any(k in t for k in keys) or ("EXCEL" in t and len(t) > 5):
                try:
                    win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                except Exception:
                    pass
    except Exception:
        pass

def msgbox_killer_loop(stop_event, interval=0.6):
    if win32gui is None:
        return
    while not stop_event.is_set():
        try:
            win32gui.EnumWindows(_close_dialog, None)
        except Exception:
            pass
        time.sleep(interval)

# === FUNÇÕES PRINCIPAIS DE BUSCA / PINTURA ===
def find_first_file_starting_with(folder, prefix3):
    """Encontra primeiro arquivo cujo nome (sem extensão) começa com prefix3 (case-insensitive)."""
    try:
        for fname in os.listdir(folder):
            if not fname.lower().endswith(EXTENSOES):
                continue
            name_no_ext = os.path.splitext(fname)[0].upper()
            if name_no_ext.startswith(prefix3.upper()):
                return os.path.join(folder, fname)
    except Exception as e:
        print("Erro listando pasta de rede:", e)
    return None

def montar_mapa_cores_do_wb(wb_rede):
    """
    Varre todas as abas do wb_rede no intervalo G1:AA6 e cria mapa {NOME_NORMALIZADO: cor_int}
    A célula à esquerda do nome contém a cor.
    """
    mapa = {}
    for sht in wb_rede.sheets:
        try:
            rng = sht.range((COR_ROW_START, COR_COL_START), (COR_ROW_END, COR_COL_END)).value
            if not rng:
                continue
            # rng é lista de linhas
            for r_idx, linha in enumerate(rng, start=COR_ROW_START):
                for c_rel, val in enumerate(linha, start=COR_COL_START):
                    if val is None or str(val).strip() == "":
                        continue
                    nome_norm = normalize_text(val)
                    try:
                        # pegar célula à esquerda
                        cell_left = sht.range((r_idx, c_rel - 1))
                        cor = cell_left.api.Interior.Color
                    except Exception:
                        cor = None
                    if nome_norm not in mapa:
                        mapa[nome_norm] = cor
        except Exception:
            time.sleep(0.01)
            continue
    return mapa

def encontrar_cor_por_nome(mapa_cores, nome_empresa):
    """Busca cor no mapa aceitando variações: 'MIRANDA' encontra 'MIRANDA CONSTRUÇÃO' etc."""
    if not nome_empresa:
        return None
    nome_norm = normalize_text(nome_empresa)
    # igualdade direta
    if nome_norm in mapa_cores:
        return mapa_cores[nome_norm]
    # busca por inclusão
    for key, cor in mapa_cores.items():
        if nome_norm in key or key in nome_norm:
            return cor
    return None

def sheet_search_line_by_key(sht, key_search):
    """
    Procura linha onde C:AA (3..27) corresponde ao key_search concatenado (igual).
    Retorna (row, joined_line) ou (None, None).
    """
    try:
        used = sht.used_range
        if used is None:
            return None, None
        last_row = used.last_cell.row
        if last_row < 1:
            return None, None
        # processa linha a linha, lendo o intervalo C:AA de cada linha (evita leitura de todo sheet quando enorme)
        for r in range(1, last_row + 1):
            vals = sht.range((r, SEARCH_COL_START), (r, SEARCH_COL_END)).value
            if not isinstance(vals, list):
                vals = [vals]
            joined = " | ".join([normalize_text(v) for v in vals if v and str(v).strip() != ""])
            if joined == key_search:
                return r, joined
        return None, None
    except Exception:
        return None, None

def sheet_search_line_by_number(sht, numero):
    """Procura linha por ocorrência do número dentro do joined C:AA da linha."""
    try:
        used = sht.used_range
        if used is None:
            return None, None
        last_row = used.last_cell.row
        if last_row < 1:
            return None, None
        for r in range(1, last_row + 1):
            vals = sht.range((r, SEARCH_COL_START), (r, SEARCH_COL_END)).value
            if not isinstance(vals, list):
                vals = [vals]
            # juntar tudo e procurar número textualmente
            joined_text = " ".join([str(v) for v in vals if v and str(v).strip() != ""])
            if numero in joined_text:
                return r, joined_text
        return None, None
    except Exception:
        return None, None

def find_in_workbook_by_key_or_number(wb_rede, key_search):
    """
    Procura o key_search dentro de todas as abas do wb_rede, no intervalo C:AA.
    Primeiro tenta encontrar linha cuja concat C:AA == key_search (exato).
    Se não achar, extrai número entre parênteses e procura numero dentro das linhas.
    Retorna (sheet_found, row_found) ou (None, None).
    """
    # busca por texto completo (igual)
    for sht in wb_rede.sheets:
        r, joined = sheet_search_line_by_key(sht, key_search)
        if r:
            return sht, r
    # fallback por número dentro de parenteses
    numero = extrair_numero_parenteses(key_search)
    if numero:
        for sht in wb_rede.sheets:
            r, joined = sheet_search_line_by_number(sht, numero)
            if r:
                return sht, r
    return None, None

def paint_cell_with_color(cell, cor_empresa, arquivo_rede_nome, aba_rede_nome, desc_text, origem_linha):
    """Pinta a célula se vazia; se já tiver cor diferente registra duplicidade (não sobrescreve)."""
    try:
        existing_color = None
        try:
            existing_color = cell.api.Interior.Color
        except Exception:
            existing_color = None
        if cor_empresa is None:
            # sem cor definida para a empresa: não pintamos, só retornamos posição encontrada
            return "no_color", None
        if is_cell_color_empty(existing_color):
            try:
                cell.api.Interior.Color = int(cor_empresa)
                return "painted", None
            except Exception as e:
                log_message(f"Erro ao pintar {arquivo_rede_nome} {aba_rede_nome} R{cell.row}C{cell.column}: {e}")
                return "error_paint", str(e)
        else:
            try:
                if int(existing_color) != int(cor_empresa):
                    msg = (f"Duplicidade: arquivo '{arquivo_rede_nome}', aba '{aba_rede_nome}', "
                           f"local R{cell.row}C{cell.column}, descrição '{desc_text}', origem linha {origem_linha}.")
                    print(msg)
                    log_message(msg)
                    return "duplicate", msg
                else:
                    return "already_same", None
            except Exception:
                log_message(f"Problema comparando cores em {arquivo_rede_nome} {aba_rede_nome} R{cell.row}C{cell.column}")
                return "compare_error", None
    except Exception as e:
        log_message(f"Erro paint_cell_with_color: {e}")
        return "error", str(e)

# ================= DETECÇÃO DE MEDIÇÕES EM UM WORKBOOK LOCAL =================
def detectar_medicoes_em_wb(wb_local):
    """
    Retorna lista de medições (inteiros) presentes no workbook local que tenham pelo menos 1 'X'
    Procura abas com 'SERV.' e '-M<number>' no nome.
    """
    medicoes = set()
    for sht in wb_local.sheets:
        try:
            nome = sht.name.upper()
            m = re.search(r"-M(\d+)$", nome)
            if "SERV." in nome and m:
                numero = int(m.group(1))
                try:
                    last = sht.used_range.last_cell.row
                    if last < 6:
                        continue
                    # leitura em bloco da coluna H
                    hvals = sht.range((6, 8), (last, 8)).value
                    if not isinstance(hvals, list):
                        hvals = [hvals]
                    if any(str(v).strip().upper() == "X" for v in hvals if v):
                        medicoes.add(numero)
                except Exception:
                    continue
        except Exception:
            continue
    return sorted(list(medicoes))

# ================= FLUXO PRINCIPAL =================
def main():
    root = tk.Tk()
    root.withdraw()

    # iniciar MsgBoxKiller
    stop_event = threading.Event()
    killer_thread = None
    if win32gui is not None:
        killer_thread = threading.Thread(target=msgbox_killer_loop, args=(stop_event,), daemon=True)
        killer_thread.start()

    # preparar app xlwings (single instance)
    app = xw.App(visible=EXCEL_VISIBLE, add_book=False)
    try:
        try:
            app.display_alerts = False
            app.api.DisplayAlerts = False
        except Exception:
            pass
        app.screen_updating = False

        files = [f for f in os.listdir(PASTA_LOCAL) if f.lower().endswith(EXTENSOES)]
        files.sort()
        if not files:
            messagebox.showwarning("Sem arquivos", f"Nenhum arquivo encontrado em {PASTA_LOCAL}")
            return

        total_painted = 0
        total_duplicates = 0

        # processa arquivo a arquivo, abrindo somente 1 local por vez
        for fname in files:
            fpath = os.path.join(PASTA_LOCAL, fname)
            print(f"\nAbrindo arquivo local: {fname}")
            try:
                wb_local = app.books.open(fpath)
            except Exception as e:
                print(f"Erro abrindo {fname}: {e}")
                continue

            try:
                # detectar medições com X nessa workbook local
                medicoes = detectar_medicoes_em_wb(wb_local)
                if not medicoes:
                    print("  Nenhuma medição com 'X' neste arquivo. Fechando e indo para o próximo.")
                    try:
                        wb_local.close()
                    except Exception:
                        pass
                    continue

                # processa enquanto houver medições nessa workbook local
                while medicoes:
                    # se só houver uma medição, processa direto; se mais, pergunta ao usuário
                    if len(medicoes) == 1:
                        medicao_num = medicoes[0]
                    else:
                        med_choices = ", ".join(str(m) for m in medicoes)
                        med_str = simpledialog.askstring("Escolher medição",
                                                         f"No arquivo {fname} foram detectadas medições com 'X': {med_choices}\nQual deseja processar agora?\n(ESC para pular este arquivo)")
                        if not med_str:
                            print(f"Usuário pulou o arquivo {fname}.")
                            break
                        if not med_str.strip().isdigit():
                            messagebox.showwarning("Entrada inválida", "Informe um número de medição válido.")
                            continue
                        medicao_num = int(med_str.strip())
                        if medicao_num not in medicoes:
                            messagebox.showwarning("Medição inválida", f"Medição {medicao_num} não está disponível neste arquivo.")
                            continue

                    print(f"  Processando medição M{medicao_num} em {fname}...")

                    # extrair prefixo 3 letras para localizar arquivo de rede
                    prefixo = os.path.splitext(fname)[0][:3].upper()
                    rede_file = find_first_file_starting_with(PASTA_REDE, prefixo)
                    wb_rede = None
                    if rede_file:
                        try:
                            wb_rede = app.books.open(rede_file)
                        except Exception as e:
                            print(f"    Erro abrindo arquivo de rede {rede_file}: {e}")
                            wb_rede = None
                    else:
                        print(f"    Nenhum arquivo de rede com prefixo '{prefixo}' encontrado. Esta medição será ignorada.")
                        # removemos e continuamos
                        medicoes = [m for m in medicoes if m != medicao_num]
                        continue

                    # montar mapa de cores (G:AA linhas 1..6) no wb_rede
                    mapa_cores = montar_mapa_cores_do_wb(wb_rede) if wb_rede else {}
                    # extrair nome da empresa do nome do arquivo local (heurística)
                    empresa_do_arquivo = None
                    base_no_ext = os.path.splitext(fname)[0]
                    parts = base_no_ext.split("_")
                    if len(parts) >= 3:
                        possible = "_".join(parts[2:])
                        possible = re.sub(r"_?Rev.*$", "", possible, flags=re.IGNORECASE)
                        empresa_do_arquivo = possible.replace("_", " ").strip()
                    elif len(parts) >= 2:
                        possible = "_".join(parts[1:])
                        possible = re.sub(r"_?Rev.*$", "", possible, flags=re.IGNORECASE)
                        empresa_do_arquivo = possible.replace("_", " ").strip()
                    cor_empresa = encontrar_cor_por_nome(mapa_cores, empresa_do_arquivo) if empresa_do_arquivo else None
                    if empresa_do_arquivo and cor_empresa is None:
                        print(f"    Não encontrou cor para '{empresa_do_arquivo}' no arquivo de rede (G:AA). Não pintará (a não ser que queira fallback).")

                    # localizar abas alvo no workbook local (SERV.*-M{medicao_num})
                    abas_alvo = [s for s in wb_local.sheets if "SERV." in s.name.upper() and f"-M{medicao_num}" in s.name.upper()]
                    if not abas_alvo:
                        print(f"    Nenhuma aba SERV.-M{medicao_num} encontrada no arquivo local.")
                        try:
                            wb_rede.close()
                        except Exception:
                            pass
                        medicoes = [m for m in medicoes if m != medicao_num]
                        continue

                    # para cada aba local alvo, percorre linhas com X
                    for sht_local in abas_alvo:
                        try:
                            last_local = sht_local.used_range.last_cell.row
                        except Exception:
                            continue
                        if last_local < 6:
                            continue
                        # leitura em bloco de colunas B:F e H para performance?
                        # Porém como precisamos por linha, lemos linha a linha minimalmente
                        for r in range(6, last_local + 1):
                            try:
                                h_val = sht_local.range((r, 8)).value
                            except Exception:
                                continue
                            if normalize_text(h_val) != "X":
                                continue
                            # montar descrição B:F
                            b_to_f = sht_local.range((r, 2), (r, 6)).value
                            if not isinstance(b_to_f, list):
                                b_to_f = [b_to_f]
                            if all((v is None or str(v).strip() == "") for v in b_to_f):
                                continue
                            desc_key = concat_range_values(b_to_f)
                            if not desc_key:
                                continue
                            # procura dentro do workbook da rede primeiro pelo texto completo, se não encontrar tenta número
                            if not wb_rede:
                                print("    Arquivo de rede não aberto; pulando pintura desta linha.")
                                continue
                            found_sheet, found_row = find_in_workbook_by_key_or_number(wb_rede, desc_key)
                            if not found_sheet:
                                print(f"    Nenhuma correspondência para key='{desc_key}' em {os.path.basename(rede_file)}")
                                continue
                            # dentro da folha encontrada, varrer C:AA da linha found_row para achar célula exata (ou achar coluna com conteudo)
                            try:
                                # lê a linha inteira C:AA
                                vals = found_sheet.range((found_row, SEARCH_COL_START), (found_row, SEARCH_COL_END)).value
                                if not isinstance(vals, list):
                                    vals = [vals]
                                # procurar a primeira célula não vazia que contenha parte do texto (preferência)
                                target_col = None
                                for idx, v in enumerate(vals, start=SEARCH_COL_START):
                                    if v and str(v).strip() != "":
                                        # checagem simples: se desc_key (normalizado) in v (normalizado)
                                        if normalize_text(v).find(normalize_text(desc_key)) != -1 or normalize_text(desc_key).find(normalize_text(v)) != -1:
                                            target_col = idx
                                            break
                                # se não encontrou célula precisa, usar a primeira não vazia da faixa
                                if target_col is None:
                                    for idx, v in enumerate(vals, start=SEARCH_COL_START):
                                        if v and str(v).strip() != "":
                                            target_col = idx
                                            break
                                if target_col is None:
                                    # nada na linha: usar coluna SEARCH_COL_START
                                    target_col = SEARCH_COL_START
                                # obter objeto cell
                                cell = found_sheet.range((found_row, target_col))
                                # pintar com checagem de duplicidade
                                result, info = paint_cell_with_color(cell, cor_empresa, os.path.basename(rede_file), found_sheet.name, desc_key, r)
                                if result == "painted":
                                    total_painted += 1
                                elif result == "duplicate":
                                    total_duplicates += 1
                                # se precisar, salvar após cada pintura (pode reduzir performance) — salvo ao final da aba/medição
                            except Exception as e:
                                log_message(f"Erro ao processar célula em {os.path.basename(rede_file)} {found_sheet.name} linha {found_row}: {e}")
                                continue
                    # após processar todas as abas alvo para essa medição, salvamos e fechamos o arquivo de rede para liberar
                    try:
                        wb_rede.save()
                    except Exception:
                        pass
                    try:
                        wb_rede.close()
                    except Exception:
                        pass

                    # remover medicao atual da lista e continuar (se existirem mais medicões, loop continua e pergunta novamente)
                    medicoes = [m for m in medicoes if m != medicao_num]
                    print(f"  Medição M{medicao_num} processada. Restam: {', '.join(str(m) for m in medicoes) if medicoes else 'nenhuma'}")

                # fim while medicoes (quando vazio, fecha workbook local e vai pro próximo)
                try:
                    wb_local.close()
                except Exception:
                    pass

            except Exception as e:
                log_message(f"Erro processando arquivo local {fname}: {e}")
                try:
                    wb_local.close()
                except Exception:
                    pass
                continue

        # fim for files
        resumo = f"Processo finalizado. Total pintadas: {total_painted}. Duplicidades: {total_duplicates}. Log em {LOG_FILE}"
        print(resumo)
        log_message(resumo)
        try:
            messagebox.showinfo("Concluído", resumo)
        except Exception:
            pass

    finally:
        # parar MsgBoxKiller
        if win32gui is not None:
            stop_event.set()
            if killer_thread:
                killer_thread.join(timeout=1.0)
        try:
            app.quit()
        except Exception:
            pass

if __name__ == "__main__":
    main()
