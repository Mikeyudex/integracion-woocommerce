import requests
from requests.auth import HTTPBasicAuth
from app.configs import Config

def upload_image_to_woocommerce(file_bytes: bytes, filename: str, content_type: str) -> dict:
    url = f"{Config.WC_URL}/wp-json/wp/v2/media"

    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Content-Type": content_type
    }

    response = requests.post(
        url,
        headers=headers,
        data=file_bytes,
        auth=HTTPBasicAuth(Config.WC_KEY, Config.WC_SECRET)
    )

    if response.status_code not in [200, 201]:
        raise Exception(f"Error al subir la imagen: {response.text}")

    return response.json()
