# Bereta Server - Smart Control Hub

O **Bereta Server** é uma solução de automação residencial e controle remoto para PC desenvolvida em Python. O sistema transforma qualquer smartphone em uma central de controle universal via rede local, eliminando a necessidade de periféricos físicos ou instalação de aplicativos no dispositivo móvel.

---

#download
link
```
https://drive.google.com/file/d/18e-w22Z88Z_TlyAZZy35kHTKKBbKlkPZ/view?usp=drive_link
```

## 📋 Funcionalidades

### 🎮 Controle e Jogos
- **Game Launcher:** Gerenciador de jogos no PC com interface visual. Permite adicionar atalhos (`.exe`, `.lnk`) que são listados automaticamente no celular para execução remota.
- **Mouse Virtual:** Touchpad responsivo na tela do celular com suporte a clique esquerdo, direito e rolagem.
- **Modo Sniper (Espelhamento):** Transmissão de tela em tempo real (MJPEG) para o celular, permitindo visualização e cliques precisos em elementos pequenos.
- **Teclado Remoto:** Envio de texto do celular para o PC.

### 🎵 Multimídia
- **Integração YouTube Music:** Busca e reprodução de músicas/álbuns diretamente pelo celular utilizando a API do YouTube Music.
- **Modo DJ Inteligente:** Sistema lógico que gerencia janelas do navegador. Ao trocar de música, o sistema identifica e fecha a janela da música anterior (modo *App* ou aba) sem interferir em outras abas de trabalho ou estudo.
- **Controles de Mídia:** Play/Pause, Avançar/Voltar Faixa, Avançar/Voltar 10s (para streaming de vídeo) e Volume.

### 📂 Arquivos e Sistema
- **Transferência de Arquivos:** Sistema bidirecional para enviar arquivos do celular para o PC e baixar arquivos do PC para o celular (pasta `compartilhado`).
- **Monitoramento:** Exibição em tempo real de uso de CPU, RAM e Temperatura (suporte a WMI no Windows).
- **Gerenciamento de Energia:** Timer de desligamento automático ("Modo Soneca") e comandos para desligar/reiniciar.
- **Gerenciamento de Janelas:** Comandos para Alt+Tab, Maximizar, Fechar Janela e Mostrar Área de Trabalho.

### 🔒 Segurança & Conexão
- **Pairing via QR Code:** Geração automática de QR Code contendo token de sessão único.
- **Autenticação Híbrida:** Suporte a login via Token (automático) ou Senha Manual configurável.
- **Isolamento:** O servidor roda localmente, sem dependência de nuvem.

---

## 🛠️ Stack Tecnológica

O projeto foi estruturado utilizando o padrão **MVC (Model-View-Controller)** para garantir organização e escalabilidade.

- **Backend:** `Python 3.10+`, `Flask` (Server Multithread).
- **Interface Desktop:** `Flet` (GUI moderna baseada em Flutter).
- **Interface Mobile:** `HTML5`, `CSS3`, `JavaScript` (SPA - Single Page Application).
- **Bibliotecas Chave:**
  - `pyautogui`: Automação de input.
  - `ytmusicapi`: Dados do YouTube Music.
  - `mss` & `pillow`: Captura e processamento de imagem para espelhamento.
  - `pygetwindow`: Gerenciamento de janelas do SO.
  - `psutil` & `wmi`: Monitoramento de hardware.

---

## 🚀 Instalação e Execução

### 1. Pré-requisitos
Certifique-se de ter o Python instalado. Clone este repositório ou baixe os arquivos.

### 2. Instalação das Dependências
Execute o comando abaixo no terminal para instalar todas as bibliotecas necessárias:


```
pip install -r requirements.txt
```
3. Executando o Servidor
Inicie a aplicação com o comando:

python main.py
Uma interface abrirá no seu PC exibindo o status e o QR Code. Escaneie com seu celular (conectado ao mesmo Wi-Fi) para iniciar o controle.

📦 Compilação (.exe)
Para distribuir o software sem necessidade de instalação do Python em outras máquinas, utilize o PyInstaller com o seguinte comando (otimizado para incluir assets e módulos ocultos):
````
pyinstaller --noconsole --name="BeretaServer" --icon="public/img/bereta.png" --add-data "public;public" --collect-all ytmusicapi --hidden-import=pygetwindow --hidden-import=pyscreeze --hidden-import=PIL main.py
````

📂 Estrutura de Diretórios
Plaintext

```
BeretaServer/
├── main.py              # Entry point e Interface Desktop (Flet)
├── src/                 # Lógica de Negócio (Backend)
│   ├── arquivos.py      # Controller de Arquivos
│   ├── buscar.py        # Controller de Busca Web
│   ├── config.py        # Configurações e Persistência JSON
│   ├── games.py         # Controller de Jogos
│   ├── mirror.py        # Streaming de Vídeo
│   ├── music.py         # Controller de Música
│   └── sistema.py       # Monitoramento de Hardware
├── view/                # Frontend
│   └── layout.py        # Template HTML/JS
└── public/              # Assets (Imagens)
```
Status do Projeto: Finalizado (v1.0).
