import os
import sys
import xlwings as xw

SENHA_PLANILHA = "E1_CONTROL_2025#@!"

TAMANHO_GRUPO = {
    "10.10": 121,
    "10.30": 321
}

def tipo_modelo(sheet):
    try:
        vals = sheet.range((14, 1), (100, 1)).value
        if isinstance(vals, list):
            for val in vals:
                if val and ".1.30" in str(val):
                    return "10.30"
    except Exception as e:
        print(f"Erro ao identificar tipo de modelo na aba {sheet.name}: {e}")
    return "10.10"

def encontrar_ultimo_grupo_com_dados(sheet, model_type):
    step = TAMANHO_GRUPO[model_type]
    linhas_inicio_grupos = [14 + (g * step) for g in range(10)]
    ultimo_grupo = 0

    for idx, row in enumerate(linhas_inicio_grupos):
        val_b = sheet.range((row, 2)).value

        if val_b is not None:
            val_str = str(val_b).strip()
            if val_str != "" and val_str != "0":
                ultimo_grupo = idx + 1
            else:
                break
        else:
            break

    return ultimo_grupo

def atualizacao_formulas(sheet, total_row, groups_count, step):
    rows_for_sum = [14 + (i * step) for i in range(groups_count)]

    cols_to_update = {
        'K': True, 'L': True, 'M': True, 'N': True, 'O': True,
        'P': "0", 'Q': "0",
        'R': "", 'S': "", 'T': "", 'U': "",
        'X': True, 'Y': True, 'Z': True,
        'AA': True, 'AB': True,
        'AC': "0", 'AD': ""
    }

    for col_letter, condition in cols_to_update.items():
        cells_to_sum = [f"{col_letter}{r}" for r in rows_for_sum]
        formula_sum_part = "+".join(cells_to_sum) if cells_to_sum else "0"

        if condition is True:
            formula = f"={formula_sum_part}"
        elif condition == "0":
            formula = f'=IF($B$5="",0,{formula_sum_part})'
        else:
            formula = f'=IF($B$5="","",{formula_sum_part})'

        sheet.range(f"{col_letter}{total_row}").formula = formula

def main():
    print("\n" + "="*50)
    print("Automação Ultra Rápida - SERV")
    print("="*50)

    base_dir = r"C:\Projetos\Divisao"

    if not os.path.exists(base_dir):
        print(f"Erro: Diretório {base_dir} não encontrado.")
        return

    files = [f for f in os.listdir(base_dir) if f.endswith(".xlsb") and not f.startswith("~$")]

    if not files:
        print("Nenhum arquivo .xlsb encontrado.")
        return

    print("\nArquivos disponíveis:")
    for i, f in enumerate(files):
        print(f"[{i}] {f}")

    try:
        idx = int(input("\nEscolha o arquivo: "))
        path_principal = os.path.join(base_dir, files[idx])
    except (ValueError, IndexError):
        print("Seleção inválida.")
        return

    print("\n[INFO] Iniciando.... a Sexta-Feira está acessando o Excel, aguarde alguns segundos")
    
    app = xw.App(visible=False)
    app.screen_updating = False
    app.display_alerts = False
    app.enable_events = False
    app.calculation = 'manual'

    wb = None
    try:
        wb = app.books.open(path_principal)
        serv_sheets = [s for s in wb.sheets if s.name.upper().startswith("SERV")]

        if not serv_sheets:
            print("Nenhuma aba SERV localizada.")
            return

        for sheet in serv_sheets:
            print(f"\nProcessing: {sheet.name}")

            try:
                if SENHA_PLANILHA:
                    sheet.api.Unprotect(Password=SENHA_PLANILHA)
                else:
                    sheet.api.Unprotect()
            except Exception as e_unprotect:
                print(f"-> Aviso ao desproteger aba: {e_unprotect}")

            model_type = tipo_modelo(sheet)
            step = TAMANHO_GRUPO[model_type]
            
            ultimo_grupo = encontrar_ultimo_grupo_com_dados(sheet, model_type)
            print(f"-> Modelo: {model_type} | Último grupo com dados: Grupo {ultimo_grupo}")

            if ultimo_grupo == 0:
                grupo_inicio_delecao = 2
            elif ultimo_grupo == 1:
                grupo_inicio_delecao = 6
            else:
                grupo_inicio_delecao = ultimo_grupo + 2

            if grupo_inicio_delecao > 10:
                print(f"-> Nenhuma linha para remover nesta aba (preservando até o Grupo {grupo_inicio_delecao - 1}).")

                if SENHA_PLANILHA:
                    sheet.api.Protect(Password=SENHA_PLANILHA)
                else:
                    sheet.api.Protect()
                continue

            start_row_del = 14 + ((grupo_inicio_delecao - 1) * step)
            end_row_del = 14 + (10 * step) - 1

            print(f"-> Excluindo a partir do Grupo {grupo_inicio_delecao} (Linhas {start_row_del} até {end_row_del})")
            sheet.range(f"{start_row_del}:{end_row_del}").api.Delete(Shift=xw.constants.DeleteShiftDirection.xlShiftUp)

            last_row_after = sheet.used_range.last_cell.row
            col_b_after = sheet.range((14, 2), (last_row_after, 2)).value
            
            total_row_after = None
            if isinstance(col_b_after, list):
                for idx_r, val in enumerate(col_b_after):
                    if val and "TOTAL" in str(val).upper():
                        total_row_after = 14 + idx_r
                        break

            if total_row_after:

                grupos_mantidos = grupo_inicio_delecao - 1
                atualizacao_formulas(sheet, total_row_after, grupos_mantidos, step)

            print("-> Sexta-feira está limpando referências (+#REF!)...")
            sheet.used_range.api.Replace(
                What="+#REF!",
                Replacement="",
                LookAt=xw.constants.LookAt.xlPart,
                SearchOrder=xw.constants.SearchOrder.xlByRows,
                MatchCase=False
            )

            try:
                if SENHA_PLANILHA:
                    sheet.api.Protect(Password=SENHA_PLANILHA)
                else:
                    sheet.api.Protect()
            except Exception as e_protect:
                print(f"-> Aviso ao proteger aba novamente: {e_protect}")

        app.calculation = 'automatic'
        
        output_path = path_principal.replace(".xlsb", "_Processada.xlsb")
        wb.save(output_path)
        
        print("\n" + "="*50)
        print(f"CONCLUÍDO COM SUCESSO! Salvo em:\n{output_path}")
        print("="*50)

    except Exception as e:
        print(f"\n[ERRO]: {e}")
    finally:
        if wb:
            wb.close()
        if app:
            app.screen_updating = True
            app.display_alerts = True
            app.enable_events = True
            app.quit()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)