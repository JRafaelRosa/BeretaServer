from flask import request
import webbrowser
from ytmusicapi import YTMusic
from src.config import app, add_log, get_modo_dj
from view.layout import render_page
import pyautogui
import time
import os
import subprocess

# Tenta importar pygetwindow
try:
    import pygetwindow as gw
except ImportError:
    gw = None

ytmusic = YTMusic()


def abrir_navegador_modo_app(url):
    """Abre em modo App e TENTA FORÇAR O AUTOPLAY"""
    navegadores = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
    ]
    for navegador in navegadores:
        if os.path.exists(navegador):
            try:
                # Adicionei a flag --autoplay-policy=no-user-gesture-required
                # Isso diz pro Chrome: "Deixe tocar som mesmo sem clique"
                subprocess.Popen([navegador, f"--app={url}", "--autoplay-policy=no-user-gesture-required"])
                return True
            except:
                pass
    webbrowser.open(url)
    return False


@app.route('/music_search', methods=['POST'])
def music_search():
    term = request.form.get('term')
    add_log(f"Music Search: {term}")
    html_results = f"<h3>🎵 Resultados: {term}</h3>"
    try:
        results = ytmusic.search(term, limit=10)
        if not results: html_results += "<p>Nada encontrado.</p>"
        for r in results:
            tipo = r['resultType']
            if tipo not in ['song', 'video', 'album']: continue
            title = r['title']
            artist = r['artists'][0]['name'] if 'artists' in r and r['artists'] else ""
            thumb = r['thumbnails'][-1]['url'] if 'thumbnails' in r and r['thumbnails'] else ""

            # --- MUDANÇA AQUI: Adicionando &autoplay=1 nos links ---
            if tipo == 'album':
                link = f"https://music.youtube.com/browse/{r['browseId']}"  # Album n aceita autoplay direto facil
                icon = "💿"
            else:
                # Para musicas e videos, forçamos o autoplay na URL
                link = f"https://music.youtube.com/watch?v={r['videoId']}&autoplay=1"
                icon = "🎵"

            html_results += f"""
            <div style="background:#1a1a1a; margin:10px; padding:10px; border-radius:10px; display:flex; align-items:center; cursor:pointer; border-bottom: 2px solid #333;" 
                 onclick="fetch('/play_music_url?link={link}')">
                <img src="{thumb}" width="60" height="60" style="border-radius:5px; object-fit:cover; margin-right:15px;">
                <div style="text-align:left; flex:1;">
                    <div style="font-weight:bold; color: #fff; font-size:15px;">{title}</div>
                    <div style="color:#aaa; font-size:12px;">{icon} {artist}</div>
                </div>
                <div style="font-size:20px;">▶</div>
            </div>
            """
    except Exception as e:
        html_results += f"<p>Erro: {e}</p>"
    return render_page(active_tab="music", results=html_results)


@app.route('/play_music_url')
def play_music_url():
    link = request.args.get('link')
    if link:
        # --- MODO DJ (Fecha Janela Anterior) ---
        if get_modo_dj() and gw:
            try:
                janelas = gw.getWindowsWithTitle('YouTube')
                for w in janelas:
                    titulo = w.title.lower()
                    # Fecha se for musica e não for curso
                    if ("music" in titulo or "youtube" in titulo) and not any(
                            x in titulo for x in ["curso", "aula", "python", "tutorial"]):
                        # Mata janela antiga
                        os.system(f'taskkill /F /FI "WINDOWTITLE eq {w.title}"')
                        time.sleep(0.3)
                        break
            except Exception as e:
                print(f"Erro ao matar janela: {e}")

        # Abre a nova música (Com a flag de autoplay)
        abrir_navegador_modo_app(link)

        # --- PLANO B (Segurança Extra) ---
        # Se o computador for lento e o autoplay falhar,
        # esperamos 5 segundos e apertamos Espaço para garantir o Play.
        # (Só faz isso se o Modo DJ estiver ligado para não atrapalhar outros usos)
        if get_modo_dj():
            time.sleep(5)
            pyautogui.press('space')

        add_log(f"Tocando Música...")

    return "OK"