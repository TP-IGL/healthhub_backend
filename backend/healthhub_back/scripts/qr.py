import qrcode
from io import BytesIO
import base64
from PIL import Image
import pyzbar.pyzbar as pyzbar

# 1. Generate a QR code and convert it to base64 (simulates backend storage)
data = {
    "patientID": "123",
    "nom": "Doe",
    "prenom": "John",
    "NSS": "987654321"
}
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)
qr.add_data(str(data))
qr.make(fit=True)
qr_image = qr.make_image(fill_color="black", back_color="white")

# Convert QR code to base64 string
buffer = BytesIO()
qr_image.save(buffer, format="PNG")
qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()

# 2. Simulate storing and retrieving the QR code as base64
print("Base64 QR Code:", qr_code_base64)

# Decode the base64 string back to an image
qr_code_data = base64.b64decode(qr_code_base64)
qr_code_image = Image.open(BytesIO(qr_code_data))

# 3. Decode the QR code to extract the data
decoded_data = pyzbar.decode(qr_code_image)
for obj in decoded_data:
    print("Decoded QR Code Data:", obj.data.decode())
