from flask import request
import webbrowser
import pyautogui
import requests
from bs4 import BeautifulSoup
from src.config import app, add_log
from view.layout import render_page


@app.route('/type/<text>')
def type_text(text):
    if not text.startswith('/'):
        pyautogui.press('/')
    pyautogui.write(text, interval=0.05)
    pyautogui.press('enter')
    add_log(f"Digitou: {text}")
    return "OK"


@app.route('/search', methods=['POST'])
def search_general():
    term = request.form.get('term')
    add_log(f"Buscando: {term}")

    html_results = f"<h3>🔎 Busca BR: {term}</h3>"

    html_results += f"""
    <div style="margin-bottom:15px;">
        <button class="btn btn-blue" onclick="fetch('/deep_search_pc?term={term}')">
            🖥️ Abrir direto no Monitor
        </button>
    </div>
    """

    try:
        url = "https://html.duckduckgo.com/html/"

        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; SM-A205U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36",
            "Referer": "https://html.duckduckgo.com/"
        }

        payload = {
            'q': term,
            'kl': 'br-pt'
        }

        response = requests.post(url, data=payload, headers=headers)

        soup = BeautifulSoup(response.text, "html.parser")

        links = soup.find_all('a', class_='result__a')

        if not links:
            html_results += "<p>Nenhum resultado encontrado.</p>"

        count = 0
        for link in links:
            if count >= 10: break

            href = link['href']
            title = link.text


            try:
                snippet = link.find_parent('div').find_parent('div').find('a', class_='result__snippet').text
            except:
                snippet = "Clique para acessar"


            if "duckduckgo.com" in href:
                continue

            html_results += f"""
            <div style="background:#222; margin:10px; padding:15px; border-radius:10px; text-align:left; cursor:pointer; border-left: 5px solid #E67E22;" 
                 onclick="fetch('/open_url?link={href}')">
                <div style="font-weight:bold; color: #fff; font-size:16px; margin-bottom:5px;">{title}</div>
                <div style="color:#ccc; font-size:12px; margin-bottom:5px;">{snippet}</div>
                <div style="color:#E67E22; font-size:10px; overflow:hidden; white-space:nowrap;">{href}</div>
            </div>
            """
            count += 1

    except Exception as e:
        html_results += f"<p>Erro técnico: {e}</p>"
        print(f"Erro: {e}")

    return render_page(active_tab="caster", results=html_results)


@app.route('/open_url')
def open_url():
    link = request.args.get('link')
    if link:
        webbrowser.open(link)
        add_log(f"Abrindo: {link}")
    return "OK"


@app.route('/deep_search_pc')
def deep_search_pc():
    term = request.args.get('term')
    webbrowser.open(f"https://www.google.com/search?q={term}")
    return "OK"