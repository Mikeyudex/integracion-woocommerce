import base64
import httpx
from fastapi import UploadFile
from app.configs import Config



async def upload_image_to_woocommerce(file: UploadFile) -> dict:
    try:
        url = f"{Config.WC_URL}/wp-json/wp/v2/media"

        # Generar header de autenticación básica
        auth_header = base64.b64encode(
            f"{Config.WORDPRESS_USERNAME}:{Config.WORDPRESS_APP_PASSWORD}".encode()
        ).decode()

        headers = {
            "Authorization": f"Basic {auth_header}"
        }

        file_bytes = file.file.read()

        async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers={
                        **headers,
                        "Content-Disposition": f'attachment; filename="{file.filename}"',
                        "Content-Type": file.content_type
                    },
                    content=file_bytes
                )


        if response.status_code == 201:
                return response.json()
        else:
            raise Exception(f"Error al subir la imagen: {response.json()}")
    except Exception as e:
        raise Exception(f"Error al subir la imagen: {e}")