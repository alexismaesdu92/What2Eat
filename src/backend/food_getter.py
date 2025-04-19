from mistralai import Mistral
from PIL import Image
import os
import torch
import base64
from dotenv import load_dotenv

device = torch.device("cuda" if torch.cuda.is_available() else
                      "mps" if torch.backends.mps.is_available() else 
                      "cpu")




def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode("utf-8")  # Décodage en string
    return encoded



class IngredientExtractor:

    def __init__(self):
        load_dotenv()
        API_KEY = os.getenv("API_KEY")
        if not API_KEY:
            raise ValueError("La clé MISTRAL_API_KEY n'est pas définie")
        self.client = Mistral(api_key = API_KEY)

    
    def get_ingredients(self, image_path):
        prompt = "Tu es un agent spécialisé dans la detection d'ingredient sur des images. Tu dois donc trouver la liste exhautive et exacte des ingrédients que se trouve sur l'image qui t'es donnée.\n" +\
                 "Tu dois simplement donner en sortie une liste énuméré des ingrédients en caractère minuscule non accentué"
        encoded = encode_image_to_base64(image_path)
        
        content = [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded}"}}
        ]

        messages = [{"role": "user", 
                     "content": content}]
        response = self.client.chat.complete(
            model = "pixtral-12b-2409",
            messages = messages
        )
        return response.choices[0].message.content



if __name__ == '__main__':
    client = IngredientExtractor()
    image_path = "foodPicture/photo_ingredient2.png"
    print(client.get_ingredients(image_path))
