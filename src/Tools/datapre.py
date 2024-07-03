import torch
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import numpy as np
from sklearn.preprocessing import StandardScaler

class DataPreprocessor:
    def __init__(self, model_name='openai/clip-vit-base-patch32'):
        self.processor = CLIPProcessor.from_pretrained(model_name)
        self.model = CLIPModel.from_pretrained(model_name)
        self.scaler = StandardScaler()

    def preprocess_text(self, text):
        inputs = self.processor(text=text, return_tensors="pt", padding=True, truncation=True)
        with torch.no_grad():
            outputs = self.model.get_text_features(**inputs)
        return outputs.numpy()

    def preprocess_image(self, image_path):
        image = Image.open(image_path)
        inputs = self.processor(images=image, return_tensors="pt")
        with torch.no_grad():
            outputs = self.model.get_image_features(**inputs)
        return outputs.numpy()

    def preprocess(self, data):
        if isinstance(data, str) and data.lower().endswith(('jpg', 'jpeg', 'png', 'bmp')):
            return self.preprocess_image(data)
        elif isinstance(data, str):
            return self.preprocess_text(data)
        else:
            raise ValueError("Unsupported data type")

# Example usage:
preprocessor = DataPreprocessor()

# Preprocess text
text_vector = preprocessor.preprocess("This is a sample text.")
print("Text Vector:", text_vector)

# # Preprocess image
# image_vector = preprocessor.preprocess("/path/to/your/image.jpg")
# print("Image Vector:", image_vector)
