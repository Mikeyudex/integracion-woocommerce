import cv2
import numpy as np
import torch
import torchvision.transforms as transforms
from PIL import Image
import os

# Definir modelo
from torch import nn

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'models', 'u2net.pth')

class DummyU2NET(nn.Module):
    def __init__(self):
        super(DummyU2NET, self).__init__()

    def forward(self, x):
        return [x] * 7  # Dummy output

def load_model(model_path):
    from app.utils.u2net import U2NET  # u2net.py con la definición del modelo
    model = U2NET(3, 1)
    model.load_state_dict(torch.load(model_path, map_location='cpu'))
    model.eval()
    return model

# Procesar una imagen
def remove_background_u2net(image_path, output_path):
    # Cargar modelo
    model = load_model(MODEL_PATH)

    # Preprocesar imagen
    image = Image.open(image_path).convert('RGB')
    transform = transforms.Compose([
        transforms.Resize((320, 320)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406],
                             [0.229, 0.224, 0.225])
    ])
    input_tensor = transform(image).unsqueeze(0)

    # Ejecutar modelo
    with torch.no_grad():
        d1, *_ = model(input_tensor)
        pred = d1[0][0]
        mask = pred.cpu().numpy()
        mask = (mask - mask.min()) / (mask.max() - mask.min())
        mask = cv2.resize(mask, image.size)
        mask = (mask * 255).astype(np.uint8)

    # Convertir la imagen original y la máscara a formato OpenCV
    original_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

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
    print(f"✅ Imagen procesada con fondo blanco: {output_path}")
    return True

# MAIN
""" if __name__ == "__main__":
    MODEL_PATH = "models/u2net.pth"
    IMAGE_PATH = "foto3.jpeg"  # <- cambia esto por tus imágenes
    OUTPUT_PATH = "foto3_u2net.jpg"

    model = load_model(MODEL_PATH)
    remove_background_u2net(IMAGE_PATH, OUTPUT_PATH, model) """
