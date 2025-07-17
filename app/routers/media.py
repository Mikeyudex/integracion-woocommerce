from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from app.services.auth_service import verify_token
from app.services.media_service import upload_image_to_woocommerce
from app.utils.remove_background import handle_remove_background

import asyncio
import psutil
import gc

router = APIRouter(prefix="/media", tags=["Media"])

# Semáforo para limitar requests simultáneas (máximo 2 para tu caso)
background_semaphore = asyncio.Semaphore(2)

def check_memory_usage():
    """Verificar uso de memoria"""
    memory = psutil.virtual_memory()
    memory_percent = memory.percent
    
    if memory_percent > 90:  # Si usa más del 90%
        print(f"⚠️ Uso de memoria alto: {memory_percent}%")
        gc.collect()  # Forzar garbage collection
        
    return memory_percent

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
    """Endpoint optimizado para remover fondo"""
    
    # Verificar memoria antes de procesar
    memory_usage = check_memory_usage()
    if memory_usage > 90:
        raise HTTPException(
            status_code=503, 
            detail="Servidor con alta carga de memoria. Intenta más tarde."
        )
    
    # Validar archivo
    if not file.filename:
        raise HTTPException(status_code=400, detail="No se proporcionó archivo")
    
    # Validar tipo de archivo
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
    import os
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Formato no soportado. Use: {', '.join(allowed_extensions)}"
        )
    
    # Usar semáforo para limitar requests simultáneas
    async with background_semaphore:
        try:
            # Procesar en hilo separado para no bloquear FastAPI
            loop = asyncio.get_event_loop()
            
            # la función existente, pero ejecutada de forma asíncrona
            result = await loop.run_in_executor(None, handle_remove_background, file)
            
            # Verificar memoria después del procesamiento
            final_memory = check_memory_usage()
            
            # Agregar información de memoria a la respuesta
            response = {
                "id": result["id"], 
                "url": result["source_url"],
                "memory_usage": f"{final_memory:.1f}%"
            }
            
            return response
            
        except Exception as e:
            print(f"❌ Error en remove_background: {str(e)}")
            
            # Limpiar memoria en caso de error
            gc.collect()
            
            raise HTTPException(status_code=500, detail=f"Error procesando imagen: {str(e)}")

# Endpoint adicional para monitorear salud del servidor
@router.get("/health")
async def health_check():
    """Endpoint para verificar salud del servidor"""
    memory = psutil.virtual_memory()
    
    return {
        "status": "healthy",
        "memory_usage": f"{memory.percent:.1f}%",
        "memory_available": f"{memory.available / (1024**3):.2f} GB"
    }