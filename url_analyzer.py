import requests 
from bs4 import BeautifulSoup



class ExtracterMarmiton:
    
    def get_ingredients(self, url: str) -> dict:
        '''
        Cette méthode  prend en entrée un lien url et renvoie en sortie un dictionnaire des ingrédients utilisés dans la recette.
        Inclus les quantités requises
        '''
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            ingredients = soup.find_all("div", class_="card-ingredient")
            liste_ingredients = []
            #print("Ingrédients :\n")
            for ing in ingredients:
                quantite = ing.select_one(".card-ingredient-quantity .count")
                unite = ing.select_one(".card-ingredient-quantity .unit")
                nom = ing.select_one(".ingredient-name")
                complement = ing.select_one(".ingredient-complement")

                texte = ""
                dico = {}
                if quantite:
                    amount = quantite.get_text(strip=True)
                    dico['quantite'] = amount
                    texte += amount + " "
                else:
                    dico['quantite'] = None
                if unite:
                    unit = unite.get_text(strip=True)
                    texte += unit + " "
                    dico["unit"] = unit
                else:
                    dico["unit"] = None
                if nom:
                    name =  nom.get_text(strip=True)
                    texte += name
                    dico['name'] = name
                else:
                    dico['name'] = None

                if complement:
                    comp = complement.get_text(strip=True)
                    if comp:
                        dico["complement"] = comp
                        texte += " " + comp
                    else:
                        dico["complement"] = None
                else:
                    dico["complement"] = None

                #print("- " + texte.strip())
                liste_ingredients.append(dico)
            return liste_ingredients
        else:
            #print("Erreur :", response.status_code)
            return None


    def get_preparation_steps(self, url):
        ''' Cette fonction prend en entrée un lien URL d'une recette marmiton et renvoie les étapes de préparation de la recette'''
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # Chaque étape est dans un bloc avec cette classe
            etapes = soup.find_all("div", class_="recipe-step-list__container")

            liste_etapes = []

            for i, etape in enumerate(etapes, start=1):
                texte = etape.find("p")
                if texte:
                    liste_etapes.append({
                        "etape": i,
                        "instruction": texte.get_text(strip=True)
                    })

            return liste_etapes
        else:
            return None
        
    def get_recipe_title(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # On essaie de trouver la balise <h1> (souvent utilisée pour le titre)
            titre = soup.find("h1")
            if titre:
                return titre.get_text(strip=True)
            else:
                return None
        else:
            return None
        
class IngredientsFormater:
    
    def format_ingredients(self, list_ingredients):
        text = ''
        for i, ingredient in enumerate(list_ingredients):
            text += f"ingredient {i+1}: {ingredient['name']}" + '\n'
    
        return text 



    
if __name__ == '__main__':
    url1 = "https://www.marmiton.org/recettes/recette_poke-bowl-a-l-hawaienne_344558.aspx"
    url2 = "https://www.marmiton.org/recettes/recette_flan-au-citron-facile_35882.aspx"
    extracter = ExtracterMarmiton()
    print(IngredientsFormater().format_ingredients(extracter.get_ingredients(url1)))


