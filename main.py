import threading
import flet as ft
import socket
import os
from flask import request, session, redirect, render_template_string
from src.config import app, FOTO_PERFIL, log_messages, SERVER_TOKEN, carregar_senha, salvar_senha, carregar_config, \
    salvar_config, get_senha
from view.layout import render_page

import src.games as games_manager
import src.favoritos as fav_manager
import src.arquivos as file_manager
import src.mirror
import src.streaming
import src.buscar
import src.sistema
import src.music
import src.gerar_qrcode as gerador_qr

LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { background-color: #121212; color: white; font-family: sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; }
        .card { background: #222; padding: 30px; border-radius: 15px; text-align: center; width: 80%; max-width: 300px; border: 1px solid #333; }
        input { padding: 15px; border-radius: 10px; border: none; width: 90%; margin-bottom: 20px; font-size: 18px; text-align: center; }
        button { padding: 15px; width: 100%; border-radius: 10px; border: none; background: #2196F3; color: white; font-size: 18px; font-weight: bold; cursor: pointer; }
        .error { color: #ff4444; margin-bottom: 15px; }
    </style>
</head>
<body>
    <div class="card">
        <h2>🔒 Bloqueado</h2>
        <p style="color:#aaa; font-size:14px;">Escaneie o QR Code ou digite a senha manual.</p>
        {% if erro %}<div class="error">{{ erro }}</div>{% endif %}
        <form action="/login" method="post">
            <input type="password" name="senha" placeholder="Senha" required>
            <button type="submit">Entrar</button>
        </form>
    </div>
</body>
</html>
"""

@app.before_request
def verificar_seguranca():
    if request.path.startswith('/public/') or request.path == '/login': return None
    if session.get('autenticado') == True: return None
    token_recebido = request.args.get('token')
    if token_recebido == SERVER_TOKEN:
        session['autenticado'] = True
        session.permanent = True
        return None
    return render_template_string(LOGIN_HTML, erro=None)


@app.route('/login', methods=['POST'])
def login():
    if request.form.get('senha') == get_senha():
        session['autenticado'] = True
        session.permanent = True
        return redirect('/')
    return render_template_string(LOGIN_HTML, erro="Senha Incorreta!")


@app.route('/')
def index(): return render_page(active_tab="apps")


from flask import send_from_directory


@app.route('/public/img/<path:filename>')
def serve_image(filename): return send_from_directory('public/img', filename)


def run_flask():
    app.run(host='0.0.0.0', port=5000, use_reloader=False, threaded=True)


def main(page: ft.Page):
    page.title = "Smart Control - Hub"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 500
    page.window_height = 850

    img_base64, link_gerado, ip_atual = gerador_qr.gerar_qr_base64()
    if os.path.exists(FOTO_PERFIL):
        img_avatar = ft.Image(src=FOTO_PERFIL, width=100, height=100, border_radius=50, fit=ft.ImageFit.COVER)
    else:
        img_avatar = ft.Icon(name="pets", size=80, color="white")

    log_list = ft.ListView(expand=True, spacing=5, auto_scroll=True)

    def update_logs():
        import time
        while True:
            if log_messages:
                msg = log_messages.pop(0)
                log_list.controls.append(ft.Text(f"> {msg}", font_family="Consolas", color="yellow", size=12))
                page.update()
            time.sleep(0.5)

    tab_conexao = ft.Container(padding=20, content=ft.Column([
        ft.Row([img_avatar, ft.Text("Bereta Server", size=24, weight="bold")], alignment=ft.MainAxisAlignment.CENTER),
        ft.Container(content=ft.Image(src_base64=img_base64, width=250, height=250, fit=ft.ImageFit.CONTAIN),
                     padding=10, alignment=ft.alignment.center),
        ft.Text(f"IP: {ip_atual}", color="grey"),
        ft.Text("🔒 Sistema Protegido", color="green", size=12),
        ft.Divider(),
        ft.Container(content=log_list, height=150, bgcolor="#222", border_radius=10, padding=10)
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER))

    lista_jogos_ui = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)

    def carregar_jogos_ui():
        lista_jogos_ui.controls.clear()
        for jogo in games_manager.carregar_jogos_json():
            row = ft.Container(bgcolor="#333", padding=10, border_radius=10, content=ft.Row([
                ft.Icon(name="games", color="white"),
                ft.Text(jogo['nome'], weight="bold", expand=True),
                ft.IconButton(icon="delete", icon_color="red",
                              on_click=lambda e, nome=jogo['nome']: (games_manager.remover_jogo_json(nome),
                                                                     carregar_jogos_ui()))
            ]))
            lista_jogos_ui.controls.append(row)
        page.update()

    def add_jogo(e: ft.FilePickerResultEvent):
        if e.files:
            games_manager.salvar_jogo_json(e.files[0].name.replace(".exe", "").replace(".lnk", ""), e.files[0].path)
            carregar_jogos_ui()

    picker_jogo = ft.FilePicker(on_result=add_jogo)
    page.overlay.append(picker_jogo)
    tab_jogos = ft.Container(padding=20, content=ft.Column([
        ft.Text("Meus Jogos", size=20, weight="bold"),
        lista_jogos_ui,
        ft.FloatingActionButton(icon="add", text="Adicionar",
                                on_click=lambda _: picker_jogo.pick_files(allow_multiple=False))
    ]))


    lista_fav_ui = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
    input_fav_nome = ft.TextField(label="Nome", height=40)
    input_fav_url = ft.TextField(label="URL", height=40)

    def carregar_fav_ui():
        lista_fav_ui.controls.clear()
        for fav in fav_manager.carregar_favoritos():
            row = ft.Container(bgcolor="#333", padding=10, border_radius=10, content=ft.Row([
                ft.Icon(name="star", color="yellow"),
                ft.Column([ft.Text(fav['nome'], weight="bold"), ft.Text(fav['url'], size=10, color="grey")],
                          expand=True),
                ft.IconButton(icon="delete", icon_color="red",
                              on_click=lambda e, nome=fav['nome']: (fav_manager.remover_favorito(nome),
                                                                    carregar_fav_ui()))
            ]))
            lista_fav_ui.controls.append(row)
        page.update()

    def salvar_fav_click(e):
        if input_fav_nome.value and input_fav_url.value:
            fav_manager.salvar_favorito(input_fav_nome.value, input_fav_url.value)
            input_fav_nome.value = ""
            input_fav_url.value = ""
            carregar_fav_ui()

    tab_favoritos = ft.Container(padding=20, content=ft.Column([
        ft.Text("Meus Favoritos", size=20, weight="bold"),
        ft.Row([input_fav_nome, input_fav_url]),
        ft.ElevatedButton("Salvar", icon="save", on_click=salvar_fav_click),
        ft.Divider(),
        lista_fav_ui
    ]))

    lista_arquivos_ui = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)

    def carregar_arquivos_ui():
        lista_arquivos_ui.controls.clear()
        arquivos = file_manager.listar_arquivos_pc()
        if not arquivos: lista_arquivos_ui.controls.append(ft.Text("Pasta vazia.", color="grey"))
        for arq in arquivos:
            row = ft.Container(bgcolor="#333", padding=10, border_radius=10, content=ft.Row([
                ft.Icon(name="description", color="blue"),
                ft.Text(arq, weight="bold", expand=True),
                ft.IconButton(icon="delete", icon_color="red",
                              on_click=lambda e, nome=arq: (file_manager.remover_arquivo(nome), carregar_arquivos_ui()))
            ]))
            lista_arquivos_ui.controls.append(row)
        page.update()

    def add_arquivo_pc(e: ft.FilePickerResultEvent):
        if e.files:
            file_manager.adicionar_arquivo_do_pc(e.files[0].path)
            carregar_arquivos_ui()
            page.snack_bar = ft.SnackBar(ft.Text("Arquivo enviado!"))
            page.snack_bar.open = True
            page.update()

    picker_arquivo = ft.FilePicker(on_result=add_arquivo_pc)
    page.overlay.append(picker_arquivo)
    tab_arquivos = ft.Container(padding=20, content=ft.Column([
        ft.Text("Arquivos", size=20, weight="bold"),
        ft.ElevatedButton("Enviar para Celular", icon="upload", on_click=lambda _: picker_arquivo.pick_files()),
        ft.Divider(),
        ft.Row(
            [ft.Text("Pasta Compartilhada"), ft.IconButton(icon="refresh", on_click=lambda _: carregar_arquivos_ui())]),
        lista_arquivos_ui
    ]))


    input_senha = ft.TextField(label="Senha Manual", password=True, can_reveal_password=True, value=get_senha())


    switch_dj = ft.Switch(label="Fechar aba de musica anterior", value=carregar_config()["modo_dj"])

    def salvar_config_click(e):
        if input_senha.value:

            salvar_config({"senha": input_senha.value, "modo_dj": switch_dj.value})

            page.snack_bar = ft.SnackBar(ft.Text("Configurações salvas!"))
            page.snack_bar.open = True
            page.update()

    tab_config = ft.Container(padding=20, content=ft.Column([
        ft.Text("Configurações", size=20, weight="bold"),
        ft.Divider(),
        ft.Text("Segurança", weight="bold"),
        input_senha,
        ft.Divider(),
        ft.Text("Comportamento", weight="bold"),
        switch_dj,
        ft.Text("Ative o Modo Musica para fechar a aba anterior ao tocar outra música.", size=12, color="grey"),
        ft.Divider(),
        ft.ElevatedButton("Salvar Tudo", icon="save", on_click=salvar_config_click)
    ]))


    t = ft.Tabs(selected_index=0, animation_duration=300, tabs=[
        ft.Tab(text="Conexão", icon="wifi", content=tab_conexao),
        ft.Tab(text="Jogos", icon="games", content=tab_jogos),
        ft.Tab(text="Favoritos", icon="star", content=tab_favoritos),
        ft.Tab(text="Arquivos", icon="folder", content=tab_arquivos),
        ft.Tab(text="Config", icon="settings", content=tab_config),
    ], expand=1)

    page.add(t)
    carregar_jogos_ui()
    carregar_fav_ui()
    carregar_arquivos_ui()
    threading.Thread(target=update_logs, daemon=True).start()


if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    ft.app(target=main)