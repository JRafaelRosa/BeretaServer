from flask import Flask
import secrets
import json
import os

app = Flask(__name__)

# --- SEGURANÇA ---
app.secret_key = secrets.token_hex(16)
SERVER_TOKEN = secrets.token_urlsafe(8)

# Configurações Globais
PASTA_JOGOS = "jogos"
FOTO_PERFIL = "public/img/bereta.png"
ARQUIVO_SETTINGS = "settings.json"

log_messages = []


def add_log(msg):
    print(f"Log: {msg}")
    if len(log_messages) > 50:
        log_messages.pop(0)
    log_messages.append(msg)


# --- FUNÇÕES DE CONFIGURAÇÃO (JSON) ---

def carregar_config():
    """Lê todas as configs do JSON"""
    padrao = {"senha": "1234", "modo_dj": False}

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
            # Garante que as chaves existam
            if "senha" not in dados: dados["senha"] = "1234"
            if "modo_dj" not in dados: dados["modo_dj"] = False
            return dados
    except:
        return padrao


def salvar_config(novos_dados):
    """Salva configs no JSON"""
    dados_atuais = carregar_config()
    dados_atuais.update(novos_dados)

    with open(ARQUIVO_SETTINGS, "w", encoding="utf-8") as f:
        json.dump(dados_atuais, f, indent=4)
    add_log("Configurações atualizadas.")


# --- FUNÇÕES ESPECÍFICAS (Que o main.py pede) ---

def carregar_senha():
    return carregar_config()["senha"]


def salvar_senha(nova_senha):
    salvar_config({"senha": nova_senha})


def get_senha():
    return carregar_config()["senha"]


def get_modo_dj():
    return carregar_config()["modo_dj"]