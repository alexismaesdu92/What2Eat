from mistralai import Mistral
from PIL import Image
import os
import torch
import base64
from dotenv import load_dotenv
import json

device = torch.device("cuda" if torch.cuda.is_available() else
                      "mps" if torch.backends.mps.is_available() else 
                      "cpu")




def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode("utf-8")  # Décodage en string
    return encoded


def extract_json_from_response(response_text):
    # Recherche du contenu entre les backticks json
    import re
    json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response_text)
    
    if json_match:
        return json_match.group(1).strip()
    
    # Si pas de backticks spécifiques, essayer de trouver tout bloc de code
    json_match = re.search(r'```\s*([\s\S]*?)\s*```', response_text)
    if json_match:
        return json_match.group(1).strip()
    
    # Sinon, retourner le texte tel quel (peut-être que l'IA a suivi les instructions)
    return response_text.strip()

def parse_ingredients_json(json_string: str) -> list:
    try:
        # Analyser la chaîne JSON
        ingredients_list = json.loads(json_string)
        
        # Normaliser les clés pour gérer les incohérences de casse
        normalized_ingredients = []
        for item in ingredients_list:
            normalized_item = {
                "ingredient": item.get("ingredient") or item.get("Ingredient", ""),
                "amount": int(item.get("amount") or item.get("Amount", 0))
            }
            normalized_ingredients.append(normalized_item)
            
        return normalized_ingredients
    except json.JSONDecodeError as e:
        print(f"Erreur lors de l'analyse JSON: {e}")
        return []

# Exemple d'utilisation
def process_ingredients_from_api(json_string):
    ingredients = parse_ingredients_json(json_string)
    
    # Exemples d'opérations sur les ingrédients
    if ingredients:
        print(f"Nombre d'ingrédients: {len(ingredients)}")
        
        # Accéder aux données
        for ingredient in ingredients:
            print(f"{ingredient['ingredient']}: {ingredient['amount']}g")
            
        # Calculer le poids total
        total_weight = sum(ingredient['amount'] for ingredient in ingredients)
        print(f"Poids total: {total_weight}g")
        
    return ingredients



class IngredientExtractor:

    def __init__(self):
        load_dotenv()
        API_KEY = os.getenv("API_KEY")
        if not API_KEY:
            raise ValueError("La clé MISTRAL_API_KEY n'est pas définie")
        self.client = Mistral(api_key = API_KEY)

    
    def get_ingredients(self, image_path):
        # TODO: Corriger le prompt pour formater le texte en sortie
        encoded = encode_image_to_base64(image_path)
        
        content = [
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded}"}}
        ]
        prompt_system = """
        You are a food ingredient detection agent. Your task is to identify the ingredients present in the provided image
        Each ingredients must be given once and only once. You must not forget any ingredient"""
        
        format_prompt = """
        #Response format

        Return a clean JSON object with this exact structure:
        ```
        [
            {"ingredient": <ingredient1>,  "amount": <amount1>},
            {"ingredient": <ingredient2>,  "amount": <amount2>},
            ...
        ]
        ```
        Do not add any other text, explanation, or comment outside the JSON object.
        In each <ingredient> field, insert only the name of the ingredient.
        In the <amount> field, insert an rough approximation of the amount of the ingredient in grams (do not precise the unit in the field).
        Only use lowercase letters or numbers to fill the JSON.  Avoid accents and special characters.
        """

        

        messages = [{"role": "system", "content": prompt_system},
                    {"role": "user", "content": content},
                    {"role": "user", "content": format_prompt}]
        
        response = self.client.chat.complete(
            model = "pixtral-12b-2409",
            messages = messages,
            temperature = 0.2,
            top_p = 0.95,
            frequency_penalty=0.8,

        )
        output = response.choices[0].message.content
        print(f"Response: {output}")
        return parse_ingredients_json(extract_json_from_response(output))



if __name__ == '__main__':
    client = IngredientExtractor()
    image_path = "foodPicture/photo_ingredient2.png"
    print(client.get_ingredients(image_path))
