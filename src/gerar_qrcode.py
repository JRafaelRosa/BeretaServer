import socket
import qrcode
import base64
from io import BytesIO
from src.config import SERVER_TOKEN

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


def gerar_qr_base64():
    ip = get_ip()

    link = f"http://{ip}:5000/?token={SERVER_TOKEN}"

    qr = qrcode.QRCode(box_size=10, border=2)
    qr.add_data(link)
    qr.make(fit=True)

    img_buffer = BytesIO()
    img = qr.make_image(fill_color="white", back_color="transparent")
    img.save(img_buffer, format="PNG")

    return base64.b64encode(img_buffer.getvalue()).decode("utf-8"), link, ip