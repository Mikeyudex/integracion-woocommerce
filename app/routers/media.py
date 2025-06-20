# app/routers/media.py
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from app.services.auth_service import verify_token
from app.services.media_service import upload_image_to_woocommerce

router = APIRouter(prefix="/media", tags=["Media"])

@router.post("/upload")
async def upload_image(file: UploadFile = File(...), user=Depends(verify_token)):
    try:
        result = upload_image_to_woocommerce(file)
        return {"id": result["id"], "url": result["source_url"]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
