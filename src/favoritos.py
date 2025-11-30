import json
import os
import webbrowser
from src.config import app, add_log, BASE_DIR

ARQUIVO_FAV = os.path.join(BASE_DIR, "favoritos.json")

def carregar_favoritos():
    if not os.path.exists(ARQUIVO_FAV):
        return []
    try:
        with open(ARQUIVO_FAV, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def salvar_favorito(nome, url):
    favs = carregar_favoritos()
    favs.insert(0, {"nome": nome, "url": url})

    with open(ARQUIVO_FAV, "w", encoding="utf-8") as f:
        json.dump(favs, f, indent=4, ensure_ascii=False)


def remover_favorito(nome):
    favs = carregar_favoritos()
    favs = [f for f in favs if f['nome'] != nome]
    with open(ARQUIVO_FAV, "w", encoding="utf-8") as f:
        json.dump(favs, f, indent=4, ensure_ascii=False)


@app.route('/open_fav')
def open_fav():
    url = request.args.get('url')
    webbrowser.open(url)
    add_log(f"Favorito aberto: {url}")
    return "OK"


from flask import request


@app.route('/add_fav', methods=['POST'])
def add_fav_route():
    nome = request.form.get('nome')
    url = request.form.get('url')
    if nome and url:
        salvar_favorito(nome, url)
        add_log(f"Novo Favorito: {nome}")
    return "<script>window.location.href='/';</script>"