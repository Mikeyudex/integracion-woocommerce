import cv2
import numpy as np
from PIL import Image
import os
from app.utils.file_process import save_temp_file
from fastapi import UploadFile, HTTPException
from app.utils.handle_process_u2net import remove_background_u2net

def advanced_edge_refinement(image_path, output_path, color_range='green'):
    """
    Método avanzado con múltiples técnicas de refinamiento de bordes
    """
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: No se pudo cargar la imagen {image_path}")
        return False
    
    # === PASO 1: DETECCIÓN DE COLOR MEJORADA ===
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    
    # Múltiples espacios de color para mejor detección
    if color_range == 'green':
        # HSV
        mask_hsv1 = cv2.inRange(hsv, np.array([35, 30, 30]), np.array([85, 255, 255]))
        mask_hsv2 = cv2.inRange(hsv, np.array([25, 30, 30]), np.array([35, 255, 255]))
        
        # LAB (mejor para ciertos tonos de verde)
        mask_lab = cv2.inRange(lab, np.array([0, 0, 0]), np.array([120, 120, 255]))
        
        # Combinar máscaras
        mask_combined = cv2.bitwise_or(mask_hsv1, mask_hsv2)
        
    elif color_range == 'blue':
        mask_hsv1 = cv2.inRange(hsv, np.array([100, 30, 30]), np.array([130, 255, 255]))
        mask_hsv2 = cv2.inRange(hsv, np.array([90, 30, 30]), np.array([100, 255, 255]))
        mask_combined = cv2.bitwise_or(mask_hsv1, mask_hsv2)
    
    # === PASO 2: REFINAMIENTO MULTI-ESCALA ===
    # Crear múltiples versiones de la máscara con diferentes niveles de procesamiento
    masks = []
    
    # Máscara conservadora (menos área)
    mask_conservative = cv2.erode(mask_combined, np.ones((3, 3), np.uint8), iterations=1)
    mask_conservative = cv2.morphologyEx(mask_conservative, cv2.MORPH_CLOSE, np.ones((2, 2), np.uint8))
    masks.append(mask_conservative)
    
    # Máscara balanceada
    mask_balanced = cv2.morphologyEx(mask_combined, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    mask_balanced = cv2.morphologyEx(mask_balanced, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    masks.append(mask_balanced)
    
    # Máscara agresiva (más área)
    mask_aggressive = cv2.dilate(mask_combined, np.ones((2, 2), np.uint8), iterations=1)
    mask_aggressive = cv2.morphologyEx(mask_aggressive, cv2.MORPH_CLOSE, np.ones((4, 4), np.uint8))
    masks.append(mask_aggressive)
    
    # === PASO 3: DETECCIÓN DE BORDES INTELIGENTE ===
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Múltiples detectores de bordes
    edges_canny = cv2.Canny(gray, 50, 150)
    edges_sobel = cv2.Sobel(gray, cv2.CV_64F, 1, 1, ksize=3)
    edges_sobel = np.uint8(np.absolute(edges_sobel))
    
    # Combinar detecciones de bordes
    edges_combined = cv2.bitwise_or(edges_canny, edges_sobel)
    
    # === PASO 4: CREACIÓN DE MÁSCARA ADAPTATIVA ===
    # Crear máscara base
    mask_base = mask_balanced.copy()
    
    # Identificar zonas problemáticas (bordes)
    mask_dilated = cv2.dilate(mask_base, np.ones((5, 5), np.uint8), iterations=1)
    mask_eroded = cv2.erode(mask_base, np.ones((5, 5), np.uint8), iterations=1)
    border_zone = cv2.subtract(mask_dilated, mask_eroded)
    
    # En zonas de borde, usar detección más precisa
    edge_refined_mask = mask_base.copy()
    
    # Aplicar lógica adaptativa en zonas de borde
    border_pixels = np.where(border_zone > 0)
    for y, x in zip(border_pixels[0], border_pixels[1]):
        # Analizar ventana local
        y_start, y_end = max(0, y-2), min(image.shape[0], y+3)
        x_start, x_end = max(0, x-2), min(image.shape[1], x+3)
        
        local_region = hsv[y_start:y_end, x_start:x_end]
        
        # Decisión basada en varianza local de color
        if color_range == 'green':
            green_pixels = np.sum((local_region[:,:,0] >= 35) & (local_region[:,:,0] <= 85) & 
                                 (local_region[:,:,1] >= 30))
            total_pixels = local_region.shape[0] * local_region.shape[1]
            
            if green_pixels / total_pixels > 0.6:
                edge_refined_mask[y, x] = 255
            else:
                edge_refined_mask[y, x] = 0
    
    # === PASO 5: SUAVIZADO AVANZADO ===
    # Convertir a float para procesamiento preciso
    mask_float = edge_refined_mask.astype(np.float32) / 255.0
    
    # Aplicar múltiples pasadas de suavizado
    mask_smooth = cv2.GaussianBlur(mask_float, (3, 3), 0.5)
    mask_smooth = cv2.bilateralFilter(mask_smooth, 5, 10, 10)
    
    # === PASO 6: APLICACIÓN FINAL ===
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    white_background = np.ones_like(image_rgb) * 255
    
    # Invertir máscara y aplicar
    mask_inv = 1.0 - mask_smooth
    mask_3d = np.stack([mask_inv, mask_inv, mask_inv], axis=2)
    
    # Combinar con transición suave
    result = image_rgb * mask_3d + white_background * (1 - mask_3d)
    
    # Post-procesamiento final
    result = cv2.bilateralFilter(result.astype(np.uint8), 9, 75, 75)
    
    # Guardar
    result_image = Image.fromarray(result)
    result_image.save(output_path)
    print(f"Imagen con bordes refinados guardada: {output_path}")
    return True


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
        #success = remove_background_green_screen(image_path, output_path, 'green')
        success = advanced_edge_refinement(image_path, output_path, 'green')
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

def handle_remove_background(file: UploadFile): 
    input_path = save_temp_file(file)
    output_path = input_path.replace(".", "_processed.")
    remove_background_u2net(input_path, output_path)
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