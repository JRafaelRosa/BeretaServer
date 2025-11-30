import os
import json
from src.config import app, add_log, BASE_DIR

ARQUIVO_JSON = os.path.join(BASE_DIR, "meus_jogos.json")


def carregar_jogos_json():
    if not os.path.exists(ARQUIVO_JSON):
        return []
    try:
        with open(ARQUIVO_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def salvar_jogo_json(nome, caminho):
    """Salva um novo jogo no JSON"""
    jogos = carregar_jogos_json()
    for j in jogos:
        if j['nome'] == nome:
            return False

    jogos.append({"nome": nome, "caminho": caminho})

    with open(ARQUIVO_JSON, "w", encoding="utf-8") as f:
        json.dump(jogos, f, indent=4, ensure_ascii=False)
    return True


def remover_jogo_json(nome):
    """Remove um jogo pelo nome"""
    jogos = carregar_jogos_json()
    jogos = [j for j in jogos if j['nome'] != nome]

    with open(ARQUIVO_JSON, "w", encoding="utf-8") as f:
        json.dump(jogos, f, indent=4, ensure_ascii=False)


@app.route('/launch_game/<nome_jogo>')
def launch_game(nome_jogo):
    jogos = carregar_jogos_json()

    caminho = None
    for j in jogos:
        if j['nome'] == nome_jogo:
            caminho = j['caminho']
            break

    if caminho and os.path.exists(caminho):
        try:

            os.startfile(caminho)
            add_log(f"Iniciando: {nome_jogo}")
        except Exception as e:
            add_log(f"Erro ao abrir: {e}")
    else:
        add_log(f"Jogo não encontrado ou caminho inválido: {nome_jogo}")

    return "OK"