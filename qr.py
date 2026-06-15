import qrcode
import sys

repo_url = "https://github.com/PlayfulHands/handmade-platform"

output_filename = "github_repo_qr.png"

print(f"Создаю QR-код для: {repo_url}")

qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)
qr.add_data(repo_url)
qr.make(fit=True)


img = qr.make_image(fill_color="black", back_color="white")
img.save(output_filename)

print(f"Готово! QR-код сохранён как '{output_filename}'")