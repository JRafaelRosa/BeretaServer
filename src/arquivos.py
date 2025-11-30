import os
import shutil
from flask import request, send_from_directory, redirect
from src.config import app, add_log, PASTA_COMPARTILHADA

if not os.path.exists(PASTA_COMPARTILHADA):
    os.makedirs(PASTA_COMPARTILHADA)


def listar_arquivos_pc():
    """Retorna lista de arquivos para o Celular e PC"""
    try:
        arquivos = os.listdir(PASTA_COMPARTILHADA)
        return [f for f in arquivos if not f.startswith('.')]
    except:
        return []


def adicionar_arquivo_do_pc(caminho_origem):
    """Copia um arquivo do PC para a pasta de compartilhamento"""
    try:
        shutil.copy(caminho_origem, PASTA_COMPARTILHADA)
        nome = os.path.basename(caminho_origem)
        add_log(f"Arquivo disponibilizado: {nome}")
        return True
    except Exception as e:
        add_log(f"Erro ao copiar: {e}")
        return False


def remover_arquivo(nome_arquivo):
    """Apaga o arquivo da pasta"""
    try:
        caminho = os.path.join(PASTA_COMPARTILHADA, nome_arquivo)
        os.remove(caminho)
        add_log(f"Arquivo removido: {nome_arquivo}")
    except:
        pass


@app.route('/upload', methods=['POST'])
def upload_file():
    # Recebe do Celular
    if 'file' not in request.files: return redirect('/')
    arquivo = request.files['file']
    if arquivo.filename == '': return redirect('/')

    if arquivo:
        caminho_salvar = os.path.join(PASTA_COMPARTILHADA, arquivo.filename)
        arquivo.save(caminho_salvar)
        add_log(f"Recebido do Celular: {arquivo.filename}")

    return "<script>window.location.href='/?tab=files';</script>"


@app.route('/get_file/<path:filename>')
def download_file(filename):
    # Envia para o Celular
    add_log(f"Enviando para celular: {filename}")
    return send_from_directory(PASTA_COMPARTILHADA, filename, as_attachment=True)