from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from app.services.auth_service import verify_token
from app.services.media_service import upload_image_to_woocommerce
from app.utils.remove_background import handle_remove_background

router = APIRouter(prefix="/media", tags=["Media"])

@router.post("/upload")
async def upload_image(file: UploadFile = File(...), user=Depends(verify_token)):
    try:
        result = await upload_image_to_woocommerce(file)
        return {"id": result["id"], "url": result["source_url"]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/remove_background")
async def remove_background(
    file: UploadFile = File(...),
    user=Depends(verify_token)
):
    try:
        result = handle_remove_background(file)
        return {"id": result["id"], "url": result["source_url"]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))