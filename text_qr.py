import qrcode
from PIL import Image

try:

    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=4,
    )
    qr.add_data("https://google.com")
    qr.make(fit=True)


    img = qr.make_image(fill_color="black", back_color="white")
    img.save("qrcode.png")
    
    print("QRCode object & image created successfully.")
except Exception as e:
    print(f"Error: {e}")