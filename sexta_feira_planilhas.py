import os
import glob
import asyncio
import subprocess
from datetime import datetime
import edge_tts
import pygame
import time

subprocess.run(["python", "automacao_subempreiteiros.py"])

# Caminho principal
PASTA_PROJETOS = r"C:\\Users\\Welber\\Desktop\\Projetos"

# Estado global
planilhas_vistas = set()
rodando_script = False
novas_enquanto_rodava = False

# === FUNÇÃO DE FALA ===
contador_fala = 0

async def falar(texto):
    """Gera e reproduz fala usando a voz Francisca (pt-BR)."""
    global contador_fala
    contador_fala += 1
    file_name = f"fala_{contador_fala}.mp3"

    communicate = edge_tts.Communicate(texto, voice="pt-BR-FranciscaNeural")
    await communicate.save(file_name)

    pygame.mixer.init()
    pygame.mixer.music.load(file_name)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        await asyncio.sleep(0.1)

    pygame.mixer.music.stop()
    pygame.mixer.quit()
    try:
        os.remove(file_name)
    except PermissionError:
        pass

def atualizar_status(planilha, progresso, mensagem):
    with open("status.txt", "w", encoding="utf-8") as f:
        f.write(f"{planilha}|{progresso}|{mensagem}")

def processar_planilhas():
    planilhas = ["SERV.X-M13.xlsb", "PMS_13.xlsb"]
    for p in planilhas:
        atualizar_status(p, 10, "Abrindo planilha...")
        time.sleep(2)
        atualizar_status(p, 20, "Executando macro...")
        time.sleep(2)
        atualizar_status(p, 40, "Atualizando fórmulas...")
        time.sleep(2)
        atualizar_status(p, 60, "Aplicando substituições...")
        time.sleep(2)
        atualizar_status(p, 90, "Finalizando...")
        time.sleep(2)
        atualizar_status(p, 100, "Concluído com sucesso.")
        time.sleep(1)

if __name__ == "__main__":
    processar_planilhas()


# === FUNÇÕES DE SUPORTE ===
def listar_planilhas():
    """Lista todas as planilhas válidas dentro da pasta Projetos e subpastas."""
    planilhas = []
    for ext in ("*.xlsx", "*.xlsb"):
        planilhas += glob.glob(os.path.join(PASTA_PROJETOS, "**", ext), recursive=True)
    return set(p for p in planilhas if not os.path.basename(p).startswith("~$"))


# === MONITORAMENTO INTELIGENTE ===
async def monitorar_planilhas(intervalo=3):
    """Monitora a pasta Projetos e gerencia a execução do rodar_planilhas.py."""
    global planilhas_vistas, rodando_script, novas_enquanto_rodava

    print(f"🟡 Monitorando planilhas em: {PASTA_PROJETOS}\n")
    planilhas_vistas = listar_planilhas()
    print(f"📁 {len(planilhas_vistas)} planilhas iniciais detectadas.\n")

    while True:
        planilhas_atuais = listar_planilhas()
        novas = planilhas_atuais - planilhas_vistas

        if novas:
            data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            print(f"\n📄 {data_hora} | Novas planilhas detectadas:")
            for arquivo in novas:
                print(f"   → {os.path.basename(arquivo)}")

            planilhas_vistas.update(novas)

            # Se o script NÃO está rodando
            if not rodando_script:
                await falar("Percebi que há novas planilhas na pasta projetos, quer que eu analise e trabalhe nelas?")
                resposta = input("\n💬 Deseja que eu trabalhe nelas agora? (sim/não): ").strip().lower()

                if resposta == "sim":
                    rodando_script = True
                    await falar("Perfeito, iniciando o trabalho nas planilhas agora.")
                    print("⚙️ Executando rodar_planilhas.py...\n")

                    # Executa o script de forma assíncrona
                    processo = await asyncio.create_subprocess_exec("python", "rodar_planilhas.py")
                    await processo.wait()

                    rodando_script = False
                    await falar("Processo concluído, Senhor Flávio.")

                    # Se houver novas planilhas enquanto rodava
                    if novas_enquanto_rodava:
                        novas_enquanto_rodava = False
                        await falar("Durante o processamento, novas planilhas foram adicionadas. Deseja que eu analise essas também?")
                        resp2 = input("\n💬 Deseja que eu trabalhe nelas também? (sim/não): ").strip().lower()
                        if resp2 == "sim":
                            rodando_script = True
                            await falar("Iniciando o trabalho nas novas planilhas.")
                            processo2 = await asyncio.create_subprocess_exec("python", "rodar_planilhas.py")
                            await processo2.wait()
                            rodando_script = False
                            await falar("As novas planilhas foram analisadas com sucesso, Senhor Flávio.")
                        else:
                            await falar("Tudo bem, deixarei as novas planilhas aguardando para análise posterior.")

                else:
                    await falar("Tudo bem, vou continuar observando a pasta projetos.")

            # Se o script já está rodando
            else:
                novas_enquanto_rodava = True
                await falar("Vejo que colocou novas planilhas, após o término das atuais irei analisá-las.")

        await asyncio.sleep(intervalo)

# === EXECUÇÃO ===
if __name__ == "__main__":
    try:
        asyncio.run(monitorar_planilhas())
    except KeyboardInterrupt:
        print("\n🟥 Monitoramento encerrado manualmente.")