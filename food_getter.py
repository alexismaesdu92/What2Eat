from mistralai import Mistral
from PIL import Image
import os
import torch
import base64

device = torch.device("cuda" if torch.cuda.is_available() else
                      "mps" if torch.backends.mps.is_available() else 
                      "cpu")




def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode("utf-8")  # Décodage en string
    return encoded



class ClientMistral:

    def __init__(self):
        API_KEY = os.getenv("MISTRAL_API_KEY")
        if not API_KEY:
            raise ValueError("La clé MISTRAL_API_KEY n'est pas définie")
        self.client = Mistral(api_key = API_KEY)

    
    def generate_answer(self):
        prompt = "Quels sont les ingrédients présent sur l'image fais uniquement une liste"
        encoded = encode_image_to_base64("foodPicture/photo_ingredient2.png")
        
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
    client = ClientMistral()
    print(client.generate_answer())
    