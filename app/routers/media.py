# app/routers/media.py
from fastapi import APIRouter, File, UploadFile, HTTPException, status
from app.services.media_service import upload_image_to_woocommerce

router = APIRouter(prefix="/media", tags=["Media"])

@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    try:
        file_bytes = await file.read()
        result = upload_image_to_woocommerce(file_bytes, file.filename, file.content_type)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al subir imagen: {str(e)}"
        )
