import json
import os

"""
Ce fichier a pour but de tenir à jour la liste des recettes présente dans ma database

"""

def load_recipes_db(db_name="recettes.json"):
    if not os.path.exists(db_name) or os.stat(db_name).st_size == 0:
        with open(db_name, "w", encoding="utf-8") as f:
            json.dump({}, f)
        return {}
    
    with open(db_name, "r", encoding="utf-8") as f:
        return json.load(f)

def save_recipes_db(recipes: dict, db_name: str) -> None:
    with open(db_name, "w", encoding = "utf-8") as f:
        json.dump(recipes, f, indent = 2, ensure_ascii=False)

def add_recipe_to_db(db_name: str, recipe: str, url: str) -> None:
    recipe_db = load_recipes_db(db_name=db_name)
    if recipe in recipe_db:
        if not url in recipe_db[recipe]:
            recipe_db[recipe].append(url)
    else:
        recipe_db[recipe] = [url]
    save_recipes_db(recipe_db, db_name)


if __name__ == '__main__':

    url1 = "https://www.marmiton.org/recettes/recette_poke-bowl-a-l-hawaienne_344558.aspx"
    url2 = "https://www.marmiton.org/recettes/recette_flan-au-citron-facile_35882.aspx"

    db_name = "recettes.json"
    add_recipe_to_db(db_name, "poke bowl", url1)
    add_recipe_to_db(db_name, "flan au citron", url2)



