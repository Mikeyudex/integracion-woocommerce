import requests
import base64
from fastapi import UploadFile
from app.configs import Config

def upload_image_to_woocommerce(file: UploadFile) -> dict:
    url = f"{Config.WC_URL}/wp-json/wp/v2/media"

    auth_str = f"{Config.WC_KEY}:{Config.WC_SECRET}"
    b64_auth = base64.b64encode(auth_str.encode()).decode()

    headers = {
        "Authorization": f"Basic {b64_auth}",
        "Content-Disposition": f"attachment; filename={file.filename}",
        "Content-Type": file.content_type or "image/jpeg",
    }

    file_bytes = file.file.read()

    response = requests.post(url, headers=headers, data=file_bytes)

    if response.status_code in [200, 201]:
        return response.json()  # contiene el id, url, etc.
    else:
        raise Exception(f"Error al subir la imagen: {response.text}")
