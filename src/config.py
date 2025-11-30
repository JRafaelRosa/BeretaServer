from flask import Flask
import secrets
import json
import os
import sys

app = Flask(__name__)

app.secret_key = secrets.token_hex(16)
SERVER_TOKEN = secrets.token_urlsafe(8)


def get_base_path():
    """Retorna o caminho exato da pasta onde o .exe está rodando"""
    if getattr(sys, 'frozen', False):

        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))



BASE_DIR = get_base_path()


PASTA_JOGOS = os.path.join(BASE_DIR, "jogos")
ARQUIVO_SETTINGS = os.path.join(BASE_DIR, "settings.json")
ARQUIVO_FAV = os.path.join(BASE_DIR, "favoritos.json")
PASTA_COMPARTILHADA = os.path.join(BASE_DIR, "compartilhado")


FOTO_PERFIL = os.path.join(BASE_DIR, "public", "img", "bereta.png")

log_messages = []


def add_log(msg):
    print(f"Log: {msg}")
    if len(log_messages) > 50:
        log_messages.pop(0)
    log_messages.append(msg)


def carregar_config():
    padrao = {"senha": "1234", "modo_dj": True}

    if not os.path.exists(ARQUIVO_SETTINGS):
        try:
            with open(ARQUIVO_SETTINGS, "w", encoding="utf-8") as f:
                json.dump(padrao, f, indent=4)
        except:
            pass
        return padrao

    try:
        with open(ARQUIVO_SETTINGS, "r", encoding="utf-8") as f:
            dados = json.load(f)
            if "senha" not in dados: dados["senha"] = "1234"
            if "modo_dj" not in dados: dados["modo_dj"] = True
            return dados
    except:
        return padrao


def salvar_config(novos_dados):
    dados_atuais = carregar_config()
    dados_atuais.update(novos_dados)

    with open(ARQUIVO_SETTINGS, "w", encoding="utf-8") as f:
        json.dump(dados_atuais, f, indent=4)
    add_log("Configurações atualizadas.")


def carregar_senha(): return carregar_config()["senha"]


def salvar_senha(nova_senha): salvar_config({"senha": nova_senha})


def get_senha(): return carregar_config()["senha"]


def get_modo_dj(): return carregar_config()["modo_dj"]