import pyautogui
import webbrowser
import os
from flask import request
from src.config import app, add_log


@app.route('/run/<app_name>')
def run_app(app_name):
    urls = {
        'netflix': 'https://netflix.com',
        'prime': 'https://primevideo.com',
        'spotify': 'spotify:',
        'ytmusic': 'https://music.youtube.com',
        'disney': 'https://www.disneyplus.com',
        'max': 'https://play.hbomax.com',
        'crunchyroll': 'https://www.crunchyroll.com/pt-br',
        'chrome': 'google-chrome'
    }
    if app_name in urls:
        webbrowser.open(urls[app_name])
        add_log(f"Abriu: {app_name}")
    else:
        add_log(f"App desconhecido: {app_name}")
    return "OK"


@app.route('/mouse_move')
def mouse_move():
    try:
        x = float(request.args.get('x'))
        y = float(request.args.get('y'))
        pyautogui.moveRel(x, y, _pause=False)
    except:
        pass
    return ""


@app.route('/cmd/<action>')
def command(action):
    # --- MÍDIA ---
    if action == 'playpause':
        pyautogui.press('playpause')
    elif action == 'prev':
        pyautogui.press('prevtrack')
    elif action == 'next':
        pyautogui.press('nexttrack')

    # Seta Direita/Esquerda para pula 10s
    elif action == 'forward':
        pyautogui.press('right')
    elif action == 'rewind':
        pyautogui.press('left')

    # Volume
    elif action == 'volumeup':
        pyautogui.press('volumeup')
    elif action == 'volumedown':
        pyautogui.press('volumedown')
    elif action == 'mute':
        pyautogui.press('volumemute')

    # Navegação
    elif action == 'up':
        pyautogui.press('up')
    elif action == 'down':
        pyautogui.press('down')
    elif action == 'left':
        pyautogui.press('left')
    elif action == 'right':
        pyautogui.press('right')
    elif action == 'enter':
        pyautogui.press('enter')
    elif action == 'back':
        pyautogui.press('browserback')
    elif action == 'tab':
        pyautogui.press('tab')

    # Sistema
    elif action == 'fullscreen':
        pyautogui.press('f11')
    elif action == 'close':
        pyautogui.hotkey('ctrl', 'w')
    elif action == 'alt_tab':
        pyautogui.hotkey('alt', 'tab')
    elif action == 'win_d':
        pyautogui.hotkey('win', 'd')
    elif action == 'shutdown':
        os.system("shutdown /s /t 10")

    # Mouse
    elif action == 'click_left':
        pyautogui.click()
    elif action == 'click_right':
        pyautogui.click(button='right')
    elif action == 'scroll_up':
        pyautogui.scroll(300)
    elif action == 'scroll_down':
        pyautogui.scroll(-300)

    add_log(f"Comando: {action}")
    return "OK"