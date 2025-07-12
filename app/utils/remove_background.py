import cv2
import numpy as np
from PIL import Image
import os
from app.utils.file_process import save_temp_file
from fastapi import UploadFile, HTTPException

def remove_background_auto(image_path, output_path):
    try:
        """
        Remueve el fondo automáticamente usando técnicas de segmentación
        """
        # Cargar imagen
        image = cv2.imread(image_path)
        if image is None:
            print(f"Error: No se pudo cargar la imagen {image_path}")
            return False
        
        # Convertir a RGB para PIL
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Crear máscara usando GrabCut
        mask = np.zeros(image.shape[:2], np.uint8)
        
        # Definir rectángulo que contenga el objeto principal (ajustable)
        height, width = image.shape[:2]
        rect = (int(width*0.1), int(height*0.1), int(width*0.8), int(height*0.8))
        
        # Inicializar modelos para GrabCut
        bgd_model = np.zeros((1, 65), np.float64)
        fgd_model = np.zeros((1, 65), np.float64)
        
        # Aplicar GrabCut
        cv2.grabCut(image, mask, rect, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_RECT)
        
        # Crear máscara final
        mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
        
        # Aplicar máscara y crear fondo blanco
        result = image_rgb.copy()
        
        # Crear fondo blanco donde la máscara es 0
        white_background = np.ones_like(image_rgb) * 255
        result = np.where(mask2[:, :, np.newaxis] == 1, result, white_background)
        
        # Guardar resultado
        result_image = Image.fromarray(result.astype(np.uint8))
        result_image.save(output_path)
        print(f"Imagen guardada: {output_path}")
        return True
    except Exception as e:
        print(f"Error durante el procesamiento: {e}")
        return False

def remove_background_green_screen(image_path, output_path, color_range='green'):
    try:
        """
        Remueve fondo basado en color específico (pantalla verde/azul)
        """
        # Cargar imagen
        image = cv2.imread(image_path)
        if image is None:
            print(f"Error: No se pudo cargar la imagen {image_path}")
            return False
        
        # Convertir a HSV para mejor detección de color
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Definir rangos de color
        if color_range == 'green':
            # Rango para verde (pantalla verde)
            lower_bound = np.array([35, 40, 40])
            upper_bound = np.array([85, 255, 255])
        elif color_range == 'blue':
            # Rango para azul (pantalla azul)
            lower_bound = np.array([100, 40, 40])
            upper_bound = np.array([130, 255, 255])
        else:
            print("Color no soportado. Use 'green' o 'blue'")
            return False
        
        # Crear máscara
        mask = cv2.inRange(hsv, lower_bound, upper_bound)
        
        # Aplicar operaciones morfológicas para limpiar la máscara
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        # Aplicar filtro gaussiano para suavizar bordes
        mask = cv2.GaussianBlur(mask, (5, 5), 0)
        
        # Convertir imagen a RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Crear fondo blanco
        white_background = np.ones_like(image_rgb) * 255
        
        # Aplicar máscara (invertida porque queremos remover el color detectado)
        mask_inv = cv2.bitwise_not(mask)
        mask_3d = np.stack([mask_inv, mask_inv, mask_inv], axis=2) / 255.0
        
        # Combinar imagen original con fondo blanco
        result = image_rgb * mask_3d + white_background * (1 - mask_3d)
        
        # Guardar resultado
        result_image = Image.fromarray(result.astype(np.uint8))
        result_image.save(output_path)
        print(f"Imagen guardada: {output_path}")
        return True
    except Exception as e:
        print(f"Error durante el procesamiento: {e}")
        return False

def main():
    print("=== Background Remover ===")
    print("1. Automático (GrabCut)")
    print("2. Pantalla Verde")
    print("3. Pantalla Azul")
    
    choice = input("\nSeleccione método (1-3): ")
    
    image_path = input("Ruta de la imagen de entrada: ")
    if not os.path.exists(image_path):
        print("Error: El archivo no existe")
        return
    
    # Generar nombre de archivo de salida
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    output_path = f"{base_name}_sin_fondo.png"
    
    if choice == '1':
        success = remove_background_auto(image_path, output_path)
    elif choice == '2':
        success = remove_background_green_screen(image_path, output_path, 'green')
    elif choice == '3':
        success = remove_background_green_screen(image_path, output_path, 'blue')
    else:
        print("Opción no válida")
        return
    
    if success:
        print(f"\n¡Proceso completado exitosamente!")
        print(f"Archivo guardado como: {output_path}")
    else:
        print("Error durante el procesamiento")

def handle_remove_background(file: UploadFile, type_process: str): 
    if type_process not in ["blue", "green", "auto"]:
        raise HTTPException(status_code=400, detail="Invalid type of process")
    
    input_path = save_temp_file(file)
    output_path = input_path.replace(".", "_processed.")

    if type_process == "auto":
        remove_background_auto(input_path, output_path)
    else:
        remove_background_green_screen(input_path, output_path, color_range=type_process)
    return {
        "id": os.path.basename(output_path),
        "source_url": f"/static/tmp/{os.path.basename(output_path)}"
    }

# Función para uso directo
def process_image(image_path, output_path=None, method='auto', color='green'):
    """
    Función simplificada para usar directamente
    
    Args:
        image_path: Ruta de la imagen
        output_path: Ruta de salida (opcional)
        method: 'auto' o 'chroma'
        color: 'green' o 'blue' (solo para método chroma)
    """
    if output_path is None:
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        output_path = f"{base_name}_sin_fondo.png"
    
    if method == 'auto':
        return remove_background_auto(image_path, output_path)
    elif method == 'chroma':
        return remove_background_green_screen(image_path, output_path, color)
    else:
        print("Método no válido. Use 'auto' o 'chroma'")
        return False

if __name__ == "__main__":
    main()