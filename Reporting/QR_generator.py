import io
import base64
QRCODE_AVAILABLE = False
try:
    import qrcode
    QRCODE_AVAILABLE = True
except:
    pass

class QRCodeGenerator:
    @staticmethod
    def generate(data):
        if QRCODE_AVAILABLE:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(data)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            buff = io.BytesIO()
            img.save(buff, format="PNG")
            return base64.b64encode(buff.getvalue()).decode()
        return ""
