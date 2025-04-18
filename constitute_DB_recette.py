from mistralai import Mistral

import os
import torch
from dotenv import load_dotenv



device = torch.device("cuda" if torch.cuda.is_available() else
                      "mps" if torch.backends.mps.is_available() else 
                      "cpu")

class RecipeNameGetter:
    """Cet agent a pour objectif d'extraire le nom d'une recette depuis le titre du site internet
        ainsi: Recette 
    """

    def __init__(self):
        load_dotenv()
        API_KEY = os.getenv("API_KEY")
        if not API_KEY:
            raise ValueError("La clé MISTRAL_API_KEY n'est pas définie")
        self.client = Mistral(api_key = API_KEY)

    
    def get_recipe_name(self, recipe_title):
        prompt = "Tu es un agent spécialisé dans l'extration d'information. Ton objectif est trouver le nom du plat depuis le titre de la recette. Tu dois donc retirer tous les qualificatifs autour du nom de la recette."+ \
                "par exemple:\n" + \
                "recette de tarte au citron facile devient tarte au citron \n" + \
                "pokebowl à l'hawaienne devient pokebowl \n" + \
                f"La recette que tu dois analyser est: {recipe_title}\n" +\
                "réponds exclusivement par le nom de la recette, la recette doit être donnée en caractère minuscule sans caractère accentué."
         
        
        content = [
            {"type": "text", "text": prompt}
        ]

        messages = [{"role": "user", 
                     "content": content}]
        response = self.client.chat.complete(
            model = "mistral-small-latest",
            messages = messages
        )
        return response.choices[0].message.content
    

if __name__ == '__main__':
    recipe_name_getter = RecipeNameGetter()
    print(recipe_name_getter.get_recipe_name("recette boeuf bourguignon"))
