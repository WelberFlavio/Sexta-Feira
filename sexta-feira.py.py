import os
import asyncio
import edge_tts  # type: ignore
from playsound import playsound  # type: ignore
from sexta_feira_planilhas import monitorar_planilhas
import subprocess

# === Pasta temporária para salvar os áudios ===
pasta_temp = "tts_temp"
os.makedirs(pasta_temp, exist_ok=True)

# === Função assíncrona para gerar e tocar o áudio ===
async def falar(frase, nome_arquivo="fala_temp.mp3"):
    """Gera e toca áudio usando a voz Francisca."""
    arquivo_audio = os.path.join(pasta_temp, nome_arquivo)
    communicate = edge_tts.Communicate(frase, voice="pt-BR-FranciscaNeural")
    await communicate.save(arquivo_audio)
    playsound(arquivo_audio)

# === Função para gerar respostas automáticas ===
def analisar_resposta(pergunta_id, resposta):
    resposta = resposta.lower().strip()
    
    # Pergunta 2 - viagem
    if pergunta_id == 2:
        if any(p in resposta for p in ["boa", "de boa", "ótima", "tranquila", "tranquilo", "bem"]):
            return "Que bom que deu tudo certo!"
        elif any(p in resposta for p in ["ruim", "trânsito", "demorada", "péssima"]):
            return "Poxa, que chato... espero que o resto do dia melhore!"
        else:
            return "Entendi. Vamos em frente!"
    
    # Pergunta 4 - analisar e-mails
    elif pergunta_id == 4:
        if "sim" in resposta:
            return "Perfeito, vou analisar agora mesmo!"
        elif "não" in resposta:
            return "Tudo bem, deixo para depois então."
        else:
            return "Entendi. Posso verificar mais tarde se quiser."
    
    # Caso genérico
    return "Interessante, obrigada por compartilhar!"

# === Fluxo principal da assistente ===
async def main():
    frases = [
        "Olá Flávio, Bom dia! Vamos pra mais um dia de trabalho!",
        "Como foi a viagem de sua casa até o trabalho?",
        "Você tem algumas modificações no seu projeto, quer que eu analise e já trabalhe nas soluções?",
        "Posso te ajudar nisso.",
        "Analisando....",
        "Pronto, análise concluída, estou pronta pra trabalhar!"
    ]
    
    for i, frase in enumerate(frases, 1):
        await falar(frase, f"fala_{i}.mp3")

        # Somente faz perguntas relevantes
        if i in [2, 4]:
            resposta = input("\nSua resposta: ")
            resposta_assistente = analisar_resposta(i, resposta)
            await falar(resposta_assistente, f"resposta_{i}.mp3")
            print(f"Sexta-feira: {resposta_assistente}\n")
        else:
            await asyncio.sleep(0.5)

    # --- Após a última fala, inicia o monitoramento das planilhas ---
    await falar("Iniciando o monitoramento de planilhas agora, senhor Flávio.")
    print("🟡 Iniciando o monitoramento de planilhas...\n")

    # Inicia o monitoramento de forma assíncrona
    await monitorar_planilhas()

subprocess.run(["python", "automacao_subempreiteiros.py"])

# === EXECUÇÃO ===
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🟥 Execução encerrada manualmente.")