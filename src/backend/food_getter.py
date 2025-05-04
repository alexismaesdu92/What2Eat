from mistralai import Mistral
from PIL import Image
import os
import torch
import base64
from dotenv import load_dotenv
import json
import re

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
        # D'abord essayer de nettoyer le JSON
        # 1. Supprimer les espaces inutiles
        cleaned = re.sub(r'\s*"\s*', '"', json_string)
        cleaned = re.sub(r'\s*:\s*', ':', cleaned)
        cleaned = re.sub(r'\s*,\s*', ',', cleaned)
        
        # 2. Corriger les guillemets doubles répétés
        cleaned = re.sub(r'""', '"', cleaned)
        
        # 3. Corriger les guillemets autour des nombres
        cleaned = re.sub(r':("?)(\d+)("?)', r':\2', cleaned)
        
        try:
            ingredients_list = json.loads(cleaned)
        except json.JSONDecodeError:
            # Si le nettoyage automatique échoue, on tente une approche ligne par ligne
            lines = json_string.strip().split('\n')
            cleaned_lines = ['[']
            
            for line in lines:
                if line.strip() == '[' or line.strip() == ']':
                    continue
                    
                if '{' in line and '}' in line:
                    # Nettoyer la ligne
                    line = re.sub(r'[{]\s*["]?\s*ingredient\s*["]?\s*:\s*["]?\s*([^"]*?)\s*["]?\s*,\s*["]?\s*amount\s*["]?\s*:\s*["]?\s*(\d+)\s*["]?\s*[}]', 
                                r'{"ingredient":"\1","amount":\2}', line)
                    
                    # Ajouter la virgule si nécessaire
                    if not line.strip().endswith(',') and '}' in line:
                        line = line.rstrip() + ','
                    
                    cleaned_lines.append(line)
            
            # Retirer la virgule de la dernière ligne
            if cleaned_lines[-1].endswith(','):
                cleaned_lines[-1] = cleaned_lines[-1][:-1]
                
            cleaned_lines.append(']')
            cleaned = '\n'.join(cleaned_lines)
            
            ingredients_list = json.loads(cleaned)
        
        # Normaliser les résultats
        normalized_ingredients = []
        for item in ingredients_list:
            # Gérer les clés avec ou sans espaces
            ingredient_key = next((k for k in item.keys() if 'ingredient' in k.lower()), '')
            amount_key = next((k for k in item.keys() if 'amount' in k.lower()), '')
            
            ingredient = item.get(ingredient_key, '')
            amount = item.get(amount_key, 0)
            
            # Assurer que amount est un entier
            if isinstance(amount, str):
                # Nettoyer et convertir
                amount = re.sub(r'[^\d]', '', amount)
                amount = int(amount) if amount else 0
            
            normalized_ingredients.append({
                "ingredient": ingredient.strip(),
                "amount": amount
            })
            
        return normalized_ingredients
    except Exception as e:
        print(f"Erreur lors de l'analyse JSON: {e}")
        print(json_string)
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

        Return a clean JSON array with EXACT formatting:
        [
            {"ingredient": <ingredient1>, "amount": <amount1>},
            {"ingredient": <ingredient2>, "amount": <amount2>},
            ...
        ]

        CRITICAL FORMATTING RULES:
        - Use ONLY double quotes (") for keys and string values
        - amount must be a NUMBER without any quotes
        - NO spaces before or after colons
        - NO spaces inside keys or between quotes
        - EXACT syntax with no variations

        The output must be a Parsable JSON. It must have exactly the same structure all along
        """

        

        messages = [{"role": "system", "content": prompt_system},
                    {"role": "user", "content": content},
                    {"role": "user", "content": format_prompt}]
        
        response = self.client.chat.complete(
            model = "pixtral-12b-2409",
            messages = messages,
            temperature = 0.1,
            max_tokens = 1000,
            top_p = 0.9,
            frequency_penalty=1,
        )
        output = response.choices[0].message.content
        return parse_ingredients_json(extract_json_from_response(output))
    
    def get_ingredients2(self, image_path):
        # ÉTAPE 1: Utiliser le modèle multimodal uniquement pour identifier les ingrédients
        encoded = encode_image_to_base64(image_path)
        content = [{"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded}"}}]
        
        simple_prompt = "List all the ingredients visible in this image. Return only ingredient names separated by commas, nothing else. Count them only once  and do not repeat them in your answer. Be as precise as possible. Do not add any other information."
        
        messages = [
            {"role": "system", "content": "You are a food ingredient detection agent."},
            {"role": "user", "content": content},
            {"role": "user", "content": simple_prompt}
        ]
        
        response = self.client.chat.complete(
            model="pixtral-12b-2409",
            messages=messages,
            temperature=0.1,
            max_tokens=300  # Moins de tokens nécessaires pour une liste simple
        )
        
        # ÉTAPE 2: Construire le JSON manuellement
        ingredient_text = response.choices[0].message.content.strip()
        print(ingredient_text)
        ingredient_list = [item.strip() for item in ingredient_text.split(',')]
        
        # Créer la structure JSON nous-mêmes

        
        return ingredient_list
        





if __name__ == '__main__':
    client = IngredientExtractor()
    image_path = "foodPicture/photo_ingredient2.png"
    print(client.get_ingredients2(image_path))
