import time
from flask import Response
import io
import pyautogui
from src.config import app, add_log


def generate_frames():
    """Gera um fluxo de imagens (MJPEG) usando PyAutoGUI (Mais compatível)"""
    print("🎥 Iniciando stream de tela...")

    while True:
        try:
            # Captura a tela
            img = pyautogui.screenshot()

            # Reduz o tamanho
            # Reduz para 600px de largura mantendo a proporção
            base_width = 600
            w_percent = (base_width / float(img.size[0]))
            h_size = int((float(img.size[1]) * float(w_percent)))
            img = img.resize((base_width, h_size))

            # Desenha o cursor
            mouse_x, mouse_y = pyautogui.position()
            scale_x = img.width / pyautogui.size().width
            scale_y = img.height / pyautogui.size().height

            # Posição do mouse na imagem pequena
            cx = int(mouse_x * scale_x)
            cy = int(mouse_y * scale_y)

            # Desenha uma bolinha vermelha manual
            try:
                from PIL import ImageDraw
                draw = ImageDraw.Draw(img)
                draw.ellipse((cx - 5, cy - 5, cx + 5, cy + 5), fill="red", outline="white")
            except:
                pass

            # Converte para Bytes
            frame_buffer = io.BytesIO()
            img.save(frame_buffer, format="JPEG", quality=30)
            frame_bytes = frame_buffer.getvalue()


            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


            time.sleep(0.1)

        except Exception as e:
            print(f"Erro no stream: {e}")
            time.sleep(1)


@app.route('/video_feed')
def video_feed():
    add_log("Iniciando Espelhamento (Modo Seguro)")
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')