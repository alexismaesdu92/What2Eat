from mistralai import Mistral

import os
import torch
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import time
from pymilvus import MilvusClient
from tqdm import tqdm

from backend.url_analyzer import ExtracterMarmiton, IngredientsFormater
from backend.milvus_DB_Manager import CollectionCreator, Indexor, Retriever
from backend.encoder import Encoder
from backend.categorizer import Categorizer

device = torch.device("cuda" if torch.cuda.is_available() else
                      "mps" if torch.backends.mps.is_available() else 
                      "cpu")

def url_exists(url):
    try:
        response = requests.get(url, timeout = 5)
        return response.status_code == 200
    except requests.RequestException:
        return False



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
                "réponds exclusivement par le nom de la recette, la recette doit être donnée en caractère minuscule sans caractère accentué ou apostrophe."
         
        
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

class Scraper:
    def __init__(self, extracter: ExtracterMarmiton, root: str = "https://www.marmiton.org/recettes"):
        self.root = root
        self.extracter = extracter
        self.formater = IngredientsFormater()
    
    def search_recipe_on_page(self, url):
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url = self.root, headers=headers)
        if response.status_code != 200:
            print(f"Erreur {response.status_code} pour l'URL : {url}")
            return []
        soup = BeautifulSoup(response.content, "html.parser")
        liens = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "recettes/recette_" in href:
                liens.append(href)
        return liens
    
    def search_on_website(self, indexor: Indexor, categorizer: Categorizer, recipe_name_getter: RecipeNameGetter)-> None:
        iPage = 50
        i = 1
        while True and iPage < 55:
            url = self.root + f"?page={iPage}"
            if url_exists(url):
                liens = self.search_recipe_on_page(url)
                for url_recipe in tqdm(liens):
                    #Extraction du titre de la recette puis récupération nom recette
                    recipe_title= self.extracter.get_recipe_title(url_recipe)
                    recipe_name = recipe_name_getter.get_recipe_name(recipe_title)
                    time.sleep(3.5)#Avoid timeout -> < 15 req/min

                    ingredients = self.formater.format_ingredients(self.extracter.get_ingredients(url_recipe))
                    indexor.index(recipe_name, url_recipe, ingredients)

                    categorizer.add_recipe_to_db(recipe_name, url_recipe)
                    i += 1
                print(f"traitement de la page {iPage} terminé !")
                iPage += 1
                time.sleep(4)#Avoid time out 
            else:
                print("j'arrive pas à me connecter")


if __name__ == '__main__':
    recipe_name_getter = RecipeNameGetter()
    extracter = ExtracterMarmiton()

    
    encoder = Encoder()
    db_path = "data/recipe.db"
    client = MilvusClient(db_path)
    collection_name = "recipe"
    #collection_creator = CollectionCreator(client, collection_name)
    #collection_creator.create_collection()
    indexor = Indexor(client, collection_name, encoder)
    #indexor.create_index()

    categorizer = Categorizer()
    scraper = Scraper(extracter)
    
    scraper.search_on_website(indexor, categorizer, recipe_name_getter)

    #retriever = Retriever(client=client, encoder=encoder, collection_name=collection_name)

    #hits = retriever.retrieve("je mets ce qque je veux99")
    #print(recipe_name_getter.get_recipe_name("recette boeuf bourguignon"))
