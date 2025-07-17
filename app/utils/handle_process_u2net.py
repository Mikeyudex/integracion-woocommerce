import cv2
import numpy as np
import torch
import torchvision.transforms as transforms
from PIL import Image
import os
import gc
import threading

# Definir modelo
from torch import nn

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'models', 'u2net.pth')

class DummyU2NET(nn.Module):
    def __init__(self):
        super(DummyU2NET, self).__init__()

    def forward(self, x):
        return [x] * 7  # Dummy output

# Singleton para el modelo (OPTIMIZACIÓN PRINCIPAL)
class ModelSingleton:
    _instance = None
    _model = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_model(self):
        if self._model is None:
            with self._lock:
                if self._model is None:
                    print("🔄 Cargando modelo U2Net una sola vez...")
                    self._model = self._load_model()
                    print("✅ Modelo cargado y listo")
        return self._model
    
    def _load_model(self):
        from app.utils.u2net import U2NET
        model = U2NET(3, 1)
        model.load_state_dict(torch.load(MODEL_PATH, map_location='cpu'))
        model.eval()
        
        # Configurar para CPU con threading optimizado
        torch.set_num_threads(2)  # Limitar threads para 2GB RAM
        
        return model

# Instancia global del singleton
model_singleton = ModelSingleton()

def load_model(model_path):
    """Función mantenida para compatibilidad, pero ahora usa singleton"""
    return model_singleton.get_model()

def optimize_image_for_memory(image):
    """Optimizar imagen para reducir uso de memoria"""
    w, h = image.size
    
    # Si la imagen es muy grande, pre-redimensionar
    if max(w, h) > 640:
        ratio = 640 / max(w, h)
        new_w = int(w * ratio)
        new_h = int(h * ratio)
        image = image.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    return image

# Procesar una imagen (OPTIMIZADA)
def remove_background_u2net(image_path, output_path):
    """Función optimizada que reutiliza el modelo singleton"""
    
    try:
        # Cargar modelo (solo una vez gracias al singleton)
        model = load_model(MODEL_PATH)
        
        # Preprocesar imagen con optimizaciones
        image = Image.open(image_path).convert('RGB')
        original_size = image.size
        
        # Optimizar tamaño si es necesario
        image = optimize_image_for_memory(image)
        
        transform = transforms.Compose([
            transforms.Resize((320, 320)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406],
                                 [0.229, 0.224, 0.225])
        ])
        
        # Ejecutar modelo con optimizaciones de memoria
        with torch.no_grad():
            input_tensor = transform(image).unsqueeze(0)
            
            # Inferencia
            outputs = model(input_tensor)
            d1 = outputs[0] if isinstance(outputs, (list, tuple)) else outputs
            
            pred = d1[0][0]
            mask = pred.cpu().numpy()
            
            # Limpiar tensores inmediatamente
            del input_tensor, d1, pred, outputs
            
            # Procesar máscara
            mask = (mask - mask.min()) / (mask.max() - mask.min())
            mask = cv2.resize(mask, original_size)
            mask = (mask * 255).astype(np.uint8)

        # Convertir la imagen original y la máscara a formato OpenCV
        # Usar la imagen original en su tamaño completo
        original_image = Image.open(image_path).convert('RGB')
        original_cv = cv2.cvtColor(np.array(original_image), cv2.COLOR_RGB2BGR)

        # Crear imagen blanca del mismo tamaño
        white_bg = np.full_like(original_cv, 255)

        # Usar la máscara como alfa: combinar foreground (objeto) con fondo blanco
        mask_normalized = mask.astype(float) / 255.0
        mask_3ch = np.stack([mask_normalized]*3, axis=2)

        # Combinar píxel a píxel
        result = original_cv * mask_3ch + white_bg * (1 - mask_3ch)
        result = result.astype(np.uint8)

        # Guardar imagen final con fondo blanco
        cv2.imwrite(output_path, result)
        
        # Limpiar memoria explícitamente
        del mask, original_cv, white_bg, mask_normalized, mask_3ch, result, original_image
        gc.collect()
        
        print(f"✅ Imagen procesada con fondo blanco: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error procesando imagen: {str(e)}")
        # Limpiar memoria en caso de error
        gc.collect()
        return False

# Función para limpiar el modelo (llamar al shutdown)
def cleanup_model():
    """Limpiar modelo de la memoria"""
    model_singleton._model = None
    gc.collect()
    print("🧹 Modelo limpiado de memoria")