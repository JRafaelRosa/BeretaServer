import os
from flask import render_template_string, request
from src.config import PASTA_JOGOS
import src.games as games_manager
import src.favoritos as fav_manager
import src.arquivos as file_manager

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>Bereta Controller</title>
    <link rel="icon" type="image/png" href="/public/img/bereta.ico">
    <style>
        body { background-color: #121212; color: #e0e0e0; font-family: sans-serif; margin: 0; padding-bottom: 80px; text-align: center; overflow-x: hidden; }

        /* --- ABAS --- */
        .tabs { display: flex; position: sticky; top: 0; background: #1f1f1f; z-index: 50; box-shadow: 0 2px 5px black; overflow-x: auto; }
        .tab-btn { flex: 1; min-width: 50px; padding: 15px 5px; background: none; border: none; color: #888; font-size: 20px; cursor: pointer; }
        .tab-btn.active { color: #2196F3; border-bottom: 3px solid #2196F3; }

        .container { display: none; padding: 20px; }
        .container.active { display: block; }
        .row { display: flex; gap: 10px; margin-bottom: 10px; justify-content: center; }

        /* --- BOTÕES GERAIS --- */
        .btn { width: 100%; padding: 20px; margin: 5px 0; border: none; border-radius: 12px; font-size: 18px; color: white; background: #333; cursor: pointer; }
        .btn:active { transform: scale(0.98); }
        .btn-red { background: #d32f2f; }
        .btn-green { background: #2e7d32; }
        .btn-blue { background: #1565c0; }
        .btn-orange { background: #ff9800; color: black; }

        /* --- ESTILOS APPS E JOGOS --- */
        .app-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
        .app-card { background: #1e1e1e; padding: 20px; border-radius: 10px; border: 1px solid #333; cursor: pointer;}

        /* --- FAVORITOS --- */
        .fav-list { text-align: left; margin-top: 20px; }
        .fav-item { background: #222; padding: 15px; margin-bottom: 10px; border-radius: 10px; display: flex; justify-content: space-between; border-left: 4px solid #FFC107; cursor: pointer; }
        .add-fav-box { background: #333; padding: 15px; border-radius: 10px; margin-top: 20px; }

        /* --- SISTEMA --- */
        .system-card { background: #222; border-radius: 15px; padding: 15px; margin-bottom: 20px; border: 1px solid #333; }
        .system-title { color: #aaa; font-size: 14px; margin-bottom: 10px; text-align: left; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; }
        .monitor-box { display: flex; justify-content: space-around; font-family: monospace; font-size: 18px; color: #00ff00; }

        /* --- ARQUIVOS --- */
        .file-box { background: #222; padding: 20px; border-radius: 15px; margin-bottom: 20px; border: 2px dashed #444; }
        .file-list-item { background: #1a1a1a; padding: 15px; margin-bottom: 10px; border-radius: 10px; display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #333; }
        .file-btn { background: #2196F3; color: white; border: none; padding: 8px 15px; border-radius: 5px; text-decoration: none; font-size: 14px;}

        /* --- FULLSCREEN MODAL (MODO SNIPER) --- */
        #fs-modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: black; z-index: 9999; overflow: hidden; }
        #fs-container { width: 100%; height: 100%; display: flex; justify-content: center; align-items: center; transform-origin: center; transition: transform 0.2s; }
        #fs-img { max-width: 100%; max-height: 100%; }
        .fs-controls { position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); display: flex; gap: 15px; background: rgba(0,0,0,0.7); padding: 10px; border-radius: 30px; }
        .fs-btn { background: none; border: 2px solid white; color: white; width: 50px; height: 50px; border-radius: 50%; font-size: 20px; cursor: pointer; }
        .fs-btn.active { background: #2196F3; border-color: #2196F3; }

        /* --- CONTROLES (Touchpad e D-Pad) --- */
        #touchpad { 
            width: 90%; height: 250px; background: #2a2a2a; margin: 20px auto; 
            border-radius: 15px; border: 2px dashed #444; 
            display: flex; justify-content: center; align-items: center; 
            color: #555; font-weight: bold; position: relative; overflow: hidden;
        }
        #screen-img { width: 100%; height: 100%; object-fit: contain; display: none; pointer-events: none; }
        #touch-text { position: absolute; pointer-events: none; }

        .dpad-area { background: #222; border-radius: 50%; width: 200px; height: 200px; margin: 20px auto; position: relative; }
        .dpad-btn { position: absolute; width: 60px; height: 60px; background: #444; border: none; color: white; border-radius: 10px; }
        .control-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-top: 10px; }

        input { width: 80%; padding: 12px; border-radius: 20px; border: none; font-size: 16px; margin-bottom: 10px; outline:none;}
        .search-btn { padding: 12px; border-radius: 20px; border: none; background: #2196F3; color: white; }
    </style>
</head>
<body>

    <div id="fs-modal">
        <div id="fs-container"><img id="fs-img" src=""></div>
        <div class="fs-controls">
            <button class="fs-btn" onclick="closeFS()">❌</button>
            <button class="fs-btn" onclick="rotateFS()">🔄</button>
            <button class="fs-btn" onclick="changeZoom(0.2)">➕</button>
            <button class="fs-btn" onclick="changeZoom(-0.2)">➖</button>
            <button id="btn-mode" class="fs-btn active" onclick="toggleMode()">🖱️</button>
        </div>
        <div style="position:fixed; top:20px; left:0; width:100%; text-align:center; color:white; pointer-events:none;">
            <span id="mode-text" style="background:rgba(0,0,0,0.5); padding:5px; border-radius:5px;">MODO: MOUSE</span>
        </div>
    </div>

    <div class="tabs">
        <button class="tab-btn active" onclick="openTab('apps', this)">🏠</button>
        <button class="tab-btn" onclick="openTab('games', this)">🎮</button>
        <button class="tab-btn" onclick="openTab('music', this)">🎵</button>
        <button class="tab-btn" onclick="openTab('files', this)">📂</button>
        <button class="tab-btn" onclick="openTab('caster', this)">🔍</button>
        <button class="tab-btn" onclick="openTab('control', this)">🕹️</button>
        <button class="tab-btn" onclick="openTab('system', this)">⚙️</button>
    </div>

    <div id="apps" class="container active">
        <h2>Apps Rápidos</h2>
        <div class="app-grid">
            <div class="app-card" onclick="fetch('/run/netflix')">📺 Netflix</div>
            <div class="app-card" onclick="fetch('/run/prime')">🎬 Prime Video</div>
            <div class="app-card" onclick="fetch('/run/ytmusic')">🎸 YT Music</div>
            <div class="app-card" onclick="fetch('/run/chrome')">▶️YouTube /div>
            <div class="app-card" onclick="fetch('/run/disney')">🏰 Disney+</div>
            <div class="app-card" onclick="fetch('/run/max')">🟣 HBO Max</div>
            <div class="app-card" onclick="fetch('/run/crunchyroll')">🟠 Crunchyroll</div>
            <div class="app-card" onclick="fetch('/run/spotify')">🎵 Spotify</div>
        </div>

        <h2 style="margin-top:30px;">⭐ Meus Favoritos</h2>
        <div class="fav-list">
            {% for fav in lista_favs %}
            <div class="fav-item" onclick="fetch('/open_fav?url={{ fav.url }}')">
                <span>{{ fav.nome }}</span>
                <span style="color:#666;">🔗</span>
            </div>
            {% endfor %}
        </div>
        <div class="add-fav-box">
            <h4>Adicionar Novo:</h4>
            <form action="/add_fav" method="post">
                <input type="text" name="nome" placeholder="Nome" required>
                <input type="text" name="url" placeholder="Link" required>
                <button class="search-btn" style="width:100%">Salvar Favorito</button>
            </form>
        </div>
    </div>

    <div id="games" class="container">
        <h2>Meus Aplicativos</h2>
        <div class="app-grid">
            {% for jogo in lista_jogos %}
            <div class="app-card" onclick="fetch('/launch_game/{{ jogo.nome }}')">🎮 {{ jogo.nome }}</div>
            {% endfor %}
        </div>
        {% if not lista_jogos %}<p style="margin-top:20px; color:#666;">Adicione jogos na aba "Meus Aplicativos" no PC.</p>{% endif %}
    </div>

    <div id="music" class="container">
        <form action="/music_search" method="post">
            <input type="text" name="term" placeholder="Música..." autocomplete="off">
            <button class="search-btn" style="background:#ff0000">Buscar</button>
        </form>

        <div class="row" style="margin-top:15px; background:#222; padding:10px; border-radius:15px;">
            <button class="btn" style="padding:15px; font-size:20px;" onclick="fetch('/cmd/prev')">⏮</button>
            <button class="btn" style="padding:15px; font-size:20px;" onclick="fetch('/cmd/rewind')">⏪</button>
            <button class="btn" style="padding:15px; font-size:24px; width:100px;" onclick="fetch('/cmd/playpause')">⏯</button>
            <button class="btn" style="padding:15px; font-size:20px;" onclick="fetch('/cmd/forward')">⏩</button>
            <button class="btn" style="padding:15px; font-size:20px;" onclick="fetch('/cmd/next')">⏭</button>
        </div>

        <div id="music_results" style="margin-top:20px;">{{ results|safe }}</div>
    </div>

    <div id="files" class="container">
        <h2>Transferência</h2>
        <div class="file-box">
            <h3 style="margin-top:0;">📤 Enviar para PC</h3>
            <form action="/upload" method="post" enctype="multipart/form-data">
                <input type="file" name="file" style="color:white; margin-bottom:15px;">
                <button class="search-btn" style="width:100%; background:#4CAF50;">Enviar</button>
            </form>
        </div>
        <h3 style="text-align:left;">📥 Baixar do PC</h3>
        <div style="text-align:left;">
            {% for arquivo in lista_arquivos %}
            <div class="file-list-item">
                <span style="font-size:14px; overflow:hidden;">📄 {{ arquivo }}</span>
                <a href="/get_file/{{ arquivo }}" class="file-btn">Baixar</a>
            </div>
            {% endfor %}
        </div>
    </div>

    <div id="caster" class="container">
        <form action="/search" method="post">
            <input type="text" name="term" placeholder="Google/Bing..." autocomplete="off">
            <button class="search-btn">Ir</button>
        </form>
        <div id="results">{{ results|safe }}</div>
    </div>

    <div id="control" class="container">
        <button class="btn btn-blue" onclick="openFS()" style="margin-bottom:20px; border:2px solid cyan;">
            👁️ Espelhamento
        </button>

        <div class="row">
            <button class="btn" style="padding:15px; font-size:20px;" onclick="fetch('/cmd/prev')">⏮</button>
            <button class="btn" style="padding:15px; font-size:20px;" onclick="fetch('/cmd/rewind')">⏪</button>
            <button class="btn btn-green" style="padding:15px; font-size:24px; width:100px;" onclick="fetch('/cmd/playpause')">⏯</button>
            <button class="btn" style="padding:15px; font-size:20px;" onclick="fetch('/cmd/forward')">⏩</button>
            <button class="btn" style="padding:15px; font-size:20px;" onclick="fetch('/cmd/next')">⏭</button>
        </div>

        <div class="row">
            <button class="btn" onclick="fetch('/cmd/volumedown')">🔉</button>
            <button class="btn btn-red" onclick="fetch('/cmd/mute')">🔇</button>
            <button class="btn" onclick="fetch('/cmd/volumeup')">🔊</button>
        </div>

        <div id="touchpad">
            <span id="touch-text">MOUSE (DESLIZE)</span>
            <img id="screen-img" src="">
        </div>

        <div class="row">
            <button class="btn" onclick="fetch('/cmd/scroll_up')">🔼 Rolar</button>
            <button class="btn" onclick="fetch('/cmd/click_right')">🖱️ Dir.</button>
            <button class="btn" onclick="fetch('/cmd/scroll_down')">🔽 Rolar</button>
        </div>

        <div class="dpad-area">
            <button class="dpad-btn" style="top:0; left:70px;" onclick="fetch('/cmd/up')">⬆</button>
            <button class="dpad-btn" style="bottom:0; left:70px;" onclick="fetch('/cmd/down')">⬇</button>
            <button class="dpad-btn" style="top:70px; left:0;" onclick="fetch('/cmd/left')">⬅</button>
            <button class="dpad-btn" style="top:70px; right:0;" onclick="fetch('/cmd/right')">➡</button>
            <button class="dpad-btn" style="top:70px; left:70px; background:#2196F3;" onclick="fetch('/cmd/enter')">OK</button>
        </div>
        <br>
        <input type="text" id="typeText" placeholder="Digitar...">
        <button class="btn btn-blue" onclick="sendText()">Enviar Texto</button>
    </div>

    <div id="system" class="container">
        <h2>Gerenciar PC</h2>
        <div class="system-card">
            <div class="system-title">Monitoramento</div>
            <div class="monitor-box" id="sys-bar">CPU: --% | RAM: --%</div>
        </div>
        <div class="system-card">
            <div class="system-title">Timer Soneca</div>
            <div class="row">
                <button class="btn" onclick="if(confirm('Desligar em 30m?')) fetch('/timer/30')">30 min</button>
                <button class="btn" onclick="if(confirm('Desligar em 1h?')) fetch('/timer/60')">1 hora</button>
                <button class="btn btn-green" onclick="fetch('/timer/0')">Cancelar</button>
            </div>
        </div>
        <div class="system-card">
            <div class="system-title">Janelas</div>
            <div class="row">
                <button class="btn" onclick="fetch('/cmd/alt_tab')">Alt+Tab</button>
                <button class="btn" onclick="fetch('/cmd/win_d')">Desktop</button>
            </div>
            <div class="row">
                <button class="btn" onclick="fetch('/cmd/fullscreen')">Tela Cheia</button>
                <button class="btn btn-orange" onclick="fetch('/cmd/close')">Fechar</button>
            </div>
        </div>
        <div class="system-card" style="border-color: #d32f2f;">
            <div class="system-title" style="color: #d32f2f;">Energia</div>
            <button class="btn btn-red" onclick="if(confirm('DESLIGAR PC?')) fetch('/cmd/shutdown')">⏻ DESLIGAR</button>
        </div>
    </div>

    <script>
        // --- Fullscreen Logic ---
        const fsModal = document.getElementById('fs-modal');
        const fsImg = document.getElementById('fs-img');
        const fsContainer = document.getElementById('fs-container');
        let currentZoom = 1.0, currentRotation = 0, modeMouse = true;
        let panX = 0, panY = 0, startPanX, startPanY, startX, startY;

        function openFS() {
            fsModal.style.display = "block";
            fsImg.src = "/video_feed?t=" + new Date().getTime();
        }
        function closeFS() {
            fsModal.style.display = "none";
            fsImg.src = "";
            currentZoom = 1.0; currentRotation = 0; panX = 0; panY = 0;
            updateTransform();
        }
        function changeZoom(delta) {
            currentZoom += delta;
            if (currentZoom < 0.5) currentZoom = 0.5;
            updateTransform();
        }
        function rotateFS() {
            currentRotation += 90;
            if (currentRotation >= 360) currentRotation = 0;
            updateTransform();
        }
        function updateTransform() {
            fsContainer.style.transform = `scale(${currentZoom}) rotate(${currentRotation}deg) translate(${panX}px, ${panY}px)`;
        }
        function toggleMode() {
            modeMouse = !modeMouse;
            const btn = document.getElementById('btn-mode');
            const txt = document.getElementById('mode-text');
            if (modeMouse) {
                btn.innerHTML = "🖱️"; btn.classList.add('active');
                txt.innerText = "MODO: MOUSE";
            } else {
                btn.innerHTML = "✋"; btn.classList.remove('active');
                txt.innerText = "MODO: MOVER TELA";
            }
        }

        fsModal.addEventListener('touchstart', (e) => {
            if (e.target.tagName === 'BUTTON') return;
            startX = e.touches[0].clientX; startY = e.touches[0].clientY;
            if (!modeMouse) { startPanX = panX; startPanY = panY; }
        });
        fsModal.addEventListener('touchmove', (e) => {
            if (e.target.tagName === 'BUTTON') return;
            e.preventDefault();
            let x = e.touches[0].clientX; let y = e.touches[0].clientY;
            let deltaX = x - startX; let deltaY = y - startY;

            if (modeMouse) {
                if (currentRotation === 90) fetch(`/mouse_move?x=${deltaY*2}&y=${-deltaX*2}`);
                else if (currentRotation === 270) fetch(`/mouse_move?x=${-deltaY*2}&y=${deltaX*2}`);
                else fetch(`/mouse_move?x=${deltaX*2}&y=${deltaY*2}`);
            } else {
                panX = startPanX + (deltaX / currentZoom);
                panY = startPanY + (deltaY / currentZoom);
                updateTransform();
            }
            if (modeMouse) { startX = x; startY = y; }
        });
        fsModal.addEventListener('click', (e) => {
            if (e.target.tagName === 'BUTTON') return;
            if (modeMouse) fetch('/cmd/click_left');
        });

        // Touchpad Pequeno (Miniatura)
        const touchZone = document.getElementById('touchpad');
        const screenImg = document.getElementById('screen-img');
        const touchText = document.getElementById('touch-text');


        if(touchZone) {
            let tStartX, tStartY;
            touchZone.addEventListener('touchstart', (e) => { tStartX = e.touches[0].clientX; tStartY = e.touches[0].clientY; });
            touchZone.addEventListener('touchmove', (e) => { 
                e.preventDefault(); 
                let x = e.touches[0].clientX; let y = e.touches[0].clientY; 
                fetch(`/mouse_move?x=${(x-tStartX)*2}&y=${(y-tStartY)*2}`); 
                tStartX = x; tStartY = y; 
            });
            touchZone.addEventListener('click', () => { fetch('/cmd/click_left'); });
        }

        // Geral
        function openTab(tabId, btn) {
            document.querySelectorAll('.container').forEach(c => c.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.getElementById(tabId).classList.add('active');
            btn.classList.add('active');
        }
        function sendText() {
            var txt = document.getElementById('typeText').value;
            if(txt) { fetch('/type/' + encodeURIComponent(txt)); document.getElementById('typeText').value = ''; }
        }
        function updateStatus() {
            if(document.getElementById('system').classList.contains('active')){
                fetch('/status').then(r => r.json()).then(data => {
                    document.getElementById('sys-bar').innerHTML = `CPU: ${data.cpu}% | RAM: ${data.ram}% | 🌡️ ${data.temp}°C`;
                });
            }
        }
        setInterval(updateStatus, 3000);

        if("{{ active_tab }}" != "") {
            var tabBtn = document.querySelector("button[onclick*='{{ active_tab }}']");
            if(tabBtn) openTab('{{ active_tab }}', tabBtn);
        }
    </script>
</body>
</html>"""

def render_page(active_tab="apps", results=""):
    jogos_data = games_manager.carregar_jogos_json()
    favs_data = fav_manager.carregar_favoritos()
    files_data = file_manager.listar_arquivos_pc()
    return render_template_string(HTML_TEMPLATE, lista_jogos=jogos_data, lista_favs=favs_data,
                                  lista_arquivos=files_data, active_tab=active_tab, results=results)